---
name: localization-qa
description: "Prove the localized build is correct, not just translated: run linguistic, functional, layout, and locale/RTL QA per shipped locale, use pseudo-localization as the first-line gate, wire in-context review, and stand up a localization regression suite that catches re-breakage."
---

# Localization QA

## "Translated" is not "correct"
A perfectly translated string can still overflow the button, sort wrong, or mis-parse the date. QA the *running localized build*, not the catalog — and across every shipped locale, not just English.

## Pseudo-localization is the gate before money is spent
Run a pseudo-locale at +30-40% length (accented, bracketed) to surface hardcoded strings, concatenation, and truncation/overflow before a translator is involved. If a string doesn't survive the pseudo-locale, no translation saves it.

## The per-locale QA matrix
- **Linguistic** — accuracy, terminology/glossary, tone/register, *in-context* review (the screen, not a TMS spreadsheet — catches verb-vs-noun "Open").
- **Functional** — date/number/currency formatting, collation/sorting, text input (IME, combining marks), locale-derived behavior.
- **Layout** — truncation, overflow, wrapping, reflow from length expansion; screenshot-diff per locale.
- **Locale + RTL/bidi** — mirroring, alignment, bidi isolation of interpolated values, numeral/date placement, directional-icon mirroring.

## Cover the kinds of breakage, not just market size
Pick the locale matrix so an RTL language, a CJK language, and a 6-plural-form language each exercise their distinct failure modes — not just the biggest markets.

## Classify every defect to its owner
Truncation → layout (`web-design`/frontend); wrong plural → i18n architecture; missing string → pipeline; bad wording → linguistic. Classify and route, don't just file.

## Regression or it silently re-breaks
Snapshot the localized layouts + functional behavior into a regression suite wired into CI, so a refactor that re-hardcodes a string or re-introduces a fixed width fails the build instead of reaching a user.

## Output
A localization-QA report: the per-locale matrix (linguistic / functional / layout / RTL), pseudo-localization coverage, the regression suite, and classified defects routed to `i18n-architect` / `localization-engineer` / `web-design` / `frontend-engineering`.
