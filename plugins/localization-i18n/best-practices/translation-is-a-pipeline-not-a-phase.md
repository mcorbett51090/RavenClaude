# Translation is a pipeline, not a phase

If sending strings to translators is a manual quarterly ritual, the catalog drifts from the code and releases ship with raw keys. Make it continuous: source strings push to the TMS on merge, completed translations pull back automatically, and CI guards completeness — failing the build on missing keys, placeholder-count mismatches, broken ICU syntax, or an untranslated required locale. Context (comments, screenshots, char-limits) travels with each string. A manual copy-paste of JSON in and out of a TMS guarantees divergence.
