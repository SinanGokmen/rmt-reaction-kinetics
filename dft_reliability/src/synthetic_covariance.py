"""Mechanism illustration, specified after the real-data comparison.

Not an independent confirmation of molecular predictive superiority. Spectral
shrinkage is supplied the true isotropic noise floor (one), explicitly an oracle
advantage unavailable in the molecular experiment.
"""
import csv
import json
import numpy as np
from sklearn.covariance import oas
from data_utils import ROOT

def spectral(S,n):
    p=len(S);gamma=p/n
    eigen,V=np.linalg.eigh(S);values=np.ones(p)
    for i,lam in enumerate(eigen):
        if lam > (1+np.sqrt(gamma))**2:
            ell=(lam+1-gamma+np.sqrt((lam+1-gamma)**2-4*lam))/2
            overlap=(1-gamma/(ell-1)**2)/(1+gamma/(ell-1))
            values[i]=1+(ell-1)*overlap
    return (V*values)@V.T

def run():
    p,r=24,6;rows=[];max_identity=0.
    for case in ['isotropic','cross_spike','tangent_spike']:
        Sigma=np.eye(p)
        if case!='isotropic':
            w=np.zeros(p)
            if case=='cross_spike':w[0]=w[r]=1/np.sqrt(2)
            else:w[r]=1
            Sigma+=10*np.outer(w,w)
        L=np.linalg.cholesky(Sigma)
        Snn=Sigma[:r,:r];Stn=Sigma[r:,:r];Stt=Sigma[r:,r:]
        oracle=np.linalg.solve(Snn,Stn.T).T
        oracle_risk=np.trace(Stt-oracle@Stn.T)
        for n in [16,32,64,128]:
            for rep in range(200):
                rng=np.random.default_rng(np.random.SeedSequence([20260911,rep,n,['isotropic','cross_spike','tangent_spike'].index(case)]))
                X=rng.normal(size=(n,p))@L.T
                S=X.T@X/n
                C,_=oas(X,assume_centered=True)
                estimates={'projection':np.eye(p),'empirical':S,'oas':C,
                           'spiked_known_floor':spectral(S,n),'oracle':Sigma}
                for method,est in estimates.items():
                    B=np.linalg.solve(est[:r,:r],est[r:,:r].T).T
                    risk=np.trace(Stt)-2*np.sum(B*Stn)+np.trace(B@Snn@B.T)
                    excess=np.trace((B-oracle)@Snn@(B-oracle).T)
                    max_identity=max(max_identity,abs(risk-oracle_risk-excess))
                    rows.append(dict(case=case,n=n,replicate=rep,method=method,
                                     tangent_mse=risk/(p-r),oracle_excess=excess/(p-r),
                                     covariance_relative_frobenius=np.linalg.norm(est-Sigma)/np.linalg.norm(Sigma)))
    assert max_identity<1e-10
    with open(ROOT/'results'/'synthetic_covariance.csv','w') as f:
        w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
    (ROOT/'results'/'synthetic_verification.json').write_text(json.dumps(dict(max_risk_identity_error=max_identity),indent=2)+'\n')
    print('completed',len(rows),'rows; exact risk identity max error',max_identity)

if __name__=='__main__':run()
