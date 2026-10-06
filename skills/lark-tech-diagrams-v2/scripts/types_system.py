"""Six system views: semantic ownership first, Canvas geometry second.

No shared Canvas, routing or validation code is changed by this module.
"""
from collections import defaultdict
from copy import deepcopy
from math import ceil

try:
    from .canvas import Canvas
    from .types_structure import _ports, _route, _compact, _crossing_gaps, _ranks
except ImportError:
    from canvas import Canvas
    from types_structure import _ports, _route, _compact, _crossing_gaps, _ranks

SYSTEM_TYPES = ('c4_context', 'c4_container', 'c4_component',
                'layered_architecture', 'deployment', 'network_topology')
C4_LEVELS = {'c4_context': 'system', 'c4_container': 'container', 'c4_component': 'component'}
DIRECTIONS = {'directed', 'bidirectional', 'undirected', 'unspecified'}


def _kind(spec, node):
    return node.get('kind', 'instance' if spec['diagram_type'] == 'deployment' else '')


def _direction(spec, edge):
    return edge.get('direction', spec.get('communication_direction', 'unspecified'))


def _contract(spec):
    errors = []
    def fail(code, **details): errors.append({'code': code, **details})
    typ = spec.get('diagram_type')
    if typ not in SYSTEM_TYPES:
        return errors
    ns, es, gs = spec.get('nodes', []), spec.get('edges', []), spec.get('groups', [])
    ids = [n['id'] for n in ns]
    groups = {g['id']: g for g in gs}
    byid = {n['id']: n for n in ns}
    if not ns: fail('system-empty-nodes')
    if len(ids) != len(set(ids)): fail('system-duplicate-node')
    if len(groups) != len(gs): fail('system-duplicate-group')
    if len({e['id'] for e in es}) != len(es): fail('system-duplicate-edge')
    for e in es:
        if e.get('source') not in byid or e.get('target') not in byid:
            fail('system-unknown-endpoint', edge=e['id'])
        if not e.get('label'): fail('system-unlabelled-edge', edge=e['id'])
        if typ != 'network_topology' and e.get('direction', 'directed') != 'directed':
            fail('system-relationship-direction-conflict', edge=e['id'])
    for n in ns:
        if n.get('group') and n['group'] not in groups:
            fail('system-unknown-boundary', node=n['id'])
    if typ in C4_LEVELS:
        level = C4_LEVELS[typ]
        allowed = {'person', 'external', level}
        # An external container is an allowed collaborator of a component view,
        # but never silently placed inside the focused container boundary.
        if typ == 'c4_component': allowed.add('container')
        for n in ns:
            k = _kind(spec, n)
            if k not in allowed: fail('c4-mixed-abstraction', node=n['id'], expected=level, actual=k)
            if k == level and not n.get('group'): fail('c4-missing-owner', node=n['id'])
            if k in ('person', 'external') and n.get('group'): fail('c4-external-inside-boundary', node=n['id'])
        if typ == 'c4_context':
            focal = [n for n in ns if n.get('kind') == 'system']
            if len(focal) != 1: fail('c4-context-single-focus')
        if len(gs) != 1: fail('c4-single-focus-boundary')
        expected = 'container-boundary' if typ == 'c4_component' else 'system-boundary'
        for g in gs:
            if g.get('kind') != expected: fail('c4-boundary-level', group=g['id'], expected=expected)
        if typ == 'c4_component':
            for n in ns:
                if n.get('kind') == 'container' and n.get('group'):
                    fail('c4-collaborator-inside-focus', node=n['id'])
    elif typ == 'layered_architecture':
        orders = [g.get('order') for g in gs]
        if not gs or any(not isinstance(o, int) or isinstance(o, bool) for o in orders) or len(set(orders)) != len(orders):
            fail('layer-order-required-and-unique')
        for g in gs:
            if g.get('kind') != 'layer':
                fail('layer-group-kind', group=g['id'])
        for n in ns:
            if n.get('group') not in groups:
                fail('layer-member-owner-required', node=n['id'])
        for e in es:
            a, b = byid.get(e.get('source'), {}), byid.get(e.get('target'), {})
            ga, gb = groups.get(a.get('group'), {}), groups.get(b.get('group'), {})
            if ga.get('order', 0) > gb.get('order', 0) and not e.get('allow_upward'):
                fail('layer-upward-dependency-needs-rationale', edge=e['id'])
            if e.get('allow_upward') and not e.get('rationale'):
                fail('layer-upward-rationale-missing', edge=e['id'])
    elif typ == 'deployment':
        for n in ns:
            if _kind(spec, n) != 'instance':
                fail('deployment-instance-kind', node=n['id'])
            if n.get('group') not in groups: fail('deployment-instance-region', node=n['id'])
    elif typ == 'network_topology':
        for g in gs:
            if g.get('kind') not in ('security-zone', 'network-segment'):
                fail('network-security-zone-kind', group=g['id'])
            if g.get('kind') == 'network-segment' and g.get('trust'):
                fail('network-neutral-segment-has-trust', group=g['id'])
        for n in ns:
            if n.get('kind') not in ('router', 'switch', 'firewall', 'service', 'store', 'external', 'client', 'host'):
                fail('network-node-kind', node=n['id'])
            if n.get('group') not in groups: fail('network-zone-membership', node=n['id'])
        for e in es:
            if _direction(spec, e) not in DIRECTIONS: fail('network-invalid-direction', edge=e['id'])
    return errors


def _group_title(spec, group):
    typ = spec['diagram_type']
    label = group.get('label', group['id'])
    if typ in C4_LEVELS:
        suffix = '容器边界' if typ == 'c4_component' else '系统边界'
        if typ == 'c4_component' and group.get('parent_system'): label = group['parent_system'] + ' / ' + label
        return label + ' · ' + suffix
    if typ == 'layered_architecture':
        return label + (' · ' + group['responsibility'] if group.get('responsibility') else '')
    if typ == 'network_topology':
        if group.get('kind') == 'network-segment':
            return label + ' · 拓扑分组'
        return label + ' · 安全区域' + (' / ' + group['trust'] if group.get('trust') else '')
    return label


def _lines(spec, n):
    typ = spec['diagram_type']; k = _kind(spec, n)
    labels = {'person': '[Person]', 'external': '[External System]', 'system': '[Software System]',
              'container': '[Container]', 'component': '[Component]', 'router': '«router» 路由设备',
              'switch': '«switch» 交换机', 'firewall': '«firewall» 防火墙',
              'client': '«client» 终端', 'host': '«host» 主机',
              'service': '«service» 网络服务', 'store': '«store» 数据存储', 'instance': '«deployment instance»'}
    result = [labels.get(k, '«module» 层内模块')] + list(n.get('lines', []))
    fields = ('artifact', 'runtime') if typ == 'deployment' else ('responsibility', 'technology')
    result += [str(n[key]) for key in fields if n.get(key)]
    # Missing technology is deliberately omitted; a node name is not evidence
    # for a particular language, framework or execution runtime.
    if typ == 'layered_architecture':
        result[0] = '«module» 层内模块'
    return result


def _network_tree(spec):
    """Orient geometry only: require a simple tree and connected ownership sets.

    Contracting connected groups in a tree gives another tree. Packing those
    group subtrees separately therefore cannot enclose a foreign member.
    Input edge direction is never used as (or replaced by) layout direction.
    """
    ns, es, gs = spec['nodes'], spec.get('edges', []), spec.get('groups', [])
    if len(es) != len(ns)-1:
        return None
    adjacent = {n['id']: [] for n in ns}
    for e in es:
        a, b = e['source'], e['target']
        if a == b or b in adjacent[a]:
            return None
        adjacent[a].append(b); adjacent[b].append(a)
    byid = {n['id']: n for n in ns}
    order = {n['id']: i for i, n in enumerate(ns)}
    # An explicit external leaf is a useful visual entry; otherwise prefer
    # a routing device, then a branching vertex. IDs and labels are opaque.
    root = min(adjacent, key=lambda i: (
        0 if byid[i]['kind'] == 'external' and len(adjacent[i]) <= 1 else
        1 if byid[i]['kind'] == 'router' else 2, -len(adjacent[i]), order[i]))
    parent = {root: None}; traversal = [root]
    for i in traversal:
        for j in adjacent[i]:
            if j not in parent:
                parent[j] = i; traversal.append(j)
    if len(parent) != len(ns):
        return None
    members = {g['id']: [n['id'] for n in ns if n['group'] == g['id']] for g in gs}
    for ids in members.values():
        if not ids:
            return None
        owned = set(ids)
        if sum(j in owned for i in ids for j in adjacent[i]) != 2*(len(ids)-1):
            return None
    return parent, traversal, members


def _network_tree_boxes(spec, c, sizes, tree, margin, start_y, inset, gapy, spacing, stub):
    """Pack non-overlapping ownership rectangles as a top-down group tree."""
    parent, traversal, members = tree
    ns, gs = spec['nodes'], spec['groups']
    owner = {n['id']: n['group'] for n in ns}
    pad, header = c.S['padding'], c.S['panel_header']
    children = defaultdict(list); branches = defaultdict(list); roots = {}
    for i in traversal:
        p = parent[i]; gid = owner[i]
        if p is None or owner[p] != gid:
            roots[gid] = i
            if p is not None: branches[owner[p]].append(gid)
        else:
            children[p].append(i)
    # Label width budgets space between sibling branches; vertical links can
    # put their badge in the gap, so no global deployment fanout tax is needed.
    label_width = max((c.measure(e['label'], c.S['label_font']) for e in spec.get('edges', [])), default=0)
    gapx = max(c.S['gap_x'], 2*stub+spacing, label_width+2*pad)
    span = {}
    for i in reversed(traversal):
        span[i] = max(sizes[i][0], sum(span[j] for j in children[i])+gapx*max(0,len(children[i])-1))
    local = {}; dims = {}
    for g in gs:
        gid = g['id']; root = roots[gid]
        width = max(span[root], c.measure(_group_title(spec,g),c.S['node_font']-2,'bold'))+2*pad
        depth = {root: 0}; queue = [root]
        for i in queue:
            for j in children[i]: depth[j] = depth[i]+1; queue.append(j)
        heights = [max(sizes[i][1] for i in queue if depth[i] == d) for d in range(max(depth.values())+1)]
        ys = [header+inset]
        for h in heights[:-1]: ys.append(ys[-1]+h+gapy)
        centers = {root: width/2}
        for i in queue:
            w,h = sizes[i]; local[i] = (centers[i]-w/2,ys[depth[i]],w,h)
            row_width = sum(span[j] for j in children[i])+gapx*max(0,len(children[i])-1)
            x = centers[i]-row_width/2
            for j in children[i]: centers[j] = x+span[j]/2; x += span[j]+gapx
        dims[gid] = (width,ys[-1]+heights[-1]+pad)
    group_order = [owner[i] for i in traversal if i == roots[owner[i]]]
    subtree = {}
    for gid in reversed(group_order):
        subtree[gid] = max(dims[gid][0],sum(subtree[j] for j in branches[gid])+gapx*max(0,len(branches[gid])-1))
    top = owner[traversal[0]]
    positions = {top: (margin+subtree[top]/2,start_y-header-inset)}
    boxes = {}; panels = []
    for gid in group_order:
        cx,y = positions[gid]; w,h = dims[gid]; x = cx-w/2
        panels.append((gid,x,y,w,h))
        for i in members[gid]:
            xx,yy,ww,hh = local[i]; boxes[i] = (x+xx,y+yy,ww,hh)
        row_width = sum(subtree[j] for j in branches[gid])+gapx*max(0,len(branches[gid])-1)
        left = cx-row_width/2
        # Branching links need independent tracks above child panel titles.
        gutter = max(c.S['gap_y'],2*stub+len(branches[gid])*spacing)
        for j in branches[gid]:
            positions[j] = (left+subtree[j]/2,y+h+gutter); left += subtree[j]+gapx
    return boxes, panels


def _render_system(spec, style):
    issues = _contract(spec)
    if issues: raise ValueError('Invalid system view: ' + repr(issues))
    # Never mutate the caller's input or shared style.
    spec = deepcopy(spec)
    ns, es, gs = spec['nodes'], spec.get('edges', []), spec.get('groups', [])
    if spec['diagram_type'] == 'network_topology':
        for e in es:
            protocol = str(e.get('protocol') or '')
            port = str(e.get('port', ''))
            prefix = protocol + (':' + port if port else '') if protocol else ('端口 ' + port if port else '')
            if protocol not in e['label'] or (port and port not in e['label']):
                e['label'] = prefix + ' / ' + e['label']
    typ = spec['diagram_type']; groupmap = {g['id']: g for g in gs}
    tree = _network_tree(spec) if typ == 'network_topology' else None
    c = Canvas(spec, style, 1200, 900); S = c.S
    pad = S['padding']; margin = max(80, S['margin']); header = S['panel_header']
    degree = defaultdict(int)
    for e in es:
        degree[e['source']] += 1; degree[e['target']] += 1
    spacing = S.get('structure_channel_spacing', 36)
    port_space = max(S.get('structure_port_spacing', 32), S['label_font']*1.35+24)
    spacing = max(spacing, S['label_font']*1.35+24)
    stub = S.get('structure_port_stub', 32 if tree else 60)
    maxlabel = max((c.measure(e.get('label', ''), S['label_font']) for e in es), default=0)
    # Tracks and labels share a gutter; their worst-case budgets need not add.
    gapx = max(S['gap_x'], 2*stub + max(degree.values(), default=0)*spacing,
               2*stub + maxlabel + 2*pad)
    if typ in ('deployment', 'network_topology'):
        fan = max((max(sum(e['source']==n['id'] for e in es),
                       sum(e['target']==n['id'] for e in es)) for n in ns),default=0)
        gapx += fan*spacing if fan>1 else 0
    gapy = max(S['gap_y'], 2*stub + spacing)
    sizes = {}; lines = {}; boxes = {}; panels = []
    for n in ns:
        i = n['id']; lines[i] = _lines(spec, n)
        w = max(320, c.measure(n['label'], S['node_font'], 'bold')*1.04+2*pad)
        w = max(w, min(520, max(c.measure(t, S['body_font'])+2*pad for t in lines[i])))
        if tree:
            incident_label = max((c.measure(e['label'], S['label_font']) for e in es
                                  if i in (e['source'], e['target'])), default=0)
            w = max(w, (degree[i]-1)*port_space+2*pad, incident_label+2*pad)
        count = sum(len(c.wrap(t, w-2*pad, S['body_font'])) for t in lines[i])
        storage = _kind(spec,n)=='store' or n.get('storage')
        # Match Canvas body baselines and retain its bottom clearance, including
        # the cylinder's 16px body offset. Ports on opposite sides share height.
        incoming = sum(e['target']==i for e in es)
        outgoing = sum(e['source']==i for e in es)
        h = max(S['node_header']+2*pad+(count*1.38+.35)*S['body_font']+(16 if storage else 0),
                S['node_header']+(0 if tree else max(0,max(incoming,outgoing)-1)*port_space)+2*pad)
        sizes[i] = (w, h)
    inset = max(pad, stub-header+50)  # top stubs clear the actual title text
    if tree:
        inset = max(inset, S['label_font']*1.35+16)
    start_y = max(260, S['margin']+100+header+inset)
    if typ == 'deployment':
        start_y += 50  # outer network header must remain below the subtitle
    if typ == 'layered_architecture':
        ordered = sorted(gs, key=lambda g: g['order'])
        members = {g['id']: [n for n in ns if n.get('group') == g['id']] for g in ordered}
        width = max([sum(sizes[n['id']][0] for n in members[g['id']])+gapx*max(0,len(members[g['id']])-1)+2*pad for g in ordered]
                    + [c.measure(_group_title(spec,g), S['node_font']-2, 'bold')+2*pad for g in ordered])
        gapy = max(S['gap_y'], 2*stub+spacing-header-inset-pad)
        y = start_y-header-inset
        for g in ordered:
            row = members[g['id']]
            row_width = sum(sizes[n['id']][0] for n in row)+gapx*max(0,len(row)-1)
            predecessors = [boxes[e['source']] for e in es
                            if e['target'] in {n['id'] for n in row} and e['source'] in boxes]
            center = (sum(b[0]+b[2]/2 for b in predecessors)/len(predecessors)
                      if predecessors else margin+width/2)
            x = max(margin+pad,min(center-row_width/2,margin+width-pad-row_width))
            height = max([sizes[n['id']][1] for n in row] or [100])
            panels.append((g['id'], margin, y, width, header+height+inset+pad))
            for n in row:
                w,h = sizes[n['id']]; boxes[n['id']] = (x,y+header+inset,w,h); x += w+gapx
            y += header+height+inset+pad+gapy
    elif tree:
        boxes, panels = _network_tree_boxes(spec,c,sizes,tree,margin,start_y,inset,gapy,spacing,stub)
    elif typ in ('deployment', 'network_topology'):
        x = margin
        for g in gs:
            members = [n for n in ns if n.get('group') == g['id']]
            width = max([sizes[n['id']][0] for n in members] + [320, c.measure(_group_title(spec,g), S['node_font']-2,'bold')])+2*pad
            y = start_y
            for n in members:
                _,h = sizes[n['id']]; boxes[n['id']] = (x+pad,y,width-2*pad,h); y += h+gapy
            panels.append((g['id'],x,start_y-header-inset,width,max(140,y-start_y-gapy)+header+inset+pad))
            x += width+gapx
    else:
        rank = _ranks(ns, es)
        levels = defaultdict(list)
        for n in ns: levels[rank[n['id']]].append(n)
        internal = defaultdict(list)
        for n in ns:
            if n.get('group'): internal[rank[n['id']]].append(n)
        # Keep short views stable. A long focus plus its collaborators must not
        # become an unbounded row: ranks order cells, not absolute x positions.
        fold = typ in ('c4_container', 'c4_component') and len(internal) >= 4 and len(levels) > 4
        if fold:
            ranks = sorted(internal)
            columns = min(3, ceil(len(ranks)**.5))
            owned_ids = {n['id'] for row in internal.values() for n in row}
            outside = {'left': [], 'right': []}
            for n in ns:
                if n['id'] in owned_ids: continue
                incoming = sum(e['source'] == n['id'] and e['target'] in owned_ids for e in es)
                outgoing = sum(e['target'] == n['id'] and e['source'] in owned_ids for e in es)
                side = 'left' if incoming > outgoing or (incoming == outgoing and rank[n['id']] < ranks[0]) else 'right'
                outside[side].append(n)
            left_width = max((sizes[n['id']][0] for n in outside['left']), default=0)
            origin = margin + left_width + gapx if outside['left'] else margin + pad
            widths = [max(sizes[n['id']][0] for j,r in enumerate(ranks) if j % columns == col
                          for n in internal[r]) for col in range(columns)]
            # Budget the boundary title once, across the entire grid.
            title_width = max(c.measure(_group_title(spec,g),S['node_font']-2,'bold') for g in gs)
            widths[-1] += max(0, title_width-sum(widths)-gapx*(columns-1))
            y = start_y
            for first in range(0, len(ranks), columns):
                x = origin; bottom = y
                for col,r in enumerate(ranks[first:first+columns]):
                    yy = y
                    for n in internal[r]:
                        h = sizes[n['id']][1]
                        boxes[n['id']] = (x,yy,widths[col],h)
                        yy += h+gapy
                    bottom = max(bottom, yy-gapy)
                    x += widths[col]+gapx
                y = bottom+gapy
            right = origin+sum(widths)+gapx*(columns-1)
            # External columns are outside the full rectangular focus envelope,
            # including its padding, even beside empty cells in a folded row.
            for side, members in outside.items():
                def neighbor_y(n):
                    adjacent = [e['target'] if e['source'] == n['id'] else e['source']
                                for e in es if n['id'] in (e['source'],e['target'])]
                    ys = [boxes[i][1] for i in adjacent if i in owned_ids]
                    return sum(ys)/len(ys) if ys else start_y
                y = start_y
                for n in sorted(members, key=neighbor_y):
                    w,h = sizes[n['id']]; y = max(y,neighbor_y(n))
                    x = origin-gapx-w if side == 'left' else right+gapx
                    boxes[n['id']] = (x,y,w,h); y += h+gapy
        else:
            x = margin
            for r in sorted(levels):
                row = levels[r]; width = max(sizes[n['id']][0] for n in row)
                # A single-column focus still has room for its boundary title.
                for n in row:
                    if n.get('group'):
                        width = max(width,c.measure(_group_title(spec,groupmap[n['group']]),S['node_font']-2,'bold'))
                y = start_y
                for n in row:
                    _,h = sizes[n['id']]; boxes[n['id']] = (x,y,width,h); y += h+gapy
                x += width+gapx
        for g in gs:
            owned = [boxes[n['id']] for n in ns if n.get('group') == g['id']]
            if not owned: continue
            left = min(b[0] for b in owned)-pad; top = min(b[1] for b in owned)-header-inset
            right = max(b[0]+b[2] for b in owned)+pad; bottom = max(b[1]+b[3] for b in owned)+pad
            panels.append((g['id'],left,top,right-left,bottom-top))
    maxx = max([b[0]+b[2] for b in boxes.values()]+[p[1]+p[3] for p in panels]); maxy = max([b[1]+b[3] for b in boxes.values()]+[p[2]+p[4] for p in panels])
    c.W = max(1200,maxx+margin); c.H = maxy+margin+180
    # Wide titles are measured before Canvas finishes a centered title.
    c.W = max(c.W, c.measure(spec['title'],S['title_font'],'bold')+2*margin,
              c.measure(spec.get('subtitle',''),S['body_font'])+2*margin)
    c.title()
    if typ == 'deployment':
        c.panel('network',margin-pad,start_y-header-inset-50,maxx-margin+2*pad,maxy-(start_y-header-inset)+70,spec.get('network_label', '部署网络边界'),role='slate',header=False)
    obstacles = []
    for gid,x,y,w,h in panels:
        g = groupmap[gid]
        c.panel('group-'+gid,x,y,w,h,_group_title(spec,g),g.get('role','slate'))
        c.panels[-1].update({'semantic_kind':g.get('kind','deployment-region'),'group':gid})
    # Only visible title text blocks routes; the blank header band is passable.
    obstacles = [(t['x'],t['y'],t['w'],t['h']) for t in c.texts
                 if (t.get('owner') or '').startswith('panel:')]
    for n in ns:
        i = n['id']; x,y,w,h = boxes[i]; k = _kind(spec,n)
        shape = 'database' if k=='store' or n.get('storage') else 'rect'
        c.node(i,x,y,w,h,n['label'],lines[i],n.get('role','blue'),shape)
        c.nodes[i].update({'semantic_kind':k,'group':n.get('group'),'abstraction':C4_LEVELS.get(typ)})
    # All terminal stubs are reserved before routing, including future edges.
    ports = _ports(c,ns,es,boxes,'layered_architecture' if tree else typ,port_space)
    terminals = {}
    for e in es:
        a,va,_,_ = ports[e['id'],'source']; b,vb,_,_ = ports[e['id'],'target']
        terminals[e['id']] = ([a,(a[0]+va[0]*stub,a[1]+va[1]*stub)],[(b[0]+vb[0]*stub,b[1]+vb[1]*stub),b])
    paths = []; routed = set()
    for e in es:
        eid = e['id']; a,va,sa,_ = ports[eid,'source']; b,vb,sb,_ = ports[eid,'target']
        ta,tb = terminals[eid]
        reserved = paths + [t for other,pair in terminals.items() if other!=eid and other not in routed for t in pair]
        foreign = [(x,y,w,h) for gid,x,y,w,h in panels
                   if tree and gid not in (c.nodes[e['source']]['group'],c.nodes[e['target']]['group'])]
        path = _compact([a]+_route(ta[-1],tb[0],list(boxes.values())+obstacles+foreign,reserved,spacing,va,vb)+[b])
        direction = _direction(spec,e) if typ=='network_topology' else 'directed'
        marker = 'arrow' if direction in ('directed','bidirectional') else 'none'
        start_marker = 'open' if direction=='bidirectional' else None
        # A vertical relationship can carry a centered badge in its inter-node
        # gap, without reserving twice the label width beside the centerline.
        label_pos = ((a[0]+b[0])/2,(a[1]+b[1])/2) if len(path)==2 and a[0]==b[0] else None
        if tree and label_pos is None:
            # A branch badge can use its child's inset below the panel title.
            # Centering it here avoids spanning neighboring parallel trunks.
            child = a if sa == 'top' else b
            label_pos = (child[0], child[1]-S['label_font']*.35-9)
        data = c.edge(eid,e['source'],e['target'],path,label=e['label'],kind=e.get('kind','flow'),marker=marker,start_marker=start_marker,label_pos=label_pos)
        data.update({'channel_id':eid,'direction':direction,'protocol':e.get('protocol'),
                     'ports':{'source':{'side':sa,'point':a},'target':{'side':sb,'point':b}}})
        paths.append(path); routed.add(eid)
    _crossing_gaps(c,paths)
    c.W = max([c.W]+[p[0]+margin for path in paths for p in path]); c.H = max([c.H]+[p[1]+margin+180 for path in paths for p in path])
    if typ == 'network_topology':
        dirs = {_direction(spec,e) for e in es}
        note = '方向：' + '；'.join({'directed':'有向通信已给定（箭头表示发起方 → 接收方）','bidirectional':'双向通信已给定',
                                   'undirected':'无向连通已给定','unspecified':'通信方向未给定（无箭头，不推断双向）'}[d] for d in sorted(dirs))
        c.W = max(c.W,c.measure(note,S['label_font'])+2*margin)
        c.note(note,y=c.H-112)
    elif typ == 'layered_architecture':
        c.note('自上而下为职责层级；箭头表示依赖，被依赖方是箭头终点',y=c.H-112)
    entries = spec.get('legend', [])
    if entries:
        c.W = max(c.W,2*margin+sum(c.measure(item['label'],S['label_font'])+60 for item in entries))
        c.legend([(i['role'],i['label']) for i in entries],y=c.H-55)
    return c


def inspect_system(spec, layout):
    """Return error dictionaries, same contract as semantic_rules.inspect.

    An empty layout performs input-only inspection. Missing direction is valid
    for a network view, provided no directional arrow is fabricated.
    """
    errors = _contract(spec)
    typ = spec.get('diagram_type')
    if typ not in SYSTEM_TYPES or not layout or errors: return errors
    def fail(code, **details): errors.append({'code':code, **details})
    boxes = {n['id']:n for n in layout.get('nodes',[])}
    drawn = {e['id']:e for e in layout.get('edges',[])}
    panels = {p['id']:p for p in layout.get('panels',[])}
    def contains(p,b):
        return p['x']<=b['x'] and p['y']+p.get('header_h',0)<=b['y'] and b['x']+b['w']<=p['x']+p['w'] and b['y']+b['h']<=p['y']+p['h']
    for n in spec.get('nodes',[]):
        b = boxes.get(n['id'])
        if not b: fail('system-node-not-rendered',node=n['id']); continue
        if b.get('semantic_kind') != _kind(spec,n): fail('system-kind-not-preserved',node=n['id'])
        gid = n.get('group'); p = panels.get('group-'+str(gid))
        if gid and (not p or not contains(p,b)): fail('system-node-outside-owner',node=n['id'],group=gid)
        if typ in C4_LEVELS and not gid:
            for p in panels.values():
                if contains(p,b): fail('c4-external-captured-by-focus',node=n['id'])
        if typ=='network_topology' and n.get('kind')=='store' and b.get('shape')!='database':
            fail('network-store-symbol',node=n['id'])
        if typ == 'network_topology':
            for other in panels.values():
                if other.get('group') != gid and (
                        min(b['x']+b['w'],other['x']+other['w']) > max(b['x'],other['x']) and
                        min(b['y']+b['h'],other['y']+other['h']) > max(b['y'],other['y'])):
                    fail('network-foreign-member-in-boundary',node=n['id'],group=other.get('group'))
    for g in spec.get('groups', []):
        p = panels.get('group-'+g['id'])
        if not p or p.get('semantic_kind') != g.get('kind', 'deployment-region'):
            fail('system-boundary-kind-not-preserved', group=g['id'])
    if typ == 'deployment':
        network = panels.get('network')
        if not network or any(not contains(network,p) for p in panels.values() if p['id'] != 'network'):
            fail('deployment-regions-outside-network')
    for e in spec.get('edges',[]):
        d = drawn.get(e['id'],{})
        if (d.get('source'),d.get('target')) != (e['source'],e['target']):
            fail('system-edge-not-preserved',edge=e['id'])
        if typ != 'network_topology' and (d.get('marker') != 'arrow' or d.get('start_marker')):
            fail('system-relationship-direction-symbol', edge=e['id'])
        if typ=='network_topology':
            direction = _direction(spec,e)
            expected = 'arrow' if direction in ('directed','bidirectional') else 'none'
            if d.get('marker')!=expected or bool(d.get('start_marker')) != (direction=='bidirectional'):
                fail('network-direction-symbol',edge=e['id'])
            if d.get('protocol')!=e.get('protocol'): fail('network-protocol-not-preserved',edge=e['id'])
    if typ=='layered_architecture':
        groups = sorted(spec.get('groups',[]),key=lambda g:g.get('order',0))
        for a,b in zip(groups,groups[1:]):
            pa,pb = panels.get('group-'+a['id']),panels.get('group-'+b['id'])
            if pa and pb and pa['y']+pa['h']>pb['y']: fail('layer-geometric-order',groups=[a['id'],b['id']])
    return errors


def render_c4_context(spec,style): return _render_system(spec,style)
def render_c4_container(spec,style): return _render_system(spec,style)
def render_c4_component(spec,style): return _render_system(spec,style)
def render_layered_architecture(spec,style): return _render_system(spec,style)
def render_deployment(spec,style): return _render_system(spec,style)
def render_network_topology(spec,style): return _render_system(spec,style)

RENDERERS = {kind: globals()['render_'+kind] for kind in SYSTEM_TYPES}
