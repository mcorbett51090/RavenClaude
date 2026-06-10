# Pseudo-localize in CI to catch i18n bugs early

**Status:** Pattern
**Domain:** Localization QA — CI quality gates
**Applies to:** `localization-i18n-engineering`

---

## Why this exists

A hard-coded string, a layout overflow in German, or a broken bidi alignment in Arabic discovered
after translation has been ordered costs roughly:

1. A translator change-request fee (or wasted work on a string that will be rewritten).
2. A development sprint to fix the underlying i18n bug.
3. A re-translation pass for the corrected string.
4. A release delay if the bug is discovered close to ship date.

The same bug discovered by a pseudo-localization CI gate costs: a CI minute and a developer hour
to fix before any translation is ordered. The ROI is straightforward.

Pseudo-localization is a **deterministic transformation** of source strings that preserves the
message structure but renders it visually distinct — typically by accenting vowels, padding the
string to simulate expansion, or wrapping in bidi override markers. It requires no translators
and no TMS. It runs in CI on every pull request.

## How to apply

**Do:**

1. **Run the expansion pseudo-locale variant on every PR.** The expansion variant (e.g., wraps
   the string in `[` / `]` and pads to ~140 % of source length) catches both:
   - Hard-coded strings (they are not in the locale file and are not transformed — they stand out
     visually against the pseudo-transformed surrounding text).
   - UI overflow (the padded string fills containers that were sized to English text).

2. **Make the gate blocking.** A non-blocking pseudo-loc job (advisory / warning) gets ignored
   within one sprint. The gate must be a required PR check that blocks merge on failure.

3. **Add the bidi variant when any RTL locale is in scope.** The bidi pseudo-locale (Unicode RLI
   markers or word-reversal) surfaces RTL layout bugs — `dir` attribute not applied, physical CSS
   properties, icon mirroring missing — without needing a full Arabic or Hebrew translation.

4. **Generate pseudo-locale files at CI time; do NOT commit them.** Pseudo-locale files are
   derived artifacts. Add them to `.gitignore`. Regenerating them in CI ensures they always
   reflect the current source strings.

5. **Integrate screenshot or snapshot testing.** Run Playwright, Cypress, or Storybook visual
   snapshots against the pseudo-locale build. A screenshot diff between the English build and the
   pseudo-locale build mechanically surfaces overflow and truncation without human visual review
   on every PR.

**Configuration example (pseudolocale npm, i18next):**

```bash
# Generate expansion pseudo-locale from source JSON
npx pseudolocale \
  --input public/locales/en-US/common.json \
  --output public/locales/en-XA/common.json \
  --strategy expand

# Run tests against the pseudo-locale
VITE_APP_LOCALE=en-XA npm test
```

**Don't:**

- Run pseudo-localization only pre-release or on demand — by then, the translation budget has
  been partially committed and the bug fix requires a change-request round-trip.
- Commit pseudo-locale files to the repo — they bloat the repo and create stale-artifact risk.
- Suppress the CI gate globally to "fix it later" — it will never be prioritized when deprioritized.

## Edge cases / when the rule does NOT apply

- **Projects with no translation requirement at all:** if a project will permanently be single-
  locale and English-only, pseudo-localization adds friction without ROI. The rule applies once
  any non-English locale is planned or in progress.
- **Projects in a true pre-alpha prototype phase:** defer until the UI is stable enough that a
  pseudo-loc failure is actionable. Add the gate before the first translation order.
- **Server-rendered pages with no component-level tests:** pseudo-loc still applies, but screenshot
  diffing requires a running server. Use snapshot tests or a dedicated pseudo-locale render job
  instead.

## See also

- [`./design-for-rtl-and-30-percent-text-expansion.md`](./design-for-rtl-and-30-percent-text-expansion.md)
- [`../skills/localization-qa-and-pseudo-loc/SKILL.md`](../skills/localization-qa-and-pseudo-loc/SKILL.md)
- [`../templates/l10n-ci-gate.md`](../templates/l10n-ci-gate.md) — the CI gate scaffold

## Provenance

Pseudo-localization as an i18n testing technique is documented in IBM's Globalization Handbook,
Google's i18n developer guide, and the Mozilla l10n documentation. The "run in CI as a blocking
gate" framing reflects the CI-first QA philosophy: the cheapest fix is the one caught at commit
time (Martin Fowler, "Continuous Integration"; see also the DORA research on shift-left testing).

---

_Last reviewed: 2026-06-08 by `claude`._
