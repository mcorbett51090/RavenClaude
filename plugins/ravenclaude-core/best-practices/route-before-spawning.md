# Traverse the routing tree before spawning a specialist

**Status:** Pattern

**Domain:** Agent design / Multi-agent dispatch

**Applies to:** ravenclaude-core

---

## Why this exists

Spawning a specialist costs tokens, latency, and a context handoff, and picking the wrong one on the first try produces rework (a builder that starts without a settled design, a reviewer handed a diff with no green tests). The Team Lead's failure mode is **keyword-matching the request to an agent name** ("the user said UI, spawn frontend-coder") instead of resolving the request's real signals — which skips the hard gates, most often the security gate. The routing tree is the proactive half of dispatch discipline: it picks the right specialist on the first attempt so the Capability Grounding Protocol only has to clean up genuine failures, not bad first picks.

## How to apply

Before spawning **any** specialist, traverse the Mermaid `## Decision Tree` in [`../knowledge/agent-routing.md`](../knowledge/agent-routing.md) top-to-bottom, resolving each condition node against the user's observable context. The **earliest-blocking gate wins** — a UI change that touches auth spawns `security-reviewer` before `frontend-coder`.

Order of the gates (each `NO` falls through to the next):

```
Q1  Trivial Q&A / single-file ≤10-line tweak / pure orchestration?  -> Team Lead handles directly, NO spawn
Q2  Touches auth, secrets, PII/PCI/PHI, RLS/FLS, new external surface? -> security-reviewer (parallel with builder)
Q3  Multi-file design not yet made, or cross-cutting interface change? -> architect FIRST, then dispatch builders
Q4  Deliverable is prose for a human, not code?                        -> documentarian / project-manager / PSM / designer / prompt-engineer / deep-researcher
Q5  It is code — which surface?                                        -> frontend / backend / fullstack / data-engineer
    then POST: needs tests -> tester-qa ; tests green -> code-reviewer
```

**Do:**
- Default to the leaf with the **smaller spawn cost** when multiple branches could apply, and escalate only if it returns insufficient.
- Default to `fullstack-coder` when one feature slice genuinely spans both ends; split into FE+BE only when the work parallelizes.
- Run `tester-qa` before `code-reviewer` — reviewing a diff with no green tests reviews the wrong artifact.
- Let a domain plugin's more-specific routing rule (e.g. `power-platform`) override this tree when one is installed and matches.

**Don't:**
- Don't spawn `architect` to ratify a trivial 5-line edit, or `deep-researcher` for a question the present user can answer in 30 seconds.
- Don't skip Q2 because the change "looks small" — auth-adjacency is the most-skipped routing call in practice, and the gate is hard regardless of diff size.
- Don't re-traverse the tree from scratch when a spawn comes back blocked — that is the Capability Grounding Protocol's job (alternate-methods enumeration), not the tree's.

## Edge cases / when the rule does NOT apply

- **Team Lead handles directly (no spawn)** when ALL hold: single file, ≤10 lines, no new interface, no security surface, user present for clarifications, tests already in place.
- **Domain override:** when an installed domain plugin's CLAUDE.md routing table matches the request more specifically, the domain routing wins and this tree defers.
- The tree is for the **Team Lead** only. Specialists receive a focused task and do not re-route work.

## See also

- [`../knowledge/agent-routing.md`](../knowledge/agent-routing.md) — the decision tree, per-leaf rationale, and the seven common wrong-first-picks
- [`../knowledge/subagent-isolation-and-tooling.md`](../knowledge/subagent-isolation-and-tooling.md) — fan reads out to sub-agents, keep branch-mutating work in the main session
- [`./three-epistemic-protocols.md`](./three-epistemic-protocols.md) — the reactive half (CGP) that handles a blocked spawn

## Provenance

Distilled from `plugins/ravenclaude-core/knowledge/agent-routing.md` (`## Decision Tree`, "Common wrong-first-picks", "Composition with the Capability Grounding Protocol") and `plugins/ravenclaude-core/CLAUDE.md` §"Agent-routing decision tree (priors — for the Team Lead)".

---

_Last reviewed: 2026-05-30 by `claude`_
