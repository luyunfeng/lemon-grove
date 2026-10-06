"""Deterministic V2 behavioral layouts. All drawing goes through Canvas."""
import math
from itertools import permutations
import unicodedata

try:
    from .canvas import Canvas
except ImportError:
    from canvas import Canvas


def _width(text, size):
    return sum(1 if unicodedata.east_asian_width(c) in 'WF' else .57 for c in str(text)) * size


def _settings(style):
    defaults = dict(body_font=20, node_font=24, label_font=18, node_header=44,
                    panel_header=42, padding=18, margin=52, gap_x=90, gap_y=64,
                    row_height=34, stroke=2)
    defaults.update(style or {})
    return defaults


def _validate(spec, edges=None):
    nodes = spec.get('nodes', [])
    ids = [n['id'] for n in nodes]
    if not nodes or len(ids) != len(set(ids)):
        raise ValueError('nodes must be nonempty with unique ids')
    edges = spec.get('edges', []) if edges is None else edges
    eids = [e['id'] for e in edges]
    if len(eids) != len(set(eids)):
        raise ValueError('edge/message ids must be unique')
    for e in edges:
        if e['source'] not in ids or e['target'] not in ids:
            raise ValueError('unknown endpoint: ' + e['id'])
    return nodes, edges


def _node_size(n, s, metrics):
    """Measure individual cards; empty bodies do not reserve a body compartment."""
    title = n.get('label', n['id'])
    kind = n.get('kind', '')
    if kind in ('initial', 'final'):
        return 30, 30
    if kind in ('fork', 'join'):
        return 240, 14
    w = max(240, min(440, max(metrics.measure(t, s['node_font'],'bold')
                             for t in str(title).split('\n')) + 2*s['padding']))
    if n.get('lines') and kind!='decision':
        w=max(w,min(440,max(metrics.measure(t,s['body_font']) for t in n['lines'])+2*s['padding']))
    if kind in ('decision','merge'):
        w = max(320, min(560, w / .68))
        rows = len(metrics.wrap(title, w*.68, s['node_font'],'bold'))
        h = max(104, rows*s['node_font']*2.5)
        if n.get('lines'):
            w = max(w, max(metrics.measure(t, s['body_font']-2) for t in n['lines']) / .55)
            h += len(n['lines'])*s['body_font']*3
        return w, h
    rows = len(metrics.wrap(title, w-2*s['padding'], s['node_font'],'bold'))
    h = s['node_header'] + (rows-1)*s['node_font']*1.2
    body = sum(len(metrics.wrap(t, w-2*s['padding'], s['body_font'])) for t in n.get('lines', []))
    if body:
        h += s['padding']*1.5 + s['body_font']*.35 + body*s['body_font']*1.38 + 6
    if kind == 'store':
        h = max(94, 38 + rows*s['node_font']*1.2 + body*s['body_font']*1.38 + 24)
    return w, h


def _size(nodes, s):
    metrics = Canvas({'nodes': nodes}, s, 1, 1)
    sizes = [_node_size(n, s, metrics) for n in nodes]
    return max(w for w,h in sizes), max(h for w,h in sizes)


def _edge(c, e, points, label_pos=None):
    c.edge(e['id'], e['source'], e['target'], points, label=e.get('label', ''),
           kind=e.get('kind', 'flow'), role=e.get('role', 'slate'), label_pos=label_pos)


def _ranks(nodes, edges):
    """Longest forward rank, removing only DFS back edges and explicit feedback.

    Retry can be a forward transition into a retry state, so its kind alone is
    not sufficient to remove it from the layout DAG.
    """
    order = {n['id']: i for i,n in enumerate(nodes)}
    outgoing = {n['id']: [] for n in nodes}
    for e in edges:
        if e.get('kind') != 'feedback' and e['source'] != e['target']:
            outgoing[e['source']].append(e)
    seen, active, back, post = set(), set(), set(), []
    def visit(id):
        seen.add(id); active.add(id)
        for e in outgoing[id]:
            target = e['target']
            if target in active:
                back.add(e['id'])
            elif target not in seen:
                visit(target)
        active.remove(id); post.append(id)
    # Initial nodes may be supplied separately at the end of the node list.
    for n in sorted(nodes, key=lambda n: (n.get('kind') != 'initial', n.get('stage', order[n['id']]))):
        if n['id'] not in seen:
            visit(n['id'])
    forward = [e for e in edges if e.get('kind') != 'feedback' and e['id'] not in back and e['source'] != e['target']]
    rank = {n['id']: 0 for n in nodes}
    for id in reversed(post):
        for e in forward:
            if e['source'] == id:
                rank[e['target']] = max(rank[e['target']], rank[id]+1)
    return rank, forward


def _positions(spec, nodes, edges, sizes, s, mode, metrics):
    rank, forward = _ranks(nodes, edges)
    if mode=='swimlane' and _orientation(spec, s)=='horizontal':
        byid={n['id']:n for n in nodes}
        compressed={id:0 for id in rank}
        for id in sorted(rank,key=rank.get):
            outgoing=[e for e in forward if e['source']==id]
            for e in outgoing:
                incoming=[f for f in forward if f['target']==e['target']]
                after=[f for f in forward if f['source']==e['target']]
                before=[f for f in forward if f['target']==id]
                same_phase=(len(outgoing)==len(incoming)==1 and byid[id]['lane']!=byid[e['target']]['lane']
                            and (not after or any(byid[f['target']]['lane']==byid[e['target']]['lane'] for f in after))
                            and (not before or any(byid[f['source']]['lane']==byid[id]['lane'] for f in before)))
                compressed[e['target']]=max(compressed[e['target']],compressed[id]+(0 if same_phase else 1))
        rank=compressed
    maxw = max(w for w,h in sizes.values())
    maxh = max(h for w,h in sizes.values())
    labelw = max([metrics.measure(e.get('label',''), s['label_font']) for e in edges] or [0])
    gx = max(s['gap_x'], labelw+56)
    gy = max(s['gap_y'], s['label_font']*3+30, labelw*.4)
    if mode == 'state':
        gy = max(gy, s['label_font']*3+60)
    left = s['margin'] + max(72, labelw*.6)
    top = 172
    boxes, panels = {}, []
    def put(n, cx, cy):
        w,h = sizes[n['id']]
        boxes[n['id']] = (cx-w/2, cy-h/2, w, h)
    if mode == 'swimlane':
        lanes = spec.get('lanes', [])
        lane_ids = [lane['id'] for lane in lanes]
        if not lanes or len(lane_ids) != len(set(lane_ids)):
            raise ValueError('swimlane requires unique lanes')
        if any(n.get('lane') not in lane_ids for n in nodes):
            raise ValueError('unknown swimlane')
        if _orientation(spec, s) == 'vertical':
            # Responsibility columns; time follows graph rank, not array order.
            slots = {}
            for n in nodes:
                slots.setdefault((n['lane'], rank[n['id']]), []).append(n)
            lane_widths = {}
            for lane in lanes:
                groups = [g for (lid, r), g in slots.items() if lid == lane['id']]
                lane_widths[lane['id']] = max(
                    300, metrics.measure(lane.get('label', lane['id']), s['node_font'], 'bold') + 48,
                    max((sum(sizes[n['id']][0] for n in group) + gx*(len(group)-1) + 96
                         for group in groups), default=0))
            row_y = {}; cursor_y = top + s['panel_header'] + 60
            for r in sorted(set(rank.values())):
                rh = max(sizes[n['id']][1] for n in nodes if rank[n['id']] == r)
                row_y[r] = cursor_y + rh/2
                cursor_y += rh + gy
            cursor_x = left
            for i, lane in enumerate(lanes):
                width = lane_widths[lane['id']]
                panels.append((lane, cursor_x, top, width, cursor_y-top+24, i))
                for (lid, r), group in slots.items():
                    if lid != lane['id']:
                        continue
                    total = sum(sizes[n['id']][0] for n in group) + gx*(len(group)-1)
                    x = cursor_x + (width-total)/2
                    for n in group:
                        nw, _ = sizes[n['id']]
                        put(n, x+nw/2, row_y[r]); x += nw+gx
                cursor_x += width + 36
            return boxes, panels
        # Horizontal responsibility bands, columns are graph-derived stages.
        # Multiple actions in the same lane/stage occupy independent subrows.
        slots = {}
        for n in nodes:
            slots.setdefault((n['lane'], rank[n['id']]), []).append(n)
        label_width = max(metrics.measure(a.get('label',a['id']),s['node_font'],'bold') for a in lanes)+40
        content_x = left + label_width + 24
        ranks=sorted(set(rank.values()))
        widths={r:max(sizes[n['id']][0] for n in nodes if rank[n['id']]==r) for r in ranks}
        # Long feedback labels have long perimeter tracks and must not enlarge every stage gap.
        primary=[e for e in forward if e.get('kind','flow')=='flow' and rank[e['target']]==rank[e['source']]+1]
        short_labels=[metrics.measure(e.get('label',''),s['label_font']) for e in primary]
        lane_gap=max(s.get('swimlane_gap_x',112),max(short_labels,default=0)+36)
        starts={};cursor=content_x
        for r in ranks:starts[r]=cursor;cursor+=widths[r]+lane_gap
        y = top
        for i,lane in enumerate(lanes):
            lane_groups={r:sorted(group,key=lambda n:any(e['source']==n['id'] and e.get('kind')=='feedback' for e in edges))
                         for (lid,r),group in slots.items() if lid==lane['id']}
            count=max([len(v) for v in lane_groups.values()] or [1])
            heights=[max((sizes[g[j]['id']][1] for g in lane_groups.values() if j<len(g)),default=s['node_header']) for j in range(count)]
            rowgap=max(64,s['label_font']*3);inset=max(60,s['node_font']*2.5)
            band_h=sum(heights)+rowgap*(count-1)+inset*2+(s['label_font']*1.8 if i==len(lanes)-1 else 0)
            panels.append((lane, left, y, cursor-lane_gap-content_x+label_width+48, band_h, i))
            for r,group in lane_groups.items():
                for j,n in enumerate(group):
                    put(n,starts[r]+widths[r]/2,y+inset+sum(heights[:j])+rowgap*j+heights[j]/2)
            y += band_h+28
    elif mode == 'dataflow':
        processes = sorted([n for n in nodes if n.get('kind','process')=='process'],key=lambda n:(rank[n['id']],n.get('stage',0)))
        row = {n['id']:i for i,n in enumerate(processes)}
        step = maxh+gy*1.7
        occupied = set()
        for n in processes:
            put(n,left+(maxw+gx)+maxw/2,top+row[n['id']]*step+maxh/2)
        for n in nodes:
            if n['id'] in row:
                continue
            neighbors = [row[e['target'] if e['source']==n['id'] else e['source']]
                         for e in edges if n['id'] in (e['source'],e['target'])
                         and (e['target'] if e['source']==n['id'] else e['source']) in row]
            r = sum(neighbors)/len(neighbors) if neighbors else len(processes)
            col = 2 if n.get('kind')=='store' else 0
            while (col,r) in occupied:
                r += 1
            occupied.add((col,r))
            put(n,left+col*(maxw+gx)+maxw/2,top+r*step+maxh/2)
    else:
        byid = {n['id']: n for n in nodes}
        parents = {id:[] for id in byid}
        children = {id:[] for id in byid}
        for e in forward:
            if e['target'] not in children[e['source']]:
                children[e['source']].append(e['target'])
                parents[e['target']].append(e['source'])
        depth = {}
        for id in sorted(byid,key=lambda id:rank[id],reverse=True):
            depth[id] = 1+max([depth[t] for t in children[id]] or [0])
        columns = {}
        for id in sorted(byid,key=lambda id:rank[id]):
            if id not in columns:
                ps = parents[id]
                columns[id] = sum(columns[p] for p in ps)/len(ps) if ps else 0
            kids = children[id]
            if len(kids)==1:
                columns.setdefault(kids[0],columns[id])
            elif kids:
                if mode=='state':
                    # Keep waiting/retry left, failure middle, success right.
                    kids = sorted(kids,key=lambda t: {'waiting':0,'failure':1,'success':2}.get(byid[t].get('kind'),1))
                    offsets = [i-(len(kids)-1)/2 for i in range(len(kids))]
                else:
                    kids = sorted(kids,key=lambda t:-depth[t])
                    offsets = list(range(len(kids)))
                for t,offset in zip(kids,offsets):
                    if len(parents[t])==1:
                        columns[t] = columns[id]+offset
        # Merge nodes return to the average predecessor column; collisions are
        # resolved per rank, independent of node ids or the benchmark content.
        used = {}
        for id in sorted(byid,key=lambda id:rank[id]):
            if len(parents[id])>1:
                columns[id] = sum(columns[p] for p in parents[id])/len(parents[id])
            elif parents[id] and len(children[parents[id][0]])==1:
                columns[id] = columns[parents[id][0]]
            col=columns[id]
            while any(abs(col-c)<.9 for c in used.get(rank[id],[])):
                col+=1
            columns[id]=col; used.setdefault(rank[id],[]).append(col)
        mincol=min(columns.values())
        row_heights={r:max(sizes[n['id']][1] for n in nodes if rank[n['id']]==r) for r in set(rank.values())}
        row_y={}; y=top
        for r in sorted(row_heights):
            row_y[r]=y+row_heights[r]/2; y+=row_heights[r]+gy
        for n in nodes:
            put(n,left+(columns[n['id']]-mincol)*(maxw+gx)+maxw/2,row_y[rank[n['id']]])
    return boxes, panels


def _ports(nodes, edges, boxes, mode):
    """Allocate ALL incoming/outgoing endpoints together, never two per port."""
    kinds={n['id']:n.get('kind','') for n in nodes}
    groups={}; sides={}
    for i,e in enumerate(edges):
        a,b=boxes[e['source']],boxes[e['target']]
        dx=b[0]+b[2]/2-a[0]-a[2]/2; dy=b[1]+b[3]/2-a[1]-a[3]/2
        if e['source']==e['target']:
            ss,ts='right','bottom'
        elif mode=='activity' and dy>0:
            ss,ts='bottom','top'
        elif mode=='dataflow':
            ss,ts=('right','left') if dx>1 else ('left','right') if dx<-1 else ('left','left')
        elif mode=='swimlane':
            ss,ts=(('right','left') if dx>1 else (('bottom','bottom') if dy>1 else ('top','top')) if dx<-1 else ('bottom','top') if dy>0 else ('top','bottom'))
            lane_ids=list(dict.fromkeys(n.get('lane') for n in nodes))
            lane_of={n['id']:n.get('lane') for n in nodes}
            if dx>1 and lane_ids.index(lane_of[e['source']])-lane_ids.index(lane_of[e['target']])>1:
                ss=ts='top'
        elif dy<0:
            ss=ts='left'
        elif abs(dx)>1:
            ss,ts=('right' if dx>0 else 'left'),'top'
        else:
            ss,ts='bottom','top'
        sides[e['id']]=(ss,ts)
        for end,(id,side,other) in enumerate(((e['source'],ss,b),(e['target'],ts,a))):
            coordinate=other[1]+other[3]/2 if side in ('left','right') else other[0]+other[2]/2
            groups.setdefault((id,side),[]).append((coordinate,i,end,e['id']))
    ports={}
    # Diamonds have four geometric vertices, not a rectangular edge with
    # sliding connection points. Allocate incoming/outgoing endpoints jointly.
    diamond_ids={id for id,kind in kinds.items() if kind in ('decision','merge')}
    for id in sorted(diamond_ids):
        x,y,w,h=boxes[id]
        vertices={'left':(x,y+h/2),'right':(x+w,y+h/2),'top':(x+w/2,y),'bottom':(x+w/2,y+h)}
        normals={'left':(-1,0),'right':(1,0),'top':(0,-1),'bottom':(0,1)}
        incidents=[]
        for i,e in enumerate(edges):
            for end,key,other_key in ((0,'source','target'),(1,'target','source')):
                if e[key]==id:
                    other=boxes[e[other_key]]
                    incidents.append((e['id'],end,(other[0]+other[2]/2,other[1]+other[3]/2),sides[e['id']][end]))
        if len(incidents)>4:
            raise ValueError('Diamond '+id+' has more than four incident edges; use an explicit multi-view/decision decomposition instead of attaching lines to sloped sides')
        def cost(assignment):
            value=0
            for (_,_,other,preferred),side in zip(incidents,assignment):
                vx,vy=vertices[side];nx,ny=normals[side];dx,dy=other[0]-vx,other[1]-vy
                value+=abs(dx)+abs(dy)+(0 if side==preferred else (w+h)*.05)
                if dx*nx+dy*ny<0:value+=(w+h)*2
            return value
        assignment=min(permutations(vertices,len(incidents)),key=cost)
        for (eid,end,_,_),side in zip(incidents,assignment):ports[eid,end]=(vertices[side],side)
    for (id,side),entries in groups.items():
        if id in diamond_ids:continue
        x,y,w,h=boxes[id]
        if kinds[id] in ('initial','final'):
            x+=w*.2; y+=h*.2; w*=.6; h*=.6
        for j,(_,i,end,eid) in enumerate(sorted(entries)):
            f=.5 if len(entries)==1 else .2+.6*j/(len(entries)-1)
            if side in ('left','right'):
                py=y+h*f; px=x if side=='left' else x+w
            else:
                px=x+w*f; py=y if side=='top' else y+h
            ports[eid,end]=((px,py),side)
    return ports


def _segment_conflict(a,b,c,d):
    """Overlap/T contacts are forbidden; a proper crossing has a high cost."""
    eps=.01
    vertical=abs(a[0]-b[0])<eps
    other_vertical=abs(c[0]-d[0])<eps
    axis=1 if vertical else 0; fixed=1-axis
    if vertical==other_vertical:
        if abs(a[fixed]-c[fixed])<eps and min(max(a[axis],b[axis]),max(c[axis],d[axis])) >= max(min(a[axis],b[axis]),min(c[axis],d[axis]))-eps:
            return None
        return 0
    p=(a[0],c[1]) if vertical else (c[0],a[1])
    if all(min(u[k],v[k])-eps<=p[k]<=max(u[k],v[k])+eps for u,v in ((a,b),(c,d)) for k in (0,1)):
        if any(abs(p[0]-q[0])<eps and abs(p[1]-q[1])<eps for q in (a,b,c,d)):
            return None
        return 1
    return 0


def _port_stub(p,side,boxes):
    endpoint_box=next((box for box in boxes if _on_box(p,box)),None)
    if endpoint_box:
        x,y,w,h=endpoint_box
        return {'left':(x-24,p[1]),'right':(x+w+24,p[1]),
                'top':(p[0],y-24),'bottom':(p[0],y+h+24)}[side]
    dx,dy={'left':(-1,0),'right':(1,0),'top':(0,-1),'bottom':(0,1)}[side]
    return (p[0]+dx*24,p[1]+dy*24)


def _route(start,end,boxes,used,index):
    """Local orthogonal visibility grid, shortest route with bend/crossing cost.

    Only local renderer geometry is considered here; text avoidance belongs to
    Canvas. Dedicated ports and reserved segments forbid false T junctions.
    """
    import heapq
    (a,ss),(b,ts)=start,end
    A,B=_port_stub(a,ss,boxes),_port_stub(b,ts,boxes)
    obstacles=[(x-10,y-10,x+w+10,y+h+10) for x,y,w,h in boxes]
    def blocked(p,q):
        for x,y,X,Y in obstacles:
            if abs(p[0]-q[0])<.01:
                if x<p[0]<X and max(min(p[1],q[1]),y)<min(max(p[1],q[1]),Y):return True
            elif y<p[1]<Y and max(min(p[0],q[0]),x)<min(max(p[0],q[0]),X):return True
        return False
    def penalty(p,q):
        result=0
        for u,v in used:
            k=_segment_conflict(p,q,u,v)
            if k is None:return None
            result+=k*600
        return result
    def compact(points):
        result=[]
        for p in points:
            if result and p==result[-1]:continue
            if len(result)>1 and ((abs(result[-2][0]-result[-1][0])<.01 and abs(p[0]-result[-1][0])<.01) or
                                  (abs(result[-2][1]-result[-1][1])<.01 and abs(p[1]-result[-1][1])<.01)):
                result[-1]=p
            else:result.append(p)
        return result
    # Common adjacent-node paths require no grid search.
    candidates=[[A,B]] if A[0]==B[0] or A[1]==B[1] else []
    elbows=[[A,(A[0],B[1]),B],[A,(B[0],A[1]),B]]
    if ss in ('left','right'):
        elbows.reverse()
    candidates += elbows
    good=[]
    for candidate in candidates:
        points=compact([a]+candidate+[b]); cost=0
        for j,(p,q) in enumerate(zip(points,points[1:])):
            # Endpoint access is permitted inside its own expanded obstacle.
            if j not in (0,len(points)-2) and blocked(p,q):break
            # Always test full route against unrelated nodes below.
            if any(_hits_box(p,q,box) for box in boxes if not (_on_box(a,box) or _on_box(b,box))):break
            v=penalty(p,q)
            if v is None:break
            cost+=abs(p[0]-q[0])+abs(p[1]-q[1])+v+30
        else:good.append((cost,points))
    direct=abs(a[0]-b[0])+abs(a[1]-b[1])
    if good and min(good,key=lambda item:round(item[0],4))[0]<direct+500:
        return min(good,key=lambda item:round(item[0],4))[1]
    offset=28+index*3
    xs=sorted(set([A[0],B[0]]+[v for x,y,w,h in boxes for v in (x-offset,x+w+offset)]))
    ys=sorted(set([A[1],B[1]]+[v for x,y,w,h in boxes for v in (y-offset,y+h+offset)]))
    source=(xs.index(A[0]),ys.index(A[1]),-1)
    target=(xs.index(B[0]),ys.index(B[1]))
    queue=[(0,0,source)]; costs={source:0}; prev={}; finish=None
    while queue:
        _,cost,state=heapq.heappop(queue)
        if cost!=costs[state]:continue
        ix,iy,direction=state
        if (ix,iy)==target:
            finish=state;break
        for jx,jy,newdir in ((ix-1,iy,0),(ix+1,iy,0),(ix,iy-1,1),(ix,iy+1,1)):
            if not (0<=jx<len(xs) and 0<=jy<len(ys)):continue
            p,q=(xs[ix],ys[iy]),(xs[jx],ys[jy])
            if blocked(p,q):continue
            v=penalty(p,q)
            if v is None:continue
            newcost=cost+abs(p[0]-q[0])+abs(p[1]-q[1])+v+(36 if direction not in (-1,newdir) else 0)
            nxt=(jx,jy,newdir)
            if newcost<costs.get(nxt,float('inf')):
                costs[nxt]=newcost;prev[nxt]=state
                heuristic=abs(q[0]-B[0])+abs(q[1]-B[1])
                heapq.heappush(queue,(newcost+heuristic,newcost,nxt))
    if finish is None:
        if good:return min(good,key=lambda item:item[0])[1]
        raise ValueError('no independent orthogonal route for edge index '+str(index))
    path=[]
    while finish!=source:
        path.append((xs[finish[0]],ys[finish[1]]));finish=prev[finish]
    return compact([a,A]+list(reversed(path))+[b])


def _on_box(p,box):
    x,y,w,h=box
    return x-.1<=p[0]<=x+w+.1 and y-.1<=p[1]<=y+h+.1


def _hits_box(a,b,box):
    x,y,w,h=box
    if abs(a[0]-b[0])<.01:
        return x+1<a[0]<x+w-1 and max(min(a[1],b[1]),y+1)<min(max(a[1],b[1]),y+h-1)
    return y+1<a[1]<y+h-1 and max(min(a[0],b[0]),x+1)<min(max(a[0],b[0]),x+w-1)


def _graph(spec, style, mode):
    nodes, edges = _validate(spec)
    style = style or {}
    if mode=='swimlane':style={**style,'label_font':style.get('swimlane_label_font',22)}
    s = _settings(style)
    c = Canvas(spec,style or {},1,1)
    if mode == 'dataflow':
        kinds = {n['id']: n.get('kind', 'process') for n in nodes}
        for e in edges:
            if not e.get('label') or 'process' not in (kinds[e['source']],kinds[e['target']]):
                raise ValueError('DFD flows require data names and a process endpoint: '+e['id'])
    sizes={n['id']:_node_size(n,s,c) for n in nodes}
    if mode=='dataflow':
        widths={kind:max(sizes[n['id']][0] for n in nodes if n.get('kind','process')==kind)
                for kind in {n.get('kind','process') for n in nodes}}
        sizes={n['id']:(widths[n.get('kind','process')],sizes[n['id']][1]) for n in nodes}
        byid={n['id']:n for n in nodes}
        for n in nodes:
            if n.get('kind')!='process':continue
            sides={'left':0,'right':0}
            for e in edges:
                if n['id'] not in (e['source'],e['target']):continue
                other=e['target'] if e['source']==n['id'] else e['source']
                sides['right' if byid[other].get('kind')=='store' else 'left']+=1
            width,height=sizes[n['id']]
            sizes[n['id']]=(width,max(height,(max(sides.values())-1)*24/.6))
    boxes,panels=_positions(spec,nodes,edges,sizes,s,mode,c)
    if mode == 'activity':
        # A synchronization bar spans its parallel branches, avoiding fake
        # serial elbows and keeping incoming/outgoing tokens on opposite sides.
        for n in nodes:
            if n.get('kind') not in ('fork','join'):
                continue
            neighbors = [e['target'] for e in edges if e['source']==n['id']] if n['kind']=='fork' else [e['source'] for e in edges if e['target']==n['id']]
            centers = [boxes[id][0]+boxes[id][2]/2 for id in neighbors]
            x,y,w,h = boxes[n['id']]
            lo,hi = min(centers)-48,max(centers)+48
            boxes[n['id']] = (lo,y,max(96,hi-lo),h)
    port_mode = 'activity' if mode == 'swimlane' and _orientation(spec, s) == 'vertical' else mode
    ports=_ports(nodes,edges,boxes,port_mode)
    paths={};used=[]
    # Short neighboring connections claim their natural corridors first.
    def distance(e):
        a,_=ports[e['id'],0];b,_=ports[e['id'],1]
        return abs(a[0]-b[0])+abs(a[1]-b[1])
    ordered=sorted(edges,key=lambda e:(e.get('kind')=='feedback',distance(e)))
    for i,e in enumerate(ordered):
        # Earlier routes must not occupy a later edge's endpoint access corridor.
        future=[]
        for pending in ordered[i+1:]:
            for end in (0,1):
                point,side=ports[pending['id'],end]
                future.append((point,_port_stub(point,side,list(boxes.values()))))
        path=_route(ports[e['id'],0],ports[e['id'],1],list(boxes.values()),used+future,i)
        paths[e['id']]=path;used.extend(zip(path,path[1:]))
    # Reserve label margins without changing any spec text.
    labelw=max([c.measure(e.get('label',''),s['label_font']) for e in edges] or [0])
    minx=min([x for x,y,w,h in boxes.values()]+[p[0] for path in paths.values() for p in path])
    shift=max(0,s['margin']+labelw-minx)
    if shift:
        boxes={id:(x+shift,y,w,h) for id,(x,y,w,h) in boxes.items()}
        paths={id:[(x+shift,y) for x,y in path] for id,path in paths.items()}
        panels=[(a,x+shift,y,w,h,i) for a,x,y,w,h,i in panels]
    c.W=max([x+w for x,y,w,h in boxes.values()]+[p[0] for path in paths.values() for p in path]+[x+w for a,x,y,w,h,i in panels])+s['margin']+labelw*.5
    c.W=max(c.W,c.measure(spec['title'],c.S['title_font'])+2*s['margin'],c.measure(spec.get('subtitle',''),s['body_font'])+2*s['margin'])
    c.H=max([y+h for x,y,w,h in boxes.values()]+[p[1] for path in paths.values() for p in path]+[y+h for a,x,y,w,h,i in panels])+100
    c.title()
    lane_roles=['blue','purple','teal','amber','slate','rose']
    for lane,x,y,w,h,i in panels:
        c.panel('lane-'+lane['id'],x,y,w,h,lane.get('label',lane['id']),role=lane.get('role',lane_roles[i%len(lane_roles)]),header=False)
    lane_role_by_id = {lane['id']: lane.get('role', lane_roles[i % len(lane_roles)])
                       for i, lane in enumerate(spec.get('lanes', []))}
    for n in nodes:
        x,y,w,h=boxes[n['id']];kind=n.get('kind','')
        shape,role='rect','blue'
        if mode=='swimlane':
            role=lane_role_by_id[n['lane']]
            shape='diamond' if kind=='decision' else 'rect'
        elif mode=='flowchart':
            shape,role=('diamond','amber') if kind=='decision' else ('rect','blue')
            if kind!='decision':role={'success':'teal','failure':'rose','reused':'slate'}.get(n.get('outcome'),'blue')
        elif mode=='activity':
            shape={'initial':'start','final':'end','fork':'fork','join':'join',
                   'decision':'diamond','merge':'diamond'}.get(kind,'rect')
            role={'initial':'slate','final':'slate','fork':'purple','join':'purple',
                  'decision':'amber','merge':'amber'}.get(kind,'blue')
        elif mode=='state':
            shape={'initial':'start','final':'end'}.get(kind,'rect')
            role={'initial':'slate','final':'slate','waiting':'purple','active':'blue','success':'teal','failure':'amber'}.get(kind,'blue')
        elif mode=='dataflow':
            shape={'store':'data_store','external':'external','process':'rect'}.get(kind,'rect')
            role={'external':'blue','process':'purple','store':'teal'}.get(kind,'purple')
        # Lane fill encodes ownership; explicit node roles retain action/outcome.
        role=n.get('role',role)
        title=n.get('label',n['id']);lines=n.get('lines',[])
        if shape in ('fork','join'):
            # Canvas supplies the actual bar primitive; labels stay outside it.
            c.node(n['id'],x,y,w,h,title='',lines=[],role=role,shape=shape,header=False)
            if title:
                c.text(x+w+16,y+h/2+s['label_font']*.3,title,s['label_font'],
                       fill=c.label_color(role),owner=None)
                c.W=max(c.W,x+w+32+c.measure(title,s['label_font']))
            continue
        if shape=='database':
            # Keep the cylinder primitive, reserve its 28px cap, and place the
            # original title/body in its barrel without changing Canvas.
            box=c.node(n['id'],x,y,w,h,title='',lines=[],role=role,shape=shape,header=False)
            box['label']=title
            yy=y+38+s['node_font']
            for text in c.wrap(title,w-2*s['padding'],s['node_font']):
                c.text(x+s['padding'],yy,text,s['node_font'],fill=c.color(role),weight='bold',owner=n['id'])
                yy+=s['node_font']*1.2
            for line in lines:
                for text in c.wrap(line,w-2*s['padding'],s['body_font']):
                    c.text(x+s['padding'],yy,text,s['body_font'],owner=n['id']);yy+=s['body_font']*1.38
        else:
            c.node(n['id'],x,y,w,h,title=title,lines=lines,role=role,shape=shape,header=shape=='rect')
    for e in edges:
        points=paths[e['id']]
        hint=None
        if len(points)==2 and points[0][0]==points[1][0] and c.measure(e.get('label',''),s['label_font'])>300:
            hint=(points[0][0],(points[0][1]+points[1][1])/2+s['label_font']*.3)
        _edge(c,e,points,hint)
    # A proper crossing is not a junction. Draw a short gap under the later edge.
    ordered_paths=list(paths.values())
    for i,path in enumerate(ordered_paths):
        seen=set()
        for a,b in zip(path,path[1:]):
            for earlier in ordered_paths[:i]:
                for p,q in zip(earlier,earlier[1:]):
                    hit=None
                    if a[0]==b[0] and p[1]==q[1]:
                        if min(a[1],b[1])<p[1]<max(a[1],b[1]) and min(p[0],q[0])<a[0]<max(p[0],q[0]):hit=(a[0],p[1]);u=(0,1)
                    elif a[1]==b[1] and p[0]==q[0]:
                        if min(a[0],b[0])<p[0]<max(a[0],b[0]) and min(p[1],q[1])<a[1]<max(p[1],q[1]):hit=(p[0],a[1]);u=(1,0)
                    if hit is None or hit in seen:continue
                    seen.add(hit);gap=c.S.get('crossing_gap',12);x,y=hit
                    segment=[(x-gap*u[0],y-gap*u[1]),(x+gap*u[0],y+gap*u[1])]
                    c.line(segment,role=c.S['canvas_fill'],width=c.S['stroke']+12)
                    c.line(segment,width=c.S['stroke'])
    if mode=='swimlane':
        c.note('泳道底色表示责任归属 · 节点色区分动作、判断与结果',y=c.H-35)
    return c

def render_flowchart(spec, style):
    return _graph(spec, style, 'flowchart')


def render_swimlane(spec, style):
    _require_behavior(spec)
    return _graph(spec, style, 'swimlane')


def render_state(spec, style):
    # Pseudonodes may be inline or in a separate list; all become semantic nodes.
    prepared = dict(spec)
    prepared['nodes'] = list(spec.get('nodes', [])) + list(spec.get('pseudonodes', []))
    return _graph(prepared, style, 'state')


def render_dataflow(spec, style):
    return _graph(spec, style, 'dataflow')


def render_sequence(spec, style):
    _require_behavior(spec)
    messages = spec.get('messages', spec.get('edges', []))
    nodes, messages = _validate(spec, messages)
    style = style or {}
    style={**style,'label_font':style.get('sequence_label_font',22)}
    s = _settings(style)
    w,h = _size(nodes,s)
    metrics=Canvas(spec,style,1,1)
    maxlabel = max([metrics.measure(m.get('label',''),s['label_font']) for m in messages] or [0])
    pitch = max(w+s['gap_x'], maxlabel+60)
    self_width = max(110, max([metrics.measure(m.get('label',''),s['label_font'])+48
                              for m in messages if m['source']==m['target']] or [0]))
    if any(m['source']==m['target'] for m in messages):
        pitch = max(pitch, self_width+80)
    margin = s['margin']+30
    xs = {n['id']:margin+i*pitch+w/2 for i,n in enumerate(nodes)}
    step = max(s['gap_y'], s['label_font']*3+28)
    base = 160+h+70
    branches = spec.get('branches', [])
    msg_ids = [m['id'] for m in messages]
    extra = {}
    for branch in branches:
        for j,operand in enumerate(branch.get('operands', [])):
            idx = msg_ids.index(operand['start'])
            extra[idx] = extra.get(idx,0)+(s['panel_header']+20 if j==0 else 16)
    ys,offset = {},0
    for i,m in enumerate(messages):
        offset += extra.get(i,0)
        ys[m['id']] = base+i*step+offset
    bottom = max(ys.values(),default=base)+70
    W = margin*2+w+max(0,len(nodes)-1)*pitch
    if any(m['source']==m['target']==nodes[-1]['id'] for m in messages):
        W += self_width
    W = max(W, metrics.measure(spec['title'], metrics.S['title_font'])+2*margin,
            metrics.measure(spec.get('subtitle',''), s['body_font'])+2*margin)
    H = bottom+120
    prepared = dict(spec, edges=messages)
    c = Canvas(prepared,style,W,H)
    c.title()
    palette=['blue','purple','teal','amber','rose','slate']
    aliases={'orange':'amber','gray':'slate','green':'teal','primary':'blue'}
    explicit={n['id']:aliases.get(n.get('role'),n.get('role')) for n in nodes}
    differentiated=len({r for r in explicit.values() if r in c.palette})>1
    participant_roles={n['id']:(explicit[n['id']] if differentiated and explicit[n['id']] in c.palette
                                else palette[i%len(palette)]) for i,n in enumerate(nodes)}
    for n in nodes:
        x = xs[n['id']]
        c._shape('line', layer='background', x1=x,y1=160+h,x2=x,y2=bottom,
                 stroke='#A9B7C6',stroke_dasharray='6 6',stroke_width=s['stroke'])
    for branch in branches:
        operands=branch.get('operands',[])
        if not operands:
            continue
        start=ys[operands[0]['start']]-s['panel_header']-20
        end=ys[operands[-1]['end']]+max(50,step*.58)
        a,b=margin-22,W-margin+22
        c.line([[a,start],[b,start],[b,end],[a,end],[a,start]],role='slate')
        c.text(a+12,start+24,branch.get('kind','alt'),size=s['label_font'],weight='bold')
        for j,op in enumerate(operands):
            y=ys[op['start']]-28
            if j:
                c.line([[a,y-26],[b,y-26]],role='slate',dash='5 5')
            guard=op.get('guard','');gw=c.measure(guard,s['label_font'])
            c._shape('rect',x=a+65,y=y-s['label_font']-4,width=gw+10,height=s['label_font']*1.4+8,fill='#FFFFFF')
            c.text(a+70,y,guard,size=s['label_font'])
    # Activations are decorations, never additional semantic participants.
    for activation in spec.get('activations',[]):
        x=xs[activation['participant']]
        role=participant_roles[activation['participant']]
        c._shape('rect',layer='background',x=x-10,y=ys[activation['start']],width=20,
                 height=ys[activation['end']]-ys[activation['start']],
                 fill=c.color(role),fill_opacity=.22,stroke=c.color(role),stroke_width=2)
    for m in messages:
        x,X,y=xs[m['source']],xs[m['target']],ys[m['id']]
        kind=m.get('kind','sync')
        if kind not in ('sync','return','async'):
            raise ValueError('sequence kind must be sync, return or async')
        points = [[x,y],[X,y]] if x != X else [[x,y],[x+self_width,y],[x+self_width,y+step*.4],[x,y+step*.4]]
        c.edge(m['id'],m['source'],m['target'],points,label=m.get('label',''),kind=kind,
               role='slate',dash='6 5' if kind=='return' else None,
               marker='open' if kind in ('async','return') else 'arrow',
               label_pos=((x+X)/2 if x!=X else x+self_width/2,y-14))
    for n in nodes:
        c.node(n['id'],xs[n['id']]-w/2,160,w,h,role=participant_roles[n['id']])
    return c


def _orientation(spec, style):
    """Horizontal is the stable default; vertical is an explicit semantic choice."""
    value = spec.get('orientation', style.get('swimlane_orientation', 'horizontal'))
    if value not in ('horizontal', 'vertical'):
        raise ValueError('swimlane orientation must be horizontal or vertical')
    return value


def render_activity(spec, style):
    prepared = dict(spec)
    prepared['nodes'] = list(spec.get('nodes', [])) + list(spec.get('pseudonodes', []))
    prepared.pop('pseudonodes', None)
    _require_behavior(prepared)
    return _graph(prepared, style, 'activity')


def _require_behavior(spec):
    errors = inspect_behavior_extra(spec)
    if errors:
        raise ValueError('behavior contract: ' + str(errors))


def inspect_behavior_extra(spec, layout=None):
    """Return additional semantic errors; usable before rendering or with layout.

    Does not replace common coverage/geometry checks or claim visual approval.
    """
    errors = []
    def fail(code, **detail):
        errors.append({'code': code, **detail})
    kind = spec.get('diagram_type')
    if kind not in ('flowchart','swimlane','sequence','state','activity'):
        return errors
    nodes = spec.get('nodes', []) + spec.get('pseudonodes', [])
    edges = spec.get('messages', spec.get('edges', []))
    byid = {n['id']: n for n in nodes}
    boxes = {n['id']: n for n in (layout or {}).get('nodes', [])}
    if len(byid) != len(nodes):
        fail('behavior-duplicate-node')
    if len({e['id'] for e in edges}) != len(edges):
        fail('behavior-duplicate-edge')
    if any(e['source'] not in byid or e['target'] not in byid for e in edges):
        fail('behavior-unknown-endpoint'); return errors
    incoming = {id: [e for e in edges if e['target']==id] for id in byid}
    outgoing = {id: [e for e in edges if e['source']==id] for id in byid}
    if kind == 'swimlane':
        lanes = spec.get('lanes', [])
        lane_ids = {l['id'] for l in lanes}
        if not lanes or len(lane_ids) != len(lanes):
            fail('swimlane-invalid-lanes')
        for n in nodes:
            if n.get('lane') not in lane_ids:
                fail('swimlane-unknown-owner', node=n['id'])
        if spec.get('orientation','horizontal') not in ('horizontal','vertical'):
            fail('swimlane-invalid-orientation')
        if layout:
            panels = {p['id']:p for p in layout.get('panels',[])}
            for lane in lanes:
                if 'lane-'+lane['id'] not in panels:
                    fail('swimlane-missing-panel', lane=lane['id'])
    if kind in ('flowchart','swimlane','activity'):
        for n in nodes:
            if n.get('kind')=='decision':
                outs=outgoing[n['id']]
                if len(outs)<2 or any(not e.get('label') for e in outs):
                    fail('behavior-decision-guards',node=n['id'])
    if kind == 'activity':
        allowed={'initial','final','action','decision','merge','fork','join'}
        starts=[n['id'] for n in nodes if n.get('kind')=='initial']
        ends=[n['id'] for n in nodes if n.get('kind')=='final']
        if len(starts)!=1 or not ends:
            fail('activity-initial-final')
        for n in nodes:
            id=n['id']; k=n.get('kind'); ni=len(incoming[id]); no=len(outgoing[id])
            if k not in allowed: fail('activity-unknown-kind',node=id,kind=k)
            if k=='initial' and (ni or no!=1):fail('activity-initial-degree',node=id)
            if k=='final' and (no or not ni):fail('activity-final-degree',node=id)
            if k=='fork' and (ni!=1 or no<2):fail('activity-fork-degree',node=id)
            if k=='join' and (ni<2 or no!=1):fail('activity-join-degree',node=id)
            if k=='merge' and (ni<2 or no!=1):fail('activity-merge-degree',node=id)
            if k=='action' and (ni!=1 or no!=1):fail('activity-action-needs-control-node',node=id)
            if k=='decision' and ni!=1:fail('activity-decision-degree',node=id)
            expected={'initial':'start','final':'end','fork':'fork','join':'join',
                      'decision':'diamond','merge':'diamond','action':'rect'}.get(k)
            if layout is not None and boxes.get(id,{}).get('shape')!=expected:
                fail('activity-symbol',node=id,expected=expected)
        def reachable(seeds, reverse=False):
            seen=set(seeds); todo=list(seeds)
            while todo:
                id=todo.pop()
                for e in incoming[id] if reverse else outgoing[id]:
                    target=e['source'] if reverse else e['target']
                    if target not in seen: seen.add(target);todo.append(target)
            return seen
        for id in byid.keys()-reachable(starts):fail('activity-unreachable',node=id)
        for id in byid.keys()-reachable(ends,True):fail('activity-no-final-path',node=id)
    if kind == 'sequence':
        indices={e['id']:i for i,e in enumerate(edges)}
        for e in edges:
            if e.get('kind','sync') not in ('sync','async','return'):
                fail('sequence-invalid-message-kind',edge=e['id'])
        intervals=[]
        for branch in spec.get('branches',[]):
            operands=branch.get('operands',[])
            if branch.get('kind','alt')!='alt' or len(operands)<2:
                fail('sequence-alt-operands');continue
            last=-1
            for op in operands:
                a=indices.get(op.get('start')); b=indices.get(op.get('end'))
                if a is None or b is None or a>b or a<=last or not op.get('guard'):
                    fail('sequence-alt-range',operand=op);continue
                last=b
            if operands and operands[0].get('start') in indices and operands[-1].get('end') in indices:
                intervals.append((indices[operands[0]['start']],indices[operands[-1]['end']]))
        intervals.sort()
        if any(b>=c for (a,b),(c,d) in zip(intervals,intervals[1:])):
            fail('sequence-overlapping-alt-frames')
        for a in spec.get('activations',[]):
            begin=indices.get(a.get('start'));end=indices.get(a.get('end'))
            if a.get('participant') not in byid or begin is None or end is None or begin>end:
                fail('sequence-activation-range',activation=a)
    return errors
