---
name: l10n-pipeline-and-tms
description: "Design and operate the localization pipeline: string extraction configuration, TMS (Phrase, Lokalise, Crowdin, Transifex) integration and handoff, XLIFF/ARB/PO/JSON format conversion, translation memory management, continuous localization in a CD cycle, and branching strategies for in-flight translations."
---

# l10n Pipeline and TMS Integration

**Purpose:** design and operate the pipeline that moves source strings from the codebase to
translators (human or machine) and back into the build — continuously, reliably, and without
blocking releases.

## The operating loop

1. **Map the extraction surface.** Identify all translatable string files: format (JSON, XLIFF,
   ARB, PO, `.properties`, `strings.xml`), source directory, namespace/bundle structure, and the
   frameworks that read them at runtime. For each framework, identify the extraction CLI tool:
   - **i18next:** `i18next-scanner` or `i18next-parser` (scans JS/TS/JSX for `t()` calls).
   - **FormatJS / react-intl:** `formatjs extract` (scans for `<FormattedMessage>` and `intl.formatMessage()`).
   - **gettext:** `xgettext` (scans source for `_()`, `gettext()`, `ngettext()`).
   - **Android:** Gradle `extractStrings` task; `strings.xml` is the source of truth.
   - **iOS:** Xcode localization export (`xcodebuild -exportLocalizations`) produces XLIFF.
   - **Flutter:** `flutter gen-l10n` reads ARB files.

2. **Choose a string catalog format.** Use the project-native format for runtime (JSON, ARB,
   `strings.xml`) and XLIFF for TMS handoff. Build format conversion into the pipeline:
   - `source format → XLIFF` (push to TMS).
   - `XLIFF → source format` (pull from TMS, import into build).
   Avoid hand-editing XLIFF — it should be pipeline-generated.

3. **Select and configure the TMS.** Traverse the TMS selection tree in
   [`../../knowledge/i18n-l10n-decision-trees.md`](../../knowledge/i18n-l10n-decision-trees.md).
   For the chosen TMS, configure:
   - **Authentication:** API key or OAuth — store in CI secrets, never in code.
   - **Branch workflow:** map source-code branches to TMS project branches (Phrase / Lokalise
     support branch-level isolation [verify-at-use]).
   - **Translation memory:** enable TM leverage; set fuzzy-match threshold (typically 75–100 %).
   - **Machine translation connector:** DeepL, Google Cloud Translation, or Amazon Translate
     for initial MT draft + post-edit workflow [verify-at-use].
   - **Glossary:** upload a terminology glossary to ensure consistent brand/product term translation.

4. **Wire the extraction CI step.** Add a CI job that:
   - Runs the extraction CLI on the source tree.
   - Diffs the output against the committed source locale file (fails on drift — extraction must
     be committed before PR merge).
   - Pushes new/changed source strings to the TMS via the TMS CLI or API.
   - Tags in-progress strings `x-state="needs-translation"` (XLIFF 2) or TMS-equivalent.

5. **Wire the import CI step (or a scheduled job).** Pull completed translations from the TMS:
   - Filter for `x-state="final"` or TMS-equivalent "approved" status only.
   - Convert from XLIFF to project-native format.
   - Validate: placeholder consistency, ICU syntax, no empty values for completed status.
   - Commit or open a PR with the updated locale files.

6. **Define the fall-through policy for untranslated strings.** Choose: (a) fall back to source
   locale (English), (b) fail the build if any required locale has a missing key, or (c) ship with
   a visible "MISSING: <key>" placeholder in non-release builds. Option (a) is the standard for
   continuous localization; option (b) is correct for a gate before a planned launch.

7. **Design the branching strategy.** Prevent translation debt on long-lived feature branches:
   - Extract on the feature branch as strings are added.
   - Push source strings to TMS immediately (even if translation is not yet requested).
   - Do not import translations until the feature branch is stable (avoids wasted translation
     of strings that will be rewritten).
   - Merge translated strings before or immediately after feature merge to main.

## Translation memory management

- Review TM for outdated segments quarterly (after significant UI copy changes).
- Keep brand names, product names, and UI element names in the glossary — TM should not translate
  these.
- Set TM leverage tiers: 100 % match (no re-translation cost), 75–99 % fuzzy (reduced cost,
  post-edit required), <75 % no-match (full translation cost).

## Anti-patterns

- Batch export/import (quarterly dump) — blocks releases and accumulates debt.
- TMS API keys committed to source control.
- Importing all TMS strings regardless of approval status — ships in-progress translations.
- No extraction CI step — drift between source strings and locale files is invisible until release.
- XLIFF hand-editing — produces format errors and breaks TM segment matching.
- A single monolithic string file with no namespace separation — slows TM leverage and confuses
  translator context.

## Output

A localization pipeline design document + TMS integration runbook. Reference
[`../../templates/l10n-ci-gate.md`](../../templates/l10n-ci-gate.md) for the CI configuration
scaffold.
