"""Generate publication figures only from stored computed results."""
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from data_utils import ROOT

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,
                     'axes.spines.right':False,'pdf.fonttype':42,'savefig.bbox':'tight'})
OUT=ROOT/'manuscript'/'figures';OUT.mkdir(parents=True,exist_ok=True)
df=pd.read_csv(ROOT/'results'/'denoising_oof.csv')
methods=['raw','translation','rigid','element_weighted','ridge','truncate','mp_bulk']
labels=['Raw','Translation','Force + torque','Element weighted','Ridge correction','Spectral truncation','MP bulk heuristic']
colors=['#7a8594','#97abb8','#547a90','#246956','#498fb3','#9b89b3','#c36b39']
fig,axes=plt.subplots(1,2,figsize=(7.2,3.35))
for ax,name,title in zip(axes,['aimnet2','transition1x'],['AIMNet2','Transition1x']):
    vals=[]
    for m in methods:
        a=df[(df.dataset==name)&(df.method==m)]
        vals.append(1000*np.sqrt(a.sse.sum()/a.n_components.sum()))
    ax.barh(np.arange(7),vals,color=colors,height=.7)
    ax.set_yticks(np.arange(7),labels if name=='aimnet2' else [])
    ax.invert_yaxis();ax.set_title(title);ax.set_xlabel('Force RMSE (meV/Angstrom)')
    ax.set_xlim(0,max(vals)*1.2)
    for i,v in enumerate(vals):ax.text(v+max(vals)*.015,i,f'{v:.3f}',va='center',fontsize=8)
fig.tight_layout();fig.savefig(OUT/'real_dft_comparison.pdf');plt.close(fig)

synthetic=pd.read_csv(ROOT/'results'/'synthetic_covariance.csv')
fig,axes=plt.subplots(1,3,figsize=(7.2,2.85),sharex=True)
styles={'projection':('#7a8594','--','Orthogonal'), 'empirical':('#b84f52','-','Empirical'),
        'oas':('#246956','-','OAS'),'spiked_known_floor':('#c36b39','-','Spiked, known floor'),
        'oracle':('#212d3d',':','Population oracle')}
for ax,case,title in zip(axes,['isotropic','cross_spike','tangent_spike'],['No correlation','Cross-subspace spike','Tangent-only spike']):
    for method,(color,style,label) in styles.items():
        s=synthetic[(synthetic.case==case)&(synthetic.method==method)].groupby('n').tangent_mse
        avg=s.mean();se=s.std()/np.sqrt(s.count())
        ax.plot(avg.index,avg,color=color,ls=style,lw=1.5,label=label)
        ax.fill_between(avg.index,avg-1.96*se,avg+1.96*se,color=color,alpha=.10,lw=0)
    ax.set_xscale('log',base=2);ax.set_xticks([16,32,64,128],[16,32,64,128]);ax.set_title(title,fontsize=9)
    ax.set_xlabel('Calibration samples')
axes[0].set_ylabel('Expected tangent MSE / component')
handles,labs=axes[0].get_legend_handles_labels();fig.legend(handles,labs,loc='lower center',ncol=3,frameon=False,fontsize=8)
fig.tight_layout(rect=[0,.20,1,1]);fig.savefig(OUT/'synthetic_risk.pdf');plt.close(fig)

# Numeric tables used directly in the manuscript.
summary=json.loads((ROOT/'results'/'denoising_summary.json').read_text())
lookup={(r['dataset'],r['method']):r for r in summary}
lines=[]
for m,label in zip(methods,labels):
    a=lookup['aimnet2',m];t=lookup['transition1x',m]
    lines.append(f"{label} & {a['rmse_mev_A']:.4f} & {t['rmse_mev_A']:.4f} & {a['median_frame_rmse_mev_A']:.4f} & {t['median_frame_rmse_mev_A']:.4f} \\\\")
(ROOT/'manuscript'/'results_table.tex').write_text(
    '\\begin{tabular}{lrrrr}\n\\toprule\n'
    '&\\multicolumn{2}{c}{Pooled force RMSE}&\\multicolumn{2}{c}{Median frame RMSE}\\\\\n'
    'Method&AIMNet2&Transition1x&AIMNet2&Transition1x\\\\\n\\midrule\n'
    +'\n'.join(lines)+'\n\\bottomrule\n\\end{tabular}\n')
print('Generated two figures and numeric table.')
