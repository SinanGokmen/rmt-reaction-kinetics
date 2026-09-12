"""Reproduce force discrepancies and decompose errors by rigid-motion symmetry."""
import csv
import json
import numpy as np
from data_utils import ROOT, load_dataset, rigid_basis, project

def run():
    rows, summary = [], []
    for name in ['ani_1x_tz','transition1x','aimnet2','spice']:
        records = load_dataset(name, allow_unvalidated=True)
        accum = dict(raw=0.,translation=0.,rigid=0.,tangent_error=0.,normal_error=0.,ref_normal=0.)
        components = 0
        for r in records:
            U = rigid_basis(r['R'])
            f, ref = r['F'], r['Fref']
            error = f-ref
            tangent = project(error,U)
            row = dict(dataset=name,index=r['index'],formula=r['formula'],n_atoms=len(f),
                       raw=np.sum(error**2),translation=np.sum((f-f.mean(0)-ref)**2),
                       rigid=np.sum((project(f,U)-ref)**2),tangent_error=np.sum(tangent**2),
                       normal_error=np.sum((error-tangent)**2),ref_normal=np.sum((ref-project(ref,U))**2))
            rows.append(row)
            components += f.size
            for key in accum:
                accum[key] += row[key]
        item = dict(dataset=name,comparison_validated=name in ('aimnet2','transition1x'),n_configs=len(records),n_formulas=len({r['formula'] for r in records}),n_components=components,
                    **{k+'_rmse_mev_A':1000*np.sqrt(v/components) for k,v in accum.items()},
                    tangent_fraction=accum['tangent_error']/accum['raw'])
        summary.append(item)
        print(json.dumps(item),flush=True)
    with open(ROOT/'results'/'audit_per_configuration.csv','w') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
    (ROOT/'results'/'audit_summary.json').write_text(json.dumps(summary,indent=2)+'\n')

if __name__ == '__main__':
    run()
