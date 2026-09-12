"""Build the manuscript from its local TeX, bibliography and generated figures."""
from pathlib import Path
import subprocess

root=Path(__file__).resolve().parents[1]
commands=[['pdflatex','-interaction=nonstopmode','-halt-on-error','main.tex'],
          ['bibtex','main'],
          ['pdflatex','-interaction=nonstopmode','-halt-on-error','main.tex'],
          ['pdflatex','-interaction=nonstopmode','-halt-on-error','main.tex']]
for command in commands:
    result=subprocess.run(command,cwd=root/'manuscript',capture_output=True,text=True)
    if result.returncode:
        print(result.stdout[-4000:]);raise SystemExit(result.returncode)
log=(root/'manuscript'/'main.log').read_text()
for line in log.splitlines():
    if 'Overfull' in line or 'undefined' in line or 'Warning' in line:
        print(line)
print(root/'manuscript'/'main.pdf')
