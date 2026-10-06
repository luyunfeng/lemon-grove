"""Independent structure, text and route checks for V2 diagram artifacts."""
import json,math,re,xml.etree.ElementTree as ET
from pathlib import Path
from collections import Counter
from semantic_rules import inspect as inspect_semantics

def normalize(s):return re.sub(r'\s+','',str(s))
def bounds_intersect(a,b,epsilon=1):return min(a['x']+a['w'],b['x']+b['w'])-max(a['x'],b['x'])>epsilon and min(a['y']+a['h'],b['y']+b['h'])-max(a['y'],b['y'])>epsilon
def segment_hits(a,b,box):
 x1,y1=a;x2,y2=b;x,y,w,h=box['x'],box['y'],box['w'],box['h'];pad=2
 if abs(x1-x2)<.01:return x+pad<x1<x+w-pad and max(min(y1,y2),y+pad)<min(max(y1,y2),y+h-pad)
 if abs(y1-y2)<.01:return y+pad<y1<y+h-pad and max(min(x1,x2),x+pad)<min(max(x1,x2),x+w-pad)
 return False

def check(spec,folder):
 p=Path(folder);layout=json.loads((p/'layout.json').read_text(encoding='utf-8'));root=ET.parse(p/'diagram.svg').getroot();errors=[];warnings=[]
 expected={n['id'] for n in spec['nodes']+spec.get('pseudonodes',[])};actual=[e.get('data-node-id') for e in root.iter() if e.get('data-node-id')]
 if expected!=set(actual) or len(actual)!=len(expected):errors.append({'code':'node-coverage','expected':sorted(expected),'actual':actual})
 expected_edges={e['id']:(e['source'],e['target']) for e in spec.get('messages',spec.get('edges',[]))};actual_edges={e.get('data-edge-id'):(e.get('data-source'),e.get('data-target')) for e in root.iter() if e.get('data-edge-id')}
 if expected_edges!=actual_edges:errors.append({'code':'edge-coverage'})
 for id,(a,b) in expected_edges.items():
  if a not in expected or b not in expected:errors.append({'code':'unknown-endpoint','edge':id})
 for e in root.iter():
  if e.tag.rsplit('}',1)[-1] in ('script','foreignObject','image','filter','mask','clipPath','pattern'):errors.append({'code':'unsupported-svg','tag':e.tag})
 alltext=normalize(''.join(''.join(e.itertext()) for e in root.iter() if e.tag.rsplit('}',1)[-1]=='text'))
 for n in spec['nodes']:
  for text in [n.get('label',n.get('title','')),*n.get('lines',n.get('detail',[]))]:
   if text and normalize(text) not in alltext:errors.append({'code':'missing-text','node':n['id'],'text':text})
 for e in spec.get('edges',[]):
  if e.get('label') and normalize(e['label']) not in alltext:errors.append({'code':'missing-edge-label','edge':e['id']})
 boxes=layout['nodes']
 # Every connector touching a diamond must terminate exactly at a vertex.
 for edge in layout['edges']:
  for node_id,point in ((edge['source'],edge['points'][0]),(edge['target'],edge['points'][-1])):
   box=next((b for b in boxes if b['id']==node_id and b.get('shape')=='diamond'),None)
   if box:
    x,y,w,h=box['x'],box['y'],box['w'],box['h'];vertices=[(x,y+h/2),(x+w,y+h/2),(x+w/2,y),(x+w/2,y+h)]
    if min(math.hypot(point[0]-vx,point[1]-vy) for vx,vy in vertices)>.1:errors.append({'code':'diamond-endpoint-not-vertex','edge':edge['id'],'node':node_id,'point':point})
 for i,a in enumerate(boxes):
  if a['x']<0 or a['y']<0 or a['x']+a['w']>layout['width'] or a['y']+a['h']>layout['height']:errors.append({'code':'node-outside-canvas','node':a['id']})
  for b in boxes[i+1:]:
   if bounds_intersect(a,b):errors.append({'code':'node-overlap','nodes':[a['id'],b['id']]})
 for item in layout.get('overflows',[]):errors.append({'code':'text-overflow',**item})
 for t in layout['texts']:
  if t['x']<-1 or t['y']<-1 or t['x']+t['w']>layout['width']+1 or t['y']+t['h']>layout['height']+1:errors.append({'code':'text-outside-canvas','text':t['text']})
  owner=t.get('owner')
  if owner and not owner.startswith('edge:'):
   box=next((b for b in boxes if b['id']==owner),None)
   if owner.startswith('panel:'):box=next((b for b in layout['panels'] if b['id']==owner[6:]),None)
   if box and (t['x']<box['x']-1 or t['x']+t['w']>box['x']+box['w']+1):errors.append({'code':'text-width-overflow','node':owner,'text':t['text']})
  if owner and owner.startswith('edge:'):
   for b in boxes:
    if bounds_intersect(t,b):errors.append({'code':'label-on-node','edge':owner[5:],'node':b['id'],'text':t['text']})
 for edge in layout['edges']:
  for a,b in zip(edge['points'],edge['points'][1:]):
   for box in boxes:
    if box['id'] not in (edge['source'],edge['target']) and segment_hits(a,b,box):errors.append({'code':'edge-through-node','edge':edge['id'],'node':box['id']})
 # Proper intersections are warnings, since shared junctions may be intentional.
 crossings=[]
 for i,ea in enumerate(layout['edges']):
  for eb in layout['edges'][i+1:]:
   for a,b in zip(ea['points'],ea['points'][1:]):
    for c,d in zip(eb['points'],eb['points'][1:]):
     if abs(a[0]-b[0])<.01 and abs(c[1]-d[1])<.01:
      if min(c[0],d[0])+.1<a[0]<max(c[0],d[0])-.1 and min(a[1],b[1])+.1<c[1]<max(a[1],b[1])-.1:crossings.append([ea['id'],eb['id'],[a[0],c[1]]])
     elif abs(a[1]-b[1])<.01 and abs(c[0]-d[0])<.01:
      if min(a[0],b[0])+.1<c[0]<max(a[0],b[0])-.1 and min(c[1],d[1])+.1<a[1]<max(c[1],d[1])-.1:crossings.append([ea['id'],eb['id'],[c[0],a[1]]])
 if crossings:warnings.append({'code':'edge-crossings','count':len(crossings),'pairs':crossings})
 shared=[]
 for i,ea in enumerate(layout['edges']):
  for eb in layout['edges'][i+1:]:
   for a,b in zip(ea['points'],ea['points'][1:]):
    for c,d in zip(eb['points'],eb['points'][1:]):
     horizontal=abs(a[1]-b[1])<.01 and abs(c[1]-d[1])<.01 and abs(a[1]-c[1])<.01
     vertical=abs(a[0]-b[0])<.01 and abs(c[0]-d[0])<.01 and abs(a[0]-c[0])<.01
     axis=0 if horizontal else 1
     if horizontal or vertical:
      overlap=min(max(a[axis],b[axis]),max(c[axis],d[axis]))-max(min(a[axis],b[axis]),min(c[axis],d[axis]))
      if overlap>4:shared.append({'edges':[ea['id'],eb['id']],'length':overlap})
 if shared:warnings.append({'code':'shared-segments-review-required','count':len(shared),'segments':shared})
 errors.extend(inspect_semantics(spec,layout))
 result={'nodes':len(boxes),'edges':len(layout['edges']),'errors':errors,'warnings':warnings,'counts':{'errors':len(errors),'warnings':len(warnings),'crossings':len(crossings)}}
 (p/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2), encoding='utf-8');return result

def native_text_check(svg,nodes):
 root=ET.parse(svg).getroot();expected=[''.join(e.itertext()) for e in root.iter() if e.tag.rsplit('}',1)[-1]=='text'];actual=Counter(normalize(n.get('text',{}).get('text','')) for n in nodes);missing=[]
 for value in expected:
  key=normalize(value)
  if not key:continue
  if actual[key]:actual[key]-=1
  else:missing.append(value)
 return {'text_count':len(expected),'missing':missing,'passed':not missing}
