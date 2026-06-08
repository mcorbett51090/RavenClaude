---
description: "Configure and run pseudo-localization for a project: select the right pseudo-loc variant (accent, expansion, bidi), generate pseudo-locale files, integrate into CI as a blocking gate, and interpret the output to triage i18n bugs."
argument-hint: "[context, e.g. 'React SPA, i18next JSON, targeting ar-SA — want expansion + bidi variants']"
---

You are running `/localization-i18n-engineering:run-pseudo-localization`. Use the
`localization-qa-engineer` discipline and the `localization-qa-and-pseudo-loc` skill.

## Steps

1. **Traverse the pseudo-loc CI gate decision tree.** Use the `Pseudo-loc in CI` tree in
   `knowledge/i18n-l10n-decision-trees.md` to select which pseudo-loc variants to run (accent /
   expansion / bidi / double-length) based on the project type (web, mobile, server-rendered) and
   the target locales (RTL locales? long-text locales?).

2. **Select or configure a pseudo-localizer tool.** Based on the project type:
   - **Web/i18next:** `pseudolocale` npm package or `i18next-pseudo`.
   - **Web/FormatJS:** `@formatjs/cli` compile with a custom transformer.
   - **Android:** Android Studio en-XA and ar-XB pseudo-locales (enable in Build Variants).
   - **iOS:** custom Ruby/Python script to transform `.strings` files.
   - **Flutter:** custom ARB transformer script.
   Provide the exact configuration (tool install, config file, CLI invocation).

3. **Generate pseudo-locale files.** Run the pseudo-localizer against the source locale file(s).
   The output files are generated artifacts — specify where to write them (e.g.,
   `public/locales/en-XA/`, `src/i18n/pseudo/`) and confirm they are in `.gitignore`.

4. **Run the application against the pseudo-locale.** Configure the application to load the
   pseudo-locale:
   - Set `VITE_APP_LOCALE=en-XA` or equivalent env var.
   - Launch the application and visually inspect (or run screenshot tests).
   - For CI: run `playwright test --project=pseudo-locale` or equivalent.

5. **Interpret the output.** For each finding:
   - **Untransformed English string visible** → hard-coded string; escalate to `i18n-architect`.
   - **Text clipped or overflowed** → container has a max-width or height constraint that can't
     accommodate expansion; escalate to `i18n-architect` for CSS fix.
   - **Layout broken in bidi pseudo-locale** → RTL CSS or `dir` attribute issue; escalate to
     `i18n-architect`.
   - **Test failure due to string mismatch** → a test is asserting on English string values instead
     of translation keys; fix the test.

6. **Configure the CI gate.** Add a step to the PR workflow:
   - Generate pseudo-locale files (step 2 command).
   - Run tests against the pseudo-locale.
   - Run screenshot comparison (Playwright / Cypress visual diff or Storybook snapshots).
   - Fail the build on any overflow/clip finding or any test failure.
   Reference `templates/l10n-ci-gate.md` for the CI YAML scaffold.

7. **Document the suppression path** for intentional pseudo-locale-only exceptions (e.g., an
   image filename that must not be transformed). Provide the suppression syntax for the chosen tool.

8. **Emit the Structured Output block** with pseudo-loc variants configured, findings from the
   initial run, CI gate configuration, and handoff to l10n-pipeline-engineer if extraction or
   import issues are discovered.
