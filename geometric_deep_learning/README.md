# Geometric deep learning baseline for DFT reliability auditing

This experimental extension learns a scalar force-discrepancy score from a
molecule's geometric graph. It is a CPU NumPy reference implementation with
analytic backpropagation, not a GPU implementation, pretrained foundation model,
SchNet reproduction, equivariant vector-force predictor or interatomic potential.
The original manuscript does not yet include these experiments.

## Representation

Nodes encode element identity and original force magnitude. Edges use interatomic
distances below 5 Angstrom, eight Gaussian radial basis functions and a smooth
cosine cutoff. A single element-conditioned radial neighbor aggregation feeds
shared learned tanh layers (32 and 16 channels). Mean pooling yields a scalar
log-discrepancy prediction. The radial basis itself is fixed; the node update
and output weights are learned. It is a shallow geometric message network.

Rotating/translating the molecule, reflecting it, or permuting node order does
not change the scalar output. Distance-only geometry cannot distinguish mirror
images. Force magnitudes are available from original calculations; reference
forces never enter inputs. Unknown elements share one category. Charge/spin and
force directions are not represented, limiting applicability.

Continuous-distance molecular convolutions are motivated by Schütt et al.,
[SchNet (2017)](https://arxiv.org/abs/1706.08566); this simplified architecture
is not claimed as their exact architecture or a new method.

## Recorded exploratory outcome

2,000 existing configurations; five overlapping formula-separated seed scenarios;
one neural initialization seed (20260916). Epochs selected within seed references,
then refit on all seed references. Total reference cost averages 28.04%, including
training. Endpoint: recall of the 100 highest-discrepancy records per source.

| Method | AIMNet2 recall | Transition1x recall |
|---|---:|---:|
| Net force, same total cost | 87.8% | 27.6% |
| Force/torque, same total cost | 95.0% | 31.8% |
| Ridge | 77.6% | 34.2% |
| MP-pooled ridge | 77.6% | 35.2% |
| Log-error trees | 76.0% | 39.0% |
| **Radial graph network** | **66.6%** | **41.6%** |

Graph recall ranges: AIMNet2 64–71%, Transition1x 25–51%. These ranges summarize
overlapping scenarios, not confidence intervals. Transition1x recall improves
in this one run, while AIMNet2 recall worsens substantially. No universal
superiority, statistically established improvement or RMT synergy is claimed.
The graph model uses different input representations and a different tuning
budget; this is a practical baseline comparison, not an isolated architecture
ablation. Additional initialization seeds and independent datasets are needed.

Log-discrepancy RMSE: 0.19149 and 0.26242. Captured squared discrepancy: 34.47%
and 59.30%; the latter is strongly affected by the known single dominant outlier.
No cleaned-data model was trained, and no new DFT calculation was performed.

## Reproduce

From the repository root (shared data and dependencies remain under `dft_reliability/`):

```bash
python -m pip install -r dft_reliability/requirements.txt
python dft_reliability/src/download_data.py
OPENBLAS_NUM_THREADS=1 python geometric_deep_learning/src/geometric_audit.py --seed 20260916
OPENBLAS_NUM_THREADS=1 python geometric_deep_learning/src/verify_geometric.py
```

Runs save models, per-scenario metrics, compressed record predictions and tuning
counts to `geometric_deep_learning/results/`. The verification script targets the recorded
seed 20260916. Model NPZ files can be regenerated from the stated seed; the GitHub
extension stores the metrics, settings, verification and predictions. Re-running
a seed overwrites its outputs; use a separate checkout for experimental changes.

Checks passed: finite-difference gradients (max error 3.46e-11), rigid-motion/node
permutation invariance, zero reference-input leakage and reconstruction of all
saved acquisition metrics (max difference below 2e-16). This checks implementation
integrity, not scientific superiority. See [the protocol](notes/GEOMETRIC_PROTOCOL.md) for the protocol.
