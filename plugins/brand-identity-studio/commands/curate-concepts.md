---
description: "The human-only curation gate — a person selects from the bulk-generated concepts and logs the selection PLUS a substantial human modification/arrangement (the documented-human-authorship step that makes the resale deliverable copyright-ownable). The curated vector becomes the deliverable and is never regenerated in Firefly."
argument-hint: "[which concept(s) the human selected + the human modification made]"
---

You are running `/brand-identity-studio:curate-concepts`. Use `identity-systems-designer` + the
`logo-and-visual-system-direction` skill.

> **This is a human-in-the-loop gate, not an autonomous step.** AI generates breadth; a **human** supplies the
> ruthless refinement and the authorship. The command RECORDS the human's decision — it does not make the
> selection itself. Not legal advice — the copyright/authorship facts route to `security-reviewer`.

## Steps

1. **Confirm a bulk concept set exists** (from `/generate-identity-concepts`). If not, route back.
2. **Record the human selection** — which concept(s) the person chose and **why** (the strategy fit, the
   distinctiveness, the B&W/mono legibility). If no human selection is provided, **pause and ask** — do not
   auto-pick.
3. **Log the documented human authorship** into `templates/curation-and-authorship-log.md`: the substantial
   human **modification or arrangement** applied to the selected concept (redraw, recomposition, custom
   kerning, palette/lockup decisions). This is the step that preserves copyrightability of the human
   contribution (B5) — without it, a pure-AI mark is not copyrightable.
4. **Record provenance** — `provider`, `indemnity_status`, `license_class` for the selected asset (from the
   media return, or manually if the prompt-pack path was used).
5. **Freeze the curated vector as the deliverable.** Note explicitly that it is NOT to be re-sent to Firefly
   for a "final" pass (regeneration voids the curation).
6. **Emit** the completed curation + authorship log + the next step (`/assemble-brand-book`) + the Structured
   Output block. Route any trademarkability/ownership claim to `security-reviewer`.
