# i18n Architecture — Decision

> Output of `i18n-architect` / the `i18n-architecture` skill. Fill every section; an empty
> "Plural/RTL plan" or "Fallback chain" section means the architecture isn't decided yet.

## 1. Locale matrix (what we ship)

| Locale | Script / direction | Plural categories (CLDR) | Notes |
|---|---|---|---|
| <e.g. en-US> | Latin / LTR | one, other | source locale |
| <e.g. de-DE> | Latin / LTR | one, other | ~35% length expansion |
| <e.g. ar> | Arabic / RTL | zero…other (6) | RTL + 6 plural forms |
| <e.g. ja> | CJK / LTR | other | no spaces, different line-break |

_If the matrix isn't decided, that's open question #1 — "add a language" should be config, not a project._

## 2. Library + message-format model

| Layer | Decision | Why |
|---|---|---|
| i18n library | <i18next / FormatJS·react-intl / gettext / Fluent / platform-native> | <ecosystem / ICU support / platform owns catalog> |
| Message format | <ICU MessageFormat / platform-native plurals> | <translator owns grammar per CLDR> |
| Formatting | <Intl: DateTimeFormat / NumberFormat / Collator / ListFormat> | <CLDR is the source of truth — never hand-rolled> |

## 3. Translation-key strategy

- **Keys:** <stable IDs + English default value / source-text-as-key (justify)>
- **Namespacing:** <feature.screen.element / flat>
- **Interpolation/placeholder convention:** <named placeholders, ICU syntax>
- **Plural/select keys:** <one ICU message per key — no concatenation>
- **Context for translators:** <comment / screenshot / char-limit attached>

## 4. Locale data + fallback chain

- **Fallback chain:** <e.g. pt-BR → pt → en>
- **Locale negotiation:** <how the active locale is chosen>
- **Bundled vs. lazy-loaded:** <which locale data ships vs. loads on demand>

## 5. RTL / bidi + formatting plan

| Concern | Approach |
|---|---|
| CSS | <logical properties: margin-inline-start, text-align: start> |
| Bidi isolation | <isolate interpolated values (Unicode isolates / `<bdi>`)> |
| Mirroring | <which icons/controls mirror — route visual to web-design> |
| Date/number/currency | <Intl/CLDR per locale> |

## 6. Explicit non-goals

- <e.g. we will not support locales outside the matrix this release>
- <e.g. we will not hand-roll any formatting>

## 7. Build handoff

| What | Routed to |
|---|---|
| The i18n call implementation in the UI | `frontend-engineering` / `mobile-engineering` |
| String extraction + TMS + CI continuous translation | `localization-engineer` |
| Pseudo-localization + the QA matrix | `localization-qa` |
| The mirrored RTL layout + translated-layout design | `web-design` |
| Locale-derived PII / data residency | `data-governance-privacy` |

---

```
Status: ...
Files changed: ...
Locale coverage: ...
i18n posture: ...
Handoff to build teams: ...
Open questions: ...
Grounding checks performed: ...
```
