# Configure the runaway brake to catch thrash loops before they burn the budget

**Status:** Pattern
**Domain:** Agent design / Safety / Auto-mode
**Applies to:** `ravenclaude-core`

---

## Why this exists

An agent in auto-mode that hits a persistent error it cannot resolve — a test that always fails, a file it cannot write, a tool that always returns the same denial — will loop: it retries the same failing call repeatedly, burning tokens and API budget without making progress, until the user's session budget is exhausted or the user intervenes. The `runaway-brake.sh` hook provides a deterministic, model-free tripwire: it counts tool calls per session and trips when the agent thrashes (≥ N consecutive byte-identical calls in a row) or blows a total-call ceiling. It converts a silent budget-burning loop into a visible stopped state the user can diagnose.

## How to apply

Configure the brake in `.ravenclaude/comfort-posture.yaml`:

```yaml
# .ravenclaude/comfort-posture.yaml
runaway:
  max_consecutive: 8    # consecutive identical calls before tripping (default 8)
  max_total: 1200       # total tool calls this session before tripping (default 1200)
```

Interpreting a brake trip:
- **`max_consecutive` trip:** the agent looped on the same call — likely a fabricated-error loop, a test that is persistently failing, or a permission it cannot acquire. Read the last N tool calls to diagnose the loop before retrying.
- **`max_total` trip:** the session used more tool calls than expected — likely a large research or analysis task that exceeded the budget. Review whether the task scope needs narrowing or the limit needs raising.

Tuning:
- Lower `max_consecutive` (e.g., 4-5) in narrow-scope sessions where you expect faster convergence.
- Raise `max_total` for legitimate long-running research tasks; set it proportional to the expected task complexity, not to infinity.
- Set `runaway: off` (not omit — omit means use the defaults) only for a specific session where you have manually confirmed the task will use more than the default total.

**Do:**
- Configure the brake before auto-mode sessions where the agent will be running unsupervised.
- When the brake trips, read the `hook-events.jsonl` or the Heimdall tab to see exactly which call repeated before diagnosing and retrying.
- Treat a `max_consecutive` trip as a diagnostic signal, not just a safety stop — the repeated call usually identifies the root cause.

**Don't:**
- Set `max_total: 0` or a near-zero limit — that traps every non-trivial session.
- Disable the brake by omitting the config entirely and hoping the defaults are right for your task — explicit configuration is safer than implicit defaults.
- Restart the session after a trip without reading the events; the same loop will recur.

## Edge cases / when the rule does NOT apply

- Interactive (non-auto) sessions where the user is present and supervising each tool call do not need the brake — the user is the supervision layer.
- CI-mode agent runs where the task is well-defined and the tool-call budget is known in advance — set `max_total` explicitly to the known budget rather than using the default.

## See also

- [`./check-runtime-state.md`](./check-runtime-state.md) — reading `hook-events.jsonl` (the Heimdall tab) is the diagnostic step after a brake trip.
- [`./definition-of-done-gate-makes-done-mean-done.md`](./definition-of-done-gate-makes-done-mean-done.md) — the DoD gate and the runaway brake compose: the brake catches loops, the gate catches "done but broken."
- [`../CLAUDE.md`](../CLAUDE.md) — "Auto-mode guardrails — runaway brake + definition-of-done gate (added 2026-05-29, v0.56.0)".

## Provenance

Distilled from `plugins/ravenclaude-core/CLAUDE.md` §"Auto-mode guardrails — runaway brake + definition-of-done gate", specifically the `runaway-brake.sh` section.

---

_Last reviewed: 2026-06-05 by `claude`_
