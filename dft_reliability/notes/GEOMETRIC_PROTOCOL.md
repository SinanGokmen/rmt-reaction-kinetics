# Exploratory geometric graph model — 2026-09-16

Protocol written before fitting this model; prior baseline outcomes are known.
Same two 1,000-record force-pair samples, same five formula-separated reference
seed scenarios and 10% acquisition from the remaining pool. Charge seed references
to total budget. No new DFT, GPU acceleration or potential training is claimed.

Model: 5 Angstrom distance graph; eight Gaussian radial channels with cosine
cutoff; eight element categories; neighbor-element radial aggregation normalized
by weighted degree. Concatenate central element and original force norm, then
shared tanh node layers 32,16, mean pooling and linear graph output. Scalar output
is natural log of frame force discrepancy. This is a shallow, invariant geometric
message network with fixed radial basis and learned node updates, not a faithful
SchNet reimplementation. NumPy analytic gradients and Adam, learning rate .003.

Select 10/25/50/100 epochs on a deterministic formula-separated validation subset
inside seed references; refit all seed references. Node scaling/target scaling
use only the relevant training subset. Fixed architecture, one initialization
seed 20260916: exploratory, no seed-robustness claim. Test labels never select
architecture, epoch, scaling, or acquisition. No pooled-source fit.

Required checks: analytical gradients vs finite differences; prediction invariance
to translation, rotation and node permutation; no reference-force feature access;
reconstruct saved metric from predictions. Compare fixed prior physics/ridge/MP
baselines at the same total reference budget. Results are not independent-fold
confidence intervals. Does not establish chemical novelty or noise removal.
