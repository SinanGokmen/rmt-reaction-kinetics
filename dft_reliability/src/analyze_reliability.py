"""Summarize budgeted detection; scenario ranges are not confidence intervals."""
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from data_utils import ROOT,load_dataset
from reliability_benchmark import descriptors

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,
                     'axes.spines.right':False,'pdf.fonttype':42,'savefig.bbox':'tight'})
OUT=ROOT/'manuscript'/'figures';OUT.mkdir(parents=True,exist_ok=True)

def run():
    m=pd.read_csv(ROOT/'results'/'reliability_metrics.csv')
    primary=m[(m.acquisition_fraction==.1)&(m.endpoint=='worst_decile')]
    summary=primary.groupby(['dataset','comparison','method']).agg(
        recall_mean=('recall','mean'),recall_min=('recall','min'),recall_max=('recall','max'),
        impact_mean=('impact_fraction','mean'),total_fraction_mean=('total_fraction','mean')).reset_index()
    summary.to_csv(ROOT/'results'/'reliability_primary_summary.csv',index=False)
    table=[]
    policies=[('total_budget','random','Random, direct'),('total_budget','net_force','Net force, direct'),
              ('total_budget','rigid_force','Force/torque, direct'),('total_budget','force_magnitude','Force magnitude, direct'),
              ('total_budget','geometry_novelty','Geometry novelty, direct'),('shared_seed','trees_log','Trees, log error'),
              ('shared_seed','trees_raw','Trees, raw error'),('shared_seed','trees_physics','Trees, physical only'),
              ('shared_seed','ridge','Ridge'),('shared_seed','mp_ridge','MP-pooled ridge')]
    for comp,method,label in policies:
        rows=[]
        for d in ['aimnet2','transition1x']:
            v=summary[(summary.dataset==d)&(summary.comparison==comp)&(summary.method==method)].iloc[0]
            rows.append(f"{100*v.recall_mean:.1f} [{100*v.recall_min:.0f}, {100*v.recall_max:.0f}]")
        table.append(label+' & '+' & '.join(rows)+r' \\')
    (ROOT/'manuscript'/'reliability_table.tex').write_text(
        '\\begin{tabular}{lrr}\n\\toprule\nPolicy & AIMNet2 (\\%) & Transition1x (\\%)\\\\\n\\midrule\n'
        +'\n'.join(table)+'\n\\bottomrule\n\\end{tabular}\n')

    fig,axes=plt.subplots(1,2,figsize=(7.1,3.1))
    for ax,d,title in zip(axes,['aimnet2','transition1x'],['AIMNet2','Transition1x']):
        records=load_dataset(d);x=[];y=[]
        for r in records:
            _,s=descriptors(r);x.append(1000*s['rigid_force']);y.append(1000*np.sqrt(np.mean((r['F']-r['Fref'])**2)))
        ax.scatter(x,y,s=9,alpha=.42,color='#336b88',edgecolors='none',rasterized=True)
        ax.set_xscale('log');ax.set_yscale('log');ax.set_title(title)
        ax.set_xlabel('Rigid-component RMS (meV/Angstrom)')
        if d=='transition1x':
            j=int(np.argmax(y));ax.scatter([x[j]],[y[j]],color='#bd463a',s=27,zorder=4)
            ax.annotate('Largest discrepancy',xy=(x[j],y[j]),xytext=(.09,.73),textcoords='axes fraction',fontsize=8,
                        arrowprops=dict(arrowstyle='-',color='#bd463a'),color='#9b382f')
        ax.grid(alpha=.15,which='major')
    axes[0].set_ylabel('Paired force RMSE (meV/Angstrom)')
    fig.tight_layout();fig.savefig(OUT/'reliability_scores.pdf');plt.close(fig)

    plotpol=[('total_budget','random','Uniform, direct','#8b8b8b','--'),
             ('total_budget','rigid_force','Force/torque, direct','#26715a','-'),
             ('total_budget','net_force','Net force, direct','#91a76b',':'),
             ('shared_seed','trees_log','Trees + seed cost','#376f9c','-'),
             ('shared_seed','ridge','Ridge + seed cost','#9674a7','--'),
             ('shared_seed','mp_ridge','MP ridge + seed cost','#c4793a','-')]
    fig,axes=plt.subplots(1,2,figsize=(7.1,3.55),sharey=True)
    for ax,d,title in zip(axes,['aimnet2','transition1x'],['AIMNet2','Transition1x']):
        for comp,method,label,color,style in plotpol:
            x=m[(m.dataset==d)&(m.endpoint=='worst_decile')&(m.comparison==comp)&(m.method==method)]
            v=x.groupby('acquisition_fraction')[['recall','total_fraction']].mean()
            ax.plot(100*v.total_fraction,100*v.recall,label=label,color=color,ls=style,lw=1.6,marker='o',ms=3)
        ax.set_title(title);ax.set_xlabel('Total reference calculations (% of dataset)');ax.set_ylim(0,103);ax.grid(alpha=.18)
    axes[0].set_ylabel('Worst-decile frames found (%)')
    h,l=axes[0].get_legend_handles_labels();fig.legend(h,l,loc='lower center',ncol=3,frameon=False,fontsize=8)
    fig.tight_layout(rect=[0,.18,1,1]);fig.savefig(OUT/'reliability_budget.pdf');plt.close(fig)

    # Error-count and squared-impact objectives lead to different assessments.
    pol=[('total_budget','net_force','Net force'),('total_budget','rigid_force','Force/torque'),
         ('total_budget','force_magnitude','Force size'),('shared_seed','trees_log','Trees'),('shared_seed','mp_ridge','MP ridge')]
    fig,axes=plt.subplots(1,2,figsize=(7.1,3.0),sharey=True)
    for ax,d,title in zip(axes,['aimnet2','transition1x'],['AIMNet2','Transition1x']):
        vals=[];impact=[]
        for comp,method,label in pol:
            v=summary[(summary.dataset==d)&(summary.comparison==comp)&(summary.method==method)].iloc[0]
            vals.append(100*v.recall_mean);impact.append(100*v.impact_mean)
        t=np.arange(len(pol));ax.bar(t-.18,vals,.36,color='#376f9c',label='Worst-decile recall')
        ax.bar(t+.18,impact,.36,color='#c4793a',label='Squared discrepancy captured')
        ax.set_xticks(t,[p[2] for p in pol],rotation=25,ha='right');ax.set_title(title);ax.set_ylim(0,105)
    axes[0].set_ylabel('Fraction (%)');h,l=axes[0].get_legend_handles_labels()
    fig.legend(h,l,loc='lower center',ncol=2,frameon=False,fontsize=8)
    fig.tight_layout(rect=[0,.1,1,1]);fig.savefig(OUT/'reliability_objectives.pdf');plt.close(fig)
    print(summary.to_string(index=False))

if __name__=='__main__':run()
