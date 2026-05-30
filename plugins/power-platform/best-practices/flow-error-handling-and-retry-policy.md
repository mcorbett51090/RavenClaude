# Every production flow gets a top-level Try-Catch-Finally and a deliberate retry policy

**Status:** Absolute rule — a production cloud flow with no error scope and no retry decision is a bug, not a style preference. (House rule §3 #10.)

**Domain:** Power Automate

**Applies to:** `power-platform`

---

## Why this exists

Without a `Scope`-based error structure, a single failed action aborts the run and you find out from an angry user, not the flow. The classic failure mode is "Send an email on failure" wired as a normal next step — it never sends, because the action *before* it failed and the email action's default run-after is `Succeeded`. Separately, a flow with **no retry decision** silently inherits the connector **Default** policy (4 retries, exponential), which is sometimes wrong: a non-idempotent `POST` retried 4 times can create 4 records. Error handling and the retry policy are part of the build, not a follow-up. (Retry mechanics verified this session against Microsoft Learn *Employ robust error handling* and *Handle errors and exceptions in Azure Logic Apps* — Power Automate shares the Logic Apps runtime contract, 2026-05-30.)

## How to apply

**Structure** — three top-level scopes:

| Scope | Configure run after (from the scope before it) |
|---|---|
| `Try` | (runs normally) |
| `Catch` | **has failed**, **has timed out**, **is skipped** |
| `Finally` | **is successful**, **has failed**, **has timed out**, **is skipped** (all four) |

In `Catch`, capture the actual error from the `Try` scope's results, then `Terminate` with `Failed` so the run is correctly marked:

```
# Filter array — Inputs: result('Try'), filter where item()['status'] is not 'Succeeded'
@not(equals(item()?['status'], 'Succeeded'))
```

Then `Terminate` with status `Failed` and a message built from that filtered result, so the run history shows *why*.

**Retry policy** — set it deliberately in each action's **Settings → Retry Policy**:

- **Default** — exponential, up to 4 retries (intervals scale by ~7.5s, capped 5–45s). Retries on 408 / 429 / 5xx. Fine for idempotent reads.
- **Exponential** — custom count + interval (ISO 8601, e.g. `PT20S`); preferred for transient backend faults because the spacing grows.
- **Fixed** — even spacing; use when the backend publishes a fixed cool-down.
- **None** — **set this explicitly on any non-idempotent write** (a `POST` that creates a record, a "send" that isn't safe to repeat). Then handle the failure in `Catch` yourself.

**Do:**
- Wire run-after on `Catch`/`Finally` to include **is skipped** and **has timed out**, not just **has failed** — a timed-out or skipped `Try` otherwise leaves `Catch` itself skipped.
- Use `actions('Action_Name')?['status']` / `result('Scope_Name')` to inspect what failed inside `Catch`.
- Set retry to **None** for non-idempotent operations and own the recovery.

**Don't:**
- Rely on a single action's default retry to cover a multi-step transaction — retry is per-action, not per-flow.
- Leave a "notify on error" action as a plain successor — it inherits run-after `Succeeded` and never fires on the path you care about.
- Retry a 401/403/404 — those are connection/permission/not-found walls, not transient faults; retrying just delays the real fix.

## Edge cases / when the rule does NOT apply

- **A throwaway personal flow** (My Flows, not in a solution, not in prod) can skip the scaffolding — but the moment it goes in a solution, the rule applies.
- **A flow whose every action is genuinely idempotent** can lean on Default retry without a `None` override — but it still needs the Try-Catch-Finally so failures are visible.
- **Child flows** terminate back to the parent; the parent's `Catch` can inspect the child's response. Don't double-handle the same error in both.

## See also

- [`../skills/power-automate/resources/error-handling-scopes-child-flows.md`](../skills/power-automate/resources/error-handling-scopes-child-flows.md) — scope + child-flow reference
- [`./flow-child-flows-and-reuse.md`](./flow-child-flows-and-reuse.md) — how child-flow failures surface in the parent
- [`../knowledge/flow-decision-trees.md`](../knowledge/flow-decision-trees.md) — `## Decision Tree: Error handling — which resilience pattern?`
- [`../agents/flow-engineer.md`](../agents/flow-engineer.md) — "Top-level Try-Catch-Finally on every cloud flow. No exceptions for 'small ones.'"
- Microsoft Learn: [Employ robust error handling](https://learn.microsoft.com/power-automate/guidance/coding-guidelines/error-handling) · [Recommendations for handling transient faults](https://learn.microsoft.com/power-platform/well-architected/reliability/handle-transient-faults)

## Provenance

Microsoft Learn error-handling coding guidelines + Logic Apps retry-policy reference (Default = 4 exponential retries, retryable on 408/429/5xx), verified this session 2026-05-30. Codifies `flow-engineer`'s agent opinion and house rule §3 #10. The "notify-on-failure never fires" case is the canonical run-after mistake the agent flags.

---

_Last reviewed: 2026-05-30 by `claude`_
