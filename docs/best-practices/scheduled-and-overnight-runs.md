# Run agents on a schedule / overnight — the sanctioned pattern

**Status:**
- **Pattern** — strong default; deviate only with a written reason.

**Domain:** Agent design / Cross-domain

**Applies to:** `ravenclaude-core`, any Claude Code (web/remote) project that wants unattended or recurring agent work.

---

## Why this exists

The article that prompted the [2026-06-04 features gap analysis](../research/2026-06-04-claude-features-gap-analysis/gap-analysis.md) lists **Scheduled Tasks** ("Claude that works while you sleep") as a capability most people never turn on. RavenClaude already has every primitive needed to do this well — but they were scattered across three surfaces with **no single doc** telling you how to combine them safely. Without that, "run it overnight" either doesn't happen, or happens without the guardrails that make unattended autonomy safe. This doc is the missing pattern: how to compose the recurring/scheduled/unattended primitives **inside** the existing destructive- and high-blast guards, so a sleeping operator never wakes up to an irreversible surprise.

**Reach this for:** "check the deploy every 5 minutes," "babysit this PR until it's green," "re-run the research each morning," "keep iterating overnight while I'm away."

## The primitives (what each one is, and where it lives)

| Primitive | What it is | Surface |
|---|---|---|
| `loop` skill | Run a prompt or slash command on a recurring interval (`/loop 5m /foo`). | Harness skill (Claude Code), not repo code |
| `send_later` | Schedule a self check-in at a future time; you're re-woken to re-evaluate. | Harness MCP tool (when available) |
| `subscribe_pr_activity` / `unsubscribe_pr_activity` | Wake the session on PR webhook events (CI failure, review comments). | GitHub MCP |
| `Monitor` (background) | Stream events from a long-running poll/tail; one notification per event until a terminal state. | Harness tool |
| `runaway-brake.sh` + `dod-gate.sh` | Depth + correctness guards — trip on thrash / block "looks done" until the DoD command passes. | `ravenclaude-core` hooks (opt-in via `comfort-posture.yaml`) |
| `guard-destructive.sh` + `security_deny` floor | The irreversible-action floor that holds **regardless** of autonomy. | `ravenclaude-core` hook + posture |

> **Honest scope note.** `loop`, `send_later`, `subscribe_pr_activity`, and `Monitor` are **harness features**, not things this repo ships — so this doc is a *composition pattern*, not new machinery. There is intentionally no `loop` skill in `plugins/`. What the repo *does* own is the guard half (`runaway-brake.sh`, `dod-gate.sh`, the `security_deny` floor), which is what makes unattended use of the harness primitives safe.

## How to apply

### 1. Recurring / scheduled work
- **Fixed interval, same task:** `loop`. Example: `/loop 10m /babysit-prs`. Keep the interval ≥ the task's runtime so runs don't stack.
- **One future re-check (not a tight loop):** `send_later` — schedule a self check-in ~an hour out, re-evaluate state when it fires, act on anything actionable, then **re-arm silently if nothing changed**. This is the right tool for "the webhook won't tell me about CI *success* or merge-conflict transitions — so come back and look."
- **Per-occurrence until a known end:** a background `Monitor` whose filter matches **every terminal state, not just the happy path** (success *and* the failure signatures). Silence must never be mistakable for success.

### 2. Event-driven (PR babysitting)
- `subscribe_pr_activity` for each PR, then **end your turn** — do not poll with `sleep`. Events wake you.
- Because webhooks do **not** deliver CI success, new pushes, or merge-conflict transitions, pair the subscription with a `send_later` re-check (or a `Monitor` poll) so the loop has a way to observe the states the webhook omits.
- A subscription is finished only when the PR is **merged or closed** — or the user says stop (then `unsubscribe_pr_activity`).

### 3. The guardrails that make "unattended" safe (non-negotiable)
Turn these on in `.ravenclaude/comfort-posture.yaml` *before* leaving an agent running unattended:

```yaml
# Bound runaway depth + total work this session
runaway:
  max_consecutive: 8 # identical calls in a row before tripping
  max_total: 1200 # total tool calls before tripping

# Turn "looks done" into "is done" — block Stop until this passes
definition_of_done:
  cmd: "npm test && npm run lint"
  max_blocks: 8

# The irreversible floor — holds at every autonomy level
security_deny:
  - "Bash(git push --force:*)"
  - "Bash(rm -rf:*)"
  # …the rest of the floor
```

**Do:**
- Compose: `subscribe_pr_activity` (event-driven) **+** `send_later` (covers the states webhooks miss) **+** `runaway` / `definition_of_done` (bound depth and correctness).
- Keep `decision_review: binding` and `design_checkins` honest — high-blast/irreversible decisions still `defer` to the human even overnight; they are exactly the things that should wait for morning.
- Make every `Monitor` filter cover the failure signatures, not just success.

**Don't:**
- Don't `sleep` in the foreground to wait for an external event — schedule a re-check (`send_later`) or stream it (`Monitor`).
- Don't relax the `security_deny` floor to "move faster overnight." Unattended is precisely when the floor matters most.
- Don't let a `loop` interval be shorter than the task runtime (runs stack and thrash the runaway brake).

## Edge cases / when the rule does NOT apply

- **A single, short, attended task** needs none of this — just run it.
- **High-blast or irreversible work** (force-push, prod deploys, deletes, publishes) should **not** be left to an unattended loop at all — these always `defer` to the human regardless of posture, so an overnight loop will (correctly) stall on them rather than complete them.
- **`send_later` unavailable** in the current session → fall back to a `Monitor` poll that exits on terminal state, or accept that only webhook-delivered events will wake you (and say so).

## See also

- [Features gap analysis (2026-06-04)](../research/2026-06-04-claude-features-gap-analysis/gap-analysis.md) — gap **B2**, which this doc closes.
- [`plugins/ravenclaude-core/CLAUDE.md`](../../plugins/ravenclaude-core/CLAUDE.md) → "Auto-mode guardrails — runaway brake + definition-of-done gate" — the guard half.
- [GitHub API + rate limits](./github-api-and-rate-limits.md) — relevant when a `Monitor` poll hits the Actions API.

## Provenance

Authored 2026-06-04 closing gap **B2** from the features gap analysis (itself prompted by an `@AnatoliKopadze` X post on Claude features). The guard primitives it composes — `runaway-brake.sh`, `dod-gate.sh`, the `security_deny` floor — are the ones already documented in `ravenclaude-core/CLAUDE.md`; this doc adds the missing "how to combine them for unattended runs" layer.

---

_Last reviewed: 2026-06-04 by `mcorbett51090`_
