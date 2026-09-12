"""Reconstruct held-out discovery metrics and enforce nested paid seed selection."""
import json
import numpy as np
import pandas as pd
from data_utils import ROOT,load_dataset
from denoise_benchmark import fold_for
from reliability_benchmark import descriptors

def run():
 metrics=pd.read_csv(ROOT/'results/small_seed_metrics.csv',dtype={'seed_label':str})
 scores=pd.read_csv(ROOT/'results/small_seed_scores.csv',dtype={'seed_label':str})
 splits=json.loads((ROOT/'results/small_seed_splits.json').read_text())
 max_error=0.;nested={};scoregroups=scores.groupby(['dataset','fold','repeat','seed_label','method'])
 records={d:load_dataset(d) for d in ['aimnet2','transition1x']}
 basic={d:{k:np.array([descriptors(x)[1][k] for x in rr]) for k in ['net_force','rigid_force','force_magnitude']} for d,rr in records.items()}
 mlookup=metrics.set_index(['dataset','fold','repeat','seed_label','method'])
 for s in splits:
  d=s['dataset'];pool=np.array(s['pool_indices']);seed=np.array(s['seed_indices']);r=records[d]
  assert len(seed)==s['seed_count'] and len(set(seed))==len(seed)
  assert set(r[i]['formula'] for i in seed).isdisjoint(r[i]['formula'] for i in pool)
  assert all(fold_for(r[i]['formula'])==s['fold'] for i in seed)
  assert set(pool)=={i for i,x in enumerate(r) if fold_for(x['formula'])!=s['fold']}
  key=(d,s['fold'],s['repeat']);nested.setdefault(key,[]).append(seed)
  q=np.array([np.sqrt(np.mean((x['F']-x['Fref'])**2)) for x in r]);w=np.array([np.sum((x['F']-x['Fref'])**2) for x in r])
  order=sorted(pool,key=lambda i:(-q[i],i));bad=set(order[:int(np.ceil(.1*len(pool)))])
  for method in ['trees_log','trees_raw','trees_physics','ridge','mp_ridge']:
   mk=key+(s['seed_label'],method);frame=scoregroups.get_group(mk)
   assert set(frame['index'])==set(pool) and len(frame)==len(pool)
   chosen=frame.sort_values(['score','index'],ascending=[False,True]).head(280-len(seed))['index'].to_numpy()
   assert set(chosen)==set(frame.loc[frame.selected,'index'])
   assert len(chosen)+len(seed)==280
   row=mlookup.loc[mk]
   recall=len(set(chosen)&bad)/len(bad);impact=w[chosen].sum()/w[pool].sum()
   max_error=max(max_error,abs(recall-row.recall),abs(impact-row.impact))
  for method in ['net_force','rigid_force','force_magnitude']:
   x=[(basic[d][method][i],i) for i in pool]
   chosen=np.array([i for _,i in sorted(x,key=lambda v:(-v[0],v[1]))[:280]])
   row=mlookup.loc[key+(s['seed_label'],method)]
   max_error=max(max_error,abs(len(set(chosen)&bad)/len(bad)-row.recall),abs(w[chosen].sum()/w[pool].sum()-row.impact))
 for arrays in nested.values():
  arrays.sort(key=len)
  for a,b in zip(arrays,arrays[1:]):assert np.array_equal(a,b[:len(a)])
 assert max_error<1e-12
 result=dict(metric_reconstruction_max_error=max_error,split_count=len(splits),score_rows=len(scores),metric_rows=len(metrics),nested_seed_sequences=len(nested),formula_disjoint=True,total_budget=280)
 (ROOT/'results/small_seed_verification.json').write_text(json.dumps(result,indent=2)+'\n');print(result)

if __name__=='__main__':run()
