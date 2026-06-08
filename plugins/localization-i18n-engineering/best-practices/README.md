# localization-i18n-engineering — best-practice docs

Named, citable rules for the `localization-i18n-engineering` plugin's specialists. Each file is
**one rule**.

---

## Index

_6 rules._

| Doc | Status | Use when |
|---|---|---|
| [`never-concatenate-translatable-strings.md`](./never-concatenate-translatable-strings.md) | Absolute rule | Writing any user-facing message that includes a variable (name, count, date) |
| [`externalize-every-user-facing-string.md`](./externalize-every-user-facing-string.md) | Absolute rule | Writing any UI string, error message, ARIA label, or notification |
| [`use-icu-messageformat-for-plurals-and-gender.md`](./use-icu-messageformat-for-plurals-and-gender.md) | Absolute rule | Handling a message that varies by count, gender, or grammatical category |
| [`design-for-rtl-and-30-percent-text-expansion.md`](./design-for-rtl-and-30-percent-text-expansion.md) | Pattern | Designing or reviewing UI layout for any internationalizable product |
| [`pseudo-localize-in-ci-to-catch-i18n-bugs-early.md`](./pseudo-localize-in-ci-to-catch-i18n-bugs-early.md) | Pattern | Adding l10n quality gates to a CI/CD pipeline |
| [`keep-translatable-content-out-of-code.md`](./keep-translatable-content-out-of-code.md) | Pattern | Writing application logic that touches user-facing messages or locale data |

---

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — plugin team constitution.
- [`../knowledge/i18n-l10n-decision-trees.md`](../knowledge/i18n-l10n-decision-trees.md) — the
  decision trees + 2026 capability map.
- [`../../../docs/best-practices/README.md`](../../../docs/best-practices/README.md) — marketplace-wide best-practice docs.
