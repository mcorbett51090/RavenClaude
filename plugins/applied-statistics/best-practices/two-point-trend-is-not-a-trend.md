# A two-point comparison is not a trend — require at least 5 observations before calling a direction

**Status:** Absolute rule
**Domain:** Descriptive statistics / dashboard QA
**Applies to:** `applied-statistics`

---

## Why this exists

"Revenue is up for the second month in a row — we're on an upward trend." Two points define a line. Every two consecutive datapoints on a random walk are "trending." A genuine trend requires enough observations to distinguish a systematic direction from noise: a minimum of 5 observations for any directional claim, and a formal trend test (Mann-Kendall or a simple regression on time) for any claim made to a stakeholder. A dashboard widget that draws a trend line through two points is noise-visualization presented as insight.

## How to apply

**Minimum observation rule:**
- Directional claim ("metric is trending up/down"): minimum 5 observations.
- Trend significant enough to cite to a stakeholder: run a Mann-Kendall test or an OLS regression on time.

```python
from scipy.stats import kendalltau
import numpy as np

def test_trend(series):
    """
    Mann-Kendall trend test.
    Returns tau (direction and magnitude) and p-value.
    """
    n = len(series)
    time = np.arange(n)
    tau, p_value = kendalltau(time, series)
    
    if len(series) < 5:
        print("WARNING: Fewer than 5 observations — trend test unreliable.")
        return None, None
    
    direction = "upward" if tau > 0 else "downward"
    significance = "significant" if p_value < 0.05 else "not significant"
    print(f"Trend: {direction}, tau={tau:.3f}, p={p_value:.3f} ({significance})")
    return tau, p_value

# Usage
tau, p = test_trend([12, 13, 11, 15, 14, 16, 17])
```

**Dashboard annotation requirement:**
When a widget shows a trend line, the annotation must state:
- Number of observations
- Trend test result (or "visual only — not tested") if fewer than 10 observations
- Time period covered

**Do:**
- Label trend lines with the number of observations and the period.
- Run a Mann-Kendall test before calling a trend "significant" to a stakeholder.
- Ask "is this still a trend if we extend the window one period earlier?" — robust trends survive window changes.

**Don't:**
- Draw a trend line through fewer than 5 data points.
- Use "trending up for N periods in a row" as evidence of a real trend without a test.
- Cite a visual upward trend from a dashboard as evidence for a decision without a trend test.

## Edge cases / when the rule does NOT apply

- A step change (before/after an intervention) is not a trend in the direction-of-time sense — use an interrupted time series model, not a trend test.
- Forecasting a trend (using a model's estimated slope to project future values) is separate from testing whether a historical trend is real. Both are needed.

## See also

- [`../agents/applied-statistician.md`](../agents/applied-statistician.md) — drives the statistical-qa-of-metrics skill
- [`./test-distinguish-signal-from-noise-on-dashboard-metrics.md`](./test-distinguish-signal-from-noise-on-dashboard-metrics.md) — the broader dashboard signal-vs-noise rule

## Provenance

Codifies applied-statistics CLAUDE.md §4 anti-patterns ("A two-point 'trend' on a dashboard presented as a trend"). The Mann-Kendall test is the standard nonparametric trend test for time-ordered data (Kendall 1975; Mann 1945).

---

_Last reviewed: 2026-06-05 by `claude`_
