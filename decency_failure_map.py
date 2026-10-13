#!/usr/bin/env python3
"""Failure map: where progress r*D meets average harm p*s. ILLUSTRATIVE."""
import json, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from decency_scenarios_v2 import TIMELINE_SCENARIOS, WORLD_TP, final_params

rep = json.load(open('demo_output_timeline_v2.json'))['scenarios']
fig, (ax, bx) = plt.subplots(2, 1, figsize=(9, 15), gridspec_kw={'height_ratios': [1, 1.1]})
fig.suptitle('Why most futures stall: the failure map', fontsize=16, weight='bold')
fig.text(0.5, 0.955, 'Illustrative, tp = judgment, not data', ha='center', style='italic', fontsize=12)

D = np.logspace(-4, 0, 300)
pick = [('Status quo', '#7f7f7f'), ('Wealth concentration (Country of Kings)', '#9467bd'),
        ('Climate failure', '#ff7f0e'), ('Best path (all helpful events)', '#e377c2')]
for name, c in pick:
    f = final_params(TIMELINE_SCENARIOS[name])
    ax.plot(D, f['r'] * D, color=c, lw=2, ls=(0, (6, 3)) if name == 'Status quo' else '-')
    ax.axhline(f['p'] * f['s'], color=c, ls='--', lw=1.3)
    ax.plot([f['D_star']], [f['p'] * f['s']], 'o', color=c, ms=10, mec='k')
    short = name.split(' (')[0]
    ax.annotate(f"{short}\nD* = {f['D_star']:.3g}", (f['D_star'], f['p'] * f['s']),
                xytext={'Status quo': (-95, 12), 'Wealth concentration (Country of Kings)': (10, -28)}.get(name, (8, 6)), textcoords='offset points', fontsize=9, color=c, weight='bold')
ax.axvline(0.01, color='green', lw=2)
ax.text(0.0105, 1.2e-6, 'agreement\nline 0.01', color='green', fontsize=9)
ax.axvspan(0.01, 1, color='red', alpha=0.05)
ax.text(0.3, 2e-6, 'D* here =\nfails forever\n(on average)', color='darkred', fontsize=9, ha='center')
ax.set_xscale('log'); ax.set_yscale('log'); ax.set_ylim(1e-6, 0.1)
ax.set_xlabel('Gap D'); ax.set_ylabel('Per year')
ax.set_title('A. Rising = progress r*D (status quo = climate r), dashed = harm p*s.\n'
             'They cross at the stall point D* = p*s/r (params at 2100)', fontsize=11)
ax.grid(alpha=0.3, which='both')

names = sorted(WORLD_TP, key=lambda n: WORLD_TP[n][0])
tps = [WORLD_TP[n][0] for n in names]
ok = [rep[n]['median_agreement_year'] is not None for n in names]
bx.barh(range(len(names)), tps, color=['#2ca02c' if o else '#d62728' for o in ok])
for i, n in enumerate(names):
    yr = rep[n]['median_agreement_year']
    bx.text(tps[i] + 0.005, i + 0.15, f"{tps[i]:.0%}  {'reaches ' + str(yr) if yr else 'fails'}",
            fontsize=9, weight='bold', va='center')
    bx.text(tps[i] + 0.005, i - 0.25, WORLD_TP[n][1], fontsize=7.5, va='center', color='#333')
bx.set_yticks(range(len(names)))
bx.set_yticklabels([n.replace(' (', '\n(') for n in names], fontsize=9)
bx.set_xlim(0, 1.0)
bx.set_title('B. tp each is the world we actually live in (judgment)\n'
             'green = median path reaches agreement, red = fails', fontsize=11)
bx.set_xlabel('tp (judgment, sums to 1)')
sq = final_params(TIMELINE_SCENARIOS['Status quo'])['D_star']
fig.text(0.5, 0.012, f'Without change, the status quo stalls at a gap of about {sq/0.01:.0f}x '
         'the goal: harm cancels progress.', ha='center', fontsize=11, weight='bold')
fig.text(0.5, 0.0, 'D* is the AVERAGE stall; noisy paths can dip below 0.01 for a while '
         '(e.g. status quo 21% of runs).', ha='center', fontsize=8)
fig.tight_layout(rect=[0, 0.03, 1, 0.95])
fig.savefig('decency_failure_map.png', dpi=130)
print('saved')
