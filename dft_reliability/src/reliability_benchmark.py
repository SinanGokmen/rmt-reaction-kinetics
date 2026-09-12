"""Budget-accounted reliability audit using only original-result descriptors."""
from pathlib import Path
import csv,json,time
import numpy as np
from scipy.stats import spearmanr
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.model_selection import GroupKFold
from data_utils import ROOT,load_dataset,rigid_basis,project
from denoise_benchmark import fold_for

ELEMENTS=['H','C','N','O','F','S','Cl','other']
BUDGETS=[.01,.02,.05,.1,.2,.3,.5]

def descriptors(r):
    # Deliberately access only geometry, original forces, species and charge.
    R,F=r['R'],r['F'];n=len(R)
    U=rigid_basis(R);normal=F-project(F,U)
    trans=np.broadcast_to(F.mean(0),F.shape);rot=normal-trans
    net=np.linalg.norm(F.sum(0))/n
    rigid=np.sqrt(np.mean(normal**2));rotation=np.sqrt(np.mean(rot**2))
    magnitude=np.linalg.norm(F,axis=1);radii=np.linalg.norm(R-R.mean(0),axis=1)
    D=np.linalg.norm(R[:,None]-R[None,:],axis=2)
    pair=D[np.triu_indices(n,1)];nearest=np.min(D+np.eye(n)*1e6,axis=1)
    vals={f'fraction_{s}':np.mean([z==s if s!='other' else z not in ELEMENTS[:-1] for z in r['symbols']]) for s in ELEMENTS}
    vals.update(n_atoms=np.log1p(n),charge=float(r['info'].get('charge',0)),
                net_force=np.log1p(net/1e-3),rigid_force=np.log1p(rigid/1e-3),
                rotational_force=np.log1p(rotation/1e-3),force_rms=np.log1p(np.sqrt(np.mean(F**2))))
    for label,array in [('force',magnitude),('radius',radii),('pair',pair),('nearest',nearest)]:
        for k,q in [('min',0),('q25',.25),('median',.5),('q75',.75),('max',1)]:
            vals[label+'_'+k]=np.log1p(np.quantile(array,q))
        vals[label+'_std']=np.log1p(np.std(array))
    return vals,dict(net_force=net,rigid_force=rigid,force_magnitude=np.sqrt(np.mean(F**2)))

def spectral_fit(X,y,alpha,pooled):
    mu=X.mean(0);sd=X.std(0);active=sd>1e-12
    sd=np.where(active,sd,1);Z=(X[:,active]-mu[active])/sd[active]
    ym=y.mean();G=Z.T@Z/len(X);b=Z.T@(y-ym)/len(X)
    eig,V=np.linalg.eigh(G);eig=np.maximum(eig,0)
    if pooled:
        bulk=eig<=(1+np.sqrt(Z.shape[1]/len(X)))**2
        if np.any(bulk):eig[bulk]=eig[bulk].mean()
    coef=(V@((V.T@b)/(eig+alpha)))
    return mu,sd,active,ym,coef

def spectral_predict(model,X):
    mu,sd,active,ym,coef=model
    return ym+((X[:,active]-mu[active])/sd[active])@coef

def fit_predictions(X,y,groups,Xtest,seed):
    start=time.perf_counter();out={};selection=[]
    logy=np.log(np.maximum(y,1e-8))
    for name,target,cols in [('trees_log',logy,np.arange(X.shape[1])),('trees_raw',y,np.arange(X.shape[1])),
                             ('trees_physics',logy,np.array([10,11]))]:
        model=ExtraTreesRegressor(n_estimators=256,min_samples_leaf=5,max_features=1.,random_state=seed,n_jobs=1)
        model.fit(X[:,cols],target);out[name]=model.predict(Xtest[:,cols])
    cv=GroupKFold(n_splits=3)
    for pooled,name in [(False,'ridge'),(True,'mp_ridge')]:
        scores=[]
        for alpha in [1e-4,1e-2,1.,100.]:
            errors=[]
            for train,val in cv.split(X,logy,groups):
                m=spectral_fit(X[train],logy[train],alpha,pooled)
                errors.extend((spectral_predict(m,X[val])-logy[val])**2)
            scores.append(np.mean(errors))
        alpha=[1e-4,1e-2,1.,100.][int(np.argmin(scores))]
        out[name]=spectral_predict(spectral_fit(X,logy,alpha,pooled),Xtest)
        selection.append(dict(method=name,alpha=alpha,cv_log_mse=min(scores)))
    return out,selection,time.perf_counter()-start

def evaluate_set(bad,impact,chosen):
    return dict(recall=float(bad[chosen].sum()/bad.sum()) if bad.sum() else None,
                impact_fraction=float(impact[chosen].sum()/impact.sum()))

def top(score,indices,k):
    # Stable index tie-break makes all choices deterministic.
    return indices[np.lexsort((indices,-score))[:k]]

def run():
    metrics=[];predictions=[];configs=[];selections=[];timings=[]
    for dataset in ['aimnet2','transition1x']:
        records=load_dataset(dataset);N=len(records)
        packs=[descriptors(r) for r in records]
        names=list(packs[0][0]);X=np.array([list(p[0].values()) for p in packs])
        assert names[10:12]==['net_force','rigid_force']
        y=np.array([np.sqrt(np.mean((r['F']-r['Fref'])**2)) for r in records])
        impact=np.array([np.sum((r['F']-r['Fref'])**2) for r in records])
        groups=np.array([r['formula'] for r in records]);folds=np.array([fold_for(g) for g in groups])
        indices=np.arange(N)
        worst=np.zeros(N,dtype=bool);worst[top(y,indices,int(np.ceil(.1*N)))]=True
        truths={'worst_decile':worst,'above_5mev':y>.005,'above_10mev':y>.010,'above_25mev':y>.025}
        basic={m:np.array([p[1][m] for p in packs]) for m in ['net_force','rigid_force','force_magnitude']}
        # Geometry novelty uses original unlabeled geometry/composition only.
        gi=np.array([i for i,n in enumerate(names) if not (n.startswith('force') or n in ('net_force','rigid_force','rotational_force'))])
        med=np.median(X[:,gi],axis=0);scale=np.std(X[:,gi],axis=0);scale=np.maximum(scale,1e-8)
        basic['geometry_novelty']=np.sum(((X[:,gi]-med)/scale)**2,axis=1)
        for i,r in enumerate(records):
            configs.append(dict(dataset=dataset,index=i,formula=r['formula'],fold=int(folds[i]),rmse_mev_A=1000*y[i],
                                squared_discrepancy=impact[i],worst_decile=bool(worst[i])))
        for scenario in range(5):
            seedidx=indices[folds==scenario];pool=indices[folds!=scenario]
            assert set(groups[seedidx]).isdisjoint(groups[pool])
            learned,chosen,duration=fit_predictions(X[seedidx],y[seedidx],groups[seedidx],X[pool],20260911+scenario)
            selections.extend(dict(dataset=dataset,scenario=scenario,**s) for s in chosen)
            timings.append(dict(dataset=dataset,scenario=scenario,seed_count=len(seedidx),pool_count=len(pool),fit_seconds=duration))
            scores={m:v[pool] for m,v in basic.items()};scores.update(learned)
            scores['reference_oracle']=y[pool]
            for method,score in scores.items():
                for i,s in zip(pool,score):
                    predictions.append(dict(dataset=dataset,scenario=scenario,index=int(i),method=method,score=float(s)))
            for fraction in BUDGETS:
                k=int(np.ceil(fraction*len(pool)));budget=len(seedidx)+k
                for endpoint,bad in truths.items():
                    common=dict(dataset=dataset,scenario=scenario,endpoint=endpoint,acquisition_fraction=fraction,
                                seed_count=len(seedidx),selected_count=k,total_count=budget,total_fraction=budget/N,
                                n_bad=int(bad.sum()))
                    for method,score in scores.items():
                        acquired=top(score,pool,k);selected=np.r_[seedidx,acquired]
                        metrics.append(dict(**common,method=method,comparison='shared_seed',**evaluate_set(bad,impact,selected),
                                            acquisition_recall=float(bad[acquired].sum()/bad[pool].sum()) if bad[pool].sum() else None))
                    # Exact expectation for uniform selection on pool, with fixed seed.
                    rec=(bad[seedidx].sum()+k/len(pool)*bad[pool].sum())/bad.sum() if bad.sum() else None
                    imp=(impact[seedidx].sum()+k/len(pool)*impact[pool].sum())/impact.sum()
                    metrics.append(dict(**common,method='random',comparison='shared_seed',recall=rec,impact_fraction=imp,
                                        acquisition_recall=k/len(pool) if bad[pool].sum() else None))
                    for method,score in basic.items():
                        selected=top(score,indices,budget)
                        metrics.append(dict(**common,method=method,comparison='total_budget',**evaluate_set(bad,impact,selected),acquisition_recall=None))
                    metrics.append(dict(**common,method='random',comparison='total_budget',recall=budget/N if bad.sum() else None,
                                        impact_fraction=budget/N,acquisition_recall=None))
                    metrics.append(dict(**common,method='reference_oracle',comparison='total_budget',
                                        **evaluate_set(bad,impact,top(y,indices,budget)),acquisition_recall=None))
            print(dataset,'scenario',scenario,'seed',len(seedidx),'pool',len(pool),'fit seconds',round(duration,2),flush=True)
        (ROOT/'results'/'reliability_feature_names.json').write_text(json.dumps(names,indent=2)+'\n')
    for name,rows in [('reliability_metrics',metrics),('reliability_predictions',predictions),('reliability_configurations',configs)]:
        with open(ROOT/'results'/f'{name}.csv','w') as f:
            w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
    (ROOT/'results'/'reliability_selection.json').write_text(json.dumps(selections,indent=2)+'\n')
    (ROOT/'results'/'reliability_timings.json').write_text(json.dumps(timings,indent=2)+'\n')

if __name__=='__main__':run()
