#!/usr/bin/env python3
import argparse,json,sys
from pathlib import Path
from types_behavior import render_sequence,render_swimlane,render_flowchart,render_state,render_dataflow,render_activity
from types_structure import render_architecture,render_er,render_class,render_deployment,render_dependency
from validate import check
RENDERERS={k:globals()['render_'+k] for k in ['architecture','sequence','swimlane','er','flowchart','state','class','deployment','dataflow','dependency']}
from types_system import RENDERERS as SYSTEM_RENDERERS
from types_data import RENDERERS as DATA_RENDERERS
RENDERERS.update(SYSTEM_RENDERERS);RENDERERS.update(DATA_RENDERERS);RENDERERS['activity']=render_activity
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--spec',required=True);ap.add_argument('--style',required=True);ap.add_argument('--out',required=True);ap.add_argument('--allow-draft',action='store_true',help='Research only: retain failed artifacts for diagnosis');a=ap.parse_args();spec=json.loads(Path(a.spec).read_text(encoding='utf-8'));style=json.loads(Path(a.style).read_text(encoding='utf-8'));c=RENDERERS[spec['diagram_type']](spec,style);c.save(a.out);r=check(spec,a.out);print(json.dumps({'type':spec['diagram_type'],**r['counts']},ensure_ascii=False));return 2 if r['counts']['errors'] and not a.allow_draft else 0
if __name__=='__main__':sys.exit(main())
