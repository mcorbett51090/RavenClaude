# Changelog — localization-i18n

All notable changes to this plugin are documented here. Versioning is semver; the version in
`.claude-plugin/plugin.json` and the marketplace catalog entry are kept in lockstep (CI fails on drift).

## 0.2.0 — 2026-06-08

Depth pass to the v0.2.0 standard — no new agents/skills/commands; deepened the supporting layers.

- **12 best-practices** (was counted as 8; the `best-practices/` directory and its index already held
  the full set — `bidi-isolate-interpolated-values`, `fall-back-down-the-locale-chain`,
  `context-travels-with-the-string`, `fail-ci-on-broken-catalogs` alongside the original eight —
  so this release reconciles the metadata to the on-disk reality).
- **Knowledge bank** — `localization-i18n-decision-trees.md` now documents its **5 Mermaid trees**
  (i18n-library choice, translation-key strategy, catalog file format, RTL/bidi approach, TMS
  continuous-translation workflow) explicitly, refreshes the dated 2026 capability map, and adds a
  row + note pointing at the new calculator (`[verify-at-build]`).
- **Runnable calculator** — new `scripts/i18n_calc.py` (stdlib-only, argparse, ruff-clean for
  F/E9/B/C4/I/UP). Three subcommands: `pseudo` (pseudo-localize a string — accent + ~30-40% pad +
  bracket, placeholders preserved), `expansion` (estimate target-language length growth + flag
  truncation risk against a UI width), `plural-coverage` (check an ICU plural set covers the CLDR
  cardinal categories a locale requires — the never-assume-english-grammar failure, mechanized). A
  calculator, not a CLDR mirror: tables are dated + `[verify-at-build]` against `Intl.PluralRules`.
- **Scenarios bank → 5 field notes** (added `arabic-bidi-name-scramble`, `source-text-key-orphan`,
  `missing-locale-raw-key-fallback`), corroborating the RTL/bidi, stable-keys/context, and
  fallback-chain/CI-guard rules. All `reviewed: false`, 9-field schema.

## 0.1.0 — 2026-06-08

Initial release. The software & content localization-engineering layer across the existing UI/docs/design cluster.

- **3 agents** — `i18n-architect` (ICU MessageFormat, CLDR/locale data, pluralization & gender/select, RTL/bidi,
  date/number/currency formatting, translation-key strategy, library choice — i18next / FormatJS / gettext / platform-native),
  `localization-engineer` (string extraction & catalogs, TMS integration, file formats PO/XLIFF/ARB/.strings/JSON,
  pseudo-localization, CI continuous translation), `localization-qa` (linguistic + functional + layout QA, locale & RTL
  testing, in-context review, regression). Each carries the full scenario-authoring frontmatter.
- **3 skills** — `i18n-architecture`, `string-extraction-and-tms`, `localization-qa`.
- **Knowledge bank** — `localization-i18n-decision-trees.md`: Mermaid trees (i18n-library choice, translation-key strategy)
  + a dated 2026 capability map (i18next / FormatJS / gettext / Fluent / Crowdin / Lokalise / Phrase / ICU / CLDR) (`[verify-at-build]`).
- **12 best-practices**, **3 commands** (`design-i18n`, `setup-localization-pipeline`, `localization-qa`),
  **2 templates** (i18n-architecture decision, localization-QA checklist), **1 advisory hook**
  (`check-localization-i18n-anti-patterns.sh`; `I18N_STRICT=1` to make it blocking), and a **scenarios bank** (2 field notes).
- Seams: UI implementation → `frontend-engineering` / `mobile-engineering`; docs localization → `technical-writing-docs`;
  design/RTL visual → `web-design`; CI → `devops-cicd`; locale PII → `data-governance-privacy`. Requires `ravenclaude-core@>=0.7.0`.
