---
scenario_id: 2026-06-05-flaky-pipeline-stabilization
contributed_at: 2026-06-05
plugin: devops-cicd
product: github-actions
product_version: "unknown"
scope: likely-general
tags: [flaky-tests, required-checks, quarantine, retry, ci-trust]
confidence: high
reviewed: false
---

## Problem

A team's required CI check failed ~30% of the time on `main`-bound PRs with no code change — the same workflow, re-run, would go green. Developers had learned to mash "Re-run failed jobs" until it passed, which (a) hid two genuinely-broken tests inside the noise and (b) trained everyone to treat a red required check as meaningless. The pipeline had stopped being a signal. The ask was "make the build reliable again" — the instinct was to add blanket job-level `retry` so re-runs were automatic.

## Context

- GitHub Actions, a monorepo with a ~12-minute integration suite as the single required check gating merge.
- Constraint: the failures were **not** uniformly transient — a blanket retry would have masked the two real defects (an ordering-dependent test and a test asserting on wall-clock time) along with the genuine flakes (a shared test DB with no isolation between parallel jobs, and an external sandbox API that 503'd intermittently).
- The required check was one monolithic job, so a single flaky test failed the whole gate — there was no way to tell "infra flap" from "real regression" from the check status alone.

## Attempts

- Tried: blanket `retry: 3` at the job level. "Worked" in that the green rate went up, but it **masked the two real bugs** (they retried green ~1 time in 4 by luck) and made the suite 3x slower on a genuine failure. Rejected — this is the §3 #1 anti-pattern (a flaky pipeline is a production incident; hiding it is not fixing it).
- Tried: categorizing each failure before treating it, per the **"retry, fail, or skip?"** decision tree in [`../knowledge/devops-cicd-decision-trees.md`](../knowledge/devops-cicd-decision-trees.md). Split the failures into three buckets: transient-infra (the external 503 — retry-eligible within a 2-attempt budget), test-isolation (the shared DB — fix the root cause, give each parallel job its own ephemeral DB), and real-defect (the ordering + wall-clock tests — fix the tests, never retry).
- Tried (the move that worked): a **quarantine lane**. The two real-defect tests were moved out of the required check into a non-blocking "flaky-watch" job (file a ticket, owner, deadline) so the required check went trustworthy immediately; the test-isolation flake was fixed at the root (per-job ephemeral DB); only the genuinely-transient external 503 got a **scoped, budgeted retry** (max 2, that step only — not the whole job). The required check returned to ~99% deterministic.

## Resolution

**A flaky pipeline is fixed by classifying each failure, not by blanket-retrying the symptom.** Retry is correct for exactly one bucket — known-transient infra noise within a tight budget — and is the wrong tool for a real defect (it hides it) or a test-isolation bug (it papers over a fixable root cause). Quarantining the real defects out of the required check restored trust in the gate _the same day_, while the underlying tests were fixed on a tracked deadline rather than under merge-blocking pressure.

**Action for the next engineer:** before adding any retry, run each failure through the retry/fail/skip decision tree. Blanket job-level retry on a required check is an anti-pattern — it trades a slow honest red for a slow dishonest green. Scope retries to the specific transient step with a 1-2 attempt budget; quarantine real defects into a non-blocking lane with a named owner + deadline so the required check stays a trustworthy signal; fix test-isolation flakes at the root (ephemeral per-job state). Cross-reference [`../best-practices/pipeline-required-checks-gate-the-merge.md`](../best-practices/pipeline-required-checks-gate-the-merge.md) and [`../best-practices/build-fast-gates-first.md`](../best-practices/build-fast-gates-first.md).

**Sources:** GitHub Actions does not natively retry individual steps; step-level retry is via a community action (e.g. `nick-fields/retry`) or shell-loop, and `re-run failed jobs` is manual — confirm the current retry mechanism against the [GitHub Actions docs](https://docs.github.com/en/actions) at use `[verify-at-use]`. Figures (30% failure rate, 12-min suite) are illustrative for this scenario; validate against the team's actual CI metrics.
