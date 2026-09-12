"""Package current manuscript and reproducible research without upstream XYZ files."""
from pathlib import Path
import hashlib,json,shutil,zipfile
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT.parent/'deliverables';OUT.mkdir(exist_ok=True)
selected=[]
for path in ROOT.rglob('*'):
    if not path.is_file():continue
    rel=path.relative_to(ROOT)
    if rel.parts[0] in {'tmp','data'} and rel.as_posix()!='data/manifest.json':continue
    if '__pycache__' in rel.parts or path.suffix in {'.aux','.log','.out','.blg','.pyc'}:continue
    if rel.name=='CHECKSUMS.json':continue
    selected.append(path)
selected.sort()
checks={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in selected}
(ROOT/'CHECKSUMS.json').write_text(json.dumps(checks,indent=2)+'\n')
selected.append(ROOT/'CHECKSUMS.json')
report=OUT/'DFT_Reliability_Auditing.pdf'
shutil.copyfile(ROOT/'manuscript/main.pdf',report)
research=OUT/'DFT_Reliability_Research_Package.zip'
with zipfile.ZipFile(research,'w',zipfile.ZIP_DEFLATED) as z:
    for p in selected:z.write(p,Path('dft_reliability_study')/p.relative_to(ROOT))
source=OUT/'DFT_Reliability_LaTeX_Source.zip'
sourcefiles=['main.tex','main.bbl','references.bib','reliability_table.tex',
             'figures/reliability_scores.pdf','figures/reliability_budget.pdf',
             'figures/reliability_objectives.pdf','figures/small_seed_budget.pdf',
             'small_seed_results.tex']
with zipfile.ZipFile(source,'w',zipfile.ZIP_DEFLATED) as z:
    for p in sourcefiles:z.write(ROOT/'manuscript'/p,p)
for p in [research,source]:
    with zipfile.ZipFile(p) as z:assert z.testzip() is None
print(json.dumps({'research_files':len(selected),
                  'files':[{ 'path':str(p),'bytes':p.stat().st_size,
                             'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
                            for p in [report,research,source]]},indent=2))
