#!/usr/bin/env python3
"""Real Mode: an illustrative model of progress toward universal decency.

This is NOT a forecast of nirvana, an afterlife model, or calibrated TP.
The gap index is hypothetical, not a measured moral score. A small aggregate
gap cannot establish that every person is safe or treated fairly.

Model: D[t+1] = (1-r[t])*D[t] + s[t], D[0] = 1 by normalization.
D may exceed 1: conditions can become worse than the starting point.
Setbacks add harm; catastrophe is never assumed to purify society.

Examples:
  python3 realmode_future_decency.py
  python3 realmode_future_decency.py --rate 0.02 --years 500 --runs 10000
  python3 realmode_future_decency.py --setback-prob 0.02 --setback-size 0.03
  python3 realmode_future_decency.py --volatility 0.01 --hold-years 20
  python3 realmode_future_decency.py --self-test

Standard library only. JSON is printed to stdout. All parameter defaults
are illustrative assumptions. No empirical calibration has been performed.
Wealth concentration is NOT assigned an invented causal coefficient. Its
effect would need to be estimated before mapping it into rates or setbacks.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import unittest
from dataclasses import asdict, dataclass
from statistics import mean


@dataclass(frozen=True)
class Assumptions:
    rate: float = 0.02
    volatility: float = 0.0
    setback_prob: float = 0.0
    setback_size: float = 0.0
    threshold: float = 0.01
    years: int = 500
    runs: int = 2000
    hold_years: int = 10
    seed: int = 20261013

    def validate(self) -> None:
        for field in ('rate', 'volatility', 'setback_prob',
                      'setback_size', 'threshold'):
            if not math.isfinite(getattr(self, field)):
                raise ValueError(f'{field} must be finite')
        if not 0 <= self.rate <= 1:
            raise ValueError('rate must be between 0 and 1')
        if self.volatility < 0 or self.setback_size < 0:
            raise ValueError('volatility and setback size must be nonnegative')
        if not 0 <= self.setback_prob <= 1:
            raise ValueError('setback probability must be between 0 and 1')
        if not 0 < self.threshold < 1:
            raise ValueError('threshold must be strictly between 0 and 1')
        if self.years < 1 or self.runs < 1:
            raise ValueError('years and runs must be positive')
        if not 1 <= self.hold_years <= self.years:
            raise ValueError('hold years must be between 1 and years')


def deterministic_years(rate: float, threshold: float = 0.01) -> int | None:
    """First year below threshold without shocks; None denotes never.

    For exact zero and 0 < rate < 1, the mathematical recurrence never
    reaches zero in finite time. Floating-point underflow is not evidence
    that the mathematical sequence reaches zero.
    """
    if not (math.isfinite(rate) and math.isfinite(threshold)):
        raise ValueError('inputs must be finite')
    if not 0 <= rate <= 1 or not 0 <= threshold < 1:
        raise ValueError('rate in [0,1] and threshold in [0,1) required')
    if rate == 1:
        return 1
    if rate == 0 or threshold == 0:
        return None
    log_decay = math.log1p(-rate)
    log_target = math.log(threshold)
    n = max(1, math.ceil(log_target / log_decay))
    # Correct possible round-off at integer boundaries using logs.
    while n > 1 and (n - 1) * log_decay <= log_target:
        n -= 1
    while n * log_decay > log_target:
        n += 1
    return n


def wilson_interval(successes: int, total: int) -> list[float]:
    """95% binomial interval for simulation sampling error ONLY."""
    p = successes / total
    z = 1.959963984540054
    den = 1 + z * z / total
    center = (p + z * z / (2 * total)) / den
    half = z * math.sqrt(p * (1 - p) / total + z*z/(4*total*total)) / den
    return [max(0.0, center - half), min(1.0, center + half)]


def simulate(a: Assumptions) -> dict:
    a.validate()
    rng = random.Random(a.seed)
    hits: list[int] = []
    final_gaps: list[float] = []
    still_below = 0
    for _ in range(a.runs):
        gap = 1.0
        streak = 0
        hit = None
        for year in range(1, a.years + 1):
            # Independent annual draws are a simplifying assumption.
            # Clipping changes the mean when volatility is appreciable.
            rate = (a.rate if a.volatility == 0 else
                    min(1.0, max(0.0, rng.gauss(a.rate, a.volatility))))
            shock = (a.setback_size if
                     rng.random() < a.setback_prob else 0.0)
            gap = (1.0 - rate) * gap + shock
            streak = streak + 1 if gap <= a.threshold else 0
            if hit is None and streak >= a.hold_years:
                hit = year
            # Continue after hitting: later relapse remains possible.
        if hit is not None:
            hits.append(hit)
        still_below += streak >= a.hold_years
        final_gaps.append(gap)
    ordered = sorted(hits)

    def percentile(q: float) -> int | None:
        return ordered[max(0, math.ceil(q * len(ordered)) - 1)] if ordered else None

    # For fixed rate and independent additive shocks, this is the
    # long-run EXPECTED gap, not a bound on individual paths.
    expected_floor = (a.setback_prob * a.setback_size / a.rate
                      if a.volatility == 0 and a.rate > 0 else None)
    return {
        'status': 'ILLUSTRATIVE_SCENARIO_NOT_EMPIRICALLY_CALIBRATED',
        'assumptions': asdict(a),
        'event': f'gap <= {a.threshold} for {a.hold_years} consecutive years '
                 f'at least once by year {a.years}',
        'conditional_simulation_success_fraction': len(hits) / a.runs,
        'simulation_sampling_interval_95_only': wilson_interval(len(hits), a.runs),
        'successful_paths': len(hits),
        'paths_not_observed_to_succeed_within_horizon': a.runs - len(hits),
        'completion_year_quantiles_successful_paths_only': {
            'p10': percentile(0.10), 'p50': percentile(0.50), 'p90': percentile(0.90)},
        'fraction_meeting_hold_condition_at_final_year': still_below / a.runs,
        'mean_final_gap': mean(final_gaps),
        'fixed_rate_long_run_expected_gap': expected_floor,
        'no_setback_first_threshold_year': deterministic_years(a.rate, a.threshold),
        'real_world_tp': None,
        'real_world_tp_reason': 'No measured index, fitted rates, or out-of-sample validation.',
        'limitations': [
            'Success concerns an aggregate proxy, not every soul or permanent decency.',
            'Unsuccessful paths are censored at the horizon, not proven impossible.',
            'Quantiles exclude censored paths and are not unconditional forecasts.',
            'Sampling intervals exclude parameter uncertainty and model error.',
            'No compulsory catastrophe or morally cleansing disaster is modeled.',
            'No birth, migration, interdependence, or political feedback model is fitted.',
            'Default constant-rate scenario is deterministic despite repeated runs.',
        ],
    }


class Tests(unittest.TestCase):
    def test_timelines(self):
        self.assertEqual([deterministic_years(r) for r in (0.05, 0.02, 0.005)],
                         [90, 228, 919])

    def test_boundaries(self):
        self.assertIsNone(deterministic_years(0.02, 0))
        self.assertIsNone(deterministic_years(0))
        self.assertEqual(deterministic_years(1, 0), 1)
        self.assertEqual(deterministic_years(0.5, 0.25), 2)

    def test_hold_and_horizon(self):
        a = Assumptions(rate=1, years=5, runs=3, hold_years=3)
        out = simulate(a)
        self.assertEqual(out['successful_paths'], 3)
        self.assertEqual(out['completion_year_quantiles_successful_paths_only']['p50'], 3)
        self.assertEqual(simulate(Assumptions(rate=0, years=10, runs=3))['successful_paths'], 0)

    def test_seed(self):
        a = Assumptions(years=30, runs=20, volatility=0.01,
                        setback_prob=0.2, setback_size=0.1)
        self.assertEqual(simulate(a), simulate(a))

    def test_setbacks(self):
        a = Assumptions(rate=1, setback_prob=1, setback_size=0.1,
                        years=10, runs=2)
        self.assertEqual(simulate(a)['successful_paths'], 0)
        a = Assumptions(rate=0, setback_prob=1, setback_size=0.1,
                        years=10, runs=2)
        self.assertGreater(simulate(a)['mean_final_gap'], 1)

    def test_invalid(self):
        for a in (Assumptions(rate=-1), Assumptions(rate=float('nan')),
                  Assumptions(threshold=0), Assumptions(hold_years=501)):
            with self.assertRaises(ValueError):
                a.validate()


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    for name in ('rate', 'volatility', 'setback_prob', 'setback_size', 'threshold'):
        p.add_argument('--' + name.replace('_', '-'), type=float,
                       default=getattr(Assumptions(), name))
    for name in ('years', 'runs', 'hold_years', 'seed'):
        p.add_argument('--' + name.replace('_', '-'), type=int,
                       default=getattr(Assumptions(), name))
    p.add_argument('--self-test', action='store_true')
    args = vars(p.parse_args())
    if args.pop('self_test'):
        result = unittest.TextTestRunner(verbosity=2).run(
            unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
        raise SystemExit(0 if result.wasSuccessful() else 1)
    try:
        output = simulate(Assumptions(**args))
    except ValueError as e:
        p.error(str(e))
    print(json.dumps(output, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
