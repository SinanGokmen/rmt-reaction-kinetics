"""Grouped out-of-fold force denoising. All parameter selection is internal."""
import csv
import hashlib
import json
import numpy as np
from data_utils import ROOT, load_dataset, rigid_basis, project

ELEMENTS = ['H','C','N','O','F','S','Cl','other']

def fold_for(formula):
    return int(hashlib.sha256(('dft-denoise-v1:'+formula).encode()).hexdigest()[:12],16)%5

def features(r):
    R, F = r['R'], r['F']
    U = rigid_basis(R)
    rigid = F - project(F,U)
    trans = np.broadcast_to(F.mean(0),F.shape)
    rot = rigid-trans
    radius = np.linalg.norm(R-R.mean(0),axis=1)
    d2 = np.sum((R[:,None,:]-R[None,:,:])**2,axis=-1)
    coord = np.exp(-d2/4).sum(1)-1
    env = np.column_stack((np.ones(len(R)),radius/(1+radius),coord/(1+coord)))
    cols = []
    for el in ELEMENTS:
        mask = np.array([s==el if el!='other' else s not in ELEMENTS[:-1] for s in r['symbols']])
        for k in range(3):
            for marker in (trans,rot):
                cols.append((marker*(mask*env[:,k])[:,None]).ravel())
    X = project(np.stack(cols,axis=1),U)
    return dict(U=U,X=X,target=project(F-r['Fref'],U).ravel(),baseline=project(F,U).ravel(),
                ref=r['Fref'].ravel(),fold=fold_for(r['formula']),record=r)

def coefficients(items, method):
    G = sum(a['X'].T@a['X'] for a in items)
    b = sum(a['X'].T@a['target'] for a in items)
    scale = np.sqrt(np.maximum(np.diag(G),1e-30))
    active = np.diag(G) > max(np.diag(G).max()*1e-12,1e-28)
    ix = np.flatnonzero(active)
    H = G[np.ix_(ix,ix)]/scale[ix,None]/scale[None,ix]
    z = b[ix]/scale[ix]
    eig,V = np.linalg.eigh(H)
    eig=np.maximum(eig,0)
    candidates=[('zero',np.zeros(len(b)))]
    if method=='ridge':
        options=[(f'alpha={alpha:g}',1/(eig+alpha)) for alpha in np.logspace(-6,2,9)]
    elif method=='truncate':
        options=[]
        for cut in [1e-6,1e-4,1e-3,1e-2,.03,.1,.3]:
            inv=np.zeros_like(eig);keep=eig>cut*eig.max();inv[keep]=1/eig[keep]
            options.append((f'cut={cut:g}',inv))
    elif method=='mp_bulk':
        upper=(1+np.sqrt(len(ix)/len(items)))**2
        bulk=eig<=upper
        pooled=eig.copy()
        pooled[bulk]=eig[bulk].mean() if np.any(bulk) else 1
        options=[]
        for blend in [.25,.5,.75,1.]:
            for floor in [1e-6,1e-3,.1,1.]:
                options.append((f'blend={blend:g};floor={floor:g}',1/((1-blend)*eig+blend*pooled+floor)))
    else:
        raise ValueError(method)
    for label,inv in options:
        theta=np.zeros(len(b));theta[ix]=(V@(inv*(V.T@z)))/scale[ix]
        candidates.append((label,theta))
    return candidates

def element_variances(items):
    values={}
    for a in items:
        r=a['record'];e=r['F']-r['Fref']
        for s,err in zip(r['symbols'],e):
            values.setdefault(s,[]).append(float(np.mean(err**2)))
    default=np.mean([x for v in values.values() for x in v])
    return {s:max(np.mean(v),default*1e-3,1e-20) for s,v in values.items()},default

def weighted_projection(a,variances,default):
    r=a['record'];U=a['U'];f=r['F'].ravel()
    w=np.repeat([variances.get(s,default) for s in r['symbols']],3)
    return f-w*(U@np.linalg.pinv(U.T@(w[:,None]*U),rcond=1e-12)@(U.T@f))

def run():
    rows,selections=[],[]
    for name in ['aimnet2','transition1x']:
        items=[features(r) for r in load_dataset(name)]
        for fold in range(5):
            train=[a for a in items if a['fold'] not in (fold,(fold+1)%5)]
            val=[a for a in items if a['fold']==(fold+1)%5]
            test=[a for a in items if a['fold']==fold]
            variances,default=element_variances(train)
            fitted={}
            for method in ['ridge','truncate','mp_bulk']:
                candidates=coefficients(train,method)
                scores=[sum(np.sum((a['baseline']-a['X']@theta-a['ref'])**2) for a in val) for _,theta in candidates]
                best=int(np.argmin(scores));label,theta=candidates[best];fitted[method]=theta
                selections.append(dict(dataset=name,fold=fold,method=method,parameter=label,
                                       calibration=len(train),validation=len(val),test=len(test),
                                       validation_sse=scores[best]))
            for a in test:
                r=a['record'];f=r['F'];ref=a['ref']
                predictions={'raw':f.ravel(),'translation':(f-f.mean(0)).ravel(),
                             'rigid':a['baseline'],'element_weighted':weighted_projection(a,variances,default)}
                predictions.update({m:a['baseline']-a['X']@theta for m,theta in fitted.items()})
                for method,pred in predictions.items():
                    err=pred-ref; tangent=project(err,a['U'])
                    rows.append(dict(dataset=name,fold=fold,index=r['index'],formula=r['formula'],
                                     method=method,n_components=f.size,sse=float(err@err),
                                     tangent_sse=float(tangent@tangent),mae=float(np.abs(err).mean()),
                                     max_abs_error=float(np.abs(err).max())))
            print(name,'fold',fold,'train/val/test',len(train),len(val),len(test),
                  {m:selections[-3+i]['parameter'] for i,m in enumerate(fitted)},flush=True)
    with open(ROOT/'results'/'denoising_oof.csv','w') as f:
        w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
    (ROOT/'results'/'model_selection.json').write_text(json.dumps(selections,indent=2)+'\n')

if __name__=='__main__':
    run()
