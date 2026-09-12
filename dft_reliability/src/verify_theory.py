"""Independent conservation, equivariance and least-squares identity checks."""
import json
import numpy as np
from data_utils import ROOT,load_dataset,rigid_basis,project
from denoise_benchmark import features

def pair_design(R):
    # Force columns = -gradient of sum_{i<j} exp(-a*distance^2).
    d=R[:,None,:]-R[None,:,:];d2=np.sum(d*d,axis=-1)
    return np.stack([(2*a*d*np.exp(-a*d2)[:,:,None]).sum(1).ravel()
                     for a in [.1,.3,.7,1.,2.,4.]],axis=1)

def run():
    rng=np.random.default_rng(20260911)
    residuals=dict(symmetry=0.,normal_equations=0.,loss_identity=0.,equivariance=0.,permutation=0.)
    for name in ['aimnet2','transition1x']:
        for r in load_dataset(name)[::25]:
            U=rigid_basis(r['R']);J=pair_design(r['R']);y=r['F'].ravel();py=project(y,U)
            residuals['symmetry']=max(residuals['symmetry'],float(np.max(np.abs(U.T@J))))
            residuals['normal_equations']=max(residuals['normal_equations'],float(np.max(np.abs(J.T@y-J.T@py))))
            theta=rng.normal(size=J.shape[1]);g=J@theta
            lhs=np.sum((g-y)**2);rhs=np.sum((g-py)**2)+np.sum((y-py)**2)
            residuals['loss_identity']=max(residuals['loss_identity'],abs(lhs-rhs)/max(lhs,1.))
            a=features(r);Q,_=np.linalg.qr(rng.normal(size=(3,3)))
            rt=dict(r,R=r['R']@Q+rng.normal(size=3),F=r['F']@Q,Fref=r['Fref']@Q)
            expected=np.einsum('nik,ij->njk',a['X'].reshape(len(r['R']),3,-1),Q).reshape(a['X'].shape)
            residuals['equivariance']=max(residuals['equivariance'],float(np.max(np.abs(features(rt)['X']-expected))))
            perm=rng.permutation(len(r['R']))
            rp=dict(r,R=r['R'][perm],F=r['F'][perm],Fref=r['Fref'][perm],symbols=[r['symbols'][i] for i in perm])
            expected=a['X'].reshape(len(perm),3,-1)[perm].reshape(a['X'].shape)
            residuals['permutation']=max(residuals['permutation'],float(np.max(np.abs(features(rp)['X']-expected))))
    assert residuals['symmetry']<1e-10
    assert residuals['normal_equations']<1e-9
    assert residuals['loss_identity']<1e-12
    assert residuals['equivariance']<1e-10
    assert residuals['permutation']<1e-10
    (ROOT/'results'/'verification.json').write_text(json.dumps(residuals,indent=2)+'\n')
    print(json.dumps(residuals,indent=2))

if __name__=='__main__':run()
