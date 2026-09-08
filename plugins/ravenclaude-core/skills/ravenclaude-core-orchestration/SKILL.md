---
name: RavenClaude Core Orchestration
description: >-
  Use this when leading multi-agent work — dispatch specialists, gate reviews,
  handoffs, walls, plan→build→verify, and disciplined problem-solving (first
  principles, Occam, quantitative failure analysis).
---
# RavenClaude Core Orchestration

Generic reusable recipe for orchestrator-worker agent teams. Adapted from RavenClaude plugin `ravenclaude-core`.

## When this applies

- A task needs more than one specialist (design, implement, review, research, security).
- You need consistent handoffs, fail-closed gates, and honest "blocked" reporting.
- Context is hot and you must choose compact vs fresh-session handoff vs a single bounded cheap-lane job.
- Any specialist (or the lead) is stuck and needs disciplined problem-solving — apply **Problem-solving stance** below and the companion skills `quantitative-problem-solving` and `game-theory-basics`.

## Non-negotiable house rules

1. **Single orchestrator.** Only the Team Lead dispatches. Sub-agents return slices + handoff notes; they do not spawn peers.
2. **Capability grounding before "I can't".** Check skills/knowledge, try the next-easiest correct path, then escalate with what was tried, what was ruled out, and the recommended next path.
3. **Structured handoffs.** Human-readable Markdown plus a delimited machine block (status, summary, deliverables, next specialist, confidence, risks).
4. **Gates are gates.** Security/code/QA review is not optional self-critique — fresh context that did not do the work.
5. **Walls escalate.** Same tool+error 3×, impossible compile/test loops, or about-to-`@ts-ignore` → stop inventing; re-read prior → documented default with citation → ask the human (via Chief of Staff when in Grok Bot).
6. **Problem-solving stance (all bots).** If the first attempt fails, **try again with a better hypothesis** — do not stop at one failure or invent a workaround that hides the failure. Ground retries in **first principles**, **logic**, and **Occam's razor** (prefer the simplest explanation that fits the evidence). Prefer quantitative ranking of next tries via [Quantitative Problem Solving](../quantitative-problem-solving/SKILL.md). Use [Game Theory Basics](../game-theory-basics/SKILL.md) when multiple agents/parties have incentives or strategic moves.

## Problem-solving stance (detail)

| Principle | Practice |
|---|---|
| **Retry with learning** | Log what failed, what was ruled out, update beliefs, pick the next EV-positive try. Blind identical retries do not count. |
| **First principles** | Strip to constraints and mechanisms; rebuild the approach from what must be true. |
| **Logic** | Explicit if/then; no leaps; contradictions force a model update. |
| **Occam's razor** | Among explanations consistent with evidence, prefer fewer free parameters / less special pleading. Encode as a prior penalty on complex hypotheses (see quantitative skill). |
| **Math over vibes** | When failure modes, costs, and history exist, score them — don't gut-feel the next poke. |

Companion skills (load when stuck or choosing among costly tries):

- `quantitative-problem-solving` — variables of failure, cost of each try, P(cause \| history), expected value of information
- `game-theory-basics` — payoffs, dominant strategies, Nash/equilibrium intuition, cooperation vs defection for multi-agent/human loops

## Recipe A — Decide whether to delegate

1. Restate goal, deliverable, constraints, and out-of-scope in one short block. If unclear in ~3 minutes, ask before spawning.
2. **Do it yourself** when: trivial Q&A, ≤10-line single-file tweak, work already fully in context, or briefing costs more than doing.
3. **Spawn (often several in one turn)** when: independent fan-out across files/branches; a named gate owns it; fresh context beats self-critique; bulk reading would crowd the lead window.
4. Prefer the **smallest spawn cost** that still meets the need; escalate only if the first specialist returns insufficient.

## Recipe B — Software-change playbook (default sequence)

1. **Architect** — design plan: files, sequencing, risks, open questions.
2. **Implement** — coders (backend/frontend/fullstack) against the plan only.
3. **Review gates** — code-reviewer; add security-reviewer when auth/crypto/secrets/trust boundaries change.
4. **Verify** — tester-qa / test suite; fix or re-route on failures.
5. **Ship hygiene** — PR with clear summary + test plan; no secrets in the diff.

Keep branch-mutating work sequential in the lead session, or give each writer an isolated worktree. Fan out **reads** freely; avoid concurrent writers on one shared tree.

## Recipe C — Gated planning (FORGE-style, condensed)

Use when the deliverable is a **reviewed plan**, not code yet.

Depth ladder (pick one): light → standard → deep.

Always-on pattern:

```
clarify → research+verify → two divergent panels → critic → gap analysis
→ expert tiebreak on conflicts → red-team → synthesize → route → exit
```

**Artifact contract (fail-closed):**

- Each gate writes its full artifact **on disk**; only a **receipt** returns to the orchestrator.
- Receipt fields: gate id, status (`pass|fail|waived`), artifact path, size, ≤5 digest lines, blockers, confidence.
- Downstream gates read upstream artifacts by path — never paste full plans into briefs.
- Append the receipt to a run log **immediately after each gate**, before advancing.
- Advance only if status allows **and** the artifact exists and is non-empty.

## Recipe D — Session continuity

| Reach for | When |
|---|---|
| Compact / continue | Default mid-task; context hot |
| Write a durable handoff brief | Always useful; can write brief then still compact |
| Fresh session handoff | Plugin/hooks must reload; next reader is another host/day/person; task genuinely done |
| Bounded cheap-lane job | One well-defined, low-blast task that should leave the expensive main loop |

Rules of thumb:

- Same task-id / run directory for continuous work — do not invent a parallel id.
- Compaction often keeps data but loses addressability; inject an anchor rather than assuming amnesia.
- Do not conflate "one bounded external job that returns" with "open a new unbounded interactive session."

## Recipe E — Hit a wall (mandatory ladder)

1. **Re-read the prior** — quote the brief/spec/decision tree verbatim into the log.
2. **Documented default** — apply with an inline citation comment naming the authorizing doc.
3. **Quantitative next try** — run `quantitative-problem-solving` (hypothesis table → costs → posteriors → pick max EV / EVPI). Prefer Occam-consistent causes.
4. **Ask the human** (via CoS in Grok Bot) — only after grounded retries; state mechanical cause, approaches tried, why silent alternatives were refused, and 1–2 concrete options.

**Forbidden:** invent APIs, delete failing assertions, `@ts-ignore` / eslint-disable to "make green", rename fields to dodge parse errors, or loop the **same** failing call without a new hypothesis.

## Recipe F — Decision / posture hygiene

- Prefer **decision trees over keyword matching** for routing.
- Treat permission/autonomy posture as an explicit config: deny / ask / allow per category; keep a hard security-deny baseline; personal overrides stay local.
- For irreversible or high-blast actions, require human confirmation before proceeding.

## Focused-task brief checklist

Every specialist brief should include:

- [ ] Narrow task statement
- [ ] Success criteria (testable)
- [ ] In-scope files / systems
- [ ] Out of scope
- [ ] Tools allowed / forbidden
- [ ] Output contract (Markdown + structured result)
- [ ] Stop / escalate conditions
- [ ] On failure: retry with updated hypothesis (first principles / Occam / quantitative skill) before escalating

## Anti-patterns

- Sub-agent spawning sub-agents (hidden orchestration).
- Skipping security/code review because "I already looked."
- Relaying entire gate artifacts through context (cost + drift); use paths.
- Advancing a gate whose artifact is missing/empty.
- Under-delegating bulk independent reads into the lead window.
- Over-delegating one-line fixes that cost more to brief than to do.
- Treating a demo or happy-path glance as verification.
- Giving up after one failure; identical blind retries; vibes over a scored hypothesis table when history exists.

## Credit

Adapted from RavenClaude plugin `ravenclaude-core` (orchestrator-worker dispatch, Capability Grounding, Structured Output, forge-pipeline, spawn-team, session-handoff, wall-handling, set-posture), extended with problem-solving stance + quantitative/game-theory companions.
