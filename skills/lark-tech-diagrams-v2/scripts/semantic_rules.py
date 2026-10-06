"""Type-specific invariants; visual grammar is still independently reviewed."""
def inspect(spec,layout):
 errors=[];kind=spec['diagram_type'];nodes=spec.get('nodes',[])+spec.get('pseudonodes',[]);byid={n['id']:n for n in nodes};edges=spec.get('messages',spec.get('edges',[]));drawn={e['id']:e for e in layout['edges']};boxes={n['id']:n for n in layout['nodes']}
 def fail(code,**detail):errors.append({'code':code,**detail})
 if kind=='er':
  for e in edges:
   card=e.get('cardinality',{})
   if not isinstance(card,dict) or any(card.get(side) not in ('1','0..1','1..*','0..*') for side in ('source','target')):fail('er-cardinality-missing-or-unsupported',edge=e['id'])
   fields={side:{f['name']:f for f in byid[e[side]].get('fields',[]) if isinstance(f,dict)} for side in ('source','target')}
   sf=e.get('source_field');tf=e.get('target_field')
   if sf not in fields['source'] or tf not in fields['target']:fail('er-missing-field-reference',edge=e['id']);continue
   if 'PK' not in str(fields['source'][sf].get('key','')) or 'FK' not in str(fields['target'][tf].get('key','')):fail('er-key-role',edge=e['id'])
   if drawn.get(e['id'],{}).get('marker')!='none':fail('er-flow-arrow',edge=e['id'])
 if kind=='class':
  for e in edges:
   d=drawn.get(e['id'],{});rel=e.get('kind')
   if rel in ('inheritance','realization') and d.get('marker')!='triangle':fail('class-triangle-direction',edge=e['id'])
   if rel=='realization' and not d.get('dash'):fail('class-realization-not-dashed',edge=e['id'])
   if rel=='composition' and d.get('start_marker')!='diamond':fail('class-composition-whole-end',edge=e['id'])
   if rel=='aggregation' and d.get('start_marker')!='diamond_open':fail('class-aggregation-whole-end',edge=e['id'])
 if kind=='sequence':
  last_y=-1
  for e in edges:
   d=drawn.get(e['id'],{});points=d.get('points',[])
   if not points:continue
   if points[0][1]<=last_y:fail('sequence-order',edge=e['id'])
   last_y=points[0][1];k=e.get('kind','sync')
   if k=='return' and (not d.get('dash') or d.get('marker')!='open'):fail('sequence-return-symbol',edge=e['id'])
   if k=='async' and (d.get('dash') or d.get('marker')!='open'):fail('sequence-async-symbol',edge=e['id'])
   if k=='sync' and (d.get('dash') or d.get('marker')!='arrow'):fail('sequence-sync-symbol',edge=e['id'])
 if kind=='swimlane':
  lanes={l['id'] for l in spec.get('lanes',[])};panels={p['id']:p for p in layout['panels']}
  for n in nodes:
   lane=n.get('lane');b=boxes.get(n['id']);p=panels.get('lane-'+str(lane))
   if lane not in lanes:fail('swimlane-unknown-owner',node=n['id'])
   if b and p and not(p['x']<=b['x'] and p['y']<=b['y'] and b['x']+b['w']<=p['x']+p['w'] and b['y']+b['h']<=p['y']+p['h']):fail('swimlane-node-outside-owner',node=n['id'])
 if kind in ('flowchart','swimlane'):
  for n in nodes:
   if n.get('kind')!='decision':continue
   out=[e for e in edges if e['source']==n['id']]
   if len(out)<2 or any(not e.get('label') for e in out):fail('decision-branches-missing',node=n['id'])
   if boxes.get(n['id'],{}).get('shape')!='diamond':fail('decision-symbol',node=n['id'])
 if kind=='state':
  starts=[n for n in nodes if n.get('kind')=='initial'];ends=[n for n in nodes if n.get('kind')=='final']
  if len(starts)!=1 or not ends:fail('state-initial-final')
  for e in edges:
   if byid.get(e['source'],{}).get('kind')=='initial' and e.get('label','').strip() and not e['label'].lstrip().startswith('/'):
    fail('state-initial-transition-must-be-effect-only',edge=e['id'])
  for n in starts:
   if any(e['target']==n['id'] for e in edges) or boxes.get(n['id'],{}).get('shape')!='start':fail('state-initial-direction',node=n['id'])
  for n in ends:
   if any(e['source']==n['id'] for e in edges) or boxes.get(n['id'],{}).get('shape')!='end':fail('state-final-direction',node=n['id'])
 if kind=='dataflow':
  for e in edges:
   if not e.get('label') or 'process' not in [byid[e['source']].get('kind'),byid[e['target']].get('kind')]:fail('dfd-invalid-data-flow',edge=e['id'])
  for n in nodes:
   if n.get('kind')=='store' and boxes.get(n['id'],{}).get('shape') not in ('database','data_store'):fail('dfd-store-symbol',node=n['id'])
 from types_system import inspect_system
 from types_data import inspect_data_extra
 from types_behavior import inspect_behavior_extra
 errors.extend(inspect_system(spec,layout));errors.extend(inspect_data_extra(spec,layout));errors.extend(inspect_behavior_extra(spec,layout))
 return errors
