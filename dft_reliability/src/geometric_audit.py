"""Small O(3)-invariant radial message network for force-discrepancy auditing.
NumPy CPU reference implementation, not SchNet or an interatomic potential.
"""
import argparse, json, hashlib
import numpy as np
import pandas as pd
from data_utils import ROOT, load_dataset
from denoise_benchmark import fold_for
from reliability_benchmark import top
ELEMENTS=['H','C','N','O','F','S','Cl','other']

def graph(r):
    # No reference-label access. Scalars preserve rotation/reflection invariance.
    R,F=r['R'],r['F']; n=len(R)
    e=np.eye(8)[[ELEMENTS.index(s) if s in ELEMENTS else 7 for s in r['symbols']]]
    d=np.linalg.norm(R[:,None]-R[None,:],axis=-1)
    cutoff=.5*(1+np.cos(np.pi*np.minimum(d/5.,1.)))
    np.fill_diagonal(cutoff,0)
    radial=np.exp(-((d[:,:,None]-np.linspace(0,5,8))/0.7)**2)*cutoff[:,:,None]
    # One continuous-distance graph aggregation, then shared learned node update.
    messages=np.einsum('ijk,jl->ilk',radial,e).reshape(n,64)
    messages/=np.maximum(cutoff.sum(1,keepdims=True),1.)
    return np.c_[e,messages,np.log1p(np.linalg.norm(F,axis=1))]

def pack(gs):
    sizes=np.array([len(g) for g in gs]); ids=np.repeat(np.arange(len(gs)),sizes)
    return np.concatenate(gs),ids,sizes

def init(p,seed):
    rng=np.random.default_rng(seed)
    return [rng.normal(0,1/np.sqrt(p),(p,32)),np.zeros(32),rng.normal(0,1/np.sqrt(32),(32,16)),np.zeros(16),rng.normal(0,1/4,16),np.zeros(1)]

def forward(theta,X,ids,sizes):
    W,b,U,c,v,a=theta
    H=np.tanh(X@W+b); J=np.tanh(H@U+c)
    P=np.zeros((len(sizes),16)); np.add.at(P,ids,J/sizes[ids,None])
    return P@v+a[0],(H,J,P)

def loss_grad(theta,X,ids,sizes,y):
    pred,(H,J,P)=forward(theta,X,ids,sizes); err=pred-y; dp=2*err/len(y)
    dJ=(dp[:,None]*theta[4])[ids]/sizes[ids,None]; dB=dJ*(1-J*J)
    dA=(dB@theta[2].T)*(1-H*H)
    grads=[X.T@dA,dA.sum(0),H.T@dB,dB.sum(0),P.T@dp,np.array([dp.sum()])]
    return float(np.mean(err*err)),grads

def fit(gs,y,epochs,seed,validation=None):
    X,ids,sizes=pack(gs); mu=X.mean(0); sd=np.maximum(X.std(0),1e-6); X=(X-mu)/sd
    ym=y.mean(); ys=max(y.std(),1e-6); yy=(y-ym)/ys
    theta=init(X.shape[1],seed); m=[np.zeros_like(t) for t in theta]; v=[t.copy() for t in m]
    selected=epochs; best=np.inf
    for epoch in range(1,epochs+1):
        loss,grad=loss_grad(theta,X,ids,sizes,yy)
        if not np.isfinite(loss): raise ValueError('Nonfinite training loss')
        for i,g in enumerate(grad):
            m[i]=.9*m[i]+.1*g; v[i]=.999*v[i]+.001*g*g
            theta[i]-=.003*(m[i]/(1-.9**epoch))/(np.sqrt(v[i]/(1-.999**epoch))+1e-8)
        if validation is not None and epoch in (10,25,50,100):
            vg,vy=validation
            pv=predict((theta,mu,sd,ym,ys),vg); score=np.mean((pv-vy)**2)
            if score<best: best=score; selected=epoch
    return (theta,mu,sd,ym,ys),selected

def predict(model,gs):
    theta,mu,sd,ym,ys=model; X,ids,sizes=pack(gs)
    return forward(theta,(X-mu)/sd,ids,sizes)[0]*ys+ym

def run(seed):
    out=ROOT/'results'/'geometric_audit';out.mkdir(exist_ok=True,parents=True)
    metrics=[];predictions=[];settings=[]
    for name in ['aimnet2','transition1x']:
        rr=load_dataset(name); gs=[graph(r) for r in rr]; groups=np.array([r['formula'] for r in rr])
        folds=np.array([fold_for(g) for g in groups]);idx=np.arange(len(rr))
        q=np.array([np.sqrt(np.mean((r['F']-r['Fref'])**2)) for r in rr]);y=np.log(np.maximum(q,1e-8))
        impact=np.array([np.sum((r['F']-r['Fref'])**2) for r in rr]);bad=np.zeros(len(rr),bool);bad[top(q,idx,100)]=True
        for f in range(5):
            tr=idx[folds==f]; te=idx[folds!=f]
            ug=sorted(set(groups[tr]),key=lambda s:hashlib.sha256(('graph-val:'+s).encode()).hexdigest())
            va_groups=set(ug[:max(1,len(ug)//5)])
            va=np.array([i for i in tr if groups[i] in va_groups]); inner=np.array([i for i in tr if groups[i] not in va_groups])
            assert len(inner) and len(va) and set(groups[tr]).isdisjoint(groups[te])
            _,epochs=fit([gs[i] for i in inner],y[inner],100,seed,([gs[i] for i in va],y[va]))
            model,_=fit([gs[i] for i in tr],y[tr],epochs,seed)
            p=predict(model,[gs[i] for i in te]);chosen=np.r_[tr,top(p,te,int(np.ceil(.1*len(te))))]
            metrics.append(dict(source=name,scenario=f,seed=seed,epochs=epochs,total_budget=len(chosen),recall=bad[chosen].sum()/bad.sum(),impact=impact[chosen].sum()/impact.sum(),log_rmse=np.sqrt(np.mean((p-y[te])**2))))
            predictions.extend(dict(source=name,scenario=f,index=int(i),prediction=float(v),log_q=float(y[i])) for i,v in zip(te,p))
            settings.append(dict(source=name,scenario=f,inner_train=len(inner),inner_validation=len(va),refit=len(tr),epochs=epochs))
            theta,mu,sd,ym,ys=model
            np.savez_compressed(out/f'{name}_fold{f}_seed{seed}.npz',**{f'theta{i}':a for i,a in enumerate(theta)},mu=mu,sd=sd,ym=ym,ys=ys)
            print(name,f,'recall',metrics[-1]['recall'],'epochs',epochs,flush=True)
    df=pd.DataFrame(metrics);df.to_csv(out/f'metrics_seed{seed}.csv',index=False)
    pd.DataFrame(predictions).to_csv(out/f'predictions_seed{seed}.csv.gz',index=False)
    (out/f'settings_seed{seed}.json').write_text(json.dumps(settings,indent=2)+'\n')
    print(df.groupby('source')[['recall','impact','log_rmse']].mean())

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--seed',type=int,default=20260916)
    run(parser.parse_args().seed)
