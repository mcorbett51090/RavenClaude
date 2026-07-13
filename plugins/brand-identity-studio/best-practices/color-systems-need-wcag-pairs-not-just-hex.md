# Color systems need WCAG pairs, not just hex

**Status:** Absolute rule
**Domain:** Color / accessibility
**Applies to:** `brand-identity-studio`

> WCAG math is durable; conformance version + operating context are `[verify-at-use]`. Measure against the
> ACTUAL rendered background.

---

## Why this exists

A palette of pretty hex values is not a color system — it's a set of swatches that may be illegible in use.
The #1 way a brand "doesn't survive the website" is a brand color that fails contrast against the surfaces it
lands on. WCAG AA is the floor: **4.5:1** for normal text, **3:1** for large text (≥18pt / 14pt bold), **3:1**
for UI components / focus indicators (SC 1.4.3 + SC 1.4.11). A palette handed off without validated text/bg
pairs pushes an accessibility failure — and a legal exposure (ADA/EAA) — downstream into the build.

## How to apply

- Define color **roles** (primary/secondary/accent/neutrals), not just swatches — with HEX/RGB/OKLCH.
- **Validate every text/background + accent + UI/focus pair** with `check-brand-a11y.py` (mirrors
  `web-design/scripts/contrast_ratio.py`). Measure against the *actual* rendered background (gradients/overlays
  flattened, every interactive state).
- **Fail the handoff** on a primary text pair under 4.5:1 — fix the palette at the role level, not the
  component.
- Carry the validated pairs into the brand book's accessibility section and the delegated token export.

**Do:** validate contrast pairs before the palette ships; fix at the role.
**Don't:** eyeball contrast, or ship a palette as "hex only" and let the site discover the failure.

## Edge cases / when the rule does NOT apply

Purely decorative, non-informational graphics that convey no content and aren't UI have no contrast minimum —
but a brand color used for text, an icon that carries meaning, or a focus ring is not decorative. When in
doubt, validate.

## See also

- Script: [`../scripts/check-brand-a11y.py`](../scripts/check-brand-a11y.py)
- Skill: [`../skills/logo-and-visual-system-direction/SKILL.md`](../skills/logo-and-visual-system-direction/SKILL.md)
- Cross-plugin: `web-design/scripts/contrast_ratio.py` (the full design-system contrast audit at token time)

## Provenance

Codifies B7 (w3.org/WAI/WCAG21/Understanding/contrast-minimum; makethingsaccessible.com). Mirrors the WCAG 2.x
math in `web-design`'s checker. Retrieval 2026-07-13.

---

_Last reviewed: 2026-07-13 by `claude`_
