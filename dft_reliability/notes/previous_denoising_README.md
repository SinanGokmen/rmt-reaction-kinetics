# Symmetry-aware DFT force denoising

This study separates three claims: repairing symmetry violations, improving noisy
force labels, and improving a trained interatomic potential. Only the first two
are experimentally addressed here. The manuscript proves a squared-loss invariance
identity and a classical conditional-prediction risk decomposition, and reports
positive and negative results on public paired DFT data.

**Current scientific status:** a reproducible theory-and-pilot study, not evidence
that RMT improves a trained MLIP or drug-discovery endpoint. The tested RMT-inspired
method does not beat the elementary element-weighted baseline on AIMNet2. No arXiv
submission or public code release has been made for this study.

## Results

| Force-label RMSE, meV/Angstrom | AIMNet2 | Transition1x |
|---|---:|---:|
| Raw | 4.7979 | 26.9007 |
| Orthogonal force/torque projection | 4.6092 | 26.8853 |
| Element-weighted projection | 4.4800 | 26.8872 |
| Ridge correction | 4.4940 | 26.8836 |
| MP bulk heuristic | 4.4909 | 26.8833 |

These are out-of-fold corrected-label discrepancies against tight DFT references,
not neural-potential test errors. The best AIMNet2 method reduces label RMSE by
6.63% from raw and 2.80% from orthogonal projection. A nominal paired cluster
bootstrap does not establish MP superiority over ridge and favors element
weighting over MP. Transition1x gains are negligible in pooled RMSE.

For an invariant energy model under squared force loss, orthogonal projection
changes the loss only by a parameter-independent constant. It cannot itself change
training gradients. A conditional correction can affect the remaining force
components when the relevant noise cross-covariance is predictable. A separate
Gaussian experiment illustrates spectral gains with a **known noise floor**;
it is not a reproduction of the molecular experiment.

## Contents

- `manuscript/main.pdf`, `main.tex`, `main.bbl`, `references.bib`: the eight-page report.
- `src/`: downloader, paired-data audit, denoising comparison, uncertainty analysis,
  mathematical checks, synthetic mechanism experiment, and plotting code.
- `results/`: all primary per-frame results, selected parameters, bootstrap summaries,
  verification values, and synthetic results.
- `notes/EXPERIMENT_PROTOCOL.md`: design fixed before fitting the molecular comparison.
- `notes/ARXIV_READINESS_TR.md`: Turkish research assessment and publication requirements.
- `data/manifest.json`: exact upstream commit, hashes and data download URLs.

The original molecular coordinates and force files are not redistributed in the
archive. Download them from the authors' repository with the supplied script.

## Reproduce

Python 3.12 was used. A CPU with NumPy/SciPy is sufficient; no GPU or DFT program is
needed. Install the pinned dependencies from `requirements.txt`. From this directory:

```bash
python3 src/download_data.py
OPENBLAS_NUM_THREADS=1 python3 src/audit_data.py
OPENBLAS_NUM_THREADS=1 python3 src/denoise_benchmark.py
OPENBLAS_NUM_THREADS=1 python3 src/analyze_results.py
OPENBLAS_NUM_THREADS=1 python3 src/verify_theory.py
OPENBLAS_NUM_THREADS=1 python3 src/synthetic_covariance.py
OPENBLAS_NUM_THREADS=1 python3 src/build_figures.py
python3 src/build_pdf.py
```

The last command requires a LaTeX installation with `pdflatex`, `bibtex`, `lmodern`,
`natbib`, `microtype`, `booktabs` and the other standard packages in `main.tex`.
The downloader verifies immutable Git blob hashes before accepting any file.
Two unvalidated source-file conventions are retained only in the audit; attempts
to load ANI-1x or SPICE into a fitted comparison raise an error by default.

## Interpretation boundaries

All 2,000 validated frames are retained, including outliers. Five-fold separation
is by molecular formula, not claimed to be by scaffold or reaction family. The
bootstrap resamples formulas conditional on already fitted out-of-fold predictors;
it does not refit the complete procedure. Calibration and validation use hundreds
of tight reference labels. Those labels must be included in any future compute or
sample-efficiency comparison. The MP molecular threshold is a structured-Gram
heuristic, not a validated random-matrix noise test.

The figures in the PDF are generated from saved result files. Neither molecular
simulation trajectories, binding free energies, trained GNN results nor new DFT
calculations are represented as having been performed.

## Sources and assistance

Primary data: Kuryla, Berger, Csanyi and Michaelides (2025),
[arXiv:2510.19774](https://arxiv.org/abs/2510.19774),
[paired data repository](https://github.com/water-ice-group/datasets_dft_accuracy).
Full methodological references and substantial ChatGPT/Codex assistance are
disclosed in the manuscript. This study is separate from the earlier synthetic
reaction-coordinate covariance study and does not overwrite its results.
