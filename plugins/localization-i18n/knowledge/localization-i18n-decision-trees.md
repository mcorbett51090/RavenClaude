# Localization & i18n — Decision Trees

_Decision trees + a dated capability map. Capability rows are `[verify-at-build]` — re-check against the vendor/project before quoting. Last reviewed: 2026-06-08. Five Mermaid trees (library, key strategy, catalog format, RTL/bidi, TMS workflow)._

Traverse before choosing an i18n library, designing the translation-key scheme, or wiring the TMS.

## Decision Tree: Which i18n library / message-format model?

Pick the library the stack and your message complexity both want — and ICU MessageFormat unless the platform forces native.

```mermaid
graph TD
  A[Need to internationalize an app] --> B{What stack?}
  B -- React / web JS-TS --> C{Heavy plural/gender/select + ICU skeletons?}
  C -- Yes --> D[FormatJS / react-intl - ICU MessageFormat first-class]
  C -- No, simple keys + namespacing --> E[i18next - ecosystem, lazy-load, plurals via CLDR]
  B -- Mobile native --> F[Platform-native: Android plurals / Apple .stringsdict / ARB for Flutter]
  B -- Server: Python-PHP-Ruby-C --> G[gettext / ngettext - mature, PO-based]
  B -- Mozilla-style asymmetric grammar --> H[Fluent / FTL - per-locale grammar logic]
  D --> I{Languages with 3+ plural forms or gender?}
  E --> I
  G --> I
  I -- Yes --> J[ICU plural/select - translator owns the grammar per CLDR]
  I -- No, still --> J
```

_Default to ICU MessageFormat for plural/select; reach for platform-native only when the OS/toolchain owns the catalog (iOS/Android). Never let developer code decide the plural category._

## Decision Tree: Translation-key strategy?

Stable IDs beat source-text-as-key for anything that outlives a sprint.

```mermaid
graph TD
  A[Choosing the key scheme] --> B{Will the English copy be edited after launch?}
  B -- Yes, frequently --> C[Stable IDs + English as default value - editing copy never orphans translations]
  B -- Rarely / prototype --> D{Small app, few strings, one team?}
  D -- Yes --> E[Source-text-as-key is OK short-term - migrate to IDs before scale]
  D -- No --> C
  C --> F{How to organize keys?}
  F -- Many features/screens --> G[Namespaced keys: feature.screen.element - lazy-loadable, collision-safe]
  F -- Flat is fine --> H[Flat keys - acceptable below a few hundred strings, revisit at scale]
  G --> I{Plural/interpolated message?}
  H --> I
  I -- Yes --> J[One ICU message per key with named placeholders - never concatenate fragments]
  I -- No --> K[Single value with the English default + a context comment for translators]
```

_Source-text-as-key reads nicely until a typo fix in English silently orphans every translation. Prefer stable IDs; always attach a context comment._

## Decision Tree: Which catalog file format?

Pick the format the stack *and* the TMS round-trip without losing plurals, context, or metadata.

```mermaid
graph TD
  A[Choosing the catalog format] --> B{What owns the runtime?}
  B -- iOS / macOS --> C[Apple .strings + .stringsdict - .stringsdict carries plural quantities]
  B -- Android --> D[Android strings.xml + plurals - quantity strings native]
  B -- Flutter --> E[ARB - intl_translation / gen-l10n, ICU-aware]
  B -- Python/PHP/Ruby/C server --> F[PO/POT gettext - mature, msgctxt + translator comments]
  B -- Web JS/TS --> G{Need rich plural/select + context metadata in the file?}
  G -- Yes --> H[XLIFF 1.2/2.0 or ICU-aware JSON - notes + context survive]
  G -- Simple key/value --> I[JSON - flat or namespaced; confirm plural convention]
  C --> J{Does the TMS round-trip this format losslessly?}
  D --> J
  E --> J
  F --> J
  H --> J
  I --> J
  J -- Yes --> K[Use it - keep one canonical format; convert at the edges only]
  J -- No, lossy --> L[Pick a TMS-native format or a lossless intermediate - never strip plurals/context in conversion]
```

_The format must preserve plural categories, placeholder names, and context/comments end to end. A lossy conversion that drops `msgctxt`, ARB `@`-metadata, or `.stringsdict` quantities silently degrades translation quality — choose the format the runtime and the TMS both speak natively._

## Decision Tree: RTL / bidi approach?

Logical, isolated, mirrored — designed in, not bolted on with `dir=rtl` at the end.

```mermaid
graph TD
  A[Ship an RTL locale - ar/he/fa/ur] --> B{CSS uses physical or logical properties?}
  B -- Physical: left/right, margin-left --> C[Migrate to logical: inline-start/end, margin-inline - mirrors automatically]
  B -- Logical already --> D{Interpolated runtime values in text?}
  C --> D
  D -- Yes --> E[Bidi-isolate each value: FSI…PDI / bdi - a Latin name can't reorder Arabic]
  D -- No --> F{Directional UI: icons, progress, carousels, back-arrows?}
  E --> F
  F -- Yes --> G[Mirror direction-sensitive elements; leave logos/media unmirrored]
  F -- No --> H{Numbers and dates in the locale?}
  G --> H
  H --> I[Format via Intl/CLDR; decide Arabic-Indic vs Latin digits per locale]
  I --> J[QA the running RTL build: mirroring, isolation, alignment, input caret - its own discipline]
```

_RTL is logical CSS + bidi isolation + selective mirroring, verified on the running build — not a single `dir` attribute. Mirror direction-sensitive chrome (navigation, progress, chevrons); never mirror logos or photographic content. Hand the visual mirroring review to `web-design`; own the contract here._

## Decision Tree: TMS workflow / continuous translation?

Source out on merge, translations back automatically, CI guards completeness — never a manual copy-paste phase.

```mermaid
graph TD
  A[Wiring translation delivery] --> B{Translation is a phase or a pipeline?}
  B -- Manual export/import phase --> C[Catalog drifts; raw keys ship; a dropped placeholder crashes prod - fix the model first]
  B -- Pipeline --> D{Push source automatically?}
  C --> D
  D -- Yes, on merge --> E[TMS CLI/API pushes new source strings to the TMS per merge]
  D -- No --> F[Automate the push - a human-remembered export is the drift]
  E --> G{Pull translations automatically?}
  F --> G
  G -- Yes --> H[Pull completed translations back into the repo - PR or auto-commit]
  H --> I{CI guards on every PR?}
  I -- Yes --> J[Pseudo-locale + missing-key + placeholder-parity + ICU-syntax checks fail the build]
  I -- No --> K[Add the guards - green build must mean the localized build renders]
  J --> L{Cloud vs self-host TMS?}
  K --> L
  L -- Hosted, glossary/TM/screenshots wanted --> M[Crowdin / Lokalise / Phrase / Transifex / Smartling - verify-at-build]
  L -- Data residency / OSS mandate --> N[Weblate / Pootle self-hosted - budget the team to run it]
```

_Continuous translation = automated push on merge + automated pull + offline CI guards (pseudo-locale, missing keys, placeholder parity, ICU syntax). The TMS choice is secondary to the pipeline shape; a manual ritual drifts no matter which TMS sits behind it._

---

## Capability map (2026, `[verify-at-build]`)

| Layer | Options | Notes |
|---|---|---|
| i18n library (web JS/TS) | i18next, FormatJS / react-intl, LinguiJS | i18next for ecosystem + lazy-load; FormatJS for first-class ICU MessageFormat `[verify-at-build]` |
| i18n library (server) | gettext / ngettext, Rails i18n, `.NET` resx, ICU4J/ICU4C | gettext mature + PO-based; ICU libraries for full MessageFormat `[verify-at-build]` |
| i18n library (mobile/desktop) | Apple `.strings`/`.stringsdict`, Android `strings.xml` + plurals, Flutter ARB | Platform-native owns the catalog + plural quantities `[verify-at-build]` |
| Asymmetric-grammar | Fluent / FTL (Mozilla) | Per-locale grammar logic lives in the translation, not the code `[verify-at-build]` |
| Message format | ICU MessageFormat (plural / select / selectordinal, number/date skeletons) | The cross-platform standard for plural/gender/select; CLDR-backed `[verify-at-build]` |
| Locale data | CLDR via `Intl` (`PluralRules`, `NumberFormat`, `DateTimeFormat`, `Collator`, `ListFormat`) | The source of truth for plural rules + formatting; never hand-roll `[verify-at-build]` |
| File formats | PO/POT (gettext), XLIFF 1.2/2.0, Android XML, ARB, Apple `.strings`/`.stringsdict`, JSON | Pick the format the stack + TMS round-trip without loss `[verify-at-build]` |
| TMS (cloud) | Crowdin, Lokalise, Phrase, Transifex, Smartling | Push/pull, branch handling, glossary + translation memory, context/screenshots `[verify-at-build]` |
| TMS (self-host/OSS) | Weblate, Pootle | Self-hosted option; budget the team to run it `[verify-at-build]` |
| Pseudo-localization | i18next-pseudo, FormatJS pseudo-locale, custom transform, pseudolocalization-tool | Length-inflate + accent + bracket to catch hardcoded strings + truncation `[verify-at-build]` |
| Localization QA | Visual-diff (Percy/Chromatic/Playwright snapshots), in-context review in the TMS | Pair automated layout diffs with human in-context linguistic review `[verify-at-build]` |
| Local decision calculator | [`../scripts/i18n_calc.py`](../scripts/i18n_calc.py) (`pseudo` / `expansion` / `plural-coverage`) | Stdlib-only; pseudo-localize a string, estimate target-length growth + truncation risk, check an ICU plural set covers a locale's CLDR categories. Tables are `[verify-at-build]` — re-ground against `Intl.PluralRules`/CLDR |

_Reference: CLDR plural categories — `zero`, `one`, `two`, `few`, `many`, `other` (Arabic uses all six; English uses `one`/`other`). ICU MessageFormat covers `plural`, `select`, `selectordinal`, plus number/date skeletons. Always read plural rules and formatting from CLDR via `Intl`; re-verify any product/library specific before quoting it to a consumer. The `plural-coverage` subcommand of [`../scripts/i18n_calc.py`](../scripts/i18n_calc.py) mechanizes the "does this message cover the required categories" check, but its locale table is a dated convenience copy — `Intl.PluralRules` remains the source of truth._
