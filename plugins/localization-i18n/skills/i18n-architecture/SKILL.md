---
name: i18n-architecture
description: "Design the internationalization architecture of an application: pick the message-format model (ICU MessageFormat plural/select vs. platform-native), the i18n library per stack, the translation-key strategy, the CLDR/locale-data and fallback chain, and the RTL/bidi + date/number/currency formatting approach — before strings get hardcoded."
---

# i18n Architecture

## Internationalize before you translate
The expensive mistakes — hardcoded strings, concatenated sentences, 2-form plural logic, physical CSS — are baked in before a word is translated. Design the seam first; retrofitting i18n is a rewrite. Every user-facing string goes through the i18n layer from day one.

## Message format: ICU MessageFormat first
Use ICU MessageFormat `plural`/`select`/`selectordinal` so the *translator* owns the grammar per CLDR (up to 6 plural categories; gender/case/word-order vary). Never let code decide the plural form (`n === 1` is English-only). Reach for platform-native (Android plurals, Apple `.stringsdict`, gettext `ngettext`) only when the OS/toolchain owns the catalog. Never concatenate translatable fragments — one message, named placeholders.

## Library choice per stack
i18next (web, ecosystem + lazy-load), FormatJS/react-intl (web, first-class ICU), gettext (server), Fluent (asymmetric grammar), or platform-native (iOS/Android/Flutter ARB). Name the trade; don't fight the platform's native catalog.

## Translation-key strategy
Prefer **stable IDs** with the English as the default value, not source-text-as-key (a typo fix orphans translations). Namespace for lazy-load + collision-safety. Attach a context comment to every key. Decide the placeholder/interpolation convention once.

## Locale data, fallback, formatting
Read plural rules and date/number/currency/list/collation from CLDR via `Intl` — never hand-roll. Define the explicit fallback chain (`pt-BR` → `pt` → `en`) and locale negotiation; decide bundled-vs-lazy locale data. For RTL: logical CSS (`margin-inline-start`), bidi-isolate interpolated values, plan mirroring.

## Output
An i18n architecture decision: the library + message-format choice, the key strategy, the locale matrix + fallback chain, the RTL/formatting plan, and the explicit non-goals — with the UI build handed to `frontend-engineering` / `mobile-engineering` and the visual mirroring to `web-design`.
