# Budgeted DFT reliability audit — protocol, 11 September 2026

Recorded after the earlier denoising pilot and before fitting the reliability
predictors. This is not an external preregistration or a fresh independent dataset.

Question: Can cheap descriptors of an existing DFT result prioritize expensive
reference recalculations better than random choice and elementary consistency
scores, after charging all training references to the audit budget?

Data: same immutable AIMNet2 and Transition1x paired samples, 1000 frames each.
Original force, geometry, composition and charge are predictors; neither the
tight force nor tight energy enters descriptors. Target is frame Cartesian force
RMSE relative to tight DFT. This is numerical/protocol reliability at the same
nominal level of theory, not an estimate of error against exact quantum mechanics.
ANI-1x/SPICE remain excluded because comparison conventions are unresolved.

Split: reuse five deterministic molecular-formula folds. In each of five scenarios,
ONE fold supplies the seed reference calculations; the other four are the unseen
audit pool. Thus every target prediction is made by a model that has not seen any
reference with the same molecular formula. Scenarios overlap and are not five
independent datasets. Actual seed counts must be reported.

Acquisition budgets: select 1%, 2%, 5%, 10%, 20%, 30%, 50% of the unseen pool,
rounding upward. Primary budget is 10%. Total reference count is seed count plus
selected count. All seed calculations count as already audited. Also report the
conditional acquisition result with shared seeds, but never call that an overall
cost saving without the total-budget comparison.

Seed-free policies: random selection (exact expected recall), net-force-per-atom
score, rigid-component RMS (force plus torque), raw-force RMS, and geometry-distance
novelty (standardized distance from descriptor median). Compare both on the unseen
pool and on the FULL original dataset at the learned method's TOTAL budget.

Learning policies: ExtraTrees regressors with fixed 256 trees, min_samples_leaf=5,
max_features=1.0, one on log force RMSE and one on untransformed force RMSE; ordinary
ridge and an MP-inspired spectral bulk-pooled ridge on the same standardized cheap
descriptors and log target. Ridge strength is chosen from 1e-4,1e-2,1,100 using
grouped three-fold validation within the seed set, then refitted on all seeds.
The spectral variant pools Gram eigenvalues below (1+sqrt(p/m))^2 to their mean,
then adds the selected ridge floor. This is a descriptor-correlation heuristic;
it is NOT a validated physical-noise decomposition. Include a physical-only
ExtraTrees ablation using net-force and rigid-component scores.

Descriptors are fixed before test scoring: eight element fractions, atom count,
charge, invariant summaries of pair distances, radius, original force magnitudes,
net force, rotation residual and rigid residual. Detailed code is authoritative.
No external ensemble prediction or SCF metadata is available in these files.

Endpoints: primary recall of the dataset's worst 10% frames ranked by reference
RMSE; secondary recall above 5, 10, 25 meV/Angstrom and fraction of total squared
Cartesian discrepancy audited. The top-decile definition uses reference values
only to define evaluation truth, never to construct scores. Report ties explicitly.
Primary recall means seed-plus-selected frames found, divided by all bad frames.
Report every scenario, mean and range; do not interpret overlap as independent
replication. No significance test based on five independent-fold assumptions.

Theory: (1) constraint violations bound only one part of the force error;
(2) without assumptions, symmetry-valid force errors are unidentifiable from
constraint checks; (3) optimal equal-cost acquisition selects largest conditional
error probabilities for count utility, or expected squared error for impact utility.
Ranking objective and error-magnitude regression are distinct. RMT must improve
budgeted detection over baselines to earn a positive applied claim.

The manuscript will report all outcomes and describe scalability as a proposed
workflow, not as an experiment on hundreds of thousands of configurations.
No material-discovery ranking, binding affinity or trained MLIP improvement is
claimed without the corresponding data and experiments.
