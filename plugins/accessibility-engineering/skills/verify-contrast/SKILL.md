---
name: verify-contrast
description: "Compute the WCAG contrast ratio from hex foreground/background values and check AA/AAA for normal and large text. Reach for this on any color question."
---

# Skill: Verify contrast

Contrast is a computed ratio, not a vibe — color approved on appearance routinely fails (§3 #5).

## Step 1 — Take the hex values
Foreground and background as hex strings.

## Step 2 — Compute relative luminance
sRGB linearization then L = 0.2126R + 0.7152G + 0.0722B per channel.

## Step 3 — Compute the ratio
(L_light + 0.05) / (L_dark + 0.05) via `accessibility_calc.py contrast` (§3 #5).

## Step 4 — Check the thresholds
AA normal >=4.5, AA large >=3.0, AAA normal >=7.0, AAA large >=4.5.

## Output
A computed contrast ratio with AA/AAA pass for normal and large text — never an eyeballed judgment.
