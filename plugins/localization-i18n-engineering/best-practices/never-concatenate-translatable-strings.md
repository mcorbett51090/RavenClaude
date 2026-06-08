# Never concatenate translatable strings

**Status:** Absolute rule
**Domain:** Internationalization (i18n) — string authoring
**Applies to:** `localization-i18n-engineering`

---

## Why this exists

Every natural language has its own word order. English puts the verb before the object
("You have 3 messages"); Japanese reverses subject and verb; German moves the verb to the end
in subordinate clauses; Arabic reads right-to-left. When a programmer builds a sentence by
concatenating fragments (`"You have " + count + " messages"`), the fragments are translated
independently and then re-joined in English word order — producing grammatically incorrect output
in most target languages.

This is not a style concern: concatenation produces strings that are **untranslatable by
construction**. Translators receive three separate segments with no structural relationship and no
ability to reorder them.

## How to apply

Use a single named-parameter message for every sentence or phrase that includes a variable.

**Do:**

```json
// en-US.json
{
  "inbox.message_count": "{count, plural, one{You have # message} other{You have # messages}}"
}
```

```js
// application code
t("inbox.message_count", { count: 3 });
// → "You have 3 messages"
// Translator sees: "You have # messages" — one segment, full sentence, reorderable
```

```json
// de-DE.json — translator can reorder the noun phrase
{
  "inbox.message_count": "{count, plural, one{Sie haben # Nachricht} other{Sie haben # Nachrichten}}"
}
```

**Don't:**

```js
// Hard-coded English word order — cannot be translated correctly for German, Japanese, Arabic
const message = "You have " + count + " messages";
const message = `Hello ${username}, you have ${count} unread messages and ${alerts} alerts`;
```

The second example above constructs a sentence with three variables and fixed English word order.
Translated as three fragments, no language other than English will produce correct output.

## Edge cases / when the rule does NOT apply

- **Non-sentence concatenation of proper nouns:** `city + ", " + country` (e.g. "Paris, France")
  is a common exception where locale-specific separators and ordering are handled by locale data
  (e.g. `Intl.DisplayNames`), not by translation. Use locale-aware APIs here, not concatenation.
- **URL construction:** concatenating URL path segments is not translatable content and is exempt.
- **Internal / developer-only strings:** log messages and debug output that never appear in the
  UI are exempt; they are not translated.

## See also

- [`./externalize-every-user-facing-string.md`](./externalize-every-user-facing-string.md)
- [`./use-icu-messageformat-for-plurals-and-gender.md`](./use-icu-messageformat-for-plurals-and-gender.md)
- ICU MessageFormat syntax reference:
  https://unicode-org.github.io/icu/userguide/format_parse/messages/

## Provenance

Codifies the consensus in the ICU / Unicode MessageFormat specification and the i18n community
(Phraseapp best-practices guide, Mozilla l10n-best-practices, Google i18n developer guide) that
sentence fragmentation is the most common and most expensive i18n bug in localized software.

---

_Last reviewed: 2026-06-08 by `claude`._
