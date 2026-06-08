# String Catalog — {{PROJECT_NAME}}

> Copy this template into `docs/i18n/string-catalog.md` in the consumer project.
> Fill in every `{{PLACEHOLDER}}` section. Keep this document in sync with the source locale files.

---

## Project metadata

| Field | Value |
|---|---|
| **Project** | {{PROJECT_NAME}} |
| **Source locale** | {{SOURCE_LOCALE}} (e.g. `en-US`) |
| **Target locales** | {{TARGET_LOCALES}} (e.g. `de-DE`, `fr-FR`, `ja-JP`, `ar-SA`) |
| **String format** | {{FORMAT}} (JSON / XLIFF / ARB / PO / strings.xml / .strings) |
| **i18n library** | {{LIBRARY}} (i18next / FormatJS / gettext / platform-native) |
| **TMS** | {{TMS}} (Phrase / Lokalise / Crowdin / Transifex / none) |
| **Last updated** | {{DATE}} |
| **Owner** | {{OWNER_NAME}} |

---

## String namespace map

> List every namespace/bundle and what it contains. One row per namespace.

| Namespace | File path | Contents | Key count (approx.) |
|---|---|---|---|
| `common` | `src/i18n/en-US/common.json` | Shared UI strings (buttons, labels, errors) | ~50 |
| `{{namespace}}` | `{{file_path}}` | {{description}} | {{count}} |

---

## Key naming convention

**Convention:** {{CONVENTION}} (e.g. `snake_case`, `camelCase`, `dot.separated.path`)

**Rules:**

- Keys describe the **semantic role**, not the English content. `button.submit` not `click_here`.
- Namespace prefix: `{{namespace}}.{{component}}.{{element}}` (e.g. `auth.login.submit_button`).
- Do NOT encode the English text in the key. `user.greeting` not `hello_user_name`.
- Keys are permanent: once a key is released and translated, rename it only by deprecating the
  old key and adding a new one (renaming deletes the TM segment and forces re-translation).

---

## ICU MessageFormat reference for this project

> List every ICU pattern used in this project. Translators need this to understand the message shape.

### Plural messages

```
# Pattern:
{count, plural,
  zero  {No items}
  one   {# item}
  other {# items}
}

# Key: cart.item_count
# Target locales need: {{PLURAL_CATEGORIES_NEEDED}}
# CLDR plural rule reference: https://www.unicode.org/cldr/charts/latest/supplemental/language_plural_rules.html
```

### Gender select messages

```
# Pattern:
{gender, select,
  male   {He updated the document}
  female {She updated the document}
  other  {They updated the document}
}

# Key: activity.user_updated_document
```

### Ordinal messages

```
# Pattern:
{position, selectordinal,
  one   {#st place}
  two   {#nd place}
  few   {#rd place}
  other {#th place}
}

# Key: leaderboard.position
```

### Date / number skeletons

```
# Date skeleton (locale-aware format, not a hard-coded format string):
{date, date, ::yMMMd}

# Number with currency:
{amount, number, ::currency/USD sign-accounting}

# Relative time (use Intl.RelativeTimeFormat — not a message string):
# new Intl.RelativeTimeFormat(locale).format(-2, 'day') → "2 days ago"
```

---

## String inventory

> For large projects, link to the actual locale files instead of listing here.
> For small projects or key string documentation, list high-impact strings below.

### `common` namespace — sample entries

| Key | Source (en-US) | Notes for translators | Max length |
|---|---|---|---|
| `common.button.submit` | Submit | Keep short — button label | 15 chars |
| `common.button.cancel` | Cancel | Keep short — button label | 15 chars |
| `common.error.network` | A network error occurred. Please try again. | Formal tone | 80 chars |
| `{{key}}` | `{{source_string}}` | `{{translator_note}}` | `{{max_chars}}` |

---

## Text expansion budget

> Provide UI component guidance so translators and developers know the constraint.

| Component | English max length | Expansion budget | Notes |
|---|---|---|---|
| Primary button | 15 chars | +40 % → 21 chars | Truncates with `…` if exceeded |
| Navigation label | 20 chars | +30 % → 26 chars | Wraps to 2 lines on mobile |
| Error message | 120 chars | +50 % → 180 chars | Full-width container |
| Toast notification | 80 chars | +30 % → 104 chars | Auto-height |
| `{{component}}` | `{{chars}}` | `{{budget}}` | `{{notes}}` |

---

## RTL locale considerations

> Fill in for projects targeting Arabic (ar-*), Hebrew (he-IL), or other RTL locales.

- **RTL locales in scope:** {{RTL_LOCALES}} (e.g. `ar-SA`, `he-IL`)
- **Layout strategy:** CSS logical properties (`margin-inline-start`, `padding-block-end`).
- **`dir` switching:** `document.documentElement.dir = rtlLocales.includes(locale) ? 'rtl' : 'ltr'`.
- **Mirrored assets:** list any icons or images that must be mirrored for RTL here.

---

## Encoding

- **Source files:** UTF-8 without BOM.
- **Database collation:** `{{DB_COLLATION}}` (e.g. `utf8mb4_unicode_ci`).
- **HTTP headers:** `Content-Type: text/html; charset=UTF-8`.
- **Font coverage:** `{{FONT_STACK}}` covers scripts: `{{SCRIPTS_COVERED}}`.

---

## Extraction configuration

```bash
# Example: i18next-scanner
i18next-scanner --config i18next-scanner.config.js 'src/**/*.{js,jsx,ts,tsx}'

# Example: FormatJS
formatjs extract 'src/**/*.{ts,tsx}' --format simple --out-file src/i18n/en-US.json

# Example: xgettext (gettext)
find src -name "*.py" | xgettext -f - -o locale/messages.pot
```

---

## Change log

| Date | Change | Author |
|---|---|---|
| {{DATE}} | Initial catalog | {{AUTHOR}} |

---

_Template version: 0.1.0. Owned by `localization-i18n-engineering` plugin._
