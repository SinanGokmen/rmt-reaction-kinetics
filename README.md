# Spectral covariance regularization for reaction-coordinate kinetics

[Read the manuscript](manuscript/main.pdf) · [LaTeX source](manuscript/main.tex) · [Simulation code](src/) · [Results and data](results/)

Repository: https://github.com/SinanGokmen/rmt-reaction-kinetics

Research manuscript and reproducibility package, revised 10 September 2026.
Author: Sinan Gökmen.
Affiliation: Department of Chemistry, Istanbul Technical University.
Email: gokmens23@itu.edu.tr. Status: **not submitted**.

## What was actually completed

- A reversible-diffusion formulation linking tensor estimation to committors and capacities.
- An exact variational perturbation identity, conditional error bounds with proofs,
  and an analytic counterexample separating matrix loss from kinetic error.
- Five synthetic scenarios, four sample sizes, 120 paired replicates per setting:
  2,400 independently seeded data sets, each with 41 local covariance problems.
- Five initial estimators and a subsequently added exploratory Protected MP control.
- Seven publication figures, per-replicate data, bootstrap summaries and paired comparisons.
- A Schur-complement preservation theorem, approximate-direction leakage bound, and
  conditional Gaussian residual law with corrected MP degrees of freedom.
- A curved-channel finite-element extension with independent pilot directions: 240
  independently seeded data pairs, 720 scenario/budget/replicate settings, 10 methods.
- Same-budget pooled estimators and fixed-sample mesh-refinement comparisons.
- An independent conductance-network check of the integral solver, perturbation checks,
  and reference-grid refinement.
- An English LaTeX manuscript, verified bibliography, and explicit AI-use disclosure.

No atomistic trajectory, experimental binding data, trained neural potential, learned
reaction coordinate, or drug-discovery success is claimed.

## Main result

RMT bulk filtering is helpful under some assumptions but is not a universal improvement.
At d=24 and n=72, MP-bulk reduces isotropic capacity error from 0.0389 to 0.0096, while
simple isotropic pooling reaches 0.0061. In the slow-reactive-mode case, MP-bulk increases
the empirical capacity error from 0.0343 to 0.4512. The useful research message is that
spectral regularization must be assessed against a kinetic observable, not only matrix loss.

Protected MP was added after examining the initial results. It keeps the prescribed
reactive variance unchanged and regularizes the complementary block. Its committor and
capacity equality with the empirical estimator is an algebraic identity in this benchmark,
not a learned prediction or an independently validated improvement in kinetics.

## Files

- `manuscript/main.tex`, `references.bib`, `main.bbl`: paper source and bibliography.
- `manuscript/main.pdf`: compiled manuscript.
- `src/benchmark.py`: generates every model observation and estimator result.
- `src/analyze.py`: generates the tables, plots, and bootstrap comparisons.
- `src/verify.py`: independently checks the solver and perturbation identities.
- `src/audit.py`: consistency, paired-sample, and reference checks.
- `results/replicates.csv`: 14,400 rows, one per method and data replicate.
- `results/initial_five_method_replicates.csv`: retained first-run records.
- `results/summary.csv`: all reported metrics and bootstrap intervals.
- `results/paired_comparisons.csv`: MP-bulk minus each comparator, with paired intervals.
- `results/profiles.json`: fixed-seed profiles and average mobilities.
- `results/run_config.json`: parameters, package versions, and random stream design.
- `results/verification.json`: mathematical and discretization checks.
- `notes/ARXIV_SUBMISSION_NOTES.md`: policy references and submission preparation.
- `notes/REFERENCE_AUDIT.md`: verified source links and limits of the literature check.
- `notes/RESEARCH_LOG.md`: honest record of initial design and exploratory extension.
- `notes/OZET_TR.md`: Turkish scientific interpretation and next-stage requirements.

## Reproduce

The recorded environment is Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0,
scikit-learn 1.8.0. Exact version pins, including Matplotlib, are in `requirements.txt`.
From the project directory:

```bash
python -m pip install -r requirements.txt
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python src/benchmark.py
OPENBLAS_NUM_THREADS=1 python src/verify.py
OPENBLAS_NUM_THREADS=1 python src/analyze.py
OPENBLAS_NUM_THREADS=1 python src/learned_direction.py
OPENBLAS_NUM_THREADS=1 python src/verify_learned.py
OPENBLAS_NUM_THREADS=1 python src/refine_learned.py
OPENBLAS_NUM_THREADS=1 python src/analyze_learned.py
python src/audit.py
python src/build_paper.py
```

The final command requires `latexmk`, pdfLaTeX, BibTeX, and standard TeX Live packages.
It copies generated PDF figures into `manuscript/figures` before compilation.
The reported 120-replicate study runs in about 80 seconds for simulation in the preparation
environment; runtime depends on hardware. Analysis and compilation are additional.
Numerical agreement, not byte-identical PDFs, is the reproduction target.

Simulation and verification scripts record fixed random seeds in code and configuration.
The entire raw Gaussian array is regenerated from seeds rather than stored. Results include
all replicates. There was no outcome-based seed or scenario selection.

## Submission packaging

`arxiv_source.zip` is a separate minimal LaTeX source bundle included with the deliverables.
Its root contains `main.tex`, the included theory/experiment/table `.tex` files,
`main.bbl`, `references.bib`, and `figures/`.
The source bundle is prepared for LaTeX compilation. Submission, category selection,
endorsement where applicable, and license selection remain with the author.

No license is selected on behalf of the author. External source publications are cited,
not redistributed. The supplied figures are programmatic plots of the supplied results.

## Independent-pilot extension

`notes/EXTENSION_DESIGN.md` records the prospective internal design and resolution
amendment. The primary mesh is 40 by 40 squares (3,200 triangles). The earlier mesh-20
run is retained as `results/learned_mesh20_initial_*`. The population committor uses
the same discrete energy as the estimators; this isolates sampling error on that mesh.
Reference grids up to 160 and a fixed five-replicate subset at grid 80 assess resolution.

- `src/learned_direction.py`: independent Gaussian sampling, FE solves, Schur estimators.
- `src/verify_learned.py`: manufactured solution, dense solve, rotation, invariance,
  angular leakage bounds, residual-Wishart trace check, reference mesh convergence.
- `src/refine_learned.py`: first five replicates per case at n=24, m=96 on grid 80.
- `src/analyze_learned.py`: paired bootstrap analysis, figures, table and record audit.
- `results/learned_replicates.csv`: all 7,200 primary estimator records; blank certificate
  and positivity fields mean not evaluated for non-Schur methods, not numerical zero.
- `results/learned_summary.csv`, `learned_paired.csv`: every budget and comparison.
- `results/learned_verification.json`, `learned_audit.json`: implementation checks.
- `results/learned_refinement.csv`, `learned_refinement_summary.json`: refinement subset.

The rank-one direction is estimated by a pilot empirical-covariance FE solve, not a
neural network. The active two-dimensional plane and equilibrium density are known.
The independent pilot is separate from the evaluation covariance; nested pilot sizes
share their initial samples. The oracle Schur method uses the evaluation baseline's
own gradient only as an algebraic check and has no independent-pilot Wishart guarantee.

At n=24 and m=96 in the slow case, learned Schur MP reduces matrix error from 0.7192 to
0.4725 while giving capacity error 0.0899 (empirical 0.0941; unprotected MP 0.7635).
Pooled empirical covariance using all 120 observations yields 0.0414 and is better.
Conditional scalar pooling also matches the protected MP result. Thus the theorem is
about preserving a baseline kinetic observable, not universal optimality or drug-design
performance. Primary refinement sensitivity is largest in the slow case (reference
capacity difference 2.57% between grids 40 and 160).

The new primary run took approximately 191 seconds in the preparation environment with
one BLAS thread; machine-dependent analysis, verification and compilation are additional.
