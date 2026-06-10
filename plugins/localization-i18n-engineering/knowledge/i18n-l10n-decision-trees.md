# i18n / l10n Engineering — Decision Trees + 2026 Capability Map

> Canonical knowledge bank for `localization-i18n-engineering`. **Traverse the relevant Mermaid
> tree top-to-bottom before choosing** — the proactive complement to the Capability Grounding
> Protocol. Volatile product/version facts in the capability map carry a retrieval date and a
> re-verify-at-use rider.

---

## Decision Tree 1: i18n Library / Format Choice

```mermaid
flowchart TD
  A[What is the platform?] --> B{Web frontend?}
  A --> C{Mobile?}
  A --> D{Backend / server-side?}

  B -->|React / Vue / Svelte| E{Need ICU MessageFormat + TypeScript + large ecosystem?}
  E -->|Yes| F[i18next + react-i18next<br/>Most widely adopted; large plugin ecosystem;<br/>formatjs-compatible extraction tools]
  E -->|ICU MessageFormat is the priority + FormatJS already in use| G[FormatJS / react-intl<br/>Strict ICU MessageFormat 2.0 compliance;<br/>smaller API surface; better TypeScript types]
  E -->|Minimal — simple key:value only, no plurals/gender needed| H[vue-i18n or Svelte-i18n<br/>Framework-native; evaluate ICU support first]

  B -->|Angular| I[Angular i18n (built-in) or ngx-translate<br/>Angular i18n: ICU native; extraction: ng extract;<br/>ngx-translate: simpler but weaker ICU]

  C -->|Android| J[Android Resources (strings.xml / plurals.xml)<br/>Native platform format; extraction: Gradle plugin]
  C -->|iOS / macOS| K[iOS Localizable.strings + .stringsdict<br/>Or: newer .xcstrings catalog (Xcode 15+)]
  C -->|Flutter| L[Flutter ARB (Application Resource Bundle)<br/>gen-l10n; ICU MessageFormat supported]
  C -->|React Native| F

  D -->|Python| M[gettext / Babel<br/>PO/POT files; xgettext extraction; wide TMS support]
  D -->|Node.js| F
  D -->|Java / Spring| N[Java ResourceBundle + MessageFormat<br/>Or: Spring MessageSource + ICU4J]
  D -->|.NET| O[.NET Resource Files (.resx)<br/>Or: Humanizer for plurals; limited ICU support]

  F --> P{TMS extraction tool compatible?}
  G --> P
  P -->|Yes| Q[Configure extraction CI step<br/>→ l10n-pipeline-and-tms skill]
  P -->|No| R[Choose TMS with format support OR add a conversion step]
```

**Leaf rule:** ICU MessageFormat support is the primary selection criterion — verify that the
library supports the full plural / gender / select syntax before committing. i18next and FormatJS
are the two proven web choices as of 2026 [verify-at-use]. For mobile, use the platform-native
format; it has the widest TMS compatibility. For a server-side Python/Java project, gettext/PO or
Java ResourceBundle are the safest choices for TMS portability.

---

## Decision Tree 2: Machine Translation vs. Human Translation

```mermaid
flowchart TD
  A[What type of content is it?] --> B{Legal / compliance / contract text?}
  B -->|Yes| C[Human translation only.<br/>No MT — liability risk.]
  B -->|No| D{Marketing / brand / creative copy?}
  D -->|Yes| E[Human translation preferred.<br/>MT + heavy post-edit acceptable if budget-constrained.]
  D -->|No| F{User-facing UI microcopy — buttons, labels, error messages?}
  F -->|Yes| G{Quality tier — consumer product or internal tool?}
  G -->|Consumer product — brand-sensitive| H[MT (DeepL or Google Translate Neural MT) + human post-edit.<br/>Post-edit tier: light (fluency) for high-TM-leverage segments;<br/>full for no-match segments.]
  G -->|Internal tool — quality threshold is functional| I[MT-only with a human spot-check pass.<br/>Flag obvious errors with automated QA checks.]
  F -->|No| J{Documentation / help content?}
  J -->|Yes| K[MT + human post-edit (full for user-guide sections;<br/>light for reference/API docs).]
  J -->|No| L{Short, repetitive, high-TM-leverage content (release notes, changelogs)?}
  L -->|Yes| M[MT-only; TM leverage reduces cost; automated QA sufficient.]
  L -->|No| N[Evaluate content-specifically against quality threshold and cost.]
  H --> O[Track MT quality with BLEU/TER or translator acceptance rate]
  I --> O
  K --> O
```

**Leaf rule:** legal text never goes through MT without a qualified human reviewer. For UI
microcopy in a consumer product, MT + post-edit (DeepL or Google Cloud Translation Neural MT
[verify-at-use]) is the current cost-quality optimum. The content tier, not the translation
volume, drives the MT vs. human decision. Always track MT quality via translator acceptance rate
or spot-check scoring; do not assume MT output is acceptable without measurement.

---

## Decision Tree 3: Pseudo-Localization in CI

```mermaid
flowchart TD
  A[What pseudo-loc variants do you need?] --> B{Does the project target any RTL locale?}
  B -->|Yes (ar-SA, he-IL, fa-IR)| C[Include bidi/RTL pseudo-locale variant.<br/>Wrap strings with Unicode RLI/PDF markers.]
  B -->|No| D[Skip bidi variant for now]

  A --> E{Does the project target any long-text locale?}
  E -->|Yes (de-DE, fi-FI, hi-IN, cs-CZ)| F[Include expansion pseudo-locale (140% of English length).<br/>This is the highest-ROI variant — run it first.]
  E -->|No| G[Still run expansion pseudo — it also catches hard-coded strings]

  F --> H[Always run: Accent pseudo-locale<br/>Detects un-externalized hard-coded strings]
  G --> H
  C --> H

  H --> I{What type of application?}
  I -->|Web SPA| J[Tool: pseudolocale npm / @formatjs/cli pseudo<br/>Generate: en-XA (expansion), en-XB (bidi)<br/>Test: Playwright screenshot diff against pseudo-locale]
  I -->|Android| K[Enable en-XA and ar-XB pseudo-locales in Build Variants<br/>Run Espresso / screenshot tests against en-XA]
  I -->|iOS| L[Custom script: transform .strings files to pseudo<br/>Run XCUITest against pseudo-locale scheme]
  I -->|Flutter| M[Custom ARB transformer; run widget tests against pseudo ARB]
  I -->|Server-rendered (SSR)| N[Transform locale file; render with pseudo-locale server-side;<br/>Compare HTML output for hard-coded strings]

  J --> O{Is the pseudo-loc CI gate blocking?}
  K --> O
  L --> O
  M --> O
  N --> O
  O -->|No — advisory only| P[⚠ Warning: a non-blocking gate gets ignored.<br/>Make it blocking on main-merge at minimum.]
  O -->|Yes — blocking on PR| Q[✅ Correct configuration. Add to required checks list.]
```

**Leaf rule:** always run the expansion pseudo-locale variant as the minimum — it catches both
hard-coded strings (not transformed) and overflow (padded string exposes container constraints).
Add the bidi variant when the project targets any RTL locale. The gate must be blocking; a
non-blocking pseudo-loc gate is theater. Do not commit pseudo-locale files to the repo — generate
them at CI time.

---

## 2026 Capability Map — i18n / l10n Tool Landscape

_Retrieved 2026-06-08. Product versions, pricing tiers, and feature availability are volatile —
re-verify at use before making procurement or architecture decisions._

### i18n Libraries (web)

| Library | ICU MessageFormat | Extraction CLI | TypeScript | Bundle size | Notes |
|---|---|---|---|---|---|
| **i18next** | Yes (via `i18next-icu` plugin) | `i18next-scanner`, `i18next-parser` | Good | ~15 kB gzip | Dominant; large ecosystem; most TMS tools support it natively [verify-at-use] |
| **FormatJS / react-intl** | Full ICU MF2 | `formatjs extract` | Excellent | ~12 kB gzip | Strict ICU compliance; ECMA-402 aligned; smaller but opinionated API [verify-at-use] |
| **LinguiJS** | Yes | `lingui extract` | Good | ~6 kB gzip | Compiles to runtime-free string maps; pseudo-locale command built in [verify-at-use] |
| **vue-i18n** | Yes (v9+) | `vue-i18n-extract` | Good | ~10 kB gzip | Vue 3 native; ICU MF in v9+ [verify-at-use] |
| **Angular i18n** | Yes (built-in) | `ng extract-i18n` | Excellent | Runtime included | Tight Angular integration; XLIFF output natively [verify-at-use] |

### i18n — Mobile / Cross-platform

| Platform | Format | ICU Support | Notes |
|---|---|---|---|
| **Android** | `strings.xml` / `plurals.xml` | Via `android.icu.text.MessageFormat` (API 24+) | Native CLDR plural rules via `<plurals>` element |
| **iOS / macOS** | `.strings` / `.stringsdict` / `.xcstrings` | Limited — no native ICU; use `NSLocalizedString` + custom | Xcode 15+ `.xcstrings` catalog improves workflow [verify-at-use] |
| **Flutter** | ARB (Application Resource Bundle) | ICU MessageFormat via `flutter_localizations` | `gen-l10n` generates typed Dart classes [verify-at-use] |
| **React Native** | JSON (via i18next or LinguiJS) | Same as web library chosen | No platform-native i18n; library-dependent |

### TMS (Translation Management Systems)

_Pricing and feature tiers change frequently — verify before procurement [verify-at-use]._

| TMS | Strength | Format support | MT connectors | CI/CD integration | Notes |
|---|---|---|---|---|---|
| **Phrase** (formerly Phrase Strings; acquired Transifex 2022) | Mature, enterprise-grade; strong branching support | XLIFF, JSON, ARB, PO, strings.xml, .strings, and more | DeepL, Google, Amazon Translate, Microsoft | GitHub Actions, CLI, API | Phrase and Transifex now share infrastructure post-acquisition; verify product roadmap [verify-at-use] |
| **Lokalise** | Developer-friendly; strong GitHub/GitLab integration | XLIFF, JSON, ARB, PO, and more | DeepL, Google, Amazon Translate | GitHub Actions, CLI, webhooks | Good TypeScript SDK; per-key commenting for translator context [verify-at-use] |
| **Crowdin** | Open-source community friendly; large free tier | XLIFF, JSON, PO, ARB, strings.xml, and more | DeepL, Google, Microsoft Translator | GitHub, GitLab, Bitbucket Actions; CLI | Strong GitHub integration; automated PR-based string sync [verify-at-use] |
| **Transifex** | Long-established; good for content-heavy projects | XLIFF, PO, JSON, strings.xml, and more | DeepL, Google | CLI, API, webhooks | Now under Phrase ownership — evaluate roadmap alignment [verify-at-use] |

### Machine Translation Engines

| Engine | Strength | Notes |
|---|---|---|
| **DeepL** | Highest quality for European languages (en, de, fr, es, it, nl, pl, pt, ru, ja, zh) | API available; supported by all major TMS [verify-at-use] |
| **Google Cloud Translation (Neural MT)** | Broad language coverage (100+ languages); fast | Batch and real-time API; integrated in most TMS [verify-at-use] |
| **Amazon Translate** | AWS-native; good for AWS-centric pipelines | 75+ languages; custom terminology support [verify-at-use] |
| **Microsoft Translator** | Azure-native; good Office/M365 ecosystem fit | 100+ languages; custom model training available [verify-at-use] |

### Pseudo-Localization Tools

| Tool | Platform | Notes |
|---|---|---|
| **pseudolocale** (npm) | Web | Expansion + accent variants; simple CLI [verify-at-use] |
| **@formatjs/cli pseudo** | Web / FormatJS | Built-in pseudo command for FormatJS projects [verify-at-use] |
| **LinguiJS pseudo** | Web / LinguiJS | Native pseudo-locale command [verify-at-use] |
| **Android en-XA / ar-XB** | Android | Device-level pseudo-locales; no config required [verify-at-use] |

### Standard References

| Resource | URL | Notes |
|---|---|---|
| CLDR Plural Rules | https://www.unicode.org/cldr/charts/latest/supplemental/language_plural_rules.html | Normative; use before writing ICU plural selectors |
| ICU MessageFormat syntax | https://unicode-org.github.io/icu/userguide/format_parse/messages/ | Canonical syntax reference |
| MessageFormat 2.0 (MF2) | https://github.com/unicode-org/message-format-wg | Emerging ECMA TC39 / Unicode standard; not yet universally supported [verify-at-use] |
| ECMA-402 (Intl API) | https://tc39.es/ecma402/ | Web standard for locale-aware formatting |
| Unicode Bidirectional Algorithm | https://unicode.org/reports/tr9/ | Normative reference for bidi/RTL |

> Provenance: library popularity data from npm download trends and GitHub stars (2026-06-08,
> volatile — re-verify at use). TMS feature sets from vendor documentation (2026-06-08).
> No invented products; all names are real products with public documentation.

---

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — team constitution and seams.
- [`../best-practices/README.md`](../best-practices/README.md) — the named, citable rules.
- Neighbour decision trees: `frontend-engineering`, `mobile-engineering`,
  `technical-writing-docs`.

_Last reviewed: 2026-06-08 by `claude`._
