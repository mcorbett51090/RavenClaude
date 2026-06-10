# localization-i18n-engineering

The **internationalization (i18n) and localization (l10n) engineering** plugin. This plugin's team
helps you design software to be localizable from the ground up, operate an efficient localization
pipeline with a Translation Management System (TMS), and gate quality with automated pseudo-
localization, l10n linting, and locale-coverage testing in CI.

> **The one-line philosophy:** localization is not a release-phase activity — it's an engineering
> discipline built into the architecture, the pipeline, and the CI suite from day one. Hard-coded
> strings, concatenated messages, and `if count == 1` plural branches are bugs.

---

## When to use this plugin (vs. its neighbours)

| You're asking… | Use |
|---|---|
| "Make this app localizable / add i18n support" | **localization-i18n-engineering** (`i18n-architect`) |
| "Handle plurals and gender correctly across languages" | **localization-i18n-engineering** (`i18n-architect`) |
| "Add RTL/bidi support or design for text expansion" | **localization-i18n-engineering** (`i18n-architect`) |
| "Set up a localization pipeline / integrate a TMS" | **localization-i18n-engineering** (`l10n-pipeline-engineer`) |
| "Extract strings and hand off to translators" | **localization-i18n-engineering** (`l10n-pipeline-engineer`) |
| "Add pseudo-localization or l10n linting to CI" | **localization-i18n-engineering** (`localization-qa-engineer`) |
| "Strings overflowing in German / missing keys in some locales" | **localization-i18n-engineering** (`localization-qa-engineer`) |
| "Wire i18next or FormatJS into a React app" | `frontend-engineering` |
| "iOS `.strings` / Android `strings.xml` implementation" | `mobile-engineering` |
| "Translate and maintain documentation or marketing copy" | `technical-writing-docs` |

---

## What's inside

- **3 agents** — `i18n-architect`, `l10n-pipeline-engineer`, `localization-qa-engineer`.
- **3 skills** — i18n-foundations-and-icu, l10n-pipeline-and-tms, localization-qa-and-pseudo-loc.
- **3 commands** — `/localization-i18n-engineering:audit-i18n-readiness`,
  `:design-l10n-pipeline`, `:run-pseudo-localization`.
- **2 templates** — `string-catalog.md` (multi-format string catalog scaffold),
  `l10n-ci-gate.md` (CI gate configuration template).
- **Knowledge bank** — `knowledge/i18n-l10n-decision-trees.md`: Mermaid decision trees for
  library/format choice, machine-vs-human translation, pseudo-loc CI gate, plus a dated 2026
  capability map of the i18n/TMS tool landscape.
- **6 best-practice rules** and **1 advisory hook** (flags hard-coded user-facing strings,
  string concatenation, if-count-1 plurals, hard-coded date/number/currency formats).

---

## House opinions (the short list)

1. Every user-facing string is externalized — hard-coded display strings are bugs.
2. Never concatenate translatable strings — use a single named-parameter message.
3. ICU MessageFormat for plurals and gender — `if count == 1` is wrong in most languages.
4. Design for 30 % text expansion and RTL from day one, not as a retrofit.
5. Pseudo-localization is a CI gate, not a pre-release chore.
6. Translatable content stays out of code — never branch on translated text values.

---

## Requires

`ravenclaude-core@>=0.7.0`. See [`CLAUDE.md`](CLAUDE.md) for the full team constitution and seams.
