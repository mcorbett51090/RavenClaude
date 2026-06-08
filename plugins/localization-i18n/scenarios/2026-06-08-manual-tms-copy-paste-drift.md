---
scenario_id: 2026-06-08-manual-tms-copy-paste-drift
contributed_at: 2026-06-08
plugin: localization-i18n
product: crowdin
product_version: "unknown"
scope: likely-general
tags: [tms, pipeline, pseudo-localization, ci, drift, placeholders]
confidence: high
reviewed: false
---

## Problem

A team handled translation as a pre-release phase: an engineer exported the source JSON, uploaded it to the TMS by hand, and weeks later pasted the completed translations back. Two failures recurred. First, the catalog drifted — strings added between exports shipped as raw keys in non-English locales (users saw `home.cta.signup`). Second, a translation occasionally dropped a `{count}` placeholder, which crashed the app only in that language, discovered in production.

## Constraints context

- ~12 locales, weekly releases, a single engineer owning the manual export/import.
- No pseudo-locale, so newly hardcoded strings weren't caught until a translator (or a user) hit them.
- "Translation done" was tracked in a spreadsheet, not enforced by anything in CI.

## Attempts

- Tried: a tighter manual checklist for the export/import ritual. Failed — it still depended on a human remembering, and the drift returned the first busy week.
- Tried: blocking releases until a manager confirmed the spreadsheet was green. Failed — it was a vanity gate; the spreadsheet didn't actually reflect catalog completeness or placeholder parity.
- Tried: wiring continuous translation — the TMS CLI pushes source on merge and pulls translations automatically, a pseudo-locale runs in CI on every PR, and a catalog-validation step fails the build on missing keys, placeholder-count mismatches, or broken ICU. This worked.

## Resolution

Making translation a pipeline instead of a phase closed the drift: source and translations stayed in sync per merge, and raw keys stopped shipping. The pseudo-locale caught newly hardcoded strings the day they were added, and the placeholder-parity check turned the production-only crash into a red build on the PR that introduced it. The single-engineer bottleneck disappeared because nobody copy-pasted JSON anymore.

## Lesson

Translation is a pipeline, not a phase — automate the push/pull through the TMS and let CI guard completeness and placeholder parity, or the catalog drifts from the code and a dropped `{count}` becomes a per-language production crash. Run pseudo-localization continuously; it's the cheapest tripwire for hardcoded strings.
