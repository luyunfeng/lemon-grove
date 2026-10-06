#!/usr/bin/env python3
"""Portable diagram authoring only; no account, network or cloud operations."""
import argparse,hashlib,json,sys
from pathlib import Path
from render import RENDERERS
from validate import check
SKILL=Path(__file__).resolve().parent.parent
def save(path,value):Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n', encoding='utf-8')
def catalog():return json.loads((SKILL/'assets/template-catalog.json').read_text(encoding='utf-8'))
def template(kind):return next(x for x in catalog()['templates'] if x['type']=={'architecture':'layered_architecture'}.get(kind,kind))
def outside(path):
 p=Path(path).expanduser().resolve()
 if p==SKILL or SKILL in p.parents:raise ValueError('Output must be outside the skill package')
 return p
def prepare(kind,out):
 t=template(kind);p=outside(out);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x', encoding='utf-8') as f:f.write((SKILL/t['spec']).read_text(encoding='utf-8'))
 return {'spec':str(p),'reference_svg':str(SKILL/t['reference_svg']),'reference_png':str(SKILL/t['reference_png']),'next':'Replace example facts and legend with the user logic; preserve the style and diagram grammar.'}
def render(spec_path,out,svg_only=False):
 spec_path=Path(spec_path).resolve();spec=json.loads(spec_path.read_text(encoding='utf-8'));template(spec['diagram_type']);out=outside(out)
 if out.exists() and any(out.iterdir()):raise ValueError('Output must be new/empty; preserve older attempts')
 out.mkdir(parents=True,exist_ok=True);style=json.loads((SKILL/'assets/style.json').read_text(encoding='utf-8'));save(out/'input.json',spec)
 canvas=RENDERERS[spec['diagram_type']](spec,style);canvas.save(out);validation=check(spec,out)
 if validation['counts']['errors']:raise ValueError('Drawing checks failed; inspect '+str(out/'validation.json'))
 svg=out/'diagram.svg';digest=hashlib.sha256(svg.read_bytes()).hexdigest();preview=None
 if not svg_only:
  from preview import rasterize
  preview=str(rasterize(svg,out/'preview.png'))
 result={'type':spec['diagram_type'],'svg':str(svg),'svg_sha256':digest,'preview':preview,'validation':str(out/'validation.json'),'geometry':validation['counts'],'passed':True,'visual_review':'pending','platform_status':'not_requested','handoff':{'format':'svg','source':str(svg),'source_sha256':digest,'instruction':'Use existing SVG with the destination tool. Preserve it; do not regenerate as Mermaid/DSL. Platform conversion, publishing and readback belong to that tool.'}}
 save(out/'result.json',result);return result
def main():
 p=argparse.ArgumentParser();sub=p.add_subparsers(dest='command',required=True);sub.add_parser('list')
 a=sub.add_parser('prepare');a.add_argument('--type',required=True,choices=sorted(RENDERERS));a.add_argument('--out',required=True)
 a=sub.add_parser('render');a.add_argument('--spec',required=True);a.add_argument('--out',required=True);a.add_argument('--svg-only',action='store_true')
 a=p.parse_args()
 try:
  result=catalog() if a.command=='list' else prepare(a.type,a.out) if a.command=='prepare' else render(a.spec,a.out,a.svg_only)
  print(json.dumps({'ok':True,**result},ensure_ascii=False));return 0
 except Exception as e:print(json.dumps({'ok':False,'error':str(e)},ensure_ascii=False),file=sys.stderr);return 1
if __name__=='__main__':sys.exit(main())
