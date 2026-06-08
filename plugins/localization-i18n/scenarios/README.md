# Localization-i18n scenarios bank

> Unverified, dated, scope-tagged narratives from real localization engagements. War stories of "we hit X
> problem, here was the situation, these were our constraints, we tried A/B/C, D worked."

This directory holds **scenarios** — field notes from real localization work. Scenarios are:

- **Schema-validated** but **not maintainer-reviewed**
- **Visible to consumers** via `/plugin install`
- **Consulted by agents** as a *secondary* source — always surfaced with the mandatory unverified-scenario preamble

For the full architecture and the retrieval pattern, see [`../../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../../ravenclaude-core/skills/scenario-retrieval/SKILL.md). Canonical knowledge lives in [`../knowledge/`](../knowledge/) and `docs/best-practices/`; scenarios never replace it.

## The 9-field schema

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>
contributed_at: <YYYY-MM-DD>
plugin: localization-i18n
product: <i18next | formatjs | gettext | crowdin | lokalise | icu | generic | etc.>
product_version: "<version or unknown>"
scope: <likely-general | product-specific>
tags: [<tag>, ...]
confidence: <high | medium | low>
reviewed: false
---
```

## Current bank

| File | Tags | Corroborates |
|---|---|---|
| [`2026-06-08-polish-plural-bug.md`](2026-06-08-polish-plural-bug.md) | plurals, icu, cldr, gender-select | `never-assume-english-grammar`, `cldr-intl-is-the-source-of-truth` |
| [`2026-06-08-manual-tms-copy-paste-drift.md`](2026-06-08-manual-tms-copy-paste-drift.md) | tms, pipeline, pseudo-localization, ci | `translation-is-a-pipeline-not-a-phase`, `pseudo-localize-continuously` |
| [`2026-06-08-arabic-bidi-name-scramble.md`](2026-06-08-arabic-bidi-name-scramble.md) | rtl, bidi, arabic, isolation, css-logical | `bidi-isolate-interpolated-values`, `translated-is-not-correct` |
| [`2026-06-08-source-text-key-orphan.md`](2026-06-08-source-text-key-orphan.md) | keys, stable-ids, orphaned-translations, context | `stable-keys-not-source-text`, `context-travels-with-the-string` |
| [`2026-06-08-missing-locale-raw-key-fallback.md`](2026-06-08-missing-locale-raw-key-fallback.md) | fallback-chain, raw-keys, regional-locales, ci-guard | `fall-back-down-the-locale-chain`, `fail-ci-on-broken-catalogs` |
