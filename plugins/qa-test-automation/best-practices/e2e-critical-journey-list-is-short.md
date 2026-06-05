# The critical-journey E2E list is short, named, and defended

**Status:** Pattern
**Domain:** E2E test strategy
**Applies to:** `qa-test-automation`

---

## Why this exists

E2E tests are expensive: slow to run, flaky under infrastructure variance, and costly to maintain. Without a defended, short list of critical journeys, E2E suites grow organically as engineers add "just one more" test for each new feature. The result is a 200-test E2E suite that takes 45 minutes, fails half the time for non-product reasons, and provides less signal than a 20-test suite of the most critical journeys. The critical-journey list is a product decision, not an engineering decision — it should be short, explicit, and justified.

## How to apply

Define the critical-journey list as a named document or code comment block listing the journeys, their business justification, and the owner. Require a discussion to add a new journey — it is not a default.

```typescript
/**
 * Critical Journey E2E Tests
 *
 * These tests cover journeys where a failure would cause immediate,
 * significant business or user impact. Each journey is here by decision,
 * not by default. Adding a new journey requires updating this list and
 * a review from the test-strategy-architect.
 *
 * Current critical journeys (as of 2026-06-05):
 *   1. User signup → email verification → first login
 *   2. Add to cart → checkout → payment → order confirmation
 *   3. Password reset flow
 *   4. Search → product page → add to cart
 *
 * NOT in this list (covered at lower level):
 *   - Profile editing (covered by component tests)
 *   - Admin CRUD operations (covered by integration tests)
 *   - Error states (covered by unit tests + API tests)
 */
```

Criteria for a critical journey:
- A failure would immediately block a user from a core value action.
- Cannot be adequately caught at a lower test level (unit or integration).
- The scenario has a meaningful end-to-end path across multiple system components.

**Do:**
- Publish the critical-journey list in the test strategy document and in the test code.
- Review the list quarterly — a journey that was critical at launch may now be low-risk.
- Set a maximum count (e.g., 15–20 journeys) and enforce it in the PR review process.

**Don't:**
- Add an E2E test "to be safe" without checking whether a lower-level test would suffice.
- Let the list grow unchallenged; a PR adding a new E2E test should justify why it belongs.
- Cover happy-path + every edge case in E2E; edge cases belong at the unit or integration level.

## Edge cases / when the rule does NOT apply

Accessibility-focused E2E tests (automated axe-core runs across pages) may warrant a broader list than functional journeys, because accessibility failures can't be caught at the unit level. Keep accessibility scans as a separate suite with its own list.

## See also

- [`../agents/test-strategy-architect.md`](../agents/test-strategy-architect.md) — owns critical-journey selection and the test strategy document.
- [`./respect-the-test-pyramid.md`](./respect-the-test-pyramid.md) — the critical-journey list is what keeps the E2E layer at the top of the pyramid, not the middle.

## Provenance

Codifies the critical user journey (CUJ) concept from Google SRE practice and the "minimal-E2E" recommendation from Kent Dodds's Testing Trophy and Martin Fowler's practical test pyramid.

---

_Last reviewed: 2026-06-05 by `claude`_
