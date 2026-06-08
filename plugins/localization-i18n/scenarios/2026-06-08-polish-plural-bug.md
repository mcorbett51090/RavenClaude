---
scenario_id: 2026-06-08-polish-plural-bug
contributed_at: 2026-06-08
plugin: localization-i18n
product: i18next
product_version: "unknown"
scope: likely-general
tags: [plurals, icu, cldr, gender-select, polish, arabic]
confidence: high
reviewed: false
---

## Problem

A SaaS product launched Polish and Arabic and immediately got bug reports that counts read wrong: "5 plików" rendered as "5 plik" and Arabic counts were nonsensical. The codebase built plural strings with `count === 1 ? singular : plural` and concatenated the number in front. Polish has three plural forms (one / few / many) and Arabic has six; the 2-form English logic was structurally incapable of being correct, and no amount of re-translation fixed it because the *code* was choosing the form.

## Constraints context

- ~600 user-facing count strings across the app, many assembled by concatenation (`count + " " + t('files')`).
- The translators had flagged it during translation but had no way to express the extra forms — the catalog only had `_singular`/`_plural` keys.
- Time pressure: the locales were already announced.

## Attempts

- Tried: adding a `_few` key and special-casing Polish in the rendering code. Failed — it hardcoded one language's rules into the app, didn't generalize to Arabic's six forms, and put grammar back in the developers' hands.
- Tried: asking translators to "just pick the closest form." Failed — there is no closest; the wrong form is simply wrong, and it looked unprofessional to native speakers.
- Tried: migrating the count strings to ICU MessageFormat (`{count, plural, one {...} few {...} many {...} other {...}}`) so the *translation* carries all the CLDR categories, reading the plural rule from `Intl.PluralRules`/the library, and removing every number-concatenation in favor of the `{count}` placeholder inside the message. This worked.

## Resolution

ICU plural moved the grammar decision out of the code and into the translation, where CLDR already defines the right categories per language — Polish got its three forms, Arabic its six, with zero language-specific code. Killing the concatenation also fixed word-order bugs that hadn't been reported yet. The fix generalized: the next RTL/complex-plural locale needed no code change, just translations.

## Lesson

Never assume English's grammar — `n === 1` is a 2-form rule shipped to languages with up to six. Use ICU plural/select so the translator owns the grammar per CLDR, and never concatenate a number into a sentence. The bug isn't in the translation; it's in the architecture that let code decide the plural form.
