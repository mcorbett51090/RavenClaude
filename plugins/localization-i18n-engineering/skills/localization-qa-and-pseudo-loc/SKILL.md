---
name: localization-qa-and-pseudo-loc
description: "Localization quality assurance methodology: pseudo-localization CI gate design (accent, expansion, bidi variants), l10n linting rules (missing keys, empty values, placeholder consistency, ICU syntax), visual and overflow QA techniques, locale-coverage test matrix, and false-positive triage for l10n lint."
---

# Localization QA and Pseudo-Localization

**Purpose:** build automated quality gates that catch i18n and l10n bugs before they reach
translators, before they block a release, and before users encounter them in production.

## The operating loop

1. **Generate pseudo-locale strings.** Pseudo-localization is a deterministic transformation of
   source strings that preserves the string structure but makes it visually distinct. Implement or
   configure a pseudo-localizer with these variants (use all three for maximum coverage):

   | Variant | Transform | What it catches |
   |---|---|---|
   | **Accent** | Replace ASCII vowels with accented equivalents (`a→ä`, `e→ë`, `o→ö`, `u→ü`) | Hard-coded English strings (they don't get transformed); non-UTF-8 rendering |
   | **Expansion** | Wrap string in `[` / `]` and pad to ~140 % of original length (`[Héllo Wörld!!!]`) | UI overflow, truncation, container width constraints |
   | **Bidi/RTL** | Wrap in Unicode RLI/PDF markers or reverse word order | RTL layout bugs, bidi algorithm edge cases, CSS `dir` not applied |
   | **Double-length** | Repeat string content to 200 % of original length | Worst-case expansion for Finnish, Hindi, Thai |

2. **Add pseudo-loc as a CI gate.** The pseudo-locale build must be a blocking check:
   - Generate pseudo-locale files from source strings at CI start.
   - Run the full test suite (unit + integration) against the pseudo-locale.
   - Run screenshot/snapshot tests against the pseudo-locale (Playwright, Cypress, Storybook).
   - Fail the build if: any UI screenshot shows clipped/overflowed text, any test fails due to
     a string mismatch, or any hard-coded string is detected (compare rendered output against
     expected pseudo-transformed output).
   - The pseudo-locale files are generated at build time — do NOT commit them to the repo.

3. **Configure l10n lint rules.** Choose a lint tool appropriate to the project:
   - **JavaScript/TypeScript:** `i18next-lint`, `eslint-plugin-i18n-json`, `@formatjs/cli lint`.
   - **Python:** `django-admin check` (i18n checks), custom script against PO files.
   - **General XLIFF:** `xliff-lint`, TMS-integrated validation.
   - **Custom:** a small script that reads source and target locale JSON/XLIFF and checks rules.

   Standard rule set:
   - **Missing key:** every key in the source locale must exist in every target locale.
   - **Extra key:** every key in a target locale must exist in the source locale (orphan detection).
   - **Empty value:** a translated value that is an empty string is almost always a bug.
   - **Untranslated value:** a translated value identical to the source value may be intentional
     (proper nouns, URLs) or a miss — flag for review with a suppression path.
   - **Placeholder consistency:** every `{name}`, `%s`, `%(count)d`, or `{{variable}}` in the
     source must appear in the translation (order may vary for ICU named placeholders).
   - **ICU syntax validity:** parse every ICU MessageFormat string and fail on syntax errors.

4. **Wire l10n lint as a blocking CI check.** Lint that produces warnings-only gets ignored.
   Add to the PR required-checks list. Provide a clear suppression syntax for known-good exceptions:
   - i18next-json: `"//": "NOQA: intentional fallback"` sibling key.
   - XLIFF: `approved="no"` with a comment `<!-- pseudo-only -->` for pseudo-locale entries.
   - ESLint: `/* eslint-disable i18next/no-literal-string */` for a specific line with justification.

5. **Define a locale-coverage test matrix.** Not every locale needs a full regression run.
   Tiered coverage:
   - **Pseudo-locale** — proxy for all locales; run on every PR. Catches structural i18n bugs.
   - **Priority locales** (top 5 by user volume, typically `en-US`, `de-DE`, `fr-FR`, `ja-JP`,
     `zh-Hans`) — run smoke suite on every PR; full regression on main merge.
   - **Long-text locales** (`de-DE`, `fi-FI`) — expansion regression on every PR (the pseudo
     expansion covers this, but spot-check with real German/Finnish strings quarterly).
   - **RTL locales** (`ar-SA`, `he-IL`) — RTL layout smoke on every PR; visual QA quarterly.
   - **Remaining locales** — run smoke suite on main merge; rely on pseudo-loc for structural
     coverage.

6. **Triage false positives.** A high false-positive rate causes teams to disable the lint gate.
   Categorize each false positive:
   - **Known-good untranslated:** proper nouns, brand names, URLs, email formats, ISO codes.
     Add to a suppression allow-list in the lint config.
   - **Test fixtures:** strings in `__tests__/`, `fixtures/`, or `*.test.*` files should be
     excluded from the extraction scope entirely.
   - **Rule too broad:** tighten the rule pattern; prefer specific rule + suppression over disabling
     the rule globally.

## Pseudo-localization tooling (2026, verify-at-use)

- **Web:** `pseudolocale` (npm), `@lingui/cli` pseudo command, `i18next-pseudo` plugin.
- **Android:** `LinguaPlank` / manual `translatable="false"` audit; Android Studio has a
  pseudo-locale (`en-XA`, `ar-XB`) that can be enabled in developer options [verify-at-use].
- **iOS:** custom script or Xcode pseudo-locale approach.
- **Flutter:** custom ARB transformer; no official pseudo-locale command as of 2026 [verify-at-use].

## Anti-patterns

- Pseudo-loc run only pre-release — too late; bugs are expensive to fix under release pressure.
- l10n lint as a non-blocking warning — warnings are noise; blocking is the point.
- Committing pseudo-locale files to the repo — they're generated artifacts; treat them like build
  outputs.
- Visual QA done only in English — expansion and RTL issues are invisible until a user reports them.
- Suppressing entire locale files to silence a noisy rule — hides real bugs.

## Output

A pseudo-localization CI gate configuration + an l10n lint rule set with suppression patterns +
a locale-coverage test matrix. Reference [`../../templates/l10n-ci-gate.md`](../../templates/l10n-ci-gate.md)
for the CI YAML scaffold.
