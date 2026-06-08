# Accessibility Engineering Unit Economics

> The arithmetic behind the team's house opinions. Every formula here is reproduced in [`../scripts/accessibility_calc.py`](../scripts/accessibility_calc.py) so the math is auditable. All multipliers/benchmarks are `[unverified — training knowledge]` — supply the client's actual figures (§3 #8).

## 1. Contrast is a computed ratio, not a vibe (§3 #5)

```
# sRGB linearization per channel c in [0,1]:
lin(c) = c/12.92                if c <= 0.03928
         ((c + 0.055)/1.055)**2.4  otherwise
L      = 0.2126*lin(R) + 0.7152*lin(G) + 0.0722*lin(B)
ratio  = (L_light + 0.05) / (L_dark + 0.05)
```

AA needs ratio >=4.5 (normal) / >=3.0 (large); AAA needs >=7.0 (normal) / >=4.5 (large). Approve color on the number, never on appearance.

## 2. Automated coverage is a fraction (§3 #2)

```
detectable_by_tools ~= a minority of WCAG issues   # [unverified — training knowledge]
human_judgment_SC   = focus order, alt-text meaning, name/role/value, reading order, ...
```

A clean scan bounds the floor of how bad things are, not the ceiling of how good. Conformance requires manual + AT testing.

## 3. Weighted conformance, not a pass-count (§3 #1)

```
weighted_score = 1 - (Σ issue_weight(severity, level) / Σ max_weight)
critical_blockers = count(level == 'A' and severity == 'critical')
```

One Level-A blocker fails the page regardless of how many AA criteria pass — surface blockers separately from the score.

## 4. Remediation is impact-over-effort (§3 #7)

```
priority = user_impact / effort
```

Fix Level-A blockers and high-impact quick wins first; defer high-effort low-impact polish. Design-time prevention beats post-release retrofit on cost by a wide margin (§3 #7).
