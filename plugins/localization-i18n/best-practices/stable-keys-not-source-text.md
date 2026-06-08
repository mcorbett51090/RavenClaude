# Stable keys, not source-text-as-key

Prefer stable translation-key IDs with the English copy as the *default value*, not the English source text used directly as the key. Source-text-as-key reads nicely until someone fixes a typo in the English string and silently orphans every translation that was keyed off the old text. Stable IDs survive copy edits, support namespacing for lazy-loading and collision-safety, and let a context comment travel with each key so translators aren't guessing verb-vs-noun.
