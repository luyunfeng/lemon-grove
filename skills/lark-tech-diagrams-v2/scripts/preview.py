"""Generic local SVG rasterization via CairoSVG, using the packaged font."""
import os,subprocess,sys,tempfile
from pathlib import Path
from html import escape
SKILL=Path(__file__).resolve().parent.parent
def rasterize(svg,out):
 svg=Path(svg).resolve();out=Path(out).resolve()
 # Fontconfig is private to this child process; never install system fonts.
 with tempfile.TemporaryDirectory(prefix='diagram-fonts-',dir=out.parent) as tmp:
  tmp=Path(tmp);config=tmp/'fonts.conf'
  config.write_text('<?xml version="1.0"?><!DOCTYPE fontconfig SYSTEM "fonts.dtd"><fontconfig><dir>'+escape(str(SKILL/'assets/fonts'))+'</dir><cachedir>'+escape(str(tmp/'cache'))+'</cachedir><alias><family>Noto Sans SC</family><prefer><family>Noto Sans CJK SC</family></prefer></alias></fontconfig>', encoding='utf-8')
  env=dict(os.environ,FONTCONFIG_FILE=str(config),FONTCONFIG_PATH=str(tmp),PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1')
  p=subprocess.run([sys.executable,'-c','import cairosvg,sys; cairosvg.svg2png(url=sys.argv[1],write_to=sys.argv[2])',str(svg),str(out)],capture_output=True,text=True,encoding="utf-8",env=env)
  if p.returncode:raise RuntimeError('Local preview failed. SVG preserved; install declared CairoSVG/Cairo dependencies or preview the SVG with a compatible tool. '+p.stderr[-500:])
 return out
