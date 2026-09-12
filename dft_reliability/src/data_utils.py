"""Minimal extxyz reader and isolated-molecule rigid-motion projectors."""
from collections import Counter
from pathlib import Path
import shlex
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
# ASE 2014 CODATA value, matching the upstream analysis convention.
HARTREE_EV = 27.211386024367243

def read_xyz(path):
    out = []
    with open(path) as stream:
        while (line := stream.readline()):
            if not line.strip():
                continue
            n = int(line)
            info = dict(t.split('=', 1) for t in shlex.split(stream.readline()) if '=' in t)
            props = info.pop('Properties').split(':')
            rows = [stream.readline().split() for _ in range(n)]
            arrays, offset = {}, 0
            for key, kind, width in zip(props[::3], props[1::3], props[2::3]):
                width = int(width)
                arr = np.array([r[offset:offset+width] for r in rows])
                arrays[key] = arr if kind == 'S' else arr.astype(float)
                offset += width
            if any(len(r) != offset for r in rows):
                raise ValueError('Incorrect row length')
            symbols = arrays['species'].ravel().tolist()
            out.append(dict(symbols=symbols, R=arrays['pos'], arrays=arrays, info=info,
                            formula=''.join(f'{s}{v}' for s,v in sorted(Counter(symbols).items()))))
    return out

def load_dataset(name, allow_unvalidated=False):
    if name not in ('aimnet2','transition1x') and not allow_unvalidated:
        raise ValueError('Upstream comparison is unresolved for this dataset; audit only.')
    records = read_xyz(ROOT / 'data' / f'{name}_configs.xyz')
    for i, r in enumerate(records):
        a = r['arrays']
        f = a['REF_forces'].copy()
        if name == 'ani_1x_tz':
            f *= HARTREE_EV
        elif name == 'spice':
            # Stored REF_forces are already in eV/A but are energy gradients.
            # Provisional D3 convention ONLY for auditing; not validated.
            f = -f - a['dftd3_forces']
        r.update(index=i, F=f, Fref=a['orca_forces'].copy())
    return records

def rigid_basis(R):
    """Orthonormal columns spanning translation and infinitesimal rotation."""
    r = R - R.mean(axis=0)
    n = len(r)
    trans = np.tile(np.eye(3), (n,1))
    rot = np.stack([np.cross(np.broadcast_to(e,r.shape),r).ravel() for e in np.eye(3)],axis=1)
    # Rescaling keeps translation/rotation blocks comparable; it preserves spans.
    rot /= max(np.linalg.norm(r), 1e-12)
    U, s, _ = np.linalg.svd(np.column_stack((trans/np.sqrt(n),rot)),full_matrices=False)
    return U[:, s > s[0]*1e-10]

def project(F, U):
    """Project vectors or a design matrix into the zero-force/torque subspace."""
    shape = F.shape
    if len(shape) == 2 and shape[1] == 3 and shape[0]*3 == len(U):
        f = F.ravel()
        return (f-U@(U.T@f)).reshape(shape)
    return F - U@(U.T@F)
