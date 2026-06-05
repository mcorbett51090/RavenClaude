# Visual regression tests are a separate, opt-in gate — not part of the main test run

**Status:** Pattern
**Domain:** E2E test automation
**Applies to:** `qa-test-automation`

---

## Why this exists

Visual regression tests (screenshot diffs) are inherently more brittle than functional tests: anti-aliasing differences, system font rendering, dynamic content (timestamps, A/B test variants), and CI environment differences all produce false positives. When visual regression failures mix with functional failures in the main CI gate, developers learn to ignore the visual failures — and then miss real visual regressions. Keeping visual regression as a separate, clearly-labeled CI job with its own review workflow prevents false-positive fatigue and keeps the functional gate trusted.

## How to apply

Run visual regression (Playwright screenshots, Percy, Chromatic, or Applitools) in its own CI job that is non-blocking (or explicitly "needs manual approval to merge"). Flag changes for review rather than failing the merge automatically on any pixel diff.

```yaml
# GitHub Actions: visual regression as a separate, non-blocking job
jobs:
  unit-tests:          # blocking required check
    ...
  e2e-tests:           # blocking required check
    ...
  visual-regression:   # separate, non-blocking, flagged for review
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    steps:
      - uses: actions/checkout@v4
      - run: npx playwright test --config=visual.config.ts
      - name: Upload snapshots for review
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: visual-regression-snapshots
          path: test-results/
```

```typescript
// visual.config.ts — Playwright visual regression config
import { defineConfig } from '@playwright/test';
export default defineConfig({
  snapshotPathTemplate: '{testDir}/__snapshots__/{testFilePath}/{arg}-{projectName}{ext}',
  expect: {
    toHaveScreenshot: {
      maxDiffPixelRatio: 0.02,  // 2% pixel change threshold — tune for your team
      animations: 'disabled',   // prevents timestamp/animation false positives
    },
  },
  use: {
    colorScheme: 'light',       // fix the color scheme to reduce env variance
  },
});
```

**Do:**
- Update baseline snapshots in a dedicated step (not automatically on every PR).
- Use Percy/Chromatic if you want a PR comment with a visual diff UI instead of raw screenshots.
- Freeze dynamic content (timestamps, random IDs, skeleton loaders) before taking screenshots.

**Don't:**
- Mix visual regression failures with functional test failures in the same blocking gate.
- Auto-approve visual diffs without human review.
- Use visual regression as a substitute for accessibility testing — they catch different classes of problems.

## Edge cases / when the rule does NOT apply

Storybook component visual regression (testing isolated components against design-system baselines) can be a blocking gate if the component library is the product. In that case, the scope is narrow and the false-positive rate is lower.

## See also

- [`../agents/e2e-automation-engineer.md`](../agents/e2e-automation-engineer.md) — owns the E2E and visual regression test setup.
- [`./automate-accessibility-and-visual-where-it-earns-it.md`](./automate-accessibility-and-visual-where-it-earns-it.md) — companion rule on accessibility automation alongside visual testing.

## Provenance

Codifies the visual regression testing practice recommended by Percy (browserstack.com/docs/percy), Chromatic (chromatic.com/docs), and Playwright's screenshot testing guide.

---

_Last reviewed: 2026-06-05 by `claude`_
