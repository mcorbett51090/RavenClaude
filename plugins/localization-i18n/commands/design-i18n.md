---
description: "Design the internationalization architecture: the message-format model, the i18n library per stack, the translation-key strategy, the CLDR/locale-data + fallback chain, and the RTL/formatting approach."
argument-hint: "[stack + target locales + the strings/plural/RTL needs]"
---

You are running `/localization-i18n:design-i18n`. Use `i18n-architect` + the `i18n-architecture` skill.

## Steps
1. Establish the locale matrix and the plural/script complexity (any 3+ plural-form language? any RTL? CJK?). If none of this is decided, name it as the first open question.
2. Pick the message-format model (ICU MessageFormat plural/select vs. platform-native) and the i18n library per stack, with the trade named.
3. Define the translation-key strategy (stable IDs vs. source-text, namespacing, placeholder convention, context comments) and the CLDR/locale-data + explicit fallback chain.
4. Define the RTL/bidi approach (logical CSS, bidi isolation, mirroring) and the date/number/currency formatting via `Intl`/CLDR. List explicit non-goals.
5. Route the builds: UI components → frontend-engineering / mobile-engineering; visual mirroring → web-design; pipeline → localization-engineer; QA → localization-qa.
6. Emit the i18n-architecture decision + the Structured Output block (with `Locale coverage:` and `Handoff to build teams:`).
