---
description: "Compute the WCAG contrast ratio from hex foreground/background values and check AA/AAA for normal and large text. Reach for this on any color question."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Verify contrast

You are running `/accessibility-engineering:verify-contrast` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Take the hex values — Foreground and background as hex strings.
2. Compute relative luminance — sRGB linearization then L = 0.2126R + 0.7152G + 0.0722B per channel.
3. Compute the ratio — (L_light + 0.05) / (L_dark + 0.05) via `accessibility_calc.py contrast` (§3 #5).
4. Check the thresholds — AA normal >=4.5, AA large >=3.0, AAA normal >=7.0, AAA large >=4.5.

## Output
A computed contrast ratio with AA/AAA pass for normal and large text — never an eyeballed judgment. See [`../skills/verify-contrast/SKILL.md`](../skills/verify-contrast/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No user PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
