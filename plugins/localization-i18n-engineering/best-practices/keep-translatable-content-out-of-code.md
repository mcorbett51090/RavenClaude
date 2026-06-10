# Keep translatable content out of code

**Status:** Pattern
**Domain:** Internationalization (i18n) — application logic
**Applies to:** `localization-i18n-engineering`

---

## Why this exists

Application logic that **branches on translated string values** is fragile in two ways:

1. **It breaks silently when translation changes.** If a conditional reads
   `if (label === "Yes")` and the German translation of "Yes" changes from "Ja" to "Ja!" (a
   punctuation tweak), the conditional silently stops working in German. There is no type error,
   no test failure, no compiler warning.

2. **It is untestable across locales.** A unit test written in English cannot cover the German
   code path unless it hard-codes the German string value — creating a test that is tightly coupled
   to a translation file and breaks whenever a translator makes a style change.

The same problem applies to **storing locale-specific formatted values** (dates, numbers,
currencies) in a database column and then parsing them back. A date stored as `"12/31/2024"` in
`en-US` format is ambiguous or invalid in `de-DE` format; a price stored as `"$1,234.56"` is
not parseable in a locale that uses `.` as the thousands separator and `,` as the decimal.

## How to apply

**Do:**

```js
// ✅ Branch on a locale-invariant message key or locale code — not on the translated value
const confirmed = messageKey === "dialog.confirm.yes_option";
// or
const confirmed = selectedOptionId === "yes"; // an application-level constant

// ✅ Store dates and numbers in locale-invariant formats in the database
// Dates: ISO 8601 (2024-12-31) in UTC
// Numbers: plain numeric type (no formatting)
// Currencies: integer minor units (1234 cents, not "$12.34")

// ✅ Format for display at the presentation layer only, using the user's locale
const displayDate = new Intl.DateTimeFormat(locale, { dateStyle: "long" }).format(date);
const displayPrice = new Intl.NumberFormat(locale, {
  style: "currency",
  currency: "USD",
}).format(amountInDollars);
```

**Don't:**

```js
// ❌ Branch on a translated string value — breaks when translation changes
if (buttonLabel === "Save") { submitForm(); }
if (statusText === "Pending") { showSpinner(); }

// ❌ Parse a locale-formatted string back to a number or date
const amount = parseFloat(formattedPrice.replace("$", "").replace(",", ""));
const date = new Date(formattedDate); // locale-sensitive parsing

// ❌ Store a locale-formatted value in a DB column
INSERT INTO orders (display_price) VALUES ('$1,234.56');
INSERT INTO events (event_date_display) VALUES ('Dec 31, 2024');
```

**Locale-aware branching — use locale codes, not translated text:**

```js
// ✅ If logic depends on locale, branch on the locale code
const isRtl = ["ar", "he", "fa", "ur"].includes(locale.split("-")[0]);

// ✅ If logic depends on plural category, use CLDR plural rules via the i18n library
// — don't re-implement plural logic in application code
const pluralCategory = i18n.getChoiceIndexOrKey(count); // library-provided
```

**Where to format:**

- Format dates, times, numbers, and currencies **only** in the UI rendering layer.
- Store all persistent values in locale-invariant formats (ISO 8601 for dates, numeric for
  numbers, ISO 4217 currency code + minor-unit integer for money).
- Never pass a formatted string as an API parameter — pass the raw value and let the client format
  for display.

## Edge cases / when the rule does NOT apply

- **Locale-specific UI components:** a date-picker component that adapts its calendar layout to
  the locale (`firstDayOfWeek`) branches on locale code or CLDR data — this is correct and
  expected. Locale-code branching is fine; translated-string-value branching is not.
- **Content management systems (CMS):** CMS-sourced content (marketing copy, help articles) may
  be stored and retrieved in locale-specific variants by locale key (`en-US`, `de-DE`) — this is
  storage of content by locale code, not branching on translated text values.

## See also

- [`./externalize-every-user-facing-string.md`](./externalize-every-user-facing-string.md)
- [`./never-concatenate-translatable-strings.md`](./never-concatenate-translatable-strings.md)
- ECMA-402 (Intl API): https://tc39.es/ecma402/
- ISO 8601 date format: https://www.iso.org/iso-8601-date-and-time-format.html
- ISO 4217 currency codes: https://www.iso.org/iso-4217-currency-codes.html

## Provenance

Codifies the standard separation-of-concerns principle applied to i18n: presentation formatting
belongs in the UI layer; storage and business logic belong in locale-invariant formats. Documented
in the ECMA-402 rationale, the Java `java.text.Format` design intent, and the Mozilla l10n
engineering guide.

---

_Last reviewed: 2026-06-08 by `claude`._
