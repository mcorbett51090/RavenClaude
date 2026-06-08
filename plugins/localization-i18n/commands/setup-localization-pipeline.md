---
description: "Build the localization pipeline: extract strings into catalogs, pick the file format, integrate the TMS, wire pseudo-localization, and gate CI on catalog completeness and placeholder parity."
argument-hint: "[stack + i18n library + TMS (or 'none yet') + target locales]"
---

You are running `/localization-i18n:setup-localization-pipeline`. Use `localization-engineer` + the `string-extraction-and-tms` skill.

## Steps
1. Confirm the i18n library + key strategy (if undecided, route to i18n-architect first — extraction needs something to extract).
2. Choose the file format (PO/XLIFF/Android XML/ARB/.strings/JSON) the stack and TMS round-trip without loss, with the rationale.
3. Define the extraction strategy (the extractor per stack, key generation, plural/interpolation handling, the staged refactor for legacy hardcoded strings).
4. Design the TMS integration: the push/pull workflow, branch/PR handling, context/screenshot upload, glossary + translation-memory sync.
5. Wire pseudo-localization as a first-class locale and the CI continuous-translation jobs (push on merge, pull translations, validate completeness/placeholder-parity/ICU, gate on required locales).
6. Route the CI runner to devops-cicd and the i18n call implementation to frontend-engineering / mobile-engineering.
7. Emit the pipeline plan + the Structured Output block (with `Locale coverage:` and `Handoff to build teams:`).
