#!/usr/bin/env python3
"""Offline demo-fidelity check; no platform tooling or network needed."""
import argparse,hashlib,json,sys
from pathlib import Path
from render import RENDERERS
from validate import check
SKILL=Path(__file__).resolve().parent.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args();out=Path(a.out).resolve()
 if out==SKILL or SKILL in out.parents or (out.exists() and any(out.iterdir())):raise ValueError('Use a new output directory outside the skill')
 out.mkdir(parents=True,exist_ok=True);fonts=json.loads((SKILL/'assets/fonts/manifest.json').read_text(encoding='utf-8'))['fonts']
 for name,digest in fonts.items():
  if sha(SKILL/'assets/fonts'/name)!=digest:raise ValueError('Packaged font differs: '+name)
 catalog=json.loads((SKILL/'assets/template-catalog.json').read_text(encoding='utf-8'));style=json.loads((SKILL/'assets/style.json').read_text(encoding='utf-8'));rows=[]
 for t in catalog['templates']:
  folder=out/t['type'];spec=json.loads((SKILL/t['spec']).read_text(encoding='utf-8'));RENDERERS[spec['diagram_type']](spec,style).save(folder);validation=check(spec,folder)
  rows.append({'type':t['type'],'errors':validation['counts']['errors'],'svg_matches_demo':sha(folder/'diagram.svg')==sha(SKILL/t['reference_svg'])==t['svg_sha256']})
 result={'passed':len(rows)==16 and len({x['type'] for x in rows})==16 and all(x['errors']==0 and x['svg_matches_demo'] for x in rows),'checks':rows,'note':'Same input SVG fidelity only; novel-task semantics and destination rendering need separate review.'};(out/'report.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n', encoding='utf-8');print(json.dumps(result,ensure_ascii=False));return 0 if result['passed'] else 1
if __name__=='__main__':sys.exit(main())
