---
name: logo-and-visual-system-direction
description: "Direct the visual identity: author the anti-slop creative brief for generative-web-media (setting indemnity_required), run the human-curation + documented-human-authorship gates, and spec the logo suite (lockups/clear-space/min-size/mono/B&W), color roles with WCAG-AA pairs, and type with web-license class. Refuses without a strategy brief. The curated vector is the deliverable — never regenerated in Firefly."
---

# Logo & Visual System Direction

This is where strategy becomes a visual system — by **directing** the generators, **curating** ruthlessly with
a human, and **specifying** the logo/color/type system. This plugin is thin: it authors the brief and sets the
indemnity flag; `generative-web-media` runs generation and picks the provider per-asset; `web-design` builds
the tokens. The value here is direction + curation, not raw pixels.

> **Two hard gates live in this skill.** (1) **strategy-before-visuals** — refuse if no `brand-strategy-brief.md`
> exists. (2) **documented-human-authorship** — a human must select and log a substantial modification before a
> concept becomes a deliverable. The **curated vector is the deliverable and is NEVER regenerated in Firefly**.
> Every font-license/IP claim routes to `security-reviewer`. Prices `[unverified]`.

## Workflow

1. **Gate: strategy exists.** No `brand-strategy-brief.md` → stop, route to `brand-strategist`.
2. **Author the generation brief (the seam).** Fill
   [`../../templates/creative-brief-for-generative-media.md`](../../templates/creative-brief-for-generative-media.md)
   — one brief per `request_kind`. Set `indemnity_required: true` for client-facing/resold assets. Do **not**
   name a provider — media's license gate chooses per-asset.
3. **Generate breadth (or fall back).** Hand the brief to `generative-web-media`. **If it is not installed,**
   emit the brief as a **copy-paste prompt-pack** (below) so the engagement is never blocked.
4. **Gate: human curation + authorship.** A human selects; log the selection **and a substantial human
   modification/arrangement** in [`../../templates/curation-and-authorship-log.md`](../../templates/curation-and-authorship-log.md).
5. **Spec the logo suite, color system, type system** (below), validating WCAG pairs with the runnable checker.
6. **Hand off** to `brand-book-assembly` (compile) and, for tokens, to `web-design:design-tokens-scaffolding`.

## Anti-slop brief authoring

The model defaults to a "legible middle" that reads as slop. Escape it with **specific** constraints:

- **Positive constraints:** "identifiable in one flat color", "reads at 16px favicon size", "geometric sans
  wordmark", "the mark works without the wordmark".
- **Negative constraints:** "no gradient mesh", "no generic swoosh/globe", "avoid the #-blue SaaS palette",
  "not a literal picture of the product".
- **Reference-anchored intent:** "like Stripe's restraint but warmer" beats "modern and clean".
- **Bulk `count`:** generate many; the human curates. Exploration is cheap; refinement is human.

### Prompt-pack fallback (when generative-web-media is absent)

If `generative-web-media` is not installed, render the brief's `intent` + `constraints` + `negative_constraints`
as a numbered prompt list the operator pastes into a vector-capable generator (Recraft/Ideogram class for
logos/wordmarks). **Carry the indemnity note forward** ("client-facing/resold — use an IP-indemnified provider
for imagery; keep the curated vector as the deliverable"), and record `provider` + `license_class` manually in
the authorship log. Never substitute a Firefly regen for the curated vector.

## Logo suite spec (the gold deliverable)

| Variant | Requirement |
|---|---|
| Primary lockup | The default mark + wordmark relationship |
| Secondary / stacked | For constrained widths |
| Mark alone | Works without the wordmark (app icon, favicon) |
| Wordmark alone | Typographic, no mark |
| Clear-space | Defined in terms of a mark-derived unit (e.g. cap-height) |
| Min-size | Smallest legible size, per medium (px for web, mm for print) |
| Mono / one-color | A single flat color version |
| Reversed / B&W | Legible knocked-out on dark and in pure B&W |
| Do / don't gallery | The specific misuses to forbid (stretch, recolor, re-spacing, drop-shadow) |

**True vector (SVG)** is the format; the mark must be **identifiable in B&W** (the acid test of a real mark
vs a gradient-dependent picture).

## Color system spec

- **Roles, not just swatches:** primary / secondary / accent / neutrals (a full neutral ramp).
- **Per color:** HEX + RGB + OKLCH (and CMYK if print is in scope).
- **WCAG pairs — validated, not asserted.** Run [`../../scripts/check-brand-a11y.py`](../../scripts/check-brand-a11y.py)
  on the text/background + accent + UI/focus pairs. AA floor: 4.5:1 normal text, 3:1 large text, 3:1 UI/focus.
  **A primary text pair under 4.5:1 fails the handoff** — fix the palette, don't ship the debt.
- Hand the role/value decisions to `web-design:design-tokens-scaffolding`; do not build the token pipeline here.

## Type system spec

- Families (display / text / mono) + a modular scale + pairing rules + weights actually loaded.
- **Explicit web-license class per family** in [`../../templates/font-license-tracker.md`](../../templates/font-license-tracker.md).
  OFL/Apache self-host is preferred. A **non-self-hostable** font (Adobe Fonts embed-only, Monotype
  pageview-metered) is **blocked from the token export** — see `brand-legal-and-licensing`.

## Anti-patterns

- Generating visuals before the strategy brief exists.
- A "modern/clean/professional" brief (the slop prompt) instead of specific + negative constraints.
- Treating a Firefly regeneration as the "final" logo — it discards the human curation the value rests on.
- A logo that dies in one color or B&W (gradient-dependent = not a mark).
- Shipping a palette whose contrast was eyeballed, not validated.
- Recording a font family with no web-license class.

## See also

- Template (the seam): [`../../templates/creative-brief-for-generative-media.md`](../../templates/creative-brief-for-generative-media.md)
- Template: [`../../templates/curation-and-authorship-log.md`](../../templates/curation-and-authorship-log.md)
- Script: [`../../scripts/check-brand-a11y.py`](../../scripts/check-brand-a11y.py)
- Best-practices: [`../../best-practices/curate-the-vector-dont-regenerate-it.md`](../../best-practices/curate-the-vector-dont-regenerate-it.md),
  [`../../best-practices/color-systems-need-wcag-pairs-not-just-hex.md`](../../best-practices/color-systems-need-wcag-pairs-not-just-hex.md)
- Skill: [`../brand-legal-and-licensing/SKILL.md`](../brand-legal-and-licensing/SKILL.md)
