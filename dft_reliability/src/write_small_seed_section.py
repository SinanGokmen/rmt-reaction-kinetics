"""Generate manuscript extension from saved summary, without manually copied results."""
import pandas as pd
from data_utils import ROOT
s=pd.read_csv(ROOT/'results/small_seed_summary.csv',dtype={'seed_label':str})
def recall(d,m,n):
 r=s[(s.dataset==d)&(s.method==m)&(s.seed_label==n)].iloc[0]
 return f'{100*r.recall:.1f}'
text=r'''\subsection{How many references should train the auditor?}
An exploratory extension fixes the total cost at 280 references per 1,000-record
sample. It uses the same five formula folds but draws nested random prefixes of
10, 20, 50 or 100 records from each designated seed fold, alongside the full fold
(mean size 200). Five deterministic permutations are used per fold. The remaining
four folds form a fixed audit pool, independent of prefix size. Unused seed-fold
records are excluded from this pool. All seeds contain at least three formulas;
the original grouped penalty selection and tree settings are retained.

A learned policy uses $m$ references for training and $280-m$ for acquisitions.
Direct policies spend all 280 on the same pool. Only pool discoveries count,
with positives defined as the worst $\lceil0.1|\mathcal U|\rceil$ pool records.
This transfer-to-unseen-formulas endpoint intentionally differs from the earlier
whole-sample recall, which credited seed discoveries. Repeats are averaged within
fold before summarizing the five overlapping scenarios; they are not independent
confirmation datasets. The extension protocol was recorded after examining the
primary results, and no fresh data were introduced.

\begin{figure}[t]
\centering\includegraphics[width=\linewidth]{figures/small_seed_budget.pdf}
\caption{Reference allocation at a fixed total budget of 280. Increasing seed
count leaves fewer acquisitions in the fixed held-out pool. Points average five
seed permutations within each of five formula scenarios. The full-fold point
has mean size 200; its actual size varies by scenario. Direct-policy lines use
280 pool acquisitions throughout.}
\label{fig:smallseed}
\end{figure}

'''
text+=f"With 50 seed references, log-error trees recover {recall('aimnet2','trees_log','50')}\\%\nof the pool's worst decile on AIMNet2 and {recall('transition1x','trees_log','50')}\\% on\nTransition1x. Using the entire seed fold gives {recall('aimnet2','trees_log','full')}\\% and\n{recall('transition1x','trees_log','full')}\\%, respectively (Figure~\\ref{{fig:smallseed}}).\nAt 50 references, ordinary ridge gives {recall('aimnet2','ridge','50')}\\% and\n{recall('transition1x','ridge','50')}\\%, while MP-pooled ridge gives\n{recall('aimnet2','mp_ridge','50')}\\% and {recall('transition1x','mp_ridge','50')}\\%.\nDirect force/torque screening gives {recall('aimnet2','rigid_force','50')}\\% and\n{recall('transition1x','rigid_force','50')}\\% on these pools.\n\n"
text+=r'''These curves measure the combined effects of predictor quality and reference
allocation, not prediction error at equal acquisition counts. More training
references need not produce more discoveries under a fixed total budget. The
comparison does not establish a universal optimal seed size, an RMT advantage,
or transfer from these molecular samples to a substantially larger database.
'''
(ROOT/'manuscript/small_seed_results.tex').write_text(text)
