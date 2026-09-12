# Budget-aware reliability auditing of DFT force datasets

**Physical consistency, error prediction and missed failures**  
Sinan Gökmen — Department of Chemistry, Istanbul Technical University  
gokmens23@itu.edu.tr — 11 September 2026

This study asks which existing DFT calculations should be checked when tight
reference calculations are expensive. It compares inexpensive physical checks
with learned error rankings, explicitly charging for their training references.
It also distinguishes finding many inaccurate records from finding the records
that dominate squared force discrepancy.

The experiment retrospectively reveals existing paired references for 2,000
public molecular configurations. No new DFT calculations were performed. This
is a reproducible research report, not a demonstrated large materials-database
service, improved interatomic potential, or drug-discovery model. No arXiv submission has been made. Code and results are published at
https://github.com/SinanGokmen/rmt-reaction-kinetics/tree/main/dft_reliability.

## Primary results

Worst-discrepancy-decile recall, percent, at an average total reference budget
of 28.04% of each sample:

| Policy | AIMNet2 | Transition1x |
|---|---:|---:|
| Uniform selection, expected | 28.04 | 28.04 |
| Direct net force | 87.8 | 27.6 |
| Direct force/torque | 95.0 | 31.8 |
| Trees predicting log discrepancy, including seed cost | 76.0 | 39.0 |
| Ridge, including seed cost | 77.6 | 34.2 |
| MP-pooled ridge, including seed cost | 77.6 | 35.2 |

Means summarize five overlapping formula-separated seed scenarios; they are not
independent replications. Seeds average 20% of the sample and new acquisitions
10% of the remaining pool. The complete budget includes both. Direct policies
spend the same total count without training references. Scenario ranges, other
methods and alternative thresholds are in the manuscript and CSV files.

The largest Transition1x discrepancy (zero-based index 255, C6H6O) contributes
97.75% of squared discrepancy, yet direct net-force and force/torque policies
miss it at all primary budgets. Its frame RMSE is 866.48 meV/Angstrom and its
rigid-force score only 0.6691 meV/Angstrom. A basic force-magnitude policy catches
it but finds fewer high-discrepancy records overall. No universal detector or
special RMT advantage is established.

The manuscript proves elementary consistency bounds and an acquisition-score
regret bound. These apply standard projection and additive-utility arguments;
they are not claimed as new general mathematical theorems. RMT supplies a
covariance-regularization comparator, not an identified physical noise spectrum.

## Reproduce the primary audit

Python 3.12 was used. Install `requirements.txt`. No GPU or DFT program is needed.
Run from this directory:

```bash
python3 src/download_data.py
OPENBLAS_NUM_THREADS=1 python3 src/audit_data.py
OPENBLAS_NUM_THREADS=1 python3 src/reliability_benchmark.py
OPENBLAS_NUM_THREADS=1 python3 src/analyze_reliability.py
OPENBLAS_NUM_THREADS=1 python3 src/verify_reliability.py
OPENBLAS_NUM_THREADS=1 python3 src/small_seed_benchmark.py
OPENBLAS_NUM_THREADS=1 python3 src/analyze_small_seed.py
OPENBLAS_NUM_THREADS=1 python3 src/verify_small_seed.py
python3 src/write_small_seed_section.py
python3 src/build_pdf.py
```

The final command needs pdflatex, BibTeX and the standard packages in `main.tex`.
The immutable upstream commit and file hashes are recorded in `data/manifest.json`.
Raw XYZ files are downloaded and verified, not redistributed. AIMNet2 and
Transition1x reproduce their published pooled comparisons; ANI-1x and SPICE are
excluded because their conventions remain unresolved, without alleging a source
publication error.

## Files

- `manuscript/main.pdf`, `main.tex`, `main.bbl`, `references.bib`: current report.
- `manuscript/figures/reliability_*.pdf`: three primary figures.
- `manuscript/figures/small_seed_budget.pdf`: fixed-budget seed sensitivity.
- `notes/SMALL_SEED_PROTOCOL.md`: exploratory extension recorded after the primary
  results. Its endpoint counts only discoveries in a fixed held-out-formula pool.
- `results/small_seed_*`: all nested seed sets, score rows, metrics and checks.
- `notes/RELIABILITY_PROTOCOL.md`: protocol recorded before the audit fits,
  but after an exploratory denoising pilot on these same samples.
- `notes/ARXIV_READINESS_TR.md`: Turkish assessment of contribution and limitations.
- `results/reliability_*.csv` and `.json`: predictions, outcomes, selected
  parameters and verification. There are 80,000 score rows and 4,760 metric rows
  for only 2,000 unique configurations, not 80,000 independent samples.
- `CHECKSUMS.json`: SHA-256 checksums of distributed research files.

The earlier denoising pilot is supporting material. Its description is preserved
in `notes/previous_denoising_README.md`, its manuscript in
`notes/previous_denoising_manuscript.tex`, and its code/results remain available.
It is not the current paper's main claim. The separate earlier reaction-kinetics
project is not part of this package.

## Scope and provenance

Splits separate molecular formulas, not guaranteed scaffolds or reaction families.
The learning target is discrepancy from tight DFT at a nominally matched protocol,
not exact quantum mechanics or experiment. CPU-hour costs, downstream model
training, periodic materials, calibrated failure probabilities and large-database
scaling have not been tested. Reference-only values do not enter descriptors.

DFT data quality has substantial prior work, including
[Carbogno et al.](https://arxiv.org/abs/2008.10402) and
[Bosoni et al.](https://arxiv.org/abs/2305.17274).
Paired data are from [Kuryla et al.](https://arxiv.org/abs/2510.19774) and their
[repository](https://github.com/water-ice-group/datasets_dft_accuracy), pinned to
`322a41229f7707a58626a7c03ce850d67920fad0`.
The manuscript attributes the prior observations and discloses extensive
ChatGPT/Codex assistance. Numerical checks do not constitute independent
scientific verification or guarantee publication acceptance.

## Small-seed extension

The additional experiment spends exactly 280 total references per sample, with
10, 20, 50, 100 or all designated seed-fold records used for training. Five nested
random prefixes are evaluated for each of the five formula scenarios. The pool
is fixed within a scenario; unused seed-fold records are not audit candidates.
The learning method acquires 280 minus the seed count, whereas a direct screen
acquires 280 records from the same pool. Only held-out-pool discoveries count.
This tests transfer to unseen formulas, with a different denominator from the
primary whole-sample audit. Repeated samples are not independent replications.
The tree settings, including minimum leaf size five, were not retuned for small
seeds. These exploratory curves do not identify an externally validated optimum.

At 50 seed references, ridge recovers 93.7% of the AIMNet2 held-out-pool worst
decile, compared with 71.7% for the full seed fold (mean 200 references). Direct
force/torque screening still recovers 95.5%. Transition1x ridge at 50 references
recovers 36.5%, close to the 35.1% uniform expectation. These are acquisition
results at fixed total cost, not proof that a model trained on fewer labels
has lower prediction error.

## Public repository packaging

Large result files are stored as gzip streams, split into numbered parts where
needed. Run `python3 src/restore_results.py` before inspecting saved results.
The script verifies SHA-256 hashes and reconstructs the original CSV/JSON files.
All result files can also be regenerated with the commands above.
