# Isolate test data and tear it down — never test against shared/prod state

**Status:** Absolute rule — a test that mutates shared or production data and leaves it behind is a defect in the test.

**Domain:** Power Platform / testing

**Applies to:** `power-platform`

---

## Why this exists

Power Platform tests touch *live* services — a Test Studio run patches Dataverse rows, a `Test → Manually` flow run creates records and fires downstream triggers, a DAX correctness check reads a semantic model. If the test runs against **shared dev data** or, worse, **production**, it pollutes the data other people depend on, makes results non-reproducible (the row count changed because someone else edited it), and can trigger real side effects (a "place order" flow actually placing an order). The `power-platform-tester` agent's stance is explicit: *"Suspicious of any test that runs only in the maker's environment. Reproduce in a clean dev environment or it doesn't count."* Isolated, seeded, torn-down test data is what makes a green run *evidence* rather than a coincidence. The teardown half matters as much as the setup: leftover test records skew the next run and leak into demos.

## How to apply

Seed a known fixture before the test, tag it so it's identifiable, assert against the seeded values, then delete it in a teardown that runs even on failure:

```
Arrange (setup):
  - run in a dedicated TEST environment, not dev-shared or prod
  - seed fixtures with a traceable marker:  mc_testrunid = "TR-2026-05-30-001"
  - Test Studio: set initial state in the test's first steps (collections, context vars)

Act + Assert:
  - act on ONLY the seeded rows (filter every assertion by mc_testrunid)
  - Assert(CountRows(Filter(Orders, mc_testrunid="TR-...")) = 3, "expected 3 seeded orders")

Teardown (MUST run even if asserts fail):
  - delete every row where mc_testrunid = "TR-2026-05-30-001"
  - disable / mock any flow that would fire a real external side effect during the test
  - verify teardown: re-query the marker → 0 rows remain
```

**Do:**
- Run in a **dedicated test environment** (or a clearly partitioned test slice), never prod.
- Tag every fixture with a unique **run ID** so setup, assertions, and teardown all target only that run's data.
- Make teardown **unconditional** — it runs whether the test passed or failed.
- **Mock or disable** flows/connectors that cause real external side effects (emails, payments, third-party API writes).

**Don't:**
- Assert against ambient data ("there are 1,402 active accounts") — it changes under you and breaks on the next run.
- Leave test records behind "to look at later" — they corrupt the next run and leak into demos/reports.
- Test a "place order" / "send notification" flow against the live connector without a mock or a no-op test path.

## Edge cases / when the rule does NOT apply

- **Read-only smoke checks** against a frozen, reference dataset (e.g., a snapshot used for DAX correctness) don't need teardown — but they *do* need the data frozen so the expected values stay stable.
- **Incremental-refresh / partition** tests deliberately operate on a backdated window — isolate by partition, and assert only the expected window changed.
- A **shared integration environment** may be unavoidable for some end-to-end tests; then run-ID tagging + teardown is the mitigation, and you accept the residual coordination risk explicitly.

## See also

- [`test-dax-correctness-as-code.md`](./test-dax-correctness-as-code.md) — frozen-dataset expected-vs-actual is the read-only sibling of this rule
- [`test-as-real-security-context-not-admin.md`](./test-as-real-security-context-not-admin.md) — isolation in identity, as this is isolation in data
- [`../knowledge/bi-pages-copilot-decision-trees.md`](../knowledge/bi-pages-copilot-decision-trees.md)
- [`../agents/power-platform-tester.md`](../agents/power-platform-tester.md) — owner ("reproduce in a clean dev environment or it doesn't count")
- [`../skills/visual-qa/SKILL.md`](../skills/visual-qa/SKILL.md) — captures the visual-evidence side of a test run

## Provenance

Grounded in the `power-platform-tester` agent's test discipline (idempotency, "clean dev environment" requirement, mock external side effects) and [Test Studio overview](https://learn.microsoft.com/power-apps/maker/canvas-apps/test-studio) (retrieved 2026-05-30). Aligns with CLAUDE.md §3 #13 "test the import, not just the export" (fresh-environment discipline).

---

_Last reviewed: 2026-05-30 by `claude`_
