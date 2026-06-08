---
description: "Run the per-locale localization QA matrix (linguistic / functional / layout / RTL), use pseudo-localization as the gate, and stand up a localization regression suite."
argument-hint: "[the locales shipped + the build/screens to QA + known symptoms]"
---

You are running `/localization-i18n:localization-qa`. Use `localization-qa` + the `localization-qa` skill.

## Steps
1. Establish the locale matrix to cover — choose locales that exercise the *kinds* of breakage (an RTL, a CJK, a 6-plural-form, a long-expansion language), not just market size.
2. Run pseudo-localization at +30-40% length first to surface hardcoded strings, concatenation, and truncation before involving real translations.
3. Execute the per-locale matrix: linguistic (in-context accuracy/terminology/tone), functional (date/number/sort/input), layout (truncation/overflow/wrapping + screenshot-diff), and RTL/bidi (mirroring/alignment/isolation/placement).
4. Classify every defect to its owner: layout → web-design/frontend; plural/RTL-arch → i18n-architect; missing string → localization-engineer; wording → linguistic.
5. Stand up the localization regression suite (snapshot + functional) wired into CI so a refactor can't silently re-break the localized build.
6. Emit the localization-QA report + the Structured Output block (with `Locale coverage:` and `Handoff to build teams:`).
