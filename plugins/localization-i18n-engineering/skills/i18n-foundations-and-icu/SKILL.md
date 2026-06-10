---
name: i18n-foundations-and-icu
description: "Core internationalization foundations: string externalization strategy, ICU MessageFormat for plurals and gender selects, CLDR plural rules, locale-aware formatting via ECMA-402/Intl APIs, RTL/bidi layout design, Unicode encoding, and text expansion budget planning."
---

# i18n Foundations and ICU MessageFormat

**Purpose:** give every application the structural foundations it needs to be localized correctly —
string externalization, ICU MessageFormat, locale-aware formatting, RTL/bidi, Unicode encoding, and
text expansion awareness.

## The operating loop

1. **Audit the externalization surface.** Grep the codebase for user-facing string literals in
   render, return, setText, `$t`, or template expression positions. Every hit is an i18n bug.
   Scope the extraction: UI strings, error messages, validation messages, notification text, ARIA
   labels, `<title>`, and `<meta>` description — but not log messages, internal IDs, or test
   fixtures.

2. **Choose a string format and key convention.** Select the format for the project type (see the
   decision tree). Establish a key-naming convention: flat keys (`user.profile.title`) vs. nested
   objects (`{ user: { profile: { title: "…" } } }`). Flat keys are more portable for TMS tools;
   nested objects map naturally to namespaces. Pick one; document it.

3. **Apply ICU MessageFormat for every message that varies.** Plural, gender, and select messages
   require ICU syntax — not branching in application code.

   - **Plural:** `{count, plural, one{# item} other{# items}}`. For target locales with more plural
     categories (Arabic: `zero`, `one`, `two`, `few`, `many`, `other`; Russian: `one`, `few`,
     `many`, `other`), provide all required categories. Consult CLDR plural rules at
     https://www.unicode.org/cldr/charts/latest/supplemental/language_plural_rules.html.
   - **Gender select:** `{gender, select, male{He uploaded} female{She uploaded} other{They uploaded}}`.
   - **Ordinal:** `{position, selectordinal, one{#st} two{#nd} few{#rd} other{#th}}`.
   - **Date/time skeleton:** `{date, date, ::yMMMd}` (CLDR skeleton; not a hard-coded format string).
   - **Number skeleton:** `{amount, number, ::currency/USD sign-accounting}`.

4. **Replace all `new Date().toLocaleString()` calls with explicit locale.** Pass the user's
   current locale: `new Date().toLocaleString(locale, options)`. Similarly for `Intl.NumberFormat`
   and `Intl.RelativeTimeFormat`. Never call these without a locale argument.

5. **Audit for RTL/bidi readiness.** Check that:
   - Layout uses CSS logical properties (`margin-inline-start`, `padding-block-end`, `inset-inline`)
     rather than physical properties (`margin-left`, `padding-bottom`, `left`).
   - The root element sets `dir` dynamically from the locale: `document.documentElement.dir = isRTL ? 'rtl' : 'ltr'`.
   - Icons and directional images are mirrored for RTL (back arrow, progress indicators).
   - Text alignment uses `text-align: start` not `text-align: left`.

6. **Audit encoding.** Verify UTF-8 end-to-end:
   - Source files, build outputs: UTF-8 (no BOM for HTML/CSS/JS).
   - Database: `utf8mb4` (MySQL) or `UTF8` collation (PostgreSQL default). `utf8` in MySQL is
     only 3-byte and cannot store emoji or supplementary characters.
   - HTTP headers: `Content-Type: text/html; charset=UTF-8`.
   - HTML `<meta charset="UTF-8">` as the first child of `<head>`.
   - Font: verify the target scripts are covered by the font stack.

7. **Plan for 30–50 % text expansion.** UI containers should accommodate text up to 150 % of the
   English source length without truncation or overflow. Use pseudo-localization (see
   `localization-qa-and-pseudo-loc`) to verify. Avoid `max-width` constraints that clip translated
   text; prefer `min-width` + `overflow: visible` or `word-break: break-word`.

## Format and library reference

See the `Library/format choice` decision tree in
[`../../knowledge/i18n-l10n-decision-trees.md`](../../knowledge/i18n-l10n-decision-trees.md) and
the 2026 capability map for current library versions [verify-at-use].

## Anti-patterns

- String concatenation to build a user-facing message.
- `if (count === 1)` plural handling — correct only for a small set of languages.
- `toLocaleDateString()` / `toLocaleString()` without a locale argument.
- Hard-coded date format strings (`"MM/DD/YYYY"`).
- Storing locale-specific formatted values in the database.
- Mixing translated text with logic (`if (label === "Yes")`).

## Output

A codebase i18n audit (list of hard-coded strings, missing ICU, bad formatting calls, RTL gaps,
encoding issues) + a remediation backlog with effort estimates. Reference
[`../../templates/string-catalog.md`](../../templates/string-catalog.md) for the catalog scaffold.
