---
name: curation-and-accessibility-gate
description: "The mandatory ship gate: brand-hex/style conformance, anti-slop QA (garbled in-image text, hands/anatomy, off-brand drift, no baked-in text), AI-drafted + human-reviewed WCAG 2.2 alt text (decorative -> alt=\"\"), and a mandatory human curation sign-off. No asset reaches production without a curation artifact — this gate is a hard blocker, not a suggestion."
---

# Curation & Accessibility Gate

The last stop before production. Every asset passes brand conformance, anti-slop QA, alt text, and a **mandatory human sign-off**. This gate is a hard blocker: `/generate-web-asset` cannot reach "done" without a curation artifact.

> **Human curation is not optional.** AI generation has a predictable failure taxonomy (garbled text most of all); a human selects and signs off before anything ships.

## Workflow

1. **Brand conformance** — verify the exact brand hex is present (overlaid, not model-approximated) and the style matches the reference. Off-brand drift → back to `brand-conditioned-generation`.
2. **Anti-slop QA** — check the predictable failures:
   - **Garbled in-image text** (the #1 failure) — reject baked-in text; overlay real type.
   - Hands/anatomy, impossible reflections, physically-wrong lighting.
   - Named light source consistent across the set.
   - Off-brand elements the negative prompt should have excluded.
3. **Alt text — AI-drafted + human-reviewed** — draft descriptive alt text, then a human confirms it (AI alone can't guarantee WCAG AA). **Decorative images get `alt=""`** (WCAG 2.2 SC 1.1.1, Level A). Informative images get a real description.
4. **Human curation sign-off (mandatory)** — a person selects the asset(s) to ship and records the decision. This is the curation artifact; without it the flow is not done.
5. **Emit** the shipped set + the curation record.

## The curation artifact (what "done" requires)

A recorded human decision: which asset(s) selected, who signed off, when, and the alt text approved. `/generate-web-asset` blocks on its presence (red-team RT6 — the gate cannot be a doc suggestion).

## Alt-text quick rules (WCAG 2.2 SC 1.1.1)

- **Decorative** (adds no information) → `alt=""` (empty, not missing).
- **Informative** → concise description of the content/function.
- **Text in the image** → don't (overlay real type); if unavoidable, the alt carries the text.
- AI drafts, a human confirms — never ship AI-only alt text as AA-guaranteed.

## Anti-patterns

- Treating the curation gate as advisory (it's a hard blocker).
- Shipping AI-only alt text as WCAG-compliant.
- `alt="image"` / missing `alt` (decorative → `alt=""`).
- Accepting garbled in-image text instead of overlaying real type.

## See also

- Best-practice: [`../../best-practices/human-curation-is-not-optional.md`](../../best-practices/human-curation-is-not-optional.md), [`../../best-practices/overlay-text-dont-bake-it.md`](../../best-practices/overlay-text-dont-bake-it.md)
- Command: [`../../commands/generate-web-asset.md`](../../commands/generate-web-asset.md)
