"""Paired formula-cluster bootstrap of fixed out-of-fold predictions."""
import json
import numpy as np
import pandas as pd
from data_utils import ROOT

def run():
    df=pd.read_csv(ROOT/'results'/'denoising_oof.csv')
    summaries=[]; comparisons=[]
    rng=np.random.default_rng(11092026)
    for name,sub in df.groupby('dataset'):
        for method,x in sub.groupby('method'):
            summaries.append(dict(dataset=name,method=method,
                rmse_mev_A=1000*np.sqrt(x.sse.sum()/x.n_components.sum()),
                tangent_rmse_mev_A=1000*np.sqrt(x.tangent_sse.sum()/x.n_components.sum()),
                median_frame_rmse_mev_A=1000*np.median(np.sqrt(x.sse/x.n_components)),
                p95_frame_rmse_mev_A=1000*np.quantile(np.sqrt(x.sse/x.n_components),.95)))
        groups=sub.groupby(['formula','method'])[['sse','n_components']].sum()
        errors=groups.sse.unstack();counts=groups.n_components.unstack().iloc[:,0]
        draws=rng.integers(0,len(errors),size=(2000,len(errors)))
        den=counts.to_numpy()[draws].sum(1)
        boot={m:1000*np.sqrt(errors[m].to_numpy()[draws].sum(1)/den) for m in errors.columns}
        for method,base in [('mp_bulk','rigid'),('mp_bulk','ridge'),('mp_bulk','element_weighted'),
                            ('element_weighted','rigid'),('ridge','rigid')]:
            diff=boot[method]-boot[base]
            estimate=1000*(np.sqrt(errors[method].sum()/counts.sum())-np.sqrt(errors[base].sum()/counts.sum()))
            comparisons.append(dict(dataset=name,method=method,baseline=base,
                                    delta_rmse_mev_A=estimate,ci95_low=float(np.quantile(diff,.025)),
                                    ci95_high=float(np.quantile(diff,.975))))
    (ROOT/'results'/'denoising_summary.json').write_text(json.dumps(summaries,indent=2)+'\n')
    (ROOT/'results'/'paired_comparisons.json').write_text(json.dumps(comparisons,indent=2)+'\n')
    print(pd.DataFrame(comparisons).to_string(index=False))

if __name__=='__main__':run()
