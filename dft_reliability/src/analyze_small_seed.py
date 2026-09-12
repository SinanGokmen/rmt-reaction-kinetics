"""Summarize nested seed experiments without treating repeats as independent data."""
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from data_utils import ROOT
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})

def run():
 m=pd.read_csv(ROOT/'results/small_seed_metrics.csv',dtype={'seed_label':str})
 f=m.groupby(['dataset','fold','seed_label','method'],as_index=False).agg(recall=('recall','mean'),impact=('impact','mean'),seed_count=('seed_count','mean'))
 summary=f.groupby(['dataset','seed_label','method'],as_index=False).agg(recall=('recall','mean'),recall_min=('recall','min'),recall_max=('recall','max'),impact=('impact','mean'),seed_count=('seed_count','mean'))
 summary.to_csv(ROOT/'results/small_seed_summary.csv',index=False)
 methods=[('trees_log','Trees','#376f9c'),('ridge','Ridge','#9674a7'),('mp_ridge','MP ridge','#c4793a')]
 fig,axs=plt.subplots(1,2,figsize=(7.1,3.2),sharey=True)
 for ax,d in zip(axs,['aimnet2','transition1x']):
  for method,label,color in methods:
   v=summary[(summary.dataset==d)&(summary.method==method)].sort_values('seed_count')
   ax.plot(v.seed_count,100*v.recall,'o-',label=label,color=color,lw=1.6,ms=3)
  for method,label,color in [('rigid_force','Direct force/torque','#26715a'),('random','Uniform, direct','#888888')]:
   v=summary[(summary.dataset==d)&(summary.method==method)].iloc[0]
   ax.axhline(100*v.recall,label=label,color=color,ls='--',lw=1.3)
  ax.set_title('AIMNet2' if d=='aimnet2' else 'Transition1x');ax.set_xlabel('Seed references (mean count)');ax.set_ylim(0,103);ax.grid(alpha=.15)
 axs[0].set_ylabel('Held-out-pool worst-decile recall (%)')
 h,l=axs[0].get_legend_handles_labels();fig.legend(h,l,loc='lower center',ncol=3,frameon=False,fontsize=8)
 fig.tight_layout(rect=[0,.18,1,1]);fig.savefig(ROOT/'manuscript/figures/small_seed_budget.pdf',bbox_inches='tight');plt.close(fig)
 print(summary[summary.method.isin(['trees_log','ridge','mp_ridge','rigid_force','random'])].to_string(index=False))

if __name__=='__main__':run()
