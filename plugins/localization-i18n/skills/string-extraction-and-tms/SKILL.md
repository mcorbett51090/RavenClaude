---
name: string-extraction-and-tms
description: "Build the localization pipeline: extract strings into catalogs, choose the file format (PO/XLIFF/ARB/.strings/JSON), integrate the TMS with a continuous push/pull workflow, wire pseudo-localization, and gate CI on catalog completeness, placeholder parity, and ICU validity."
---

# String Extraction & TMS

## Extraction is mechanical or it rots
Extract strings via tooling keyed off the i18n calls (i18next-parser, FormatJS extract, `xgettext`, `genstrings`), not by hand. For a legacy codebase with scattered hardcoded strings, plan a staged refactor that keeps the app shippable each step, and run a pseudo-locale to catch the stragglers.

## File format = the interface to translators' tools
Pick the format the stack *and* the TMS round-trip without loss: PO/gettext, XLIFF (1.2/2.0), Android `strings.xml`, ARB (Flutter), Apple `.strings`/`.stringsdict`, or JSON (i18next/FormatJS). Never lossy-convert in a way that strips plurals, context comments, or metadata.

## TMS integration is continuous push/pull
Crowdin / Lokalise / Phrase / Transifex / Weblate `[verify-at-build]`: push source on merge, pull completed translations, handle branches/PRs, upload context + screenshots + char-limits, and sync the glossary + translation memory (the cost-control levers). A manual export a human runs by hand is a future incident.

## Pseudo-localization as a first-class locale
Wire a pseudo-locale (accented, length-inflated, bracketed) into the build to surface hardcoded strings, concatenation, and truncation before translation spend. Run it in CI on every PR.

## CI fails the build on a broken catalog
Validate every catalog: missing keys, placeholder-count parity (a dropped `{count}` is a crash in another language), broken ICU syntax, untranslated required locales. Gate the release on required-locale completeness. Prune stale keys so translators aren't paid to translate dead strings.

## Output
A localization-pipeline plan: the file-format + TMS choice, the extraction strategy, the push/pull continuous-translation CI jobs with completeness/placeholder guards, and the pseudo-locale wiring — handing the CI runner to `devops-cicd` and the i18n call implementation to the UI teams.
