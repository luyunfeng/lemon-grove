"""Structure-specific layouts, independently routed semantic edges, Canvas-only drawing."""
from collections import defaultdict
import heapq

try:
    from .canvas import Canvas
except ImportError:
    from canvas import Canvas


def _field(row):
    if isinstance(row, str):
        return row
    return ' '.join(str(row[k]) for k in ('key', 'name', 'type') if row.get(k))


def _ranks(nodes, edges, reverse=False):
    rank = {n['id']: 0 for n in nodes}
    explicit = {n['id']: int(n['rank']) for n in nodes if 'rank' in n}
    for _ in range(max(0, len(nodes)-1)):
        previous = rank.copy()
        for edge in edges:
            a, b = edge['source'], edge['target']
            if reverse and edge.get('kind') in ('inheritance', 'realization'):
                a, b = b, a
            if b not in explicit:
                rank[b] = max(rank[b], previous[a]+1)
        rank.update(explicit)
        if rank == previous:
            break
    return rank


def _segments(path):
    return zip(path, path[1:])


def _overlap(a, b, p, q):
    """Positive-length collinearity, never an implicit shared bus."""
    for axis in (0, 1):
        other = 1-axis
        if a[axis] == b[axis] == p[axis] == q[axis]:
            if min(max(a[other], b[other]), max(p[other], q[other])) > max(min(a[other], b[other]), min(p[other], q[other]))+.01:
                return True
    return False


def _cross(a, b, p, q):
    if a[0] == b[0] and p[1] == q[1]:
        x, y = a[0], p[1]
        if min(a[1], b[1]) <= y <= max(a[1], b[1]) and min(p[0], q[0]) <= x <= max(p[0], q[0]):
            return (x, y)
    if a[1] == b[1] and p[0] == q[0]:
        return _cross(p, q, a, b)
    return None


def _near_collinear(a, b, p, q, gap):
    """Disjoint tracks also need a visible break; tiny gaps resemble a shared bus."""
    for axis in (0,1):
        other=1-axis
        if a[axis]==b[axis]==p[axis]==q[axis]:
            distance=max(min(a[other],b[other]),min(p[other],q[other]))-min(max(a[other],b[other]),max(p[other],q[other]))
            if distance<gap-.01:
                return True
    return False

def _parallel_too_close(a,b,p,q,gap=14):
    for fixed,travel in ((0,1),(1,0)):
        if abs(a[fixed]-b[fixed])<.01 and abs(p[fixed]-q[fixed])<.01:
            distance=abs(a[fixed]-p[fixed])
            overlap=min(max(a[travel],b[travel]),max(p[travel],q[travel]))-max(min(a[travel],b[travel]),min(p[travel],q[travel]))
            if .01<distance<gap and overlap>8:return True
    return False


def _compact(path):
    result = []
    for point in path:
        if result and point == result[-1]:
            continue
        if len(result)>1 and (result[-2][0] == result[-1][0] == point[0] or result[-2][1] == result[-1][1] == point[1]):
            result.pop()
        result.append(point)
    return result


def _route(a, b, boxes, reserved, spacing, start_vector, end_vector, fine=False):
    """Orthogonal visibility graph: node/title obstacles and exclusive edge tracks."""
    obstacles = [(x-8, y-8, x+w+8, y+h+8) for x,y,w,h in boxes]
    xs = {a[0], b[0]}
    ys = {a[1], b[1]}
    for l,t,r,d in obstacles:
        xs.update((l-12, r+12)); ys.update((t-12, d+12))
    for path in reserved:
        for x,y in path:
            xs.update((x-spacing, x+spacing)); ys.update((y-spacing, y+spacing))
            if fine:
                xs.update((x-16,x+16));ys.update((y-16,y+16))
    xs = sorted(x for x in xs if x >= 20)
    ys = sorted(y for y in ys if y >= 150)
    def inside(x,y):
        return any(l<x<r and t<y<d for l,t,r,d in obstacles)
    points = {(i,j):(x,y) for i,x in enumerate(xs) for j,y in enumerate(ys) if not inside(x,y)}
    start = (xs.index(a[0]), ys.index(a[1])); end = (xs.index(b[0]), ys.index(b[1]))
    occupied = [s for path in reserved for s in _segments(path)]
    occupied_corners = {p for path in reserved for p in path}
    cache = {}
    def cost(p,q):
        key = tuple(sorted((p,q)))
        if key in cache:
            return cache[key]
        x,y=p; X,Y=q
        if any((x==X and l<x<r and max(min(y,Y),t)<min(max(y,Y),d)) or
               (y==Y and t<y<d and max(min(x,X),l)<min(max(x,X),r)) for l,t,r,d in obstacles):
            return None
        # Reserve a turning area around future terminal ends as well as their
        # segments; a nearby corner can otherwise trap a later edge's approach.
        for cx,cy in occupied_corners:
            qx=max(min(x,X),min(max(x,X),cx));qy=max(min(y,Y),min(max(y,Y),cy))
            if (cx-qx)**2+(cy-qy)**2 < 13.99**2:return None
        crossings = 0
        for u,v in occupied:
            if _near_collinear(p,q,u,v,spacing) or _parallel_too_close(p,q,u,v):
                return None
            crossing = _cross(p,q,u,v)
            if crossing:
                if crossing in occupied_corners:
                    return None
                # Grid subdivision must not charge twice for one crossing.
                crossings += .5 if crossing in (p,q) else 1
        cache[key] = abs(x-X)+abs(y-Y)+crossings*spacing*3
        return cache[key]
    # Count bends against the fixed port stubs too, not only inside the graph.
    start_axis = 1 if start_vector[0] else 2
    end_axis = 1 if end_vector[0] else 2
    bend_cost = 2*spacing
    queue = [(0,start,start_axis)]; dist = {(start,start_axis):0}; prev = {}; finish = None
    while queue:
        value,key,direction = heapq.heappop(queue)
        if value != dist.get((key,direction)):
            continue
        if key == end:
            finish = (key,direction); break
        i,j = key
        for nxt,axis in [((i-1,j),1),((i+1,j),1),((i,j-1),2),((i,j+1),2)]:
            if nxt not in points or key not in points:
                continue
            delta=tuple(points[nxt][k]-points[key][k] for k in (0,1))
            if key==start and sum(delta[k]*start_vector[k] for k in (0,1))<0:
                continue
            if nxt==end and sum(delta[k]*end_vector[k] for k in (0,1))>0:
                continue
            step = cost(points[key],points[nxt])
            if step is None:
                continue
            # A bend at a crossing would create an apparent junction.
            if direction and direction != axis and any(_cross(points[key],points[key],u,v) for u,v in occupied):
                continue
            nc = value+step+(bend_cost if direction != axis else 0)
            if nxt == end and axis != end_axis:
                nc += bend_cost
            state = (nxt,axis)
            if nc < dist.get(state,float('inf')):
                dist[state]=nc; prev[state]=(key,direction); heapq.heappush(queue,(nc,nxt,axis))
    if finish is None:
        if not fine:return _route(a,b,boxes,reserved,spacing,start_vector,end_vector,True)
        raise ValueError('No exclusive unobstructed route between ports')
    path = []
    while finish:
        path.append(points[finish[0]]); finish=prev.get(finish)
    return _compact(list(reversed(path)))


def _cardinality(edge, side):
    card = edge.get('cardinality',{})
    if isinstance(card,dict):
        return str(card.get(side, edge.get(side+'_cardinality','')))
    if isinstance(card,(list,tuple)) and len(card)==2:
        return str(card[0 if side=='source' else 1])
    return str(edge.get(side+'_cardinality',''))


def _crowfoot(c, port, outward, card):
    if card not in ('1','0..1','1..*','0..*'):
        raise ValueError('Unsupported ER cardinality: '+card)
    x,y=port; dx,dy=outward; px,py=-dy,dx
    def p(d,s=0):
        return (x+dx*d+px*s,y+dy*d+py*s)
    if '*' in card:
        for s in (-6,0,6):
            c.line([p(18),p(2,s)])
        if card.startswith('0'):
            cx,cy=p(29);c._shape('circle',cx=cx,cy=cy,r=5,fill='#FFFFFF',stroke=c.color('slate'),stroke_width=c.S['stroke'])
        else:
            c.line([p(29,-6),p(29,6)])
    else:
        c.line([p(9,-6),p(9,6)])
        if card=='1':
            c.line([p(16,-6),p(16,6)])
        else:
            cx,cy=p(22);c._shape('circle',cx=cx,cy=cy,r=5,fill='#FFFFFF',stroke=c.color('slate'),stroke_width=c.S['stroke'])
    # Symbol and nearby text both encode optionality.
    c.text(x+dx*43,y-10,card,size=c.S['label_font'],anchor='middle')


def _class_layout(ns, es, sizes, margin, gapx, gapy):
    """Adjacent inheritance families, independent dependency clients, entity chains."""
    parent = {n['id']: n['id'] for n in ns}
    def root(i):
        while parent[i] != i:
            i=parent[i]
        return i
    def union(a,b):
        parent[root(a)] = root(b)
    family = set()
    for e in es:
        if e.get('kind') in ('inheritance','realization'):
            family.update((e['source'],e['target'])); union(e['source'],e['target'])
    clients = {e['source'] for e in es if e.get('kind')=='dependency'}-family
    degree={n['id']:sum(n['id'] in (e['source'],e['target']) for e in es) for n in ns}
    for e in es:
        if e.get('kind')=='dependency' and e['source'] in clients and e['target'] not in family and degree[e['target']]==1:
            union(e['source'],e['target'])
    for e in es:
        if e['source'] not in family|clients and e['target'] not in family|clients:
            union(e['source'],e['target'])
    components = defaultdict(list)
    for n in ns:
        components[root(n['id'])].append(n)
    clusters = sorted(components.values(), key=lambda nn: 0 if any(n['id'] in family for n in nn) else 1 if any(n['id'] in clients for n in nn) else 2)
    # Keep neighboring relationship clusters adjacent rather than inserting a
    # dependency client between two groups that directly reference each other.
    if len(clusters)>2:
        ordered=[clusters.pop(0)]
        while clusters:
            previous={n['id'] for n in ordered[-1]}
            def links(group):
                ids={n['id'] for n in group}
                return sum((e['source'] in previous and e['target'] in ids) or (e['target'] in previous and e['source'] in ids) for e in es)
            best=max(range(len(clusters)),key=lambda i:(links(clusters[i]),-i));ordered.append(clusters.pop(best))
        clusters=ordered
    depended = {e['target'] for e in es if e.get('kind')=='dependency'}
    boxes = {}; x=margin
    for members in clusters:
        ids = {n['id'] for n in members}
        row_gap=min(gapy,280) if ids & family else min(gapy,140)
        sibling_gap=min(gapx,240);cluster_gap=min(gapx,320)
        edges = [e for e in es if e['source'] in ids and e['target'] in ids]
        # Spec ranks are hints; topology within each semantic cluster takes precedence.
        rank = _ranks([{'id':n['id']} for n in members],edges,True)
        levels = defaultdict(list)
        for n in members:
            levels[rank[n['id']]].append(n)
        widths = {r:sum(sizes[n['id']][0] for n in nn)+sibling_gap*(len(nn)-1) for r,nn in levels.items()}
        width = max(widths.values()); y=210
        for r in sorted(levels):
            row = sorted(levels[r],key=lambda n:n['id'] in depended)
            xx=x+(width-widths[r])/2
            for n in row:
                w,h=sizes[n['id']]; boxes[n['id']]=(xx,y,w,h); xx+=w+sibling_gap
            y+=max(sizes[n['id']][1] for n in row)+row_gap
        x+=width+cluster_gap
    return boxes


def _sink_distances(vertices, edges):
    """Longest distance to a sink; None for a cycle, including self-loops."""
    outgoing = {g: set() for g in vertices}
    predecessors = {g: set() for g in vertices}
    for a, b in edges:
        outgoing[a].add(b); predecessors[b].add(a)
    remaining = {g: len(v) for g, v in outgoing.items()}
    distance = {g: 0 for g in vertices}
    ready = [g for g in vertices if not remaining[g]]
    visited = 0
    while ready:
        g = ready.pop(); visited += 1
        for p in predecessors[g]:
            distance[p] = max(distance[p], distance[g]+1)
            remaining[p] -= 1
            if not remaining[p]: ready.append(p)
    return distance if visited == len(outgoing) else None


def _dependency_distances(ns, es):
    owner = {n['id']: n.get('group', '') for n in ns}
    if _sink_distances(owner, [(e['source'], e['target']) for e in es]) is None:
        return None
    return _sink_distances(dict.fromkeys(owner.values()),
                          [(owner[e['source']], owner[e['target']]) for e in es
                           if owner[e['source']] != owner[e['target']]])


def _dependency_layout(c, ns, es, sizes, groups, margin, gapx, gapy, distance):
    """Keep real groups separate, with equally distant groups in one column."""
    members = defaultdict(list)
    owner = {n['id']: n.get('group', '') for n in ns}
    for n in ns:
        members[owner[n['id']]].append(n)
    columns = defaultdict(list)
    for g in members:
        columns[distance[g]].append(g)
    boxes = {}; panels = []; x = margin
    pad = c.S['padding']; panel_header = c.S['panel_header']
    row_gap = max(c.S['gap_y'], min(gapy, 80))
    for depth in sorted(columns, reverse=True):
        column = columns[depth]
        # Put groups with already placed callers first; independent adapters
        # stay in their own lower panel rather than between callers and core.
        def incoming_y(g):
            yy = [boxes[e['source']][1] for e in es
                  if owner[e['target']] == g and e['source'] in boxes]
            return sum(yy)/len(yy) if yy else float('inf')
        column.sort(key=incoming_y)
        width = max(max(sizes[n['id']][0] for n in members[g]) for g in column)
        width = max(width, max(c.measure(groups.get(g, {}).get('label', str(g)),
                         c.S['node_font']-2, 'bold')*1.04 for g in column))
        panel_y = 210
        for g in column:
            yy = panel_y+panel_header+pad
            for n in members[g]:
                w, h = sizes[n['id']]
                callers = [boxes[e['source']] for e in es
                           if e['target'] == n['id'] and e['source'] in boxes
                           and owner[e['source']] != g]
                if callers:
                    yy = max(yy, sum(b[1]+b[3]/2 for b in callers)/len(callers)-h/2)
                boxes[n['id']] = (x+pad, yy, width, h)
                yy += h+row_gap
            bottom = yy-row_gap+pad
            # Tighten the top as well as the bottom of a displaced core panel.
            top = min(boxes[n['id']][1] for n in members[g])-panel_header-pad
            panels.append((g, x, top, width+2*pad, bottom-top))
            panel_y = bottom+row_gap
        x += width+2*pad+gapx
    return boxes, panels


def _event_layout(ns, sizes, rank, margin, gapx, gapy):
    """Three-column serpentine bands preserve every forward stage and DLQ.

    The next band begins below the entire preceding band, so late subscribers
    cannot be mistaken for ordinary fanout consumers in the first band.
    """
    levels = defaultdict(list)
    for n in ns: levels[rank[n['id']]].append(n)
    ordered = sorted(levels)
    widths = [0, 0, 0]
    positions = {}
    for i, r in enumerate(ordered):
        band, col = divmod(i, 3)
        if band % 2: col = 2-col
        positions[r] = (band, col)
        widths[col] = max(widths[col], max(sizes[n['id']][0] for n in levels[r]))
    xs = [margin, margin+widths[0]+gapx, margin+widths[0]+widths[1]+2*gapx]
    boxes = {}; top = 210
    for band in range((len(ordered)+2)//3):
        bottom = top
        for r in ordered:
            row, col = positions[r]
            if row != band: continue
            y = top
            for n in levels[r]:
                w, h = sizes[n['id']]
                boxes[n['id']] = (xs[col]+(widths[col]-w)/2, y, w, h)
                y += h+gapy
            bottom = max(bottom, y-gapy)
        top = bottom+max(gapy, 220)
    return boxes


def _ports(c, ns, es, boxes, diagram, spacing):
    requests=defaultdict(list)
    vectors={'left':(-1,0),'right':(1,0),'top':(0,-1),'bottom':(0,1)}
    for e in es:
        a=boxes[e['source']]; b=boxes[e['target']]
        # Inheritance follows the family rows even for diagonal siblings.
        # Same-column instances use the vertical corridor, not opposing stubs.
        vertical_family = (diagram=='class' and e.get('kind') in ('inheritance','realization')
                           and (a[1]+a[3]<=b[1] or b[1]+b[3]<=a[1]))
        vertical_layer = diagram=='layered_architecture' and (a[1]+a[3]<=b[1] or b[1]+b[3]<=a[1])
        horizontal = diagram=='er' or (not vertical_family and not vertical_layer and
                       (a[0]+a[2]<=b[0] or b[0]+b[2]<=a[0]))
        if e['source']==e['target']:
            sa,sb='right','bottom'
        elif horizontal:
            sa,sb=('right','left') if b[0]>a[0] else ('left','right')
        else:
            sa,sb=('bottom','top') if b[1]>a[1] else ('top','bottom')
        for side,node,port,other in [('source',e['source'],sa,b),('target',e['target'],sb,a)]:
            field=e.get(side+'_field') if diagram=='er' else None
            key=(node,port,field)
            requests[key].append((e['id'],side,other[1]+other[3]/2 if horizontal else other[0]+other[2]/2))
    result={}
    for (node,port,field),items in requests.items():
        x,y,w,h=boxes[node]; items.sort(key=lambda item:(item[2],item[0]))
        for index,(eid,side,_) in enumerate(items):
            offset=(index-(len(items)-1)/2)*spacing
            if diagram=='er':
                if field not in c.nodes[node]['field_y']:
                    raise ValueError('ER edge needs a valid '+side+'_field: '+str(field))
                yy=c.nodes[node]['field_y'][field]+offset
            else:
                yy=y+c.S['node_header']+(h-c.S['node_header'])/2+offset
            if port in ('left','right'):
                point=(x if port=='left' else x+w, yy)
            else:
                point=(x+w/2+offset,y if port=='top' else y+h)
            result[eid,side]=(point,vectors[port],port,field)
    return result


def _symbol(c, x, y, kind):
    """Actual neutral relationship samples, drawn through the public line API."""
    dash='7,5' if kind in ('dependency','realization') else None
    c.line([(x+20 if kind in ('composition','aggregation') else x,y),(x+48 if kind in ('inheritance','realization') else x+68,y)],dash=dash)
    if kind in ('inheritance','realization'):
        c.line([(x+48,y-10),(x+68,y),(x+48,y+10),(x+48,y-10)])
    elif kind in ('composition','aggregation'):
        c.line([(x,y),(x+10,y-7),(x+20,y),(x+10,y+7),(x,y)])
        for d in (range(3,18,2) if kind=='composition' else []):
            half=min(d,20-d)*.7
            c.line([(x+d,y-half),(x+d,y+half)],width=3)
    else:
        c.line([(x+56,y-6),(x+68,y),(x+56,y+6)])


def _legend(c, diagram):
    x=c.S['margin']; y=c.H-55; size=c.S['label_font']
    if diagram=='dependency':
        # Module implementation is not UML class realization. Keep the open
        # dependency arrow and explicitly distinguish relationship colors.
        kinds={e.get('kind') for e in c.spec.get('edges',[])}
        if c.spec.get('legend'):
            c.H += 50; y += 50
            c.legend([(item['role'],item['label']) for item in c.spec['legend']],y=y-50)
        entries=[]
        if kinds & {'dependency','import'}: entries.append(('slate','import / 依赖'))
        if 'implements' in kinds: entries.append(('orange','implements / 实现'))
        for role,label in entries:
            c.line([(x,y-6),(x+68,y-6)],role=role,dash='7,5')
            c.line([(x+56,y-12),(x+68,y-6),(x+56,y)],role=role)
            c.text(x+85,y,label,size,fill=c.S['ink'])
            x+=85+c.measure(label,size)+50
        c.text(x,y,'箭头指向被依赖模块',size,fill=c.S['ink'])
        return
    if 'legend' in c.spec:
        if c.spec['legend']:c.legend([(item['role'],item['label']) for item in c.spec['legend']],y=y)
        return
    if diagram=='architecture':
        c.legend([('blue','提交 / 接入 / 外部系统'),('purple','执行与消息'),('cyan','数据存储'),('orange','交付通知')],y=y)
    elif diagram=='er':
        c.text(x,y,'PK 主键 · FK 外键',size); x+=c.measure('PK 主键 · FK 外键',size)+65
        for card,label in [('1','恰好一个'),('0..*','零个或多个')]:
            c.line([(x,y-6),(x+80,y-6)]); _crowfoot(c,(x,y-6),(1,0),card)
            c.text(x+95,y,label,size); x+=95+c.measure(label,size)+65
    else:
        entries = [('inheritance','继承'),('realization','实现'),('dependency','依赖'),('composition','组合'),('aggregation','聚合：菱形为整体端')] if diagram=='class' else [('dependency','箭头指向被依赖模块 · 具体关系见线标签')] if diagram=='dependency' else [('flow','有向网络通信 · 标签为协议与端口')]
        for kind,label in entries:
            _symbol(c,x,y-6,kind); c.text(x+85,y,label,size)
            x+=85+c.measure(label,size)+50


def _crossing_gaps(c, paths):
    """Explicit non-junctions: a short halo on the later, uninterrupted edge."""
    for i,path in enumerate(paths):
        for a,b in _segments(path):
            seen=set()
            for earlier in paths[:i]:
                for p,q in _segments(earlier):
                    hit=_cross(a,b,p,q)
                    if not hit or hit in seen:
                        continue
                    seen.add(hit); x,y=hit
                    u=(0,1) if a[0]==b[0] else (1,0)
                    halo=c.S.get('crossing_gap',12)
                    points=[(x-halo*u[0],y-halo*u[1]),(x+halo*u[0],y+halo*u[1])]
                    c.line(points,role=c.S['canvas_fill'],width=c.S['stroke']+12)
                    c.line(points,role=c.edges[i].get('role','slate'),width=c.S['stroke'],dash=c.edges[i].get('dash'))


def _render(spec, style, diagram):
    ns=spec.get('nodes',[]); es=spec.get('edges',[])
    ids=[n['id'] for n in ns]
    if len(set(ids))!=len(ids): raise ValueError('Duplicate node IDs')
    if len({e['id'] for e in es})!=len(es): raise ValueError('Duplicate edge IDs')
    if any(e['source'] not in ids or e['target'] not in ids for e in es): raise ValueError('Unknown edge endpoint')
    c=Canvas(spec,style,1200,900); S=c.S
    c.palette.setdefault('cyan',c.palette.get('teal',['#0891B2','#ECFEFF']))
    pad=S['padding']; margin=max(S['margin'],80)
    channel=S.get('structure_channel_spacing',36); port_space=S.get('structure_port_spacing',40 if diagram=='er' else 32)
    gapx=max(S['gap_x'],S.get('structure_gap_x',320 if diagram=='er' else 260 if diagram=='dependency' else 240 if diagram=='deployment' else 160))
    gapy=max(S['gap_y'],S.get('structure_gap_y',140))
    stub=S.get('structure_port_stub',84 if diagram=='er' else 60)
    dependency_distance=_dependency_distances(ns,es) if diagram=='dependency' else None
    compact_dependency=diagram=='dependency' and dependency_distance is not None
    degree=defaultdict(int)
    for e in es:
        degree[e['source']]+=1; degree[e['target']]+=1
    # A fan needs two terminal stubs, independent tracks, and room for its
    # widest label beside those tracks. Size corridors before placing panels.
    fan=max(degree.values(),default=0)
    label_width=max((c.measure(e.get('label',''),S['label_font']) for e in es),default=0)
    if diagram in ('architecture','event_flow') or compact_dependency:
        # Tracks and labels can occupy different segments of the same corridor.
        gapx=max(gapx,2*stub+(fan+1)*channel,2*stub+label_width+2*pad)
        if diagram=='event_flow':
            # Reverse acknowledgement turns still need dedicated tracks beside
            # a long delivery label, particularly with three or more consumers.
            returns=max((sum(e.get('kind')=='ack' and e['target']==n['id'] for e in es) for n in ns),default=0)
            gapx=max(gapx,2*stub+label_width+2*pad+returns*channel)
    else:
        gapx=max(gapx,2*stub+(fan+1)*channel+label_width+2*pad)
    if diagram=='class':
        gapy=max(gapy,2*stub+(fan+1)*channel+S['label_font']*1.35+2*pad)
    if diagram=='er':
        field_uses=defaultdict(int)
        for e in es:
            for side in ('source','target'):
                field_uses[e[side],e.get(side+'_field')]+=1
        # Only the referenced field grows to hold its own independent ports.
    header=S['node_header']; rowh=S['row_height']; font=S['body_font']
    # Canvas measures regular glyphs; title bands use bold glyphs in SVG renderers.
    title_factor=S.get('structure_title_width_factor',1.04)
    sizes={}; texts={}; rows={}; row_heights={}
    for n in ns:
        i=n['id']; lines=list(n.get('lines',[]))
        if diagram=='architecture':
            lines=[n.get('type_label',{'person':'[Person]','external':'[External System]','system':'[Software System]','container':'[Container]','component':'[Component]','module':'[Module]'}.get(n.get('kind'),'[Container]'))]+lines
            lines += [str(n[k]) for k in ('responsibility','technology') if n.get(k)]
        elif diagram=='deployment':
            lines=['«deployment instance»']+lines+[str(n[k]) for k in ('artifact','runtime') if n.get(k)]
        elif diagram=='dependency':
            lines+=n.get('lines_hint',[])
        elif diagram=='event_flow':
            lines=[n['type_label']]+lines
        texts[i]=lines
        if diagram in ('er','class'):
            rr=[_field(f) for f in n.get('fields',[])]
            if diagram=='class': rr+=['—']+[_field(m) for m in n.get('methods',[])]
            rows[i]=rr
            row_heights[i]=[max(rowh,(field_uses[i,f['name']]-1)*port_space+40) for f in n.get('fields',[])] if diagram=='er' else [rowh]*len(rr)
            w=max([300,c.measure(n['label'],S['node_font'],'bold')*title_factor+pad*2]+[c.measure(r,font)+pad*2 for r in rr]); h=header+sum(row_heights[i])+8
        else:
            w=max(300,c.measure(n['label'],S['node_font'],'bold')*title_factor+pad*2)
            w=max(w,min(500,max([0]+[c.measure(t,font)+pad*2 for t in lines])))
            count=sum(len(c.wrap(t,w-2*pad,font)) for t in lines)
            degree=sum(e['source']==i or e['target']==i for e in es)
            h=max(130,header+2*pad+count*font*1.5+(20 if n.get('kind')=='database' else 0),header+degree*port_space+2*pad)
            if compact_dependency:
                # Opposite sides can reuse vertical space; count only the
                # larger fan, while reserving the full independent port pitch.
                side_fan=max(sum(e['source']==i for e in es),sum(e['target']==i for e in es))
                h=max(header+2*pad+count*font*1.5,header+max(0,side_fan-1)*port_space+2*pad)
        sizes[i]=(w,h)
    rank=_ranks(ns,es,diagram=='class')
    groups={g['id']:g for g in spec.get('groups',[])}
    buckets=defaultdict(list)
    for n in ns:
        buckets[n.get('group','') if diagram=='deployment' else rank[n['id']]].append(n)
    order=list(buckets) if diagram=='deployment' else sorted(buckets)
    boxes={}; panels=[]; x=margin; y=210
    if diagram=='class':
        boxes=_class_layout(ns,es,sizes,margin,gapx,gapy)
    elif diagram=='event_flow':
        boxes=_event_layout(ns,sizes,rank,margin,gapx,gapy)
    else:
        for key in order:
            members=buckets[key]; bw=max(sizes[n['id']][0] for n in members)
            panelled=diagram in ('deployment','dependency')
            gid=key if diagram=='deployment' else members[0].get('group',str(key))
            if panelled:
                bw=max(bw,c.measure(groups.get(gid,{}).get('label',str(gid)),S['node_font']-2,'bold')*title_factor)
            yy=y+(S['panel_header']+pad if panelled else 0)
            for n in members:
                _,h=sizes[n['id']]; boxes[n['id']]=(x+pad if panelled else x,yy,bw,h); yy+=h+gapy
            if panelled: panels.append((gid,x,y,bw+2*pad,yy-y-gapy+pad))
            x+=bw+gapx+(2*pad if panelled else 0)
        if compact_dependency:
            boxes,panels=_dependency_layout(c,ns,es,sizes,groups,margin,gapx,gapy,dependency_distance)
    if diagram=='architecture':
        for gid in groups:
            bb=[boxes[n['id']] for n in ns if n.get('group')==gid and n.get('kind') not in ('person','external')]
            if bb:
                l=min(b[0] for b in bb)-pad; t=min(b[1] for b in bb)-S['panel_header']-pad
                r=max(b[0]+b[2] for b in bb)+pad; d=max(b[1]+b[3] for b in bb)+pad
                panels.append((gid,l,t,r-l,d-t))
    maxx=max([800]+[b[0]+b[2] for b in boxes.values()]); maxy=max([350]+[b[1]+b[3] for b in boxes.values()])
    c.W=maxx+margin; c.H=maxy+margin+100
    c.title()
    if diagram=='deployment':
        c.panel('network',margin-pad,145,maxx-margin+3*pad,maxy-145+2*pad,spec.get('network_label','Network boundary'),role='slate',header=False)
    title_obstacles=[]
    for gid,px,py,pw,ph in panels:
        g=groups.get(gid,{})
        c.panel('group-'+str(gid),px,py,pw,ph,g.get('label',str(gid)),role=g.get('role','blue'))
        # Reserve the complete title strip, not merely its current glyph bounds.
        title_obstacles.append((px,py,pw,S['panel_header']))
    for n in ns:
        i=n['id']; x,y,w,h=boxes[i]
        if diagram in ('er','class'):
            _,actual_h=c.table_node(i,x,y,w,n['label'],rows[i],role=n.get('role','blue'),row_heights=row_heights[i])
            if abs(actual_h-h)>.1: raise ValueError('Canvas table height differs from planned rows')
        else:
            c.node(i,x,y,w,h,title=n['label'],lines=texts[i],role=n.get('role','blue'),shape='database' if n.get('kind')=='database' else 'rect')
    ports=_ports(c,ns,es,boxes,diagram,port_space)
    decorations=defaultdict(list)
    for e in es:
        before=len(c.texts)
        for side in ('source','target'):
            port,vector,_,_=ports[e['id'],side]
            card=_cardinality(e,side)
            if not card:
                continue
            if diagram=='er':
                _crowfoot(c,port,vector,card)
            else:
                c.text(port[0]+vector[0]*32+14,port[1]+vector[1]*32,card,size=S['label_font'])
        decorations[e['id']]=[(t['x'],t['y'],t['w'],t['h']) for t in c.texts[before:]]
    # Allocate every terminal before routing any edge. Otherwise an early route
    # can consume a later edge's stub or turn exactly at its escape point.
    terminals={}
    for e in es:
        start,va,sa,sf=ports[e['id'],'source']; end,vb,sb,tf=ports[e['id'],'target']
        source_stub=stub
        if diagram=='er':
            siblings=sorted([other for other in es if other['source']==e['source'] and other.get('source_field')==sf and ports[other['id'],'source'][2]==sa],key=lambda other:ports[other['id'],'source'][0][1])
            if len(siblings)>1:
                # Nested exits: the shorter upper relation takes the outer track.
                source_stub+=channel*(len(siblings)-siblings.index(e))
        p=(start[0]+va[0]*source_stub,start[1]+va[1]*source_stub); q=(end[0]+vb[0]*stub,end[1]+vb[1]*stub)
        terminals[e['id']]=([start,p],[q,end])
    paths=[]; routed=set()
    for e in es:
        start,va,sa,sf=ports[e['id'],'source']; end,vb,sb,tf=ports[e['id'],'target']
        source_terminal,target_terminal=terminals[e['id']]
        p=source_terminal[-1]; q=target_terminal[0]
        obstacles=list(boxes.values())+title_obstacles+[box for eid,bb in decorations.items() if eid!=e['id'] for box in bb]
        if compact_dependency:
            owners={n.get('group','') for n in ns if n['id'] in (e['source'],e['target'])}
            obstacles.extend((px,py,pw,ph) for gid,px,py,pw,ph in panels if gid not in owners)
        reserved=paths+[terminal for eid,pair in terminals.items() if eid!=e['id'] and eid not in routed for terminal in pair]
        path=_compact([start]+_route(p,q,obstacles,reserved,channel,va,vb)+[end])
        if any(_overlap(a,b,u,v) for a,b in _segments(path) for prev in paths for u,v in _segments(prev)):
            raise ValueError('Port stub shares an existing edge: '+e['id'])
        kind=e.get('kind','flow'); marker='arrow'; sm=None; dash=None
        if diagram=='er': marker='none'
        elif diagram=='class':
            marker={'inheritance':'triangle','realization':'triangle','composition':'none','aggregation':'none','association':'open','dependency':'open'}.get(kind,'open')
            if kind=='composition': sm='diamond'
            if kind in ('realization','dependency'): dash='7,5'
            if kind=='aggregation': sm='diamond_open'
        elif diagram=='dependency': marker='open'; dash='7,5'
        elif diagram=='event_flow':
            marker='open'
            dash='7,5' if kind=='ack' else None
        edge_role=e.get('role','slate') if diagram=='event_flow' else 'slate'
        if diagram=='dependency' and kind=='implements': edge_role='orange'
        data=c.edge(e['id'],e['source'],e['target'],path,label=e.get('label',''),kind=kind,marker=marker,start_marker=sm,dash=dash,role=edge_role)
        data['ports']={'source':{'side':sa,'point':start,'field':sf},'target':{'side':sb,'point':end,'field':tf}}
        data['channel_id']=e['id']
        paths.append(path)
        routed.add(e['id'])
    _crossing_gaps(c,paths)
    c.W=max([c.W]+[p[0]+margin for path in paths for p in path]); c.H=max([c.H]+[p[1]+margin+100 for path in paths for p in path])
    _legend(c,diagram)
    return c


def render_architecture(spec,style): return _render(spec,style,'architecture')
def render_er(spec,style): return _render(spec,style,'er')
def render_class(spec,style): return _render(spec,style,'class')
def render_deployment(spec,style): return _render(spec,style,'deployment')
def render_dependency(spec,style): return _render(spec,style,'dependency')
