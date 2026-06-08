# l10n CI Gate — {{PROJECT_NAME}}

> Copy this template into `.github/workflows/l10n-ci-gate.yml` (GitHub Actions) or adapt to your
> CI platform. Fill in every `{{PLACEHOLDER}}`. This gate should be a **required** PR check.

---

## Overview

This CI gate enforces four l10n quality checks on every pull request:

1. **Extraction drift** — fails if source strings in code have drifted from the committed source
   locale file (un-extracted strings are invisible to translators).
2. **l10n lint** — fails on missing keys, empty translations, or placeholder mismatches in any
   target locale file.
3. **Pseudo-localization** — runs the app against a generated expansion pseudo-locale; fails on
   overflow or hard-coded strings detected in tests/screenshots.
4. **ICU syntax** — validates that every MessageFormat string in source and target locale files
   parses without errors.

---

## GitHub Actions workflow (adapt to your platform)

```yaml
# .github/workflows/l10n-ci-gate.yml
name: l10n CI gate

on:
  pull_request:
    paths:
      - "src/**"
      - "{{LOCALE_DIR}}/**" # e.g. public/locales/**

jobs:
  # ──────────────────────────────────────────────────────────────────────────
  # Job 1: Extraction drift check
  # Verifies that all translatable strings in source code are present in the
  # committed source locale file. Fails if extraction produces a diff.
  # ──────────────────────────────────────────────────────────────────────────
  extraction-drift:
    name: Extraction drift
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "{{NODE_VERSION}}" # e.g. 20
          cache: npm
      - run: npm ci
      - name: Run string extraction
        run: |
          # Replace with your extraction command:
          # i18next:
          npx i18next-scanner --config i18next-scanner.config.js 'src/**/*.{js,jsx,ts,tsx}'
          # FormatJS:
          # npx formatjs extract 'src/**/*.{ts,tsx}' --format simple --out-file {{SOURCE_LOCALE_FILE}}
      - name: Check for drift
        run: |
          if ! git diff --exit-code {{SOURCE_LOCALE_FILE}}; then
            echo "ERROR: Extracted strings differ from committed locale file."
            echo "Run the extraction command locally, commit the updated file, and re-push."
            exit 1
          fi

  # ──────────────────────────────────────────────────────────────────────────
  # Job 2: l10n lint
  # Checks all target locale files for missing keys, empty values,
  # placeholder mismatches, and ICU syntax errors.
  # ──────────────────────────────────────────────────────────────────────────
  l10n-lint:
    name: l10n lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "{{NODE_VERSION}}"
          cache: npm
      - run: npm ci
      - name: Run l10n lint
        run: |
          # Option A — i18next-lint:
          npx i18next-lint --config i18next-lint.config.json
          #
          # Option B — FormatJS compile (validates ICU syntax in all locale files):
          # for locale in {{TARGET_LOCALES}}; do
          #   npx formatjs compile public/locales/$locale/{{NAMESPACE}}.json \
          #     --ast --out-file /dev/null
          # done
          #
          # Option C — custom script (see scripts/l10n-lint.js in your project):
          # node scripts/l10n-lint.js --source {{SOURCE_LOCALE_FILE}} \
          #   --targets '{{LOCALE_DIR}}/**/*.json' \
          #   --rules missing-key,empty-value,placeholder-mismatch,icu-syntax
        env:
          # Add suppression config if needed:
          L10N_LINT_SUPPRESS: "{{SUPPRESS_CONFIG_PATH}}"

  # ──────────────────────────────────────────────────────────────────────────
  # Job 3: Pseudo-localization gate
  # Generates an expansion pseudo-locale, runs the test suite and/or
  # screenshot tests against it, and fails on overflow or hard-coded strings.
  # ──────────────────────────────────────────────────────────────────────────
  pseudo-loc:
    name: Pseudo-localization
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "{{NODE_VERSION}}"
          cache: npm
      - run: npm ci
      - name: Generate pseudo-locale files
        run: |
          # Replace with your pseudo-loc tool:
          # pseudolocale npm package:
          npx pseudolocale --source {{SOURCE_LOCALE_FILE}} \
            --output {{PSEUDO_LOCALE_DIR}}/en-XA.json \
            --strategy expand
          # FormatJS pseudo:
          # npx formatjs pseudo-locale --strategy expand \
          #   {{SOURCE_LOCALE_FILE}} {{PSEUDO_LOCALE_DIR}}/en-XA.json
      - name: Run tests against pseudo-locale
        run: |
          # Unit/integration tests:
          VITE_APP_LOCALE=en-XA npm test -- --testPathPattern="{{TEST_GLOB}}"
          # Screenshot tests (Playwright):
          # LOCALE=en-XA npx playwright test --project=pseudo-locale
        env:
          PSEUDO_LOCALE_DIR: "{{PSEUDO_LOCALE_DIR}}"
      - name: Upload pseudo-locale screenshots (on failure)
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: pseudo-loc-screenshots
          path: "{{PLAYWRIGHT_SCREENSHOTS_DIR}}"

  # ──────────────────────────────────────────────────────────────────────────
  # Job 4: ICU syntax validation
  # Parses every MessageFormat string in source and target locale files.
  # Fails on syntax errors (unmatched braces, unknown selectors, etc.)
  # ──────────────────────────────────────────────────────────────────────────
  icu-syntax:
    name: ICU syntax
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "{{NODE_VERSION}}"
          cache: npm
      - run: npm ci
      - name: Validate ICU MessageFormat
        run: |
          # FormatJS compile validates ICU syntax:
          for locale in {{SOURCE_LOCALE}} {{TARGET_LOCALES}}; do
            echo "Validating $locale..."
            npx formatjs compile "{{LOCALE_DIR}}/$locale/{{NAMESPACE}}.json" \
              --ast --out-file /dev/null
          done
          # If not using FormatJS, use @messageformat/core to parse:
          # node -e "
          #   const { parse } = require('@messageformat/parser');
          #   const files = require('glob').sync('{{LOCALE_DIR}}/**/*.json');
          #   files.forEach(f => {
          #     const strings = JSON.parse(fs.readFileSync(f, 'utf8'));
          #     Object.entries(strings).forEach(([k, v]) => {
          #       try { parse(v); }
          #       catch(e) { console.error(f + ':' + k + ': ' + e.message); process.exit(1); }
          #     });
          #   });
          # "
```

---

## Configuration variables

| Variable | Example value | Description |
|---|---|---|
| `{{PROJECT_NAME}}` | `my-app` | Project name |
| `{{NODE_VERSION}}` | `20` | Node.js version |
| `{{SOURCE_LOCALE_FILE}}` | `public/locales/en-US/common.json` | Source locale file path |
| `{{SOURCE_LOCALE}}` | `en-US` | Source locale code |
| `{{TARGET_LOCALES}}` | `de-DE fr-FR ja-JP ar-SA` | Space-separated target locale codes |
| `{{LOCALE_DIR}}` | `public/locales` | Root directory for locale files |
| `{{NAMESPACE}}` | `common` | String namespace/bundle name |
| `{{PSEUDO_LOCALE_DIR}}` | `public/locales` | Directory for generated pseudo-locale files |
| `{{TEST_GLOB}}` | `src/**/*.test.{ts,tsx}` | Test file glob |
| `{{PLAYWRIGHT_SCREENSHOTS_DIR}}` | `test-results` | Playwright screenshot output directory |
| `{{SUPPRESS_CONFIG_PATH}}` | `.l10n-suppress.json` | Path to lint suppression config |

---

## Making this a required check

In GitHub: **Settings → Branches → Branch protection rules → Require status checks to pass
before merging** → add `Extraction drift`, `l10n lint`, `Pseudo-localization`, `ICU syntax`.

---

## Suppression syntax reference

```json
// .l10n-suppress.json — known-good exceptions
{
  "suppressions": [
    {
      "key": "common.brand_name",
      "rule": "untranslated-value",
      "reason": "Brand name — intentionally not translated"
    },
    {
      "key": "common.iso_currency_code",
      "rule": "untranslated-value",
      "reason": "ISO 4217 currency code — locale-invariant"
    }
  ]
}
```

---

_Template version: 0.1.0. Owned by `localization-i18n-engineering` plugin._
