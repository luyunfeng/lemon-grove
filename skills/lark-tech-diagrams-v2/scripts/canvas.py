"""Small deterministic SVG vocabulary for software-engineering diagrams."""
from pathlib import Path
from html import escape
from math import hypot, ceil
import json,re
from PIL import ImageFont

FONT = str(Path(__file__).resolve().parent.parent / 'assets/fonts/NotoSansCJK-Regular.ttc')
DEFAULT = dict(body_font=20,title_font=36,node_font=24,node_header=44,panel_header=42,row_height=34,padding=18,margin=52,gap_x=90,gap_y=64,stroke=2,label_font=18,label_background=True,radius=10,canvas_fill='#FFFFFF',ink='#243247',muted='#64748B')
PALETTE={'blue':['#2563EB','#EFF6FF'],'purple':['#7C3AED','#F5F0FF'],'teal':['#0F9D92','#EAFBF6'],'amber':['#D88A10','#FFF6E4'],'slate':['#526B86','#F0F4F8'],'rose':['#BE3455','#FFF0F4']}

def fnum(x):return str(round(float(x),2)).rstrip('0').rstrip('.') if float(x)%1 else str(int(x))
def attrs(d):return ' '.join(f'{k.replace("_","-")}="{escape(str(v),quote=True)}"' for k,v in d.items() if v is not None)
def luminance(c):
 rgb=[int(c[i:i+2],16)/255 for i in (1,3,5)]
 return sum((v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4)*a for v,a in zip(rgb,[.2126,.7152,.0722]))

class Canvas:
 def __init__(self,spec,style,width=1800,height=1100):
  self.spec=spec;self.S={**DEFAULT,**style};self.W=width;self.H=height;self.palette={**PALETTE,**style.get('palette',{})}
  self.nodes={};self.edges=[];self.texts=[];self.panels=[];self.overflows=[];self.background=[];self.connectors=[];self.objects=[];self.labels=[];self._fonts={}
  self.node_specs={n['id']:n for n in spec.get('nodes',[])}
 def _role(self,role):
  return role if role in self.palette else {'orange':'amber','gray':'slate','green':'teal','primary':'blue','cyan':'teal'}.get(role,role)
 def color(self,role):
  if isinstance(role,str) and role.startswith('#'):return role
  return self.palette.get(self._role(role),self.palette['slate'])[0]
 def tint(self,role):return self.palette.get(self._role(role),self.palette['slate'])[1]
 def label_color(self,role):return self.S.get('text_colors',{}).get(self._role(role),self.color(role))
 def border(self,role):return self.S.get('border_colors',{}).get(self._role(role),self.color(role))
 def measure(self,value,size,weight="normal"):
  key=int(round(size))
  if key not in self._fonts:
   self._fonts[key]=ImageFont.truetype(FONT,key)
  font=self._fonts[key]
  raw=float(font.getlength(str(value)))
  factor=self.S.get('native_bold_width_factor',1.36) if str(weight) in ('bold','700') else self.S.get('native_regular_width_factor',1.10)
  return raw*factor
 def wrap(self,value,width,size,weight="normal"):
  lines=[]
  for source in str(value).split('\n'):
   segment_start=len(lines)
   # Keep short parenthetical phrases and CamelCase words intact when possible.
   tokens=re.findall(r'[（(][^（）()\n]*[）)]|[A-Z]+(?=[A-Z][a-z]|\b)|[A-Z]?[a-z]+|[A-Z]+|[0-9]+|\s+|[^\s]',source)
   units=[]
   for token in tokens:
    units.extend([token] if self.measure(token,size,weight)<=width else list(token))
   line=''
   for token in units:
    if line and self.measure(line+token,size,weight)>width:
     carry=''
     if token[0] in '）)]}，。；：！？、' and line:
      carry=line[-1];line=line[:-1]
     elif line[-1:] in '（([{':carry=line[-1];line=line[:-1]
     if line:lines.append(line.rstrip())
     line=carry+token.lstrip()
    else:line+=token
   lines.append(line)
   if len(lines)-segment_start>=2 and self.measure(lines[-1],size,weight)<width*.28:
    combined=lines[-2]+lines[-1]
    if not re.search(r'[A-Za-z]',combined):
     options=[]
     for cut in range(1,len(combined)):
      left,right=combined[:cut],combined[cut:]
      if right[0] in '）)]}，。；：！？、' or left[-1] in '（([{':continue
      lw,rw=self.measure(left,size,weight),self.measure(right,size,weight)
      if max(lw,rw)<=width:options.append((abs(lw-rw),cut,left,right))
     if options:
      _,_,left,right=min(options);lines[-2:]=[left,right]
  return lines
 def _shape(self,tag,layer='objects',**values):getattr(self,layer).append(f'<{tag} {attrs(values)}/>')
 def text(self,x,y,value,size=None,fill=None,weight='normal',anchor='start',owner=None,layer='objects'):
  value=str(value);size=size or self.S['body_font'];fill=fill or self.S['ink'];w=self.measure(value,size,weight)
  left=x-w/2 if anchor=='middle' else x-w if anchor=='end' else x
  self.texts.append({'text':value,'x':left,'y':y-size,'w':w,'h':size*1.35,'font_size':size,'owner':owner,'layer':layer})
  element=f'<text {attrs(dict(x=x,y=y,font_family="Noto Sans SC",font_size=size,font_weight=weight,fill=fill,text_anchor=anchor))}>{escape(value)}</text>'
  getattr(self,layer).append(element);return element
 def title(self):
  if self.S.get('title_centered'):
   self._title_pending=True;return
  m=self.S['margin'];self.text(m,m+30,self.spec['title'],self.S['title_font'],weight='bold')
  if self.spec.get('subtitle'):self.text(m,m+65,self.spec['subtitle'],self.S['body_font'],fill=self.S['muted'])
 def _finish_title(self):
  if not getattr(self,'_title_pending',False):return
  self._title_pending=False;m=self.S['margin'];cx=self.W/2
  self._shape('line','background',x1=cx-160,y1=m-10,x2=cx,y2=m-10,stroke=self.color('blue'),stroke_width=6,stroke_linecap='round')
  self._shape('line','background',x1=cx,y1=m-10,x2=cx+160,y2=m-10,stroke=self.color('teal'),stroke_width=6,stroke_linecap='round')
  self.text(cx,m+36,self.spec['title'],self.S['title_font'],fill=self.S.get('title_ink',self.S['ink']),weight='bold',anchor='middle',layer='background')
  if self.spec.get('subtitle'):self.text(cx,m+72,self.spec['subtitle'],self.S['body_font'],fill=self.S['muted'],anchor='middle',layer='background')
 def panel(self,id,x,y,w,h,title,role='slate',header=True):
  color=self.color(role);self.panels.append({'id':id,'x':x,'y':y,'w':w,'h':h,'header_h':self.S['panel_header'] if header else 38})
  soft=self.S.get('soft_cards',False)
  self._shape('rect','background',x=x,y=y,width=w,height=h,rx=self.S['radius'],fill=self.tint(role),stroke=self.border(role) if soft else color,stroke_width=self.S.get('panel_border_width',1),stroke_opacity=1 if soft else .3)
  if header and not soft:
   self._shape('rect','background',x=x,y=y,width=w,height=self.S['panel_header'],rx=self.S['radius'],fill=color)
   ink='#FFFFFF' if (1.05/(luminance(color)+.05))>=4 else '#243247'
   self.text(x+self.S['padding'],y+self.S['panel_header']*.69,title,self.S['node_font']-2,fill=ink,weight='bold',owner='panel:'+id,layer='background')
  else:self.text(x+self.S['padding'],y+30,title,self.S['node_font']-2,fill=self.label_color(role),weight='bold',owner='panel:'+id,layer='background')
 def node(self,id,x,y,w,h,title=None,lines=None,role=None,shape='rect',header=True):
  n=self.node_specs.get(id,{});title=n.get('label',n.get('title',id)) if title is None else title
  lines=n.get('lines',n.get('detail',[])) if lines is None else lines;role=role or n.get('role','blue');color=self.color(role);pad=self.S['padding']
  if id in self.nodes:raise ValueError('duplicate node '+id)
  box={'id':id,'x':x,'y':y,'w':w,'h':h,'shape':shape,'role':role,'label':title};self.nodes[id]=box
  self.objects.append(f'<g data-node-id="{escape(id)}">')
  if shape in ('start','end'):
   r=min(w,h)*.3;cx=x+w/2;cy=y+h/2
   self._shape('circle',cx=cx,cy=cy,r=r,fill=color if shape=='start' else '#FFFFFF',stroke=color,stroke_width=self.S['stroke'])
   if shape=='end':self._shape('circle',cx=cx,cy=cy,r=r*.65,fill=color)
   if title:self.text(cx,y+h+24,title,self.S['label_font'],anchor='middle',owner=None)
  elif shape in ('fork','join'):
   self._shape('rect',x=x,y=y,width=w,height=h,rx=min(3,h/3),fill=color,stroke=color,stroke_width=self.S['stroke'])
   if title:self.text(x+w/2,y+h+24,title,self.S['label_font'],fill=self.label_color(role),anchor='middle')
  elif shape=='diamond':
   self._shape('polygon',points=f'{x+w/2},{y} {x+w},{y+h/2} {x+w/2},{y+h} {x},{y+h/2}',fill=self.tint(role),stroke=color,stroke_width=self.S['stroke'])
   tx=self.wrap(title,w*.68,self.S['node_font'],'bold');lh=self.S['node_font']*1.22
   for i,s in enumerate(tx):self.text(x+w/2,y+h/2-lh*(len(tx)-1)/2+i*lh+self.S['node_font']*.36,s,self.S['node_font'],weight='bold',anchor='middle',owner=id)
   if lines:
    for j,s in enumerate(lines):self.text(x+w/2,y+h*.73+j*self.S['body_font']*1.2,s,self.S['body_font']-2,anchor='middle',owner=id)
  else:
   if shape=='database':
    ry=14;self._shape('rect',x=x,y=y+ry,width=w,height=h-2*ry,fill=self.tint(role),stroke=color,stroke_width=self.S['stroke'])
    self._shape('ellipse',cx=x+w/2,cy=y+h-ry,rx=w/2,ry=ry,fill=self.tint(role),stroke=color,stroke_width=self.S['stroke'])
    self._shape('rect',x=x+1,y=y+ry,width=w-2,height=h-2*ry,fill=self.tint(role),stroke='none')
    self._shape('ellipse',cx=x+w/2,cy=y+ry,rx=w/2,ry=ry,fill='#FFFFFF',stroke=color,stroke_width=self.S['stroke'])
   elif shape=='data_store':
    self._shape('rect',x=x,y=y,width=w,height=h,fill=self.tint(role),stroke='none')
    self.line([(x+w,y),(x,y),(x,y+h),(x+w,y+h)],role=role,width=self.S['stroke'])
   else:self._shape('rect',x=x,y=y,width=w,height=h,rx=0 if shape=='external' else self.S['radius'],fill=self.tint(role),stroke=color,stroke_width=self.S['stroke'])
   heading=self.wrap(title,w-2*pad,self.S['node_font'],'bold');head_h=self.S['node_header']+(len(heading)-1)*self.S['node_font']*1.2
   if header and shape!='database' and not self.S.get('soft_cards'):
    self._shape('rect',x=x,y=y,width=w,height=head_h,rx=self.S['radius'],fill=color)
    ink='#FFFFFF' if (1.05/(luminance(color)+.05))>=4 else '#243247'
   else:ink=self.label_color(role)
   if self.S.get('soft_cards') and lines and header:
    self._shape('line',x1=x+pad,y1=y+head_h,x2=x+w-pad,y2=y+head_h,stroke=self.border(role),stroke_width=1)
   base_y=y+(self.S['node_header']+self.S['node_font'])*.5-5+(18 if shape=='database' else 0)
   for i,s in enumerate(heading):self.text(x+pad,base_y+i*self.S['node_font']*1.2,s,self.S['node_font'],fill=ink,weight='bold',owner=id)
   cy=y+head_h+pad+self.S['body_font']*.75+(16 if shape=='database' else 0)
   for line in lines:
    for s in self.wrap(line,w-2*pad,self.S['body_font']):
     self.text(x+pad,cy,s,owner=id);cy+=self.S['body_font']*1.38
   if lines and cy-self.S['body_font']*.4>y+h-pad/2:self.overflows.append({'node':id,'needed_bottom':cy,'available_bottom':y+h})
  self.objects.append('</g>');return box
 def table_node(self,id,x,y,w,title,rows,role='blue',header_labels=None,row_heights=None):
  head=self.S['node_header'];heights=row_heights or [self.S['row_height']]*len(rows);h=head+sum(heights)+8
  if len(heights)!=len(rows):raise ValueError('row heights must match table rows')
  box=self.node(id,x,y,w,h,title,[],role);color=self.color(role);box['field_y']={}
  centers=[];yy=y+head
  for i,row in enumerate(rows):
   rh=heights[i];centers.append(yy+rh/2)
   fill=self.tint(role) if self.spec.get('diagram_type')=='class' else ('#FFFFFF' if i%2 else self.tint(role))
   self._shape('rect',x=x+1,y=yy,width=w-2,height=rh,fill=fill,stroke='none')
   if row=='—':self.line([(x,yy+rh/2),(x+w,yy+rh/2)],role=role,width=1)
   else:self.text(x+self.S['padding'],yy+rh/2+self.S['body_font']*.5,row,self.S['body_font'],owner=id)
   box['field_y'][str(row)]=yy+rh/2
   yy+=rh
  fields=self.node_specs.get(id,{}).get('fields',[])
  for i,item in enumerate(fields):box['field_y'][item['name'] if isinstance(item,dict) else str(item)]=centers[i]
  # A soft header needs a real compartment divider; color alone cannot encode
  # the UML name/attribute boundary. Paint the frame last to keep it continuous.
  self.line([(x,y+head),(x+w,y+head)],role=role,width=max(1.2,self.S['stroke']*.7))
  self._shape('rect',x=x,y=y,width=w,height=h,rx=self.S['radius'],fill='none',stroke=color,stroke_width=self.S['stroke'])
  return w,h
 def line(self,points,role='slate',dash=None,width=None):
  # Individual line preserves diagonals; use polyline only for orthogonal routes.
  for a,b in zip(points,points[1:]):self._shape('line',x1=a[0],y1=a[1],x2=b[0],y2=b[1],stroke=self.color(role),stroke_width=width or self.S['stroke'],stroke_dasharray=dash,fill='none')
 def _cap(self,symbol,tip,neighbor,color):
  if symbol in (None,'none'):return
  dx,dy=neighbor[0]-tip[0],neighbor[1]-tip[1];length=hypot(dx,dy) or 1;u=(dx/length,dy/length);v=(-u[1],u[0])
  def q(d,s=0):return (tip[0]+d*u[0]+s*v[0],tip[1]+d*u[1]+s*v[1])
  def seg(a,b):self._shape('line','connectors',x1=a[0],y1=a[1],x2=b[0],y2=b[1],stroke=color,stroke_width=self.S['stroke'])
  if symbol=='open':seg(q(12,6),tip);seg(q(12,-6),tip)
  elif symbol in ('one','zero_many','many'):
   if symbol=='one':
    for d in (10,18):seg(q(d,-8),q(d,8))
   else:
    for side in (-8,0,8):seg(q(16),q(0,side))
    if symbol=='zero_many':self._shape('circle','connectors',cx=q(29)[0],cy=q(29)[1],r=5,fill='#FFFFFF',stroke=color,stroke_width=self.S['stroke'])
    else:seg(q(27,-8),q(27,8))
  elif symbol=='triangle':
   pts=[tip,q(20,10),q(20,-10)];self._shape('polygon','connectors',points=' '.join(f'{a},{b}' for a,b in pts),fill='#FFFFFF',stroke=color,stroke_width=self.S['stroke'])
  elif symbol in ('diamond','diamond_open'):
   pts=[tip,q(10,7),q(20),q(10,-7)];self._shape('polygon','connectors',points=' '.join(f'{a},{b}' for a,b in pts),fill='#FFFFFF' if symbol=='diamond_open' else color,stroke=color,stroke_width=self.S['stroke'])
 def edge(self,id,source,target,points,label='',kind='flow',role='slate',dash=None,marker='arrow',start_marker=None,label_pos=None):
  color=self.color(role);points=[list(p) for p in points]
  data={'id':id,'source':source,'target':target,'points':points,'label':label,'kind':kind,'dash':dash,'marker':marker,'start_marker':start_marker,'role':role,'label_hint':label_pos};self.edges.append(data)
  attrib={'data-edge-id':id,'data-source':source,'data-target':target,'points':' '.join(f'{a},{b}' for a,b in points),'fill':'none','stroke':color,'stroke-width':self.S['stroke'],'stroke-dasharray':dash,'stroke-linejoin':'round'}
  if marker=='arrow':attrib['marker-end']='url(#arrow-'+str(role).replace('#','')+')'
  self.connectors.append('<polyline '+attrs(attrib)+'/>')
  if marker!='arrow':self._cap(marker,points[-1],points[-2],color)
  self._cap(start_marker,points[0],points[1],color)
  # Labels are placed at save-time, once every node and panel is known.
  return data
 def badge(self,x,y,text,role='slate'):
  w=self.measure(text,self.S['label_font'])+22;self._shape('rect',x=x,y=y,width=w,height=32,rx=6,fill=self.tint(role));self.text(x+11,y+23,text,self.S['label_font'],fill=self.color(role),weight='bold')
 def legend(self,items,y=None):
  y=y or self.H-35;x=self.S['margin']
  for role,label in items:
   self._shape('rect',x=x,y=y-16,width=16,height=16,rx=3,fill=self.color(role));self.text(x+25,y,label,self.S['label_font'],fill=self.S['muted']);x+=self.measure(label,self.S['label_font'])+60
 def note(self,text,y=None):self.text(self.S['margin'],y or self.H-72,text,self.S['label_font'],fill=self.S['muted'])
 def _place_edge_labels(self):
  if getattr(self,'_labels_placed',False):return
  self._labels_placed=True
  def intersects(a,b,gap=3):return min(a['x']+a['w']+gap,b['x']+b['w'])>max(a['x']-gap,b['x']) and min(a['y']+a['h']+gap,b['y']+b['h'])>max(a['y']-gap,b['y'])
  obstacles=list(self.nodes.values())+[{'x':p['x'],'y':p['y'],'w':p['w'],'h':p['header_h']} for p in self.panels]
  # Labels may belong inside a container, but must not straddle its border.
  for p in self.panels:
   obstacles.extend([{'x':p['x']-4,'y':p['y']+p['h']-6,'w':p['w']+8,'h':12},
                     {'x':p['x']-6,'y':p['y'],'w':12,'h':p['h']},
                     {'x':p['x']+p['w']-6,'y':p['y'],'w':12,'h':p['h']}])
  # Titles, legends, notes and table text are visible obstacles too.
  obstacles+=list(self.texts)
  placed=[]
  for edge in self.edges:
   label=edge['label']
   if not label:continue
   size=self.S['label_font'];width=self.measure(label,size);height=size*1.35
   points=edge['points'];candidates=[]
   hint=edge.get('label_hint')
   if hint:candidates.append((hint[0],hint[1]))
   if self.node_specs.get(edge['source'],{}).get('kind')=='decision':
    for a,b in list(zip(points,points[1:]))[:2]:
     for ratio in (.65,.85,.35):
      x=a[0]+(b[0]-a[0])*ratio;y=a[1]+(b[1]-a[1])*ratio
      if a[1]==b[1]:
       candidates.extend([(x,y-10),(x,y+size+12)])
      else:
       candidates.extend([(x+width/2+10,y+size*.3),(x-width/2-10,y+size*.3)])
   segments=sorted(zip(points,points[1:]),key=lambda ab:-hypot(ab[1][0]-ab[0][0],ab[1][1]-ab[0][1]))
   for a,b in segments:
    if a[1]==b[1]:
     for ratio in (.5,.33,.67,.2,.8,.1,.9,.15,.25,.75,.85,.05,.95,.4,.6):
      x=a[0]+(b[0]-a[0])*ratio
      for offset in (-10,size+12,-size-20,2*size+24):candidates.append((x,a[1]+offset))
    else:
     for ratio in (.5,.33,.67,.2,.8,.1,.9,.15,.25,.75,.85,.05,.95,.4,.6):
      y=a[1]+(b[1]-a[1])*ratio+size*.3
      for offset in (width/2+10,-width/2-10,width/2+26,-width/2-26):candidates.append((a[0]+offset,y))
   def crossed_by_other(box):
    for other in self.edges:
     if other['id']==edge['id']:continue
     for a,b in zip(other['points'],other['points'][1:]):
      if a[0]==b[0] and box['x']<a[0]<box['x']+box['w'] and max(min(a[1],b[1]),box['y'])<min(max(a[1],b[1]),box['y']+box['h']):return True
      if a[1]==b[1] and box['y']<a[1]<box['y']+box['h'] and max(min(a[0],b[0]),box['x'])<min(max(a[0],b[0]),box['x']+box['w']):return True
    return False
   def path_distance(x,y,path):
    distances=[]
    for a,b in zip(path,path[1:]):
     dx,dy=b[0]-a[0],b[1]-a[1];den=dx*dx+dy*dy
     ratio=max(0,min(1,((x-a[0])*dx+(y-a[1])*dy)/den)) if den else 0
     distances.append(hypot(x-a[0]-ratio*dx,y-a[1]-ratio*dy))
    return min(distances,default=float('inf'))
   def nearer_to_other(x,y):
    cy=y-size*.35;own=path_distance(x,cy,points)
    return any(path_distance(x,cy,other['points'])<own+2 for other in self.edges if other['id']!=edge['id'])
   chosen=None
   for x,y in candidates:
    box={'x':x-width/2-5,'y':y-size-3,'w':width+10,'h':height+6}
    if box['x']<8 or box['y']<8 or box['x']+box['w']>self.W-8 or box['y']+box['h']>self.H-8:continue
    if any(intersects(box,o) for o in obstacles+placed) or crossed_by_other(box) or nearer_to_other(x,y):continue
    chosen=(x,y,box);break
   if chosen is None:
    x,y=candidates[0];box={'x':x-width/2-5,'y':y-size-3,'w':width+10,'h':height+6};chosen=(x,y,box)
    self.overflows.append({'edge':edge['id'],'issue':'no-clear-label-placement'})
   x,y,box=chosen;placed.append(box);edge['label_position']=[x,y]
   if self.S['label_background']:self._shape('rect','labels',x=box['x'],y=box['y'],width=box['w'],height=box['h'],rx=3,fill='#FFFFFF',fill_opacity=.95)
   self.text(x,y,label,size,fill=self.S['ink'],anchor='middle',owner='edge:'+edge['id'],layer='labels')
 def save(self,output_dir):
  self._finish_title()
  self._place_edge_labels()
  p=Path(output_dir);p.mkdir(parents=True,exist_ok=True)
  defs=[]
  roles=set(self.palette)|{e.get('role','slate') for e in self.edges}
  for role in sorted(roles):
   color=self.color(role);defs.append(f'<marker id="arrow-{role}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 Z" fill="{color}"/></marker>')
  svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.W} {self.H}" width="{self.W}" height="{self.H}"><defs>'+''.join(defs)+'</defs>'
  svg+=f'<rect x="0" y="0" width="{self.W}" height="{self.H}" fill="{self.S["canvas_fill"]}"/>'
  svg+='\n'.join(self.background+self.connectors+self.objects+self.labels)+'</svg>'
  (p/'diagram.svg').write_text(svg, encoding='utf-8')
  layout={'width':self.W,'height':self.H,'nodes':list(self.nodes.values()),'edges':self.edges,'texts':self.texts,'panels':self.panels,'overflows':self.overflows}
  (p/'layout.json').write_text(json.dumps(layout,ensure_ascii=False,indent=2), encoding='utf-8')
  return p/'diagram.svg'
