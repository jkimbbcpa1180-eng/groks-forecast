#!/usr/bin/env python3
"""Chart of illustrative timeline scenarios from decency_scenarios_v2.
ILLUSTRATIVE ONLY: all rates, shocks and event years are guesses."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from decency_scenarios_v2 import TIMELINE_SCENARIOS, EVENTS, HELPFUL_EVENTS, run_timeline

COLORS = ['#2ca02c', '#1f77b4', '#d62728', '#000000', '#ff7f0e', '#9467bd', '#7f7f7f', '#17becf', '#e377c2']
fig, (ax, bx) = plt.subplots(2, 1, figsize=(9, 18),
                             gridspec_kw={'height_ratios': [3.6, 2.4]})
fig.suptitle('Gap to "basic life agreement" (D) by scenario, 2026-2326',
             fontsize=15, weight='bold')
ax.set_title('Illustrative model, all rates are guesses, not a forecast.',
             fontsize=11, style='italic')
marks = {}
for (name, spec), c in zip(TIMELINE_SCENARIOS.items(), COLORS):
    r = run_timeline(spec)
    yr = r['median_agreement_year']
    lab = f"{name}: {yr if yr else 'never'}"
    if yr is None and r['fraction_never_within_horizon'] < 1:
        lab += f" ({(1-r['fraction_never_within_horizon'])*100:.0f}% of paths do)"
    ax.plot(r['years'], r['median'], color=c, lw=2.2, label=lab)
    ax.fill_between(r['years'], r['p10'], r['p90'], color=c, alpha=0.12)
    if yr:
        ax.plot([yr], [0.01], 'o', color=c, ms=8)
    for y, l, _ in spec['events']:
        marks.setdefault((y, l), c)
ax.axhline(0.01, color='green', ls='--', lw=1.5)
ax.text(2150, 0.0068, 'basic life agreement (gap 0.01)', color='green', fontsize=10)
key = []
for i, ((y, l), c) in enumerate(sorted(marks.items()), 1):
    ax.axvline(y, color=c, ls=':', lw=1)
    ax.text(y, 3.6 / (1.35 ** ((i - 1) % 5)), str(i), color='white', fontsize=8,
            ha='center', va='center', weight='bold',
            bbox=dict(boxstyle='circle,pad=0.2', fc=c, ec='none'))
    key.append(f'{i} {l} ({y})')
ax.text(0.99, 0.99, 'Events:\n' + '\n'.join(key), transform=ax.transAxes,
        ha='right', va='top', fontsize=8,
        bbox=dict(fc='white', ec='#ccc', alpha=0.9))
ax.set_yscale('log'); ax.set_ylim(0.004, 4)
ax.set_xlabel('Year (illustrative)'); ax.set_ylabel('Gap D (log scale; 1 = today)')
ax.legend(title='Scenario: year agreement is reached (median)',
          fontsize=9, title_fontsize=9, loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=1)
ax.grid(alpha=0.3)

allev = [(e[0], e[1], e[2], '#4c72b0') for e in EVENTS] + \
        [(f'+ {h[1]} (~{h[0]})', h[2], h[3], '#2ca02c') for h in HELPFUL_EVENTS]
allev = allev[::-1]
names = [e[0] for e in allev]; tps = [e[1] for e in allev]; levs = [e[2] for e in allev]
bars = bx.barh(range(len(names)), tps, color=[e[3] for e in allev])
for i, (t, lv) in enumerate(zip(tps, levs)):
    bx.text(t + 0.01, i, f'{t:.0%}  (moves {lv})', va='center', fontsize=9)
bx.set_yticks(range(len(names)))
bx.set_yticklabels([n if len(n) < 42 else n[:40] + '...' for n in names], fontsize=9)
bx.set_xlim(0, 1.15)
bx.set_title('Blue: must happen. Green (+): helpful speed-ups. tp = JUDGMENT, not data',
             fontsize=11)
bx.set_xlabel('tp (judgment)')
fig.text(0.5, 0.005, 'D(t+1) = (1 - r) D(t) + s(t). Lines = median of 500 paths; '
         'bands = 10-90%. Reunification cost source: NABO 2016 via Hankyoreh.',
         ha='center', fontsize=8)
fig.tight_layout(rect=[0, 0.015, 1, 0.97])
fig.savefig('decency_scenarios_timeline.png', dpi=130)
print('saved')
