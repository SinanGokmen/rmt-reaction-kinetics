# Experiment protocol — 11 September 2026

This protocol is recorded after descriptive error auditing and before fitting the
denoisers. It is not an externally registered preregistration.

## Question and scope

Can constraint violations in a noisy force label predict its error within the
zero-net-force/torque subspace on held-out molecular compositions? Does spectral
regularization help relative to ridge and elementary constraint projection?
The tightly recomputed DFT force is an operational reference, not exact quantum
truth. This experiment tests force-label correction, not binding affinity.

## Data validation

Immutable upstream commit: 322a41229f7707a58626a7c03ce850d67920fad0,
water-ice-group/datasets_dft_accuracy, accompanying Kuryla et al., arXiv:2510.19774.
AIMNet2 (1000 configurations) and Transition1x (1000) reproduce the reported force
RMSDs, 4.80 and 26.9 meV/Angstrom. Use their stored force columns without conversion.
Retain all configurations including outliers in the primary analysis.

Do not use ANI-1x or SPICE for the fitted comparison: available file conventions
do not currently reproduce the reported values. ANI converted with Hartree/eV
gives 173.86 rather than 33.2 meV/Angstrom, with near-zero original net forces.
SPICE has 998 frames and gradients, and its D3 comparison is unresolved. These are
unresolved reproducibility checks, not evidence of an error in the publication.

## Leakage control

Assign entire molecular formulas to five outer folds with a deterministic hash.
One outer fold is test, the next is validation, and the remaining three are
calibration. Grouping by formula is stricter than identity for fixed-composition
conformers; it does not establish generalization across scaffolds or reaction
families. Report counts. Each frame receives exactly one out-of-fold prediction.
No target from the outer test fold enters fitting, scaling or parameter selection.

## Methods

Raw force; translation removal; orthogonal force/torque projection;
heteroscedastic force/torque projection with calibration-set element variances;
equivariant linear correction trained to predict the tangent-space discrepancy
from projected element/environment-weighted rigid-motion error markers.

The learned correction uses fixed element channels H/C/N/O/F/S/Cl/other,
three environment scalars (1, bounded radial distance, smooth coordination), and
two vector markers (translation and rotation parts of the force). Every feature
is projected into the allowed subspace. It is equivariant under rigid rotations
and translations and permutation-equivariant within species. It is not itself a
globally conservative force field. It is intended for preprocessing targets of
an invariant energy model.

Compare ridge (relative penalties 1e-6 to 1e2), spectral truncation (relative
cutoffs 1e-6 to 0.3), and MP-inspired covariance bulk pooling (blend strengths
0.25,0.5,0.75,1, plus a ridge floor). Choose by validation force MSE, including
zero correction as a candidate. The MP formula is only a heuristic here: atomic
rows are dependent, channels are structured, and isotropic Wishart assumptions
are not established. Do not present it as an RMT theorem for molecular data.

## Endpoints

Primary: pooled Cartesian-component RMSE against the operational reference on
all out-of-fold predictions. Secondary: RMSE restricted to tangent discrepancy,
per-configuration median error and tail error. Paired bootstrap by formula
(2000 replicates) for differences vs orthogonal projection and ridge.
Do not interpret failed superiority tests as evidence of equivalence.

## Mechanistic check

For an invariant differentiable energy E_theta(R), F_theta=-grad E_theta is in
the allowed subspace. Verify that raw vs orthogonally projected force labels
give the same parameter-dependent least-squares objective using an analytic
conservative pair-potential basis. Projection alone cannot change gradients
under a fixed scalar-weighted squared force loss. Weighted/robust losses and
label-dependent scheduling are outside that statement.

## Decision

No claim of a better interatomic potential without an additional matched-budget
downstream training experiment against tight test references. No claim that RMT
is necessary unless it improves on tuned ridge and simpler alternatives. Keep
negative outcomes and data-audit exclusions visible. Do not tune this protocol
after viewing outer-fold outcomes.
