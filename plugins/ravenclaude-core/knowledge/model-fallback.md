# Model-fallback — the model-unavailable ladder for RavenClaude's own `claude -p` calls

When a model a RavenClaude process invokes **errors or becomes unavailable**, the process should
retry the same call on the next model in a configured ladder rather than failing — and **fail safe**
(the caller's existing abstain path) when the ladder is exhausted. This is the shared mechanism; the
retry logic lives in **one** place: [`hooks/_model-fallback.sh`](../hooks/_model-fallback.sh).

FORGE-planned 2026-06-24 (cross-model panels A=haiku/B=sonnet — the panel dispatch itself walked the
ladder `opus 529 → fable unavailable → haiku ✓`, live proof of the failure mode). Run record:
`.ravenclaude/runs/forge/model-fallback/`.

## The hard scope boundary (load-bearing)
| Surface | Can RavenClaude fall it back? |
| --- | --- |
| **RavenClaude's own model calls** — tribunal seats (`thing-seat.sh`), the convergence judge (`judge.sh`), the orchestrator (`claude-orchestrate.sh`), decision-review (`thing-decide.py`), workflow agent dispatches | **YES** — the ladder below |
| **The harness** — the auto-mode **safety classifier** (fixed to `claude-opus-4-8`) and the **main-loop / session model** | **NO** — RavenClaude cannot fall back the layer it runs *inside*. See the runbook at the bottom. |

A model-fallback ladder is **net-new**, not a duplicate of `claude-orchestrate.sh`: that script already
"falls back" — but to the **host CLI**, never to another **model**. The ladder inserts *before* that
host-fallback.

## The error-classification table (the crux)
`claude -p --output-format json` returns `is_error: true` for *every* failure — auth, bad input,
overload, model-not-found. Retrying the wrong ones **masks a real bug and burns budget**. So the helper
captures the error body (never `2>/dev/null` — the Copilot-adapter Phase-1 stderr-capture pattern) and
classifies:

| Error | Action | Why |
| --- | --- | --- |
| `overloaded_error` / 429 / 529 / 503 / network / timeout | **retry next rung** | capacity/connectivity — another model satisfies it |
| `authentication_error` / `permission_denied` / `invalid_api_key` | **STOP (no retry)** | same auth on every model; retrying loops silently |
| `invalid_request_error` / `context_length_exceeded` / "prompt is too long" | **STOP** | same input fails identically |
| `model_not_found` / "no such model" | **skip this rung, try next** (don't spend a retry) | a named model is gone, not an outage |
| pre-call exits — secret-scrub / injection / recursion-guard | **STOP** | not a model problem; retrying bypasses a correct guard |
| unknown nonzero failure | **STOP (conservative)** | never silently mask an unclassified error |

## The two seams (the highest-risk interaction)
The invariants are checked on the **configured** model, but fallback changes the **resolved** model:
1. **Tribunal model-diversity** (`thing-decision.py`, v0.32.0): ≥2 distinct backbones when ≥2 seats.
2. **Judge anti-self-grade** (`judge.sh`): judge model ≠ author model.

So the helper takes `--exclude <peer/author models>` (never returns an excluded model) AND exposes the
**resolved** model (via `_MF_RESOLVED_FILE`) so the caller re-checks the invariant on what *actually*
answered — not what was configured. **At `extreme` tier the panel FAILS CLOSED rather than downgrade
the mandatory Forseti security seat to a weaker model.** (The resolved-model re-check is the planned
**Gate 121**, landed when the callers are wired — see "Phasing" below.)

## Config (`.ravenclaude/comfort-posture.yaml`) — opt-in, default OFF
```yaml
model_fallback:
  enabled: false          # absent/false ⇒ byte-identical to a single direct call
  ladder: [claude-haiku-4-5, claude-sonnet-5, claude-opus-4-8]
  max_retries: 2          # fallback attempts after the primary (hard cap 3 — the cost bound)
  on_exhausted: fail-safe # caller's existing abstain path; never silently wrong
```

## The helper contract (`hooks/_model-fallback.sh`)
Sourced (not executed). The caller provides a one-arg **runner** that runs its full `claude -p …
--model <model> …`, prints stdout, writes stderr to `$_MF_ERRFILE`, and returns claude's exit code:
```bash
. "$(dirname "$0")/_model-fallback.sh"
_run() { claude -p --output-format json --model "$1" --tools "" --append-system-prompt "$sp" "$user" 2>"$_MF_ERRFILE"; }
MODEL_FALLBACK_PRIMARY="$THING_MODEL" MODEL_FALLBACK_ENABLED=1 \
MODEL_FALLBACK_LADDER="claude-sonnet-5,claude-opus-4-8" \
  _model_call_with_fallback --runner _run --exclude "$author_model"
# on success: stdout = the winning model's result; $(cat "$_MF_RESOLVED_FILE") = the resolved model
# on exhaustion / a STOP-class error: non-zero → caller maps to its abstain exit (5 / 6 / 3 / defer)
```
The disabled path (`enabled` ≠ 1) tries only the primary, once — byte-identical to today. Proven by
**Gate 120** (`hooks/tests/test-gate120-model-fallback.sh`): classification, the cost cap, `--exclude`,
disabled-byte-identical, and a must-fail half (stripping the classifier ⇒ auth retries — teeth).

## Phasing (status)
- **P0/P1 — shipped:** config schema + this knowledge file + the shared helper + **Gate 120**.
- **P2a — shipped (security-cleared):** `claude-orchestrate.sh` wired (the helper inserts before its
  existing host-fallback).
- **P2b — shipped (security-cleared):** `judge.sh` wired with `--exclude author` **and** a
  family-aware anti-self-grade RE-CHECK on the resolved model (the unified `_is_selfgrade`).
- **P3 — shipped (security-reviewed 🟡, residual tracked):** the command-review tribunal **seats**
  wired. `thing-orchestrator.sh` passes each seat the OTHER convened seats' **primary** models as
  `MODEL_FALLBACK_EXCLUDE`, so a fallback never lands on a peer's *configured* model; an exhausted
  ladder abstains (fail-closed). No `thing-decision.py` change (the orchestrator derives the
  peer-exclude from the panel JSON it already reads).
  - **Two-layer guard.** (1) *Prevent* — peer-exclude keeps a fallback off a peer's configured
    model (reduces, doesn't eliminate, collision: two distinct-primary seats that both overload could
    still fall to the same shared-ladder rung). (2) **Detect + fail closed (the actual closure)** —
    each seat surfaces its **resolved** model (`_MF_RESOLVED_FILE` → `$tmp/$role.resolved`); the
    orchestrator's post-panel **runtime model-diversity gate** counts distinct resolved models among
    *voted* seats and, if <2, forces the verdict to `$posture` (fail closed — a genuine deny for the
    high-stakes categories). So a runtime collapse can no longer pass as a clean panel. Proven by
    **Gate 121** (collapse ⇒ deny+reason / distinct ⇒ inert / neutered-guard ⇒ no-deny teeth). When
    fallback is OFF (default) seats resolve to their pre-enforced-distinct configured models, so the
    gate never triggers — zero behavior change.
  - **Remaining minor notes:** the prevent-layer is conservatively exclude-*all*-peers (can force an
    abstain on a ≥3-seat panel where a collision would still leave ≥2 distinct — safe over-
    approximation); and **Thor** (the tie-breaker, run after the panel as the decider) is dispatched
    without a peer-exclude — decide its posture if the exclude semantics are revisited. Neither is a
    floor concern.
- **P4 — deliberately NOT wired (reasoned disposition).** `rc-deep-research.js`'s research `agent()`
  fan-out already fails safe by two existing mechanisms: the Workflow runtime **already retries an
  `agent()` call on transient errors and returns `null`** on terminal failure, and the workflow
  **`.filter(Boolean)`s** those nulls — an overloaded model degrades research completeness, never
  crashes the run. Adding an explicit model-fallback wrapper there would be largely redundant with
  that resilience AND would have to thread through the workflow's two strict byte-identical floors
  (Gate 51 substrate-adapter, Gate 52 dispatch-evaluator) for marginal value. Disposition: rely on
  the existing runtime retry + null-filter; revisit only if research-under-overload completeness
  becomes a measured problem. (This is the value-add-completeness discipline: don't force a rung that
  duplicates existing resilience and risks two gates.)

## Runbook — when the HARNESS layer is down (out of RavenClaude's control)
If the **safety classifier** (`claude-opus-4-8`) or the **main-loop model** is unavailable — symptom:
*"<model> is temporarily unavailable, so auto mode cannot determine the safety of …"* gating Bash/MCP/
agent-dispatch — RavenClaude code cannot route around it. The fallbacks are operator-level:
1. **Run the command yourself** via the `!` prefix (user-invoked → not agent-classified).
2. **Switch the permission mode** so the classifier isn't consulted: Shift+Tab to *bypass permissions*,
   or relaunch `claude --dangerously-skip-permissions`.
3. **Wait** — the outage is usually transient and intermittent.

*(This session, 2026-06-24, is the worked example: an extended `claude-opus-4-8` classifier outage
gated every non-read-only tool; the FORGE panels that planned this very feature completed only after
switching to bypass-permissions mode — and Panel A reached a model by walking the ladder this feature
defines.)*
