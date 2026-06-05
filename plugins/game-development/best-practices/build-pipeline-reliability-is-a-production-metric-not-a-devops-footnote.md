# Build Pipeline Reliability Is a Production Metric, Not a DevOps Footnote

**Status:** Pattern
**Domain:** Game development — production management, engineering
**Applies to:** `game-development`

---

## Why this exists

An unreliable build pipeline — slow, flaky, or frequently broken CI builds — is a direct production-velocity tax. Every broken build costs the team a context switch, delays the QA queue, and pushes playtests. On a 10-person team where a broken build wastes 30 minutes of investigation and resolution across 4–5 people, a once-per-day break rate consumes 10+ hours per week of senior engineering time. Worse, when builds are unreliable, developers start committing less frequently to "avoid breaking the build" — which turns individual integration risk into large, risky merges that are harder to QA. Build pipeline health belongs on the weekly production standup, not buried in a DevOps backlog.

## How to apply

**Metrics to track weekly:**

| Metric | Target | Alarm Threshold |
|---|---|---|
| Build success rate | ≥ 95% | < 90% |
| Mean time to green (MTTG) — time from commit to passing build | ≤ 20 min (small proj) / ≤ 45 min (large) | > 60 min |
| Mean time to resolution (MTTR) — broken build to green | ≤ 30 min | > 2 hours |
| Flaky test rate (tests that fail non-deterministically) | < 2% | > 5% |

**How to diagnose a failing build pipeline:**

```
1. Categorize every broken build by root cause for 2 weeks:
   - Merge conflict / integration issue
   - Flaky test (non-deterministic failure)
   - Environment / dependency issue (wrong SDK, package version drift)
   - Actual code defect introduced in the commit
   - Asset pipeline failure (content build, shader compile)

2. Rank by frequency. The top root cause drives the fix.

3. Common patterns and fixes:
   - Flaky tests → quarantine the test, fix or delete within 1 sprint
   - Environment drift → lock dependency versions (lock file), use container-based builds
   - Long build times → split into fast (unit test) and slow (integration/content) stages;
     require only the fast stage to pass before merge
   - Asset pipeline failures → run asset builds on their own schedule; separate from code builds
```

**Integration practices that protect build stability:**
- Feature branches merge into main only after a passing CI build.
- A "build captain" rotates weekly — one person owns broken-build triage that week.
- Builds that break main are reverted within 30 minutes if not fixed — no "leave it for tomorrow."
- Daily builds include a smoke-test play session (5 minutes) to catch runtime issues that pass unit tests.

**Do:**
- Track build success rate and MTTG on the production dashboard alongside milestone burndown.
- Treat a flaky test as a bug — quarantine it, track it, fix it on a deadline.
- Invest in build speed incrementally every sprint — a 10-minute faster build compounds into hours weekly.

**Don't:**
- Normalize a "known broken build" for more than one business day — it erodes the team's trust in the signal.
- Skip the build system entirely ("just copy the DLL") to meet a milestone — the short-term speed comes back as a merge nightmare.
- Blame the build system without categorizing root cause — "the CI is unreliable" is a symptom, not a diagnosis.

## Edge cases / when the rule does NOT apply

Solo or two-person indie projects without a formal CI setup may not have enough team size to justify a full pipeline reliability tracking regime. Apply the underlying discipline — categorize broken builds, fix flaky tests, keep build time under 15 minutes — without the formal weekly metrics. The principles scale down; the bureaucracy does not need to.

## See also
- [`../agents/gameplay-engineer.md`](../agents/gameplay-engineer.md) — owns technical risk and build infrastructure as engineering decision-support.
- [`../agents/gamedev-producer.md`](../agents/gamedev-producer.md) — tracks production velocity and owns the build pipeline metric on the production dashboard.

## Provenance

Codifies standard continuous integration practice applied to game development production management; time benchmarks are [unverified — training knowledge] and vary by project size, engine, and content volume.

---

_Last reviewed: 2026-06-05 by `claude`_
