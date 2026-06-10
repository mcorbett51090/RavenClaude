# Platform Engineering (IDP) Unit Economics

> The arithmetic behind the team's house opinions. Every formula here is reproduced in [`../scripts/platform_engineering_idp_calc.py`](../scripts/platform_engineering_idp_calc.py) so the math is auditable. All multipliers/benchmarks are `[unverified — training knowledge]` — supply the client's actual figures (§3 #8).

## 1. Adoption is the scoreboard (§3 #7)

```
adoption_pct = teams_on_golden_path / total_teams
gap_teams    = total_teams - teams_on_golden_path
```

A platform at 80% adoption with a clear gap backlog is winning; a feature-rich platform at 20% adoption is accumulating maintenance and cognitive-load debt. The numerator must be a concrete on-path definition, not aspiration.

## 2. Toil ROI is the automation case (§3 #4)

```
hours_per_year = (task_minutes * frequency_per_year * engineers) / 60
```

A 15-minute task done weekly by 40 engineers is 15 × 52 × 40 ÷ 60 = 520 engineer-hours/yr — that is the budget you have to build a self-service action against. Rare edge cases rarely clear the bar.

## 3. The error budget gates change (§3 #6)

```
error_budget = (1 - slo_target) * window
```

At a 99.5% paved-path success SLO over a 30-day window, the budget is 0.5% of runs; when it's spent, platform feature work freezes and reliability work takes over — exactly as for a user-facing service.

## 4. DORA classification is the defensible signal (§3 #3)

```
classify(deploy_freq, lead_time, change_fail, mttr) -> elite | high | medium | low
```

Each of the four keys classifies independently; the org's band is the weakest key, and that key is the lever. 'Developers seem happier' is sentiment, not a key.
