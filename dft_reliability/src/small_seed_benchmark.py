"""Fixed-budget, fixed held-out-pool sensitivity to number of seed references."""
import json
import numpy as np
import pandas as pd
from data_utils import ROOT,load_dataset
from denoise_benchmark import fold_for
from reliability_benchmark import descriptors,fit_predictions,top,evaluate_set


def run():
    metrics=[];scores=[];splits=[];params=[]
    for dataset in ['aimnet2','transition1x']:
        records=load_dataset(dataset);idx=np.arange(len(records))
        packs=[descriptors(r) for r in records]
        X=np.array([list(p[0].values()) for p in packs])
        groups=np.array([r['formula'] for r in records]);folds=np.array([fold_for(g) for g in groups])
        y=np.array([np.sqrt(np.mean((r['F']-r['Fref'])**2)) for r in records])
        impact=np.array([np.sum((r['F']-r['Fref'])**2) for r in records])
        basic={k:np.array([p[1][k] for p in packs]) for k in ['net_force','rigid_force','force_magnitude']}
        for fold in range(5):
            candidate=idx[folds==fold];pool=idx[folds!=fold]
            bad=np.zeros(len(idx),bool);bad[top(y[pool],pool,int(np.ceil(.1*len(pool))))]=True
            denominator=impact[pool].sum()
            for repeat in range(5):
                perm=np.random.default_rng(2026091100+10*fold+repeat).permutation(candidate)
                for size in [10,20,50,100,len(candidate)]:
                    label='full' if size==len(candidate) else str(size)
                    seed=perm[:size];budget=280;k=budget-size
                    assert len(np.unique(groups[seed]))>=3
                    assert set(groups[seed]).isdisjoint(groups[pool])
                    pred,selected,_=fit_predictions(X[seed],y[seed],groups[seed],X[pool],2026091100+10*fold+repeat)
                    context=dict(dataset=dataset,fold=fold,repeat=repeat,seed_label=label,seed_count=size,pool_count=len(pool),total_count=budget)
                    splits.append(dict(**context,seed_indices=seed.tolist(),pool_indices=pool.tolist()))
                    params.extend(dict(**context,**p) for p in selected)
                    for method,score in pred.items():
                        chosen=top(score,pool,k)
                        metrics.append(dict(**context,method=method,selected_count=k,
                          recall=bad[chosen].sum()/bad.sum(),impact=impact[chosen].sum()/denominator))
                        chosen_set=set(chosen)
                        scores.extend(dict(dataset=dataset,fold=fold,repeat=repeat,seed_label=label,
                          method=method,index=int(i),score=float(s),selected=bool(i in chosen_set)) for i,s in zip(pool,score))
                    for method,score in basic.items():
                        chosen=top(score[pool],pool,budget)
                        metrics.append(dict(**context,method=method,selected_count=budget,
                          recall=bad[chosen].sum()/bad.sum(),impact=impact[chosen].sum()/denominator))
                    metrics.append(dict(**context,method='random',selected_count=budget,recall=budget/len(pool),impact=budget/len(pool)))
            print(dataset,fold,'completed',flush=True)
    for name,rows in [('metrics',metrics),('scores',scores)]:
        pd.DataFrame(rows).to_csv(ROOT/'results'/f'small_seed_{name}.csv',index=False)
    (ROOT/'results/small_seed_splits.json').write_text(json.dumps(splits)+'\n')
    (ROOT/'results/small_seed_parameters.json').write_text(json.dumps(params,indent=2)+'\n')

if __name__=='__main__':run()
