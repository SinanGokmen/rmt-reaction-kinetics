# Exploratory small-seed sensitivity protocol

Recorded 11 September 2026 before fitting this extension, after the original
reliability results were inspected. This is not independent confirmation.

Question: at a fixed total reference count, how much of the budget should be
spent on fitting an auditor for unseen molecular formulas?

Reuse the five formula folds. The audit pool is the four non-seed folds and is
identical across seed sizes within each scenario. Randomly permute records in
the designated seed fold using five fixed seeds, 2026091100+10*fold+repeat.
Use nested prefixes of 10, 20, 50, 100 and all available seed records. Only
prefix references are revealed. Unused seed-fold records are not audit candidates.
No pool formula occurs in a seed fold. Small seeds may contain repeated formulas;
three-fold grouped penalty selection requires at least three seed formulas.
An explicit assertion stops the experiment if this condition is not met; no
split will be silently discarded or replaced.

Total budget is exactly 280 references per 1000-frame sample. A learned method
spends m on seeds and 280-m on pool acquisitions; a direct screen spends all
280 on the same pool. All seed folds have fewer than 280 records. Endpoints
count only pool discoveries, so training-only seeds receive no discovery credit.
This is a held-out-formula transfer task and NOT the earlier whole-sample recall.
Primary positive set: worst ceil(10% of pool size) by paired frame RMSE.
Secondary: fraction of pool squared discrepancy captured. Retain every outlier.

Use the existing fixed ExtraTrees and grouped-tuned ridge/MP-ridge settings,
including the minimum tree leaf size of five even at small sample sizes.
Evaluate net force, rigid force and force magnitude direct screens and the exact
expectation for uniform pool selection. No new policy or tuning from pool labels.
Save per-pool scores, selected indices, seed indices, parameters and all metrics.
Report scenario means/ranges, with repeats averaged within each formula scenario;
no independent-sample confidence interval. Inspect variation in seed composition.

These results will not establish CPU-hour savings, large-dataset scaling, fresh
external validation or universal RMT superiority. The fixed-pool comparison
isolates reference-training expense under formula transfer, and deliberately
uses a different endpoint from the primary whole-sample experiment.
