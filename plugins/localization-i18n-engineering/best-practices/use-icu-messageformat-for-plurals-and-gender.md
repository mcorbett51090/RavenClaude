# Use ICU MessageFormat for plurals and gender

**Status:** Absolute rule
**Domain:** Internationalization (i18n) — message authoring
**Applies to:** `localization-i18n-engineering`

---

## Why this exists

Every language has its own plural rules. English has two: `one` (singular) and `other` (plural).
This gives programmers the false impression that `if count === 1 … else …` is a correct
generalization. It is not:

- **Arabic** has **six** plural categories: `zero`, `one`, `two`, `few`, `many`, `other`.
- **Russian, Polish, Czech, Slovak** have **three or four**: `one`, `few`, `many`, `other` — with
  complex rules (Russian: numbers ending in 1 except 11 are `one`; ending in 2–4 except 12–14 are
  `few`; all others are `many`/`other`).
- **Japanese, Chinese, Korean, Thai** have **one** plural category (`other`) — but their sentence
  structure differs in ways that still require a full-sentence message, not a fragment.
- **Welsh** has **six** categories; **Maltese** has **four**.

An `if count === 1` branch is correct only for English (and a handful of other languages). Shipped
to Arabic without ICU plural rules, it produces wrong output for every number except 1.

The same principle applies to **gender**: constructing "He/She/They uploaded the document" with
an if-else is fragile, untestable, and incorrect for languages with grammatical gender agreement
that extends beyond the pronoun.

## How to apply

**Do:**

```json
// en-US.json — ICU MessageFormat plural
{
  "cart.item_count": "{count, plural, one{# item} other{# items}}",
  "inbox.unread_count": "{count, plural, zero{No unread messages} one{# unread message} other{# unread messages}}"
}

// ar-SA.json — translator provides all 6 Arabic plural categories
{
  "cart.item_count": "{count, plural, zero{لا عناصر} one{عنصر واحد} two{عنصران} few{# عناصر} many{# عنصرًا} other{# عنصر}}"
}

// ru-RU.json — translator provides Russian plural categories
{
  "cart.item_count": "{count, plural, one{# элемент} few{# элемента} many{# элементов} other{# элемента}}"
}
```

```json
// Gender select
{
  "activity.user_updated": "{gender, select, male{Он обновил} female{Она обновила} other{Обновлено}}"
}
```

**Don't:**

```js
// ❌ English-only plural logic — wrong for Arabic, Russian, Polish, Welsh…
const message = count === 1 ? "1 item" : `${count} items`;
const label = count === 1 ? t("item_singular") : t("item_plural");

// ❌ Ternary in JSX — same problem
<span>{count === 1 ? "message" : "messages"}</span>

// ❌ Gender with if-else — no path for non-binary, no grammatical agreement
if (user.gender === "male") { message = "He uploaded"; }
else { message = "She uploaded"; }
```

**Lookup CLDR plural rules before writing any plural message:**

https://www.unicode.org/cldr/charts/latest/supplemental/language_plural_rules.html

Identify every plural category (`zero`, `one`, `two`, `few`, `many`, `other`) required for each
target locale. Provide all required categories in the source message and in the translator notes —
translators need to know all categories are expected.

## Edge cases / when the rule does NOT apply

- **Ordinals** also have locale-specific forms — use `selectordinal` in ICU MessageFormat:
  `{position, selectordinal, one{#st} two{#nd} few{#rd} other{#th}}`. Same rule applies.
- **Languages with one plural category** (Japanese, Chinese, Korean) still require the `other`
  category to be present in the ICU selector. This is not an exception — the rule is satisfied
  when the translator provides the single `other` form.
- **Date/time and number formatting** are handled by `{date, date, ::skeleton}` and
  `{amount, number, ::skeleton}` ICU patterns, or by platform `Intl` APIs — not by ICU plural.
  Both still require locale-aware APIs, not hard-coded format strings.

## See also

- [`./never-concatenate-translatable-strings.md`](./never-concatenate-translatable-strings.md)
- CLDR Plural Rules: https://www.unicode.org/cldr/charts/latest/supplemental/language_plural_rules.html
- ICU MessageFormat syntax: https://unicode-org.github.io/icu/userguide/format_parse/messages/
- [`../skills/i18n-foundations-and-icu/SKILL.md`](../skills/i18n-foundations-and-icu/SKILL.md)

## Provenance

Codifies the CLDR / Unicode MessageFormat specification requirement and the consensus in every
major i18n framework (i18next, FormatJS, LinguiJS, Android plural resources, iOS `.stringsdict`,
Flutter ARB) that plural rules must follow the CLDR plural rule taxonomy, not an English-specific
binary branch.

---

_Last reviewed: 2026-06-08 by `claude`._
