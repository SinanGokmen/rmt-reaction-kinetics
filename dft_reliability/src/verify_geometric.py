"""Numerical and scientific-integrity checks for the radial graph audit."""
import copy,json
import numpy as np
import pandas as pd
from geometric_audit import graph,pack,init,forward,loss_grad,predict
from data_utils import ROOT,load_dataset
from denoise_benchmark import fold_for
from reliability_benchmark import top
rng=np.random.default_rng(51);rr=load_dataset('aimnet2');r=rr[0];g=graph(r)
X,ids,sizes=pack([graph(x) for x in rr[:3]]);theta=init(X.shape[1],7);y=rng.normal(size=3)
loss,grads=loss_grad(theta,X,ids,sizes,y);errs=[]
for j,a in enumerate(theta):
 for flat in rng.choice(a.size,min(a.size,6),replace=False):
  k=np.unravel_index(flat,a.shape);before=a[k];eps=1e-6
  a[k]=before+eps;hi=loss_grad(theta,X,ids,sizes,y)[0]
  a[k]=before-eps;lo=loss_grad(theta,X,ids,sizes,y)[0];a[k]=before
  errs.append(abs((hi-lo)/(2*eps)-grads[j][k]))
assert max(errs)<1e-7
Q,_=np.linalg.qr(rng.normal(size=(3,3)));perm=rng.permutation(len(r['R']))
r2=copy.deepcopy(r);r2['R']=(r['R']@Q+np.array([7.,-3.,2.]))[perm];r2['F']=(r['F']@Q)[perm];r2['symbols']=[r['symbols'][i] for i in perm]
model=(theta,np.zeros(X.shape[1]),np.ones(X.shape[1]),0.,1.)
invariance=float(abs(predict(model,[g])[0]-predict(model,[graph(r2)])[0]));assert invariance<1e-10
r2=copy.deepcopy(r);r2['Fref']=rng.normal(size=r['Fref'].shape)*1e9
assert np.array_equal(graph(r2),g)
result=dict(gradient_max_error=float(max(errs)),rigid_permutation_prediction_error=invariance,reference_feature_leakage=0.)
out=ROOT/'results/geometric_audit';seed=20260916
prediction_path=out/f'predictions_seed{seed}.csv.gz'
if not prediction_path.exists(): prediction_path=out/f'predictions_seed{seed}.csv'
p=pd.read_csv(prediction_path);m=pd.read_csv(out/f'metrics_seed{seed}.csv');reconstruction=[]
assert len(p)==8000 and not p.duplicated(['source','scenario','index']).any()
for name in ['aimnet2','transition1x']:
 records=load_dataset(name);idx=np.arange(len(records));folds=np.array([fold_for(r['formula']) for r in records])
 q=np.array([np.sqrt(np.mean((r['F']-r['Fref'])**2)) for r in records]);bad=set(top(q,idx,100));impact=np.array([np.sum((r['F']-r['Fref'])**2) for r in records])
 for f in range(5):
  v=p[(p.source==name)&(p.scenario==f)];seedidx=idx[folds==f];pool=idx[folds!=f]
  assert set(v['index'])==set(pool)
  chosen=set(seedidx)|set(v.sort_values(['prediction','index'],ascending=[False,True]).head(int(np.ceil(.1*len(pool))))['index'])
  row=m[(m.source==name)&(m.scenario==f)].iloc[0]
  reconstruction.extend([abs(len(chosen&bad)/100-row.recall),abs(impact[list(chosen)].sum()/impact.sum()-row.impact)])
assert max(reconstruction)<1e-12
result.update(metric_reconstruction_max_error=float(max(reconstruction)),prediction_rows=len(p),unique_geometries=2000)
(out/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
