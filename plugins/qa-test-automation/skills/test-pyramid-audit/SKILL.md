---
name: test-pyramid-audit
description: "Audit procedure for diagnosing test pyramid shape — identifies ice-cream-cone suites, slow E2E over-reliance, and unit test gaps, then produces a concrete rebalancing plan."
---

# Test Pyramid Audit

## When to Use This

The CI suite is slow, often red for reasons that don't represent real bugs, or the team feels the tests don't catch the things that actually break in production. This audit diagnoses the pyramid shape and produces a concrete rebalancing plan.

## Step 1 — Measure the Current Shape

Collect from CI:

| Metric | Where to find it |
|---|---|
| Test count by level (unit / integration / E2E) | Test runner report; tag/label by level |
| Runtime by level | CI timing logs |
| Failure rate by level (last 30 days) | CI analytics or a query against build history |
| Flake rate by level | Quarantine list + re-run count |

Target healthy pyramid ratios (adjust for your domain):

| Level | Count ratio | Runtime share |
|---|---|---|
| Unit | 70–80% | < 20% of total suite time |
| Integration | 15–20% | 30–40% |
| E2E | 5–10% | 40–50% |

If E2E is > 30% of count or > 70% of runtime, you have an **ice-cream cone** — the most expensive shape.

## Step 2 — Identify Mis-leveled Tests

For each E2E test, ask:
1. **Does this test require a real browser/full stack to be valid?** If no → it can move to integration or unit.
2. **Does this test only check a single service's logic in isolation?** If yes → it's a unit test in E2E clothing.
3. **Does this test duplicate coverage already in a unit test?** If yes → it's redundant at the E2E level.

For each unit test, ask:
1. **Does it test implementation details (private methods, internal state)?** If yes → it will break on refactors that don't change behavior; rewrite to test the public interface.
2. **Does it mock so heavily that no real logic runs?** If yes → it's a test of mock configuration, not behavior.

## Step 3 — Classify Gaps by Defect Class

Map defect types to the test level that catches them cheapest:

| Defect class | Cheapest catching level |
|---|---|
| Business logic / calculations | Unit |
| Service boundary / API contract | Integration (consumer-driven contract) |
| Database query correctness | Integration (against real DB, test schema) |
| Cross-service end-to-end flow | E2E (critical journeys only) |
| UI rendering / accessibility | Component test or visual diff |
| Auth / permission enforcement | Integration |

Audit: for each defect class, do you have coverage at the cheapest level? Mark gaps.

## Step 4 — Produce the Rebalancing Plan

Structure the plan as three columns:

| Test to migrate/add/remove | From level | To level | Effort (hrs) | Priority |
|---|---|---|---|---|
| `checkout_happy_path.spec.ts` splits into unit + integration | E2E | Unit + Integration | 4 | High |
| Add unit tests for `discount-calculator.ts` | None | Unit | 2 | High |
| Remove duplicate E2E for login (covered by integration) | E2E | Delete | 0.5 | Medium |

Sort by: (slowest / most flaky tests to eliminate) first.

## Step 5 — Set Pyramid Health Gates

Add CI checks that enforce the target shape over time:

```yaml
# Example: fail the build if E2E count exceeds 200
- name: Pyramid health gate
  run: |
    E2E_COUNT=$(grep -r "@e2e" tests/ | wc -l)
    if [ "$E2E_COUNT" -gt 200 ]; then
      echo "E2E count $E2E_COUNT exceeds limit of 200. Move coverage down the pyramid."
      exit 1
    fi
```

Alternatively, track E2E runtime as a percentage and alert when it exceeds 70% of total suite time.

## Audit Report Template

```
## Test Pyramid Audit — <Service/Repo> — <Date>

### Current shape
- Unit: <count> (<runtime>s, <failure rate>%)
- Integration: <count> (<runtime>s, <failure rate>%)
- E2E: <count> (<runtime>s, <failure rate>%)
- Flaky tests quarantined: <count>

### Diagnosis
<Describe the dominant problem: ice-cream cone / missing unit coverage / over-mocked units / etc.>

### Top 5 rebalancing actions
<table from Step 4, top 5 rows>

### Proposed pyramid health gate
<threshold + CI check>
```

## Pitfalls

- Measuring line coverage % as the proxy for pyramid health — a suite can have 90% coverage and still be an ice-cream cone.
- Migrating E2E tests to unit level by adding more mocks — the resulting "unit" tests test mocks, not real behavior. Prefer integration tests with a real DB over mock-heavy unit tests for IO-heavy code.
- Setting the E2E count gate so high it never triggers — 200 E2E tests for a small service is already an ice-cream cone.

## See Also

- [`../../agents/test-strategy-architect.md`](../../agents/test-strategy-architect.md) — pyramid shape, what to test vs not, coverage philosophy
- [`../../agents/test-infrastructure-engineer.md`](../../agents/test-infrastructure-engineer.md) — parallelization and coverage reporting in CI
