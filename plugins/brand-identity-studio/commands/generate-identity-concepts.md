---
description: "Author the anti-slop creative brief for generative-web-media (setting indemnity_required) and generate a bulk concept set for human curation — REFUSES if no strategy brief exists (the strategy-before-visuals gate). Emits a copy-paste prompt-pack if generative-web-media is absent. Logos are the curated vector, never a Firefly regen."
argument-hint: "[what to generate: logo | wordmark | imagery | favicon-set + any specific constraints]"
---

You are running `/brand-identity-studio:generate-identity-concepts`. Use `identity-systems-designer` + the
`logo-and-visual-system-direction` skill.

> **Gate (hard precondition):** a `brand-strategy-brief.md` MUST exist. If it does not, **STOP** and route to
> `brand-strategist` / `/start-brand-engagement` — visuals before strategy read as slop. This command does NOT
> pick a generation provider (that is `generative-web-media`'s per-asset call) and does NOT regenerate logos in
> Firefly (the curated vector is the deliverable).

## Steps

1. **Check the strategy gate.** No `brand-strategy-brief.md` → stop, return the gate failure, route to
   `brand-strategist`. Proceed only if it exists.
2. **Author the generation brief** into `templates/creative-brief-for-generative-media.md` (the frozen
   contract_version 1.0 schema) — one brief per `request_kind`. Write **specific** `constraints` +
   `negative_constraints` (escape the legible middle), a bulk `count`, `format_hints`
   (`svg-vector-preferred` + `mono-safe` for logos), and `indemnity_required: true` for client-facing assets.
3. **Dispatch or fall back:**
   - If `generative-web-media` is installed → hand it the brief; it runs generation + picks the provider +
     returns the provenance/indemnity/license fields.
   - If absent → emit the brief as a **copy-paste prompt-pack** (numbered prompts for a vector-capable
     generator), carrying the indemnity note forward.
4. **Stage for curation** — present the bulk set and route to `/curate-concepts`. Do NOT auto-select a winner.
5. **Emit** the brief + the concept set (or prompt-pack) + the next step (`/curate-concepts`) + the Structured
   Output block. Record intended `provider`/`license_class` placeholders in the authorship log.
