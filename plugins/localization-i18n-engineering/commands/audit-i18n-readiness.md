---
description: "Audit a codebase for i18n readiness: hard-coded user-facing strings, string concatenation, if-count-1 plurals, locale-unaware date/number formatting, RTL/bidi gaps, and encoding issues. Produces a prioritized remediation backlog."
argument-hint: "[context, e.g. 'React SPA, i18next, targeting de-DE fr-FR ja-JP ar-SA']"
---

You are running `/localization-i18n-engineering:audit-i18n-readiness`. Use the `i18n-architect`
discipline and the `i18n-foundations-and-icu` skill.

## Steps

1. **Grep for hard-coded user-facing strings.** Search for string literals in render/return/template
   positions that are not routed through a translation function (`t()`, `i18n.t()`,
   `<FormattedMessage>`, `intl.formatMessage()`, `NSLocalizedString`, `getString(R.string.*)`).
   Document each hit with file, line, and string value.

2. **Grep for string concatenation used to build user-facing messages.** Search for `+` operator
   or template literals that combine two or more user-facing fragments (e.g. `"Hello " + name`).
   Each hit is an untranslatable sentence structure.

3. **Grep for `if count == 1` / `if count === 1` plural handling.** Every `if`/`ternary` that
   switches on `count === 1` or `count > 1` for a user-facing message is an i18n bug. List all
   occurrences with file and line.

4. **Grep for locale-unaware date, number, and currency formatting.** Search for:
   - `new Date().toLocaleDateString()` / `.toLocaleString()` / `.toLocaleTimeString()` without a
     locale argument.
   - Hard-coded format strings like `"MM/DD/YYYY"`, `"dd/MM/yyyy"`.
   - Currency symbols hard-coded as string literals (`"$"`, `"€"`, `"£"`).
   - `Intl.NumberFormat()` or `Intl.DateTimeFormat()` without a locale argument.

5. **Audit RTL/bidi readiness.** Check for:
   - Physical CSS properties (`margin-left`, `padding-right`, `left:`, `right:`) in layout-critical
     stylesheets — should be logical properties.
   - Missing `dir` attribute on the root element or per-locale `dir` switching logic.
   - Hard-coded `text-align: left` or `text-align: right`.

6. **Audit encoding.** Spot-check:
   - Database schema collation (if accessible) — `utf8mb4` for MySQL.
   - HTTP response headers (if accessible) — `charset=UTF-8`.
   - HTML `<meta charset>` declaration position (must be first in `<head>`).
   - Font stack coverage for target scripts.

7. **Classify and prioritize findings.** For each category, assign severity:
   - **Critical:** hard-coded strings, string concatenation, `if count === 1` (will break every
     non-English locale).
   - **High:** locale-unaware formatting (produces platform-default locale output).
   - **Medium:** RTL/bidi gaps (breaks RTL locales).
   - **Low:** encoding gaps (may cause character rendering issues in specific locales).

8. **Produce the remediation backlog.** For each finding group, write a task:
   - What to do (extract string, replace with ICU, use `Intl.NumberFormat(locale)`).
   - Effort estimate (small / medium / large).
   - The `i18n-foundations-and-icu` skill step that applies.

9. **Emit the Structured Output block** with findings summary, severity counts, and handoff
   recommendations (l10n-pipeline-engineer for TMS setup; localization-qa-engineer for CI gates).
