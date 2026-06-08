---
description: "Design a localization pipeline: select a TMS, configure string extraction, define the handoff workflow, choose machine-vs-human translation strategy, and produce a CI integration plan for continuous localization."
argument-hint: "[context, e.g. 'React/i18next, targeting 8 languages, CD pipeline, Phrase or Lokalise']"
---

You are running `/localization-i18n-engineering:design-l10n-pipeline`. Use the
`l10n-pipeline-engineer` discipline and the `l10n-pipeline-and-tms` skill.

## Steps

1. **Establish the extraction scope.** From the context provided or by reading the codebase:
   identify the framework(s), the string externalization format already in use (or to be adopted),
   the source locale, and the target locales. List the extraction CLI tool for each framework.

2. **Traverse the TMS selection tree.** Use the `TMS selection` decision tree in
   `knowledge/i18n-l10n-decision-trees.md` to select a TMS. Document the path taken (team size,
   format requirements, MT need, budget tier). Present the recommendation with explicit "not this"
   decisions and the key trade-offs.

3. **Traverse the machine-vs-human translation tree.** Classify string content into tiers
   (UI microcopy, error messages, marketing copy, legal text). For each tier, apply the
   `Machine-vs-human translation` decision tree and recommend: MT-only, MT + post-edit, or
   human-only. Estimate volume and per-locale cost tier.

4. **Design the extraction CI step.** Specify:
   - The extraction CLI command and configuration file location.
   - The CI trigger (on PR? on merge to main?).
   - The drift-detection check (extraction output vs. committed source locale file).
   - The TMS push command (CLI or API, with secret name for the API key).

5. **Design the import step.** Specify:
   - The TMS pull command (approved-only filter).
   - Format conversion (XLIFF → project-native format).
   - Validation checks (placeholder consistency, ICU syntax, no empty values).
   - Commit strategy (direct commit vs. open PR with locale file changes).

6. **Define the branching and fall-through strategy.** Specify:
   - How feature-branch strings are isolated in the TMS.
   - The fall-through policy for untranslated strings (source fallback vs. build failure).
   - The timeline from string commit to translated string available in build.

7. **Produce the CI integration plan.** Reference `templates/l10n-ci-gate.md` for the scaffold.
   Include: extraction job definition, import job definition, required secrets, and the
   pseudo-localization gate hook-point (hand off to localization-qa-engineer for that gate).

8. **Emit the Structured Output block** with pipeline design summary, TMS recommendation, MT
   strategy, and handoff to localization-qa-engineer for CI quality gates.
