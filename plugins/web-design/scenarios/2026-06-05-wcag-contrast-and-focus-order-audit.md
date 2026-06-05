---
scenario_id: 2026-06-05-wcag-contrast-and-focus-order-audit
contributed_at: 2026-06-05
plugin: web-design
product: html-css
product_version: "unknown"
scope: likely-general
tags: [wcag, contrast, focus-order, keyboard, audit, remediation]
confidence: high
reviewed: false
---

## Problem

A pre-launch WCAG 2.2 AA audit of a marketing site surfaced two recurring blockers the team had treated as polish: (1) the brand's "light grey on white" secondary text and the accent-colour CTA both failed contrast, and (2) a custom mega-menu and a "skip to content" link put keyboard focus in an order that did not match the visual/reading order — `Tab` jumped from the logo into the footer, then back up into the nav. The stakeholder framing was "make the Lighthouse accessibility score 100 and we ship." Lighthouse was already 96.

## Constraints context

- **WCAG 2.2 AA is the launch floor** (constitution §3 #1). The audit must cite the success criterion, not a vibe.
- Lighthouse/axe automation finds ~30–40% of issues; contrast on **gradient/overlay** backgrounds and **focus-order** are largely in the manual 60–70% (the `accessibility-auditor` agent's standing position).
- The "grey on white" was a **brand token** (`--text-secondary`), so a fix had to change the token, not patch one component — and the visual designer owned that decision.
- The accent CTA colour was a brand red the marketing team would not abandon; the fix had to preserve brand identity.

## Attempts

- Tried: trusting the Lighthouse 96. Outcome: it had **not** flagged the secondary-text contrast (the sampled node happened to sit on a darker section) nor the focus-order (automation can't judge "matches reading order"). A 96 is not a pass — manual + keyboard testing is the rest.
- Tried: measuring contrast against `#ffffff` only. Outcome: the CTA actually rendered on a **light-grey hero gradient**, so the real ratio was worse than the nominal one — contrast must be measured against the **actual displayed background**, including hover/active states, gradients, and image overlays (SC 1.4.3, 4.5:1 normal / 3:1 large + UI components per SC 1.4.11).
- Tried: `tabindex` values (`tabindex="1"`, `2`, …) to "fix" the focus order. Outcome: anti-pattern — positive `tabindex` creates a brittle parallel tab sequence and broke as soon as a new nav item was added. The fix was to **correct DOM order** so visual order == source order (SC 2.4.3 Focus Order), and use `tabindex="0"`/`-1"` only for managed focus.

## Resolution

**Contrast is a constraint, focus order is the DOM, and Lighthouse 100 ≠ accessible.** The remediation that shipped:

1. **Fix contrast at the token, against the real background.** Darkened `--text-secondary` until it cleared **4.5:1** on the lightest surface it ever renders on; nudged the CTA's text/background pairing (kept the brand red as a *fill*, used white text + a darker red that cleared 4.5:1, verified on the gradient). Re-verified every state (default/hover/active/disabled) — disabled UI is exempt, the rest are not. Measured with a contrast formula (relative luminance per WCAG), not by eye.
2. **Fix focus order in the source, never with positive `tabindex`.** Reordered the nav DOM so tab order follows reading order; the skip link became the first focusable element and was made **visible on focus** (a permanently visually-hidden skip link is broken on first tab). SC 2.4.3 + SC 2.4.1.
3. **Make focus visible.** Restored a real focus indicator (the brand had `outline: none`) clearing SC 2.4.7 and the WCAG 2.2 SC 2.4.11 Focus Not Obscured / 2.4.13 Focus Appearance bar.
4. **Rank by user impact, not by tool count.** A contrast fail on the primary CTA and a broken keyboard path to the primary task are **P0** (blocks the conversion flow for low-vision and keyboard/AT users); a contrast fail on a decorative caption is P3. Each finding got a WCAG SC, a severity, an owner, and a target date.

**Action for the next auditor:** never accept a Lighthouse score as the verdict. Measure contrast against the **actual rendered background and every interactive state**, fix grey-on-white at the **token** (loop in `visual-designer`), and fix focus order by **correcting DOM order** — positive `tabindex` is the bug, not the fix. Cross-reference [`../best-practices/visual-color-contrast-is-a-constraint.md`](../best-practices/visual-color-contrast-is-a-constraint.md), [`../best-practices/a11y-visible-focus-and-target-size.md`](../best-practices/a11y-visible-focus-and-target-size.md), and the [`../skills/accessibility-review/SKILL.md`](../skills/accessibility-review/SKILL.md) checklist; the contrast arithmetic is mechanizable with [`../scripts/contrast_ratio.py`](../scripts/contrast_ratio.py).

**Sources for the standards cited:** WCAG 2.2 SC 1.4.3 Contrast (Minimum) — 4.5:1 normal / 3:1 large text — https://www.w3.org/TR/WCAG22/ and https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html ; SC 2.4.3 Focus Order, SC 2.4.7 Focus Visible, SC 2.4.11/2.4.13 (WCAG 2.2 focus additions) — https://www.w3.org/TR/WCAG22/ (retrieved 2026-06-05). The WCAG version + thresholds are `[verify-at-use]` — re-confirm on the Researcher sweep.
