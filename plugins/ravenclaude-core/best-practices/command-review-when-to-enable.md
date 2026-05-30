# Turn on command review only where native auto-mode can't reach

**Status:** Pattern

**Domain:** Agent design / Guardrails

**Applies to:** ravenclaude-core

---

## Why this exists

The command-review tribunal (the Thing) convenes up to three cross-vendor reviewer seats on a Bash/tool call and votes ALLOW / EDIT / DENY — real protection, but it costs latency (parallel `claude -p` seats cold-start ~24-29s each) and requires `claude -p` to be available. That cost is only worth paying where it has no cheaper substitute. The Thing exists to put **portable, model-agnostic** guardrails on agentic AI that **routes across multiple model vendors** (e.g. GitHub Copilot CLI using Claude + ChatGPT + Grok), where Claude Code's native `auto` permission mode is unavailable (Anthropic-API/Claude-only). If you run *only* Claude Code, native `auto` may already deliver the catastrophe floor, so the tribunal is an optional add-on, not a requirement.

## How to apply

Decide by host first, then opt in per category:

```
Run ONLY Claude Code?
  -> Prefer native `auto` permission mode for containment.
  -> Treat the Thing as OPTIONAL — add it for its domain concerns, audit trail,
     and yes/no decision-routing, not for the catastrophe floor `auto` already gives.

Route across multiple model vendors (Copilot CLI: Claude/ChatGPT/Grok)?
  -> `auto` is unavailable. The Thing is the layer that delivers the deterministic
     catastrophe floor, self-tamper guard, secret-egress prevention, and
     cross-vendor anti-correlated review. Turn it on.
```

The Thing is **off by default and opt-in per category** — toggle a category's `thing:` switch from the dashboard's Command-review panel, stored in `.ravenclaude/comfort-posture.yaml`. The PreToolUse hook short-circuits with a single `grep` when nothing is toggled, so a non-adopter pays zero cost.

**Do:**
- Run the portable `runaway-brake.sh` + `dod-gate.sh` hooks as the cross-host equivalent of `auto`'s runaway brake and a definition-of-done gate — these complement, not replace, the tribunal (it gates command *safety*; they gate *runaway behavior* and *correctness*).
- Rely on the deterministic pre-LLM screen even when you skip the expensive panel — hard-rule deny (force-push to a protected branch, `curl|sh`) and the self-disable guard **always run**, category-independently, once the Thing is on for any category.
- Keep high-blast / irreversible actions surfaced to the human — force-push is denied outright; `rm -rf`, publish, `gh pr merge` always reach you regardless of `gate_floor`.

**Don't:**
- Don't reach for the Thing as your *primary* containment under pure Claude Code when `auto` covers the floor more cheaply.
- Don't assume the tribunal contains a **subprocess** the agent spawns — it gates the agent's own tools; only the container/worktree (OS-enforced) bounds a script the agent writes and runs.
- Don't expect a category toggle alone to change design behavior — permission level governs tool *execution*, not design *judgment* (that's the separate `design_checkins` flag).

## Edge cases / when the rule does NOT apply

- **High-blast / irreversible decisions never auto-resolve** regardless of mode or host — they always surface to the human (the `security_deny` family, force-push, deletes, prod actions).
- An abstaining or inconclusive panel fails **CLOSED** (deny) at every tier — except in the verified maintainer/dev-repo context, where an abstain downgrades to `ask` (a latency artifact, not a security signal) and never to allow.
- The Thing **can never relax the `security_deny` floor**, and it cannot disable itself (`xc.tribunal-self-disable` denies pre-LLM any mutation of its own substrate).

## See also

- [`./three-epistemic-protocols.md`](./three-epistemic-protocols.md) — the tribunal is the enforced complement to the Claim Grounding protocol
- [`../knowledge/concerns-catalog.md`](../knowledge/concerns-catalog.md) — the machine-readable concern catalog driving seat routing and the pre-LLM screen
- [`../knowledge/claude-code-permissions.md`](../knowledge/claude-code-permissions.md) — §"Read/Edit rules do not protect against subprocess access" (the containment limit)

## Provenance

Distilled from `plugins/ravenclaude-core/CLAUDE.md` §"Command review (the Thing) — tribunal T5" (the "When command review is for you" scope blockquote), §"Auto-mode guardrails — runaway brake + definition-of-done gate", §"Containment posture", and the v0.60.0 dev-repo abstain-downgrade note.

---

_Last reviewed: 2026-05-30 by `claude`_
