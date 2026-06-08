---
scenario_id: 2026-06-08-contrast-eyeballed-and-failed
contributed_at: 2026-06-08
plugin: accessibility-engineering
product: contrast
product_version: "n/a"
scope: likely-general
tags: [color-contrast, design-tokens, measurement, wcag-1.4.3]
confidence: medium
reviewed: false
---

## Problem

A design team approved a light-gray body text on white because it 'looked clean,' and it shipped into the design-system tokens. The risk: contrast is a computed ratio from relative luminance, not an appearance judgment, and a color that looks acceptable routinely fails the 4.5:1 AA bar for normal text (§3 #5).

## Context

- Surface: design-system color tokens used across the product.
- Constraint: WCAG SC 1.4.3 requires >=4.5:1 for normal text, computed from sRGB-linearized luminance (§3 #5).
- The team reasoned from how the color looked on their monitors.

## Attempts

- Tried: **computed the actual ratio** from the hex values via `accessibility_calc.py contrast`. Outcome: the gray-on-white landed around 3.5:1 — a clear AA failure for normal text, though it would pass for large text.
- Tried: **checked the large-text exception.** Outcome: the token was used for body copy, so the 3:1 large-text allowance did not apply.
- Tried: **darkened the token to clear 4.5:1** and re-computed. Outcome: a token that passes by measurement, fixed once in the design system rather than per page (§3 #7).

## Resolution

The fix was to **darken the shared token to a measured >=4.5:1 and verify every token by computed ratio at design time** — not to approve color on appearance. The output was the computed ratios, the failing token, and the corrected design-system value.

**Action for the next consultant hitting this pattern:** **compute the contrast ratio; never eyeball color.** Verify every color token by the WCAG formula at design time and fix it once in the design system, not per page. See the `accessibility_calc.py` `contrast` mode and §3 #5 #7.

Benchmark figures are segment-/region-/date-dependent — treat as `[unverified — training knowledge]` and validate against the client's own data before any deliverable (§3 #8).
