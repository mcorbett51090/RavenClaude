---
scenario_id: 2026-06-05-flaky-test-quarantine-graveyard
contributed_at: 2026-06-05
plugin: qa-test-automation
product: generic
product_version: "unknown"
scope: likely-general
tags: [flaky, quarantine, ci-signal, retry, determinism, ownership]
confidence: high
reviewed: false
---

## Problem

A team's CI had a `@flaky` / `retry(3)` habit: any test that failed intermittently got wrapped in an auto-retry and, if that didn't help, tagged `@quarantine` and excluded from the merge gate. Two years on, the quarantine bucket held 140+ tests, nobody owned any of them, and — the real damage — engineers had learned to **re-run red CI until it went green** rather than read the failure. A genuine regression (a real null-deref in checkout) shipped because the failing test looked like "just another flake" and got retried past.

## Constraints context

- A large suite (several thousand tests) across unit + integration + a thick E2E layer.
- The retry wrapper was applied at the runner level, so a test passing on attempt 2 or 3 was recorded as **green** — the flake was invisible in the dashboard.
- The quarantine list was a CI config array with no owner, no date, no linked ticket — an append-only graveyard.
- No flake-rate measurement: nobody could say which tests were *most* flaky or whether the rate was getting better or worse.

## Attempts

- Tried: raising the retry count from 3 to 5 to "stabilize" CI. Made it worse — it further hid the real regression rate and made the suite slower, while training people even harder to ignore red. Retry-to-green treats the alarm, not the fire.
- Tried: bulk-deleting the whole quarantine list to "start clean." Rejected in review — some of those 140 guarded genuinely-critical journeys; a blind delete would have dropped real coverage with the noise.
- Tried (the move that worked): (1) measured first — turned on per-test retry accounting so a test that passed only on retry was logged as a **flake event, not a pass**, and computed a flake rate per test over 30 days. (2) Made quarantine a **deadline with an owner**, not a tag: each quarantined test got a named owner + a 2-sprint expiry; at expiry it is fixed or deleted with a reason, never silently renewed. (3) Triaged the existing 140 by the flake-triage tree (sleep→condition-wait, shared-state→isolation, real-clock/network→fake/stub, order-dependence→remove the assumption); the residue with no owner and no critical behavior was deleted on purpose.

## Resolution

**A flaky test is a broken test, and quarantine is a deadline — not a graveyard.** The two structural fixes were: stop recording retry-passes as green (so the flake is *visible* and measurable), and attach an owner + expiry to every quarantine entry (so the lane drains instead of filling). Auto-retry without flake accounting is the anti-pattern — it converts a determinism problem into a silent reliability tax and trains the team to dismiss red CI, which is how the real regression slipped through.

**Action for the next engineer:** before touching retries, instrument the flake **rate** (a test passing only on retry is a flake event, not a pass) so you can see the problem and prove it shrinking. Then triage by the [flake-triage tree](../knowledge/qa-test-automation-decision-trees.md), and make every quarantine entry carry `owner` + `deadline` + the suspected root cause — an entry that can't name an owner is a delete candidate, not a quarantine candidate. Cross-reference: [`a-flaky-test-is-a-broken-test`](../best-practices/a-flaky-test-is-a-broken-test.md), [`quarantine-is-a-deadline-not-a-graveyard`](../best-practices/quarantine-is-a-deadline-not-a-graveyard.md), and the `flake_rate` mode of [`scripts/qa_suite_metrics.py`](../scripts/qa_suite_metrics.py).
