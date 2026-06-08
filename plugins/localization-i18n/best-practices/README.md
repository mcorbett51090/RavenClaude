# Localization-i18n best-practices

Atomic, enforceable rules the localization-i18n agents apply. Each file is one rule with a short rationale; the agents cite them by filename. Canonical decision logic lives in [`../knowledge/localization-i18n-decision-trees.md`](../knowledge/localization-i18n-decision-trees.md); these rules are the always-on priors.

| Rule | Gist |
|---|---|
| internationalize-before-you-translate | Design the i18n seam first; retrofitting is a rewrite |
| never-assume-english-grammar | ICU plural/select per CLDR, never `n === 1` logic |
| never-concatenate-translatable-fragments | One message with placeholders; word order varies |
| cldr-intl-is-the-source-of-truth | Read plural/format rules from CLDR/`Intl`, never hand-roll |
| stable-keys-not-source-text | Stable IDs + English default; source-text keys orphan |
| pseudo-localize-continuously | A pseudo-locale in CI catches hardcoding + truncation early |
| translation-is-a-pipeline-not-a-phase | Continuous push/pull through the TMS; CI guards completeness |
| translated-is-not-correct | QA the running build — linguistic, functional, layout, RTL |
