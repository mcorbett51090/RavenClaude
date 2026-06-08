# Externalize every user-facing string

**Status:** Absolute rule
**Domain:** Internationalization (i18n) — string externalization
**Applies to:** `localization-i18n-engineering`

---

## Why this exists

A string that is hard-coded in source code cannot be translated without modifying the code. Once
a product ships to more than one locale, every hard-coded user-facing string is a bug: it forces
either a code change per locale (not scalable) or a release with un-translated content (not
acceptable for a professional product). The cost of fixing a hard-coded string discovered
post-translation is an order of magnitude higher than externalizing it during initial development.

The rule is also a forcing function for better design: externalizing a string requires giving it
a key, which forces the developer to name the semantic role of the string (`error.network_timeout`
rather than `"An error occurred"`), which makes the codebase more readable and the translation
more accurate.

## How to apply

**Do:**

```js
// ✅ Externalized — translatable
const label = t("user.profile.save_button");
// locale file: { "user.profile.save_button": "Save profile" }

// ✅ ARIA label externalized
<button aria-label={t("nav.close_menu_button")}> ... </button>

// ✅ Error message externalized
throw new UserVisibleError(t("error.validation.email_invalid"));

// ✅ Page title externalized
document.title = t("page.settings.title");

// ✅ Notification text externalized
showToast(t("notification.changes_saved"));
```

**Don't:**

```js
// ❌ Hard-coded — not translatable
const label = "Save profile";
<button aria-label="Close menu"> ... </button>
throw new Error("Invalid email address");
document.title = "Settings";
showToast("Your changes have been saved");
```

**What must be externalized:**

- All text rendered in the UI (button labels, headings, paragraph copy, form labels, placeholders).
- Error messages that are shown to the user (validation errors, network errors, permission errors).
- Notification and toast messages.
- ARIA labels and `title` attributes used for accessibility.
- Browser `<title>` and `<meta name="description">` content.
- Email subject lines and body text (if generated in code for the user).
- Alt text for images (unless the image is locale-specific and handled by locale-specific assets).

**What is exempt:**

- Log messages and debug output (developer-only, not user-facing).
- Internal identifiers, slugs, and route paths.
- API response field names.
- Test fixture strings that never appear in the UI.

## Edge cases / when the rule does NOT apply

- **Developer-facing tooling:** CLI tools, linter output, compiler error messages that target
  developers (not end-users) may remain in English if the developer audience is universally English.
  This is a narrow exception — user-facing tools and IDEs with broad international audiences must
  still be externalized.
- **Prototype / throwaway code:** in a true throwaway prototype (not shipping to users), the
  overhead may be deferred. Once the code is on the path to production, externalize before merge.

## See also

- [`./never-concatenate-translatable-strings.md`](./never-concatenate-translatable-strings.md)
- [`./use-icu-messageformat-for-plurals-and-gender.md`](./use-icu-messageformat-for-plurals-and-gender.md)
- [`../skills/i18n-foundations-and-icu/SKILL.md`](../skills/i18n-foundations-and-icu/SKILL.md)
  (Step 1: Audit the externalization surface)

## Provenance

Codifies the foundational requirement of every i18n framework and every major platform's
localization guide (Apple HIG, Android developer guide, W3C Internationalization best practices,
Mozilla L10n best practices). The "every user-facing string" scope is the consistent consensus
across all platforms.

---

_Last reviewed: 2026-06-08 by `claude`._
