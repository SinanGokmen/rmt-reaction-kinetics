"""Check held-out isolation, budget arithmetic and score invariance."""
import json,copy
import numpy as np
import pandas as pd
from data_utils import ROOT,load_dataset
from reliability_benchmark import descriptors,top

def run():
    rng=np.random.default_rng(20260912);max_rotation=0.;max_reference=0.
    for name in ['aimnet2','transition1x']:
        for r in load_dataset(name)[::50]:
            x=np.array(list(descriptors(r)[0].values()))
            rt=copy.deepcopy(r);rt['Fref']=rng.normal(size=r['Fref'].shape)*1e8
            rt['info']['orca_energy']='999999999'
            xt=np.array(list(descriptors(rt)[0].values()));max_reference=max(max_reference,float(np.max(np.abs(x-xt))))
            Q,_=np.linalg.qr(rng.normal(size=(3,3)))
            rt=copy.deepcopy(r);rt['R']=r['R']@Q+np.array([1.,2.,3.]);rt['F']=r['F']@Q
            xt=np.array(list(descriptors(rt)[0].values()));max_rotation=max(max_rotation,float(np.max(np.abs(x-xt))))
    assert max_reference==0.;assert max_rotation<1e-9
    p=pd.read_csv(ROOT/'results'/'reliability_predictions.csv')
    c=pd.read_csv(ROOT/'results'/'reliability_configurations.csv')
    m=pd.read_csv(ROOT/'results'/'reliability_metrics.csv')
    assert c.groupby(['dataset','formula']).fold.nunique().eq(1).all()
    joined=p.merge(c[['dataset','index','fold']],on=['dataset','index'])
    assert (joined.scenario!=joined.fold).all()
    assert (m.total_count==m.seed_count+m.selected_count).all()
    assert np.allclose(m.total_fraction,m.total_count/1000)
    assert m.recall.dropna().between(0,1).all()
    assert m.impact_fraction.between(0,1+1e-12).all()
    # Reconstruct the primary total-budget endpoint from saved scores and labels.
    max_recall=0.
    for d in ['aimnet2','transition1x']:
        a=c[c.dataset==d].sort_values('index');bad=a.worst_decile.to_numpy(dtype=bool)
        for s in range(5):
            seed=a.loc[a.fold==s,'index'].to_numpy();pool=a.loc[a.fold!=s,'index'].to_numpy()
            for method in ['trees_log','ridge','mp_ridge']:
                v=p[(p.dataset==d)&(p.scenario==s)&(p.method==method)].sort_values('index')
                k=int(np.ceil(.1*len(pool)));selected=np.r_[seed,top(v.score.to_numpy(),pool,k)]
                assert len(np.unique(selected))==len(seed)+k
                rec=bad[selected].sum()/bad.sum()
                target=m[(m.dataset==d)&(m.scenario==s)&(m.method==method)&(m.endpoint=='worst_decile')&(m.acquisition_fraction==.1)].recall.iloc[0]
                max_recall=max(max_recall,abs(rec-target))
    assert max_recall<1e-12
    result=dict(reference_feature_leakage=max_reference,rigid_transform_feature_error=max_rotation,
                reconstructed_recall_error=max_recall,prediction_rows=len(p),metric_rows=len(m),
                unique_configurations=len(c))
    (ROOT/'results'/'reliability_verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':run()
