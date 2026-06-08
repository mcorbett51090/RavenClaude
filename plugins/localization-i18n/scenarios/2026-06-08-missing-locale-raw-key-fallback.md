---
scenario_id: 2026-06-08-missing-locale-raw-key-fallback
contributed_at: 2026-06-08
plugin: localization-i18n
product: generic
product_version: "unknown"
scope: likely-general
tags: [fallback-chain, locale-chain, raw-keys, regional-locales, ci-guard, completeness]
confidence: medium
reviewed: false
---

## Problem

A product supported regional variants — `pt-BR`, `pt-PT`, `es-MX`, `es-ES`, `en-GB` — but only a few
strings actually differed per region; most were shared. The team copied the base catalog into each
regional file and translated the differences, then forgot to keep them in sync. New strings landed in
`pt` but not in the hand-copied `pt-BR`, and because the loader did an exact-locale lookup with no
fallback, Brazilian users saw raw keys (`checkout.tax.notice`) wherever `pt-BR` lacked an entry. The
same gap hit `es-MX` against `es`. It looked like missing translations but was actually a missing
*fallback chain*: a regional miss should degrade to the language, then to the default, never to a key.

## Constraints context

- 5 base languages × regional variants, ~1,100 strings, only ~5% genuinely region-specific.
- The runtime loaded the exact locale and stopped — no `region → language → default` resolution.
- CI checked that each locale file was valid JSON, but not that every required key resolved through
  the chain, so the gaps shipped silently.

## Attempts

- Tried: re-copying the base catalog into each regional file before every release. Failed — it
  duplicated 95% of strings, the copies drifted again within a sprint, and it made every base edit a
  multi-file change nobody completed reliably.
- Tried: telling translators to "fill in" the regional files completely. Failed — most regional
  entries are identical to the base, so this manufactured busywork and still left gaps whenever a new
  base string appeared between fills.
- Tried: implementing a real fallback chain in the loader (`pt-BR → pt → en`, `es-MX → es → en`),
  keeping only genuinely region-specific overrides in the regional files, and adding a CI guard that
  every required key *resolves through the chain* for every shipping locale (not just that the file is
  valid). This worked.

## Resolution

The fallback chain meant a missing `pt-BR` string degraded to `pt` (then `en`) and rendered real
words instead of a raw key, so the regional files shrank to only the handful of true overrides and
stopped drifting. The CI resolution-guard turned "a Brazilian user finds a raw key in production" into
a red build on the PR that added an unresolved key. Region-specific copy still lived where it
belonged; everything else inherited, by design, down the chain.

## Lesson

Always resolve down the locale chain — `region → language → default` — so a missing `pt-BR` string
falls back to `pt`/`en` and never renders a raw key (`fall-back-down-the-locale-chain`). Keep only
genuine regional overrides in regional files, and have CI fail when a required key doesn't resolve
through the chain, not merely when a file is malformed (`fail-ci-on-broken-catalogs`).
