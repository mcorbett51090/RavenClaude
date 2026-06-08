# Localization & i18n

The **localization-i18n** plugin — the software & content localization-engineering craft: the internationalization architecture, the translation pipeline, and the localization QA that ship a product *correctly* in many languages — distinct from the UI components, the help docs, and the visual design themselves.

## Agents

- **`i18n-architect`** — Internationalization architecture: the message-format model (ICU MessageFormat plural/select vs. platform-native), the i18n library per stack (i18next / FormatJS·react-intl / gettext / platform-native), the translation-key strategy (stable IDs, namespacing, collisions), the CLDR/locale-data + fallback-chain plan, and the RTL/bidi + date/number/currency formatting approach. Designs i18n before strings get hardcoded into a corner.
- **`localization-engineer`** — The localization pipeline: string extraction into catalogs, TMS integration + workflow (Crowdin / Lokalise / Phrase / Transifex), the file-format choice (PO/gettext, XLIFF, Android XML, ARB, Apple `.strings`/`.stringsdict`, JSON), pseudo-localization wiring, and CI continuous translation (push source on merge, pull translations, fail the build on missing/broken catalogs).
- **`localization-qa`** — Localization QA: linguistic QA (accuracy, terminology, in-context review), functional QA (date/number/sort/input per locale), layout QA (truncation/overflow/wrapping from length expansion), locale + RTL/bidi testing, pseudo-localization as a QA gate, and a localization regression suite.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install localization-i18n@ravenclaude
```

## Seams

- **The UI component / screen implementation and the i18n wiring in code** → `frontend-engineering` / `mobile-engineering`; this team defines the i18n contract, they build the components.
- **The help/docs content (and its words)** → `technical-writing-docs`; we can pipe docs through the same TMS, they own the content.
- **The mirrored RTL layout and the translated-layout visual review** → `web-design`; we say RTL must work and length expands, they design the layout.
- **The CI runner the translation and pseudo-locale jobs run in** → `devops-cicd`; we specify the continuous-translation jobs, they run them.
- **Locale-derived PII, translator PII, and TMS data residency** → `data-governance-privacy`; we encode their policy into the pipeline.

Inherits `ravenclaude-core` protocols (Capability Grounding + Structured Output). Requires `ravenclaude-core@>=0.7.0`. Designed to be installed alongside `frontend-engineering`, `mobile-engineering`, `technical-writing-docs`, and `web-design`.
