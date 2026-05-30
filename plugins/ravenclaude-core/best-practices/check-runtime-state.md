# Check your runtime state before you act — the observability substrate is there to be read

**Status:** Pattern

**Domain:** Agent design / Situational awareness

**Applies to:** ravenclaude-core

---

## Why this exists

An agent that acts blind to what already happened in the repo repeats avoidable mistakes: it retries a command a guardrail just denied, re-proposes a posture change that was made an hour ago, or surfaces a scenario without knowing it was already useful (or already wrong) last week. RavenClaude emits a **structured event substrate** precisely so the agent — and the human — can answer "what just happened here?" without reconstructing it from memory. Reading that substrate before acting is the situational-awareness complement to the SessionStart capability banner: the banner tells you what you _can_ do; the event log tells you what _has been done_.

This is **situational awareness as a discipline**, not a feature: the data only helps if the agent (or operator) actually consults it at the moments it matters.

## The three event streams and their readers

Every guardrail verdict, posture change, and surfaced scenario lands in an append-only JSONL stream under `.ravenclaude/`, and each has a read-only dashboard surface:

| Stream | Emitted by | Dashboard reader | Answers |
| --- | --- | --- | --- |
| `runs/<session>/hook-events.jsonl` | the verdict-emitting hooks (`enforce-layout`, `guard-destructive`, `guard-recursive-spawn`) | **Heimdall** tab (`#/heimdall`) | "what guardrail tripped just now, and how bad?" |
| `posture-events.jsonl` | `apply-comfort-posture.py` on every change | **Víðarr** tab (`#/vidarr`) | "how did my security posture change over time?" |
| `runs/<run-id>/events.jsonl` (`scenario_surfaced`) | the `scenario-retrieval` skill | **Norns** tab (`#/norns`, Urðr column) | "when was this knowledge last useful?" |

All three are **read-only mirrors** — the readers surface what the upstream sources already emitted; they never write back.

## How to apply

**When you hit a guardrail deny, read the event before retrying.** A `deny`/`warn` verdict wrote a line to `hook-events.jsonl` with the `rule` token that fired (`off-allow-list`, `destructive-pattern`, `task-scope-out-of-scope`, …). The `rule` tells you _why_ — which usually points at the fix (add the glob to `.repo-layout.json`, widen `task-scope.json`, or recognize the command is genuinely refused) faster than guessing. Re-running the identical command without reading the verdict is the anti-pattern.

**Before proposing a posture change, check whether it already happened.** `posture-events.jsonl` (the Víðarr tab) records every `security_deny`/override diff with its source (`dashboard-save`, `slash-command`, `reapply`, …). If the change you're about to suggest is already in the log, surface that instead of re-proposing it.

**When citing a scenario, the Urðr column shows its surfacing history.** A scenario that has surfaced repeatedly is a stronger prior than one that never has; one that surfaced and was then contradicted is a flag. This is the substrate the unverified-scenario preamble leans on.

**The data is served-only.** The hook/posture/scenario logs are git-ignored and per-consumer, so the dashboard reads them through the local server (`scripts/serve-dashboards.py` / `rc dashboard`), not on a static GitHub Pages host. On a static host each panel shows an honest empty state pointing at the served dashboard — that empty state is **not** "all clear," it means "this surface can't see your files from here."

## Anti-patterns

- **Retrying a denied command unchanged.** The verdict already told you the rule that fired; read it, then fix the cause or accept the refusal — don't loop.
- **Treating a static-host empty state as "nothing happened."** It means the panel can't read the per-consumer logs from a static host, not that the perimeter is clean. Open the served dashboard.
- **Re-proposing a posture/security change already in `posture-events.jsonl`.** Check Víðarr first.
- **Writing to the event logs to "fix" the display.** They are append-only mirrors of upstream emitters; the fix belongs at the source, never in the log.

## See also

- [`three-epistemic-protocols.md`](./three-epistemic-protocols.md) — the honesty floor; "check before you act" is the situational-awareness sibling of "verify before you claim."
- [`../CLAUDE.md`](../CLAUDE.md) — the "Structured event substrate", "Heimdall", "Víðarr", and "Norns" sections (the authoritative reference for each stream + reader).
- [`../CLAUDE.md`](../CLAUDE.md) § "Session-start environment-context load" — the capability banner, the _can-do_ half of situational awareness.
