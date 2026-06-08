---
scenario_id: 2026-06-08-source-text-key-orphan
contributed_at: 2026-06-08
plugin: localization-i18n
product: i18next
product_version: "unknown"
scope: likely-general
tags: [keys, stable-ids, source-text-as-key, orphaned-translations, context, tms]
confidence: high
reviewed: false
---

## Problem

A product used the English source string itself as the translation key (`t("Save changes")`). It read
nicely in code and was fast to start, but it silently rotted the catalog. A copy-editor fixed a typo —
"Cancel subscripton" → "Cancel subscription" — and the next build orphaned every translation of that
string in all 14 locales: the key no longer matched any catalog entry, so non-English users saw the
raw English. Worse, two different buttons both said "Open" (a verb on one screen, an adjective on a
file-state label on another); they collapsed into one key and one translation, which was wrong in
genders/cases for half the languages because the translator had no way to tell them apart.

## Constraints context

- ~900 strings, 14 locales, copy edited frequently by non-engineers who had no idea an English edit
  was a breaking key change.
- The TMS keyed entries on the source text, so a source edit looked like "delete old string, add new
  untranslated string" — translation memory sometimes caught it, often didn't.
- No per-string context, so identical English words with different grammar collapsed.

## Attempts

- Tried: a rule that "only engineers edit copy, and they update all locales." Failed — it didn't
  survive contact with a busy release; copy edits are exactly the kind of change non-engineers make,
  and the orphaning returned.
- Tried: leaning on the TMS translation memory to re-suggest the old translation after a source edit.
  Failed — TM is fuzzy and best-effort; it papered over some orphans and missed others, and it did
  nothing for the colliding-homograph problem.
- Tried: migrating to stable IDs with the English as the default *value*, not the key
  (`t("billing.cancel.confirm")` → default "Cancel subscription"), namespacing by feature, and
  attaching a context comment per string (`// verb, button` vs `// adjective, file state`). This
  worked.

## Resolution

With stable IDs, editing the English copy became a value change that never touched the key, so a typo
fix stopped orphaning translations — the catalog entry stayed put and translators got a normal "source
updated" diff. Namespacing killed the homograph collisions (the two "Open"s became distinct keys), and
the context comments rode to the TMS so translators picked the right gender/case. The English default
value meant a brand-new key still rendered readable English before its translation arrived, falling
back gracefully instead of showing a raw key.

## Lesson

Use stable IDs with the English as the default value, never source-text-as-key — a source-text key
orphans every translation the instant someone fixes an English typo, and collapses homographs that
need different grammar (`stable-keys-not-source-text`). Always attach a context comment so the
translator isn't guessing verb-or-adjective (`context-travels-with-the-string`).
