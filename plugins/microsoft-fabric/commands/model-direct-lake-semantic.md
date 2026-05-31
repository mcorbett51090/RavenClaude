---
description: Model a Direct Lake semantic model on Fabric — name the mode (on-OneLake vs on-SQL) first, build a star schema over conformed gold, declare relationships, and design gold to that mode's failure shape so framing never errors or falls back.
argument-hint: "[the model, e.g. 'a Direct Lake sales model over the gold lakehouse']"
---

# Model a Direct Lake semantic model

You are running `/microsoft-fabric:model-direct-lake-semantic`. Build (or diagnose) the Direct Lake model for what the user described (`$ARGUMENTS`), following this plugin's `fabric-semantic-model-engineer` discipline — "Direct Lake" without the mode is an unfinished sentence.

## When to use this

A Direct Lake model is being built, or a fallback/empty-results problem is being diagnosed. If the question is about a measure, a visual, or a `.pbix`, that's `power-platform/power-bi-engineer`; this command owns the storage mode, framing, and the gold tables underneath.

## Steps

1. **Name the mode first** — Direct Lake on OneLake (modern default, **no DirectQuery fallback** — an unprocessed table errors, a bad security role yields empty) vs Direct Lake on SQL (older path, **falls back** to DirectQuery on guardrail breach or unsupported feature; SQL OLS/RLS forces the fallback). This is the #1 mistake; write it in the spec (`name-your-direct-lake-mode.md`).
2. **Design gold to that mode's failure shape** — on-OneLake: every gold table framed, empty results read as a OneLake-security misconfig; on-SQL: keep gold under the SKU guardrails (`name-your-direct-lake-mode.md`, `directlake-stay-under-guardrails.md`).
3. **Stay under the Direct Lake guardrails** — keep well under ~10,000 Parquet files (framing fails past it), 1M–16M row groups, 400 MB–1 GB files; OPTIMIZE to compact, and size the SKU for the model's VertiPaq footprint (`directlake-stay-under-guardrails.md`).
4. **Model a star schema, not a wide flat table** — facts at one declared grain + conformed dimensions, single-direction relationships by default (bidirectional only when justified), mark the date dimension (`semantic-star-schema-over-flat.md`).
5. **Confirm gold is shaped for Direct Lake** — V-Order on, large files/row groups; never point Direct Lake on OneLake at a non-materialized SQL view (`shape-gold-for-direct-lake.md`).
6. **Reframe as the final step** of any load that feeds the model. Use the `templates/direct-lake-semantic-model-spec.md` shape.

## Guardrails

- Never assume Direct Lake on OneLake "falls back gracefully" — it errors; design for that.
- Never diagnose a fallback or empty result without first naming the mode — the root-cause taxonomy is mode-specific.
- This plugin is advisory: emit the TMDL/PBIP + `fab` snippets the consultant runs. OneLake-security/RLS/OLS design routes to `ravenclaude-core/security-reviewer`; DAX measure authoring routes to `power-platform/power-bi-engineer`.
