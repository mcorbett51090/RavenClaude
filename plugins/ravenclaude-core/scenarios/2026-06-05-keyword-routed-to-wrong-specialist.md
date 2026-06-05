---
scenario_id: 2026-06-05-keyword-routed-to-wrong-specialist
contributed_at: 2026-06-05
plugin: ravenclaude-core
product: orchestration
product_version: "n/a"
scope: likely-general
tags: [team-lead, routing, route-before-spawning, security-reviewer, dispatch, decision-tree]
confidence: medium
reviewed: false
---

## Problem

A Team Lead session received "add a dark-mode toggle to the settings page" and keyword-matched "settings page / toggle / UI" straight to `frontend-coder`. The coder built the toggle by persisting the preference to a new `/api/user/preferences` endpoint that read a session cookie — i.e. the change quietly touched auth and an external surface. No `security-reviewer` was spawned because the *word* "auth" never appeared in the request. The diff reached review with an unauthenticated write path on a user-scoped resource. The miss was a **route-before-spawning** violation: the Team Lead pattern-matched the request's surface words to an agent name instead of traversing the routing decision tree against the request's *observable signals*.

## Context

- Surface: domain-neutral, `ravenclaude-core` Team Lead orchestrating the 14-agent roster.
- The routing rule the session skipped is explicit: traverse [`../knowledge/agent-routing.md`](../knowledge/agent-routing.md) `## Decision Tree` top-to-bottom and resolve each gate against the request's signals — **do NOT keyword-match the request to an agent name** (CLAUDE.md §"Agent-routing decision tree (priors)").
- The tree's Q2 ("Touches auth, secrets, PII/PCI/PHI, RLS/FLS, or a new external surface?") is a **hard, earliest-blocking gate** that fires *before* Q5 (which surface does the code touch). A UI change that touches auth spawns `security-reviewer` first — that is exactly the worked example in the constitution's routing note.
- Why it slipped: "settings page" reads as pure UI. The auth surface was *latent* in the implementation, not stated in the request — so a keyword match could never have caught it; only traversing the gates against what the change would actually *do* catches it.

## Attempts

- Tried: keyword-match request → `frontend-coder` (the wrong-first-pick). Outcome: a UI build that silently added an unauthenticated write endpoint; the earliest-blocking security gate was skipped.
- Tried: re-running the routing tree *after* the blocked review, against the change's observable signals rather than its words. Q2 now fires — the feature persists a per-user preference (a user-scoped external surface), so `security-reviewer` is mandatory and runs in parallel with `frontend-coder`. Outcome: the gate that should have fired first now fires.
- Tried (the move that worked): made the Team Lead's first step a top-to-bottom tree traversal on **what the change does**, not what it's called — and treated the **earliest-blocking gate as the winner** even when a later branch (Q5 → frontend) looks like the obvious home. The auth gate (Q2) beats the surface gate (Q5). Outcome: `security-reviewer` spawned alongside the builder; the unauthenticated-write path was caught pre-merge instead of at review.

## Resolution

The defect was **keyword-matching a request to an agent name instead of traversing the routing tree against observable signals** — the single most-flagged dispatch failure in the constitution. "Settings page" is not a routing signal; "persists a per-user resource over an endpoint" is, and it trips the auth gate. The fix is procedural, not a code change: route-before-spawning means *traverse, don't pattern-match*, and the earliest-blocking gate wins over the more-obvious later leaf.

**Action for the next session hitting this pattern:** before spawning any specialist, traverse [`../knowledge/agent-routing.md`](../knowledge/agent-routing.md) against what the change will *do*, not what it's called. Treat Q2 (auth / secrets / PII / RLS / new external surface) as a hard gate that fires before any surface-of-code branch — a UI change that touches auth spawns `security-reviewer` first. When two branches both apply, the earliest-blocking one wins. This is the proactive half of dispatch discipline; the reactive half (a chosen specialist comes back blocked → enumerate alternatives) is the Capability Grounding Protocol. `[verify-at-use]` the current routing tree — the roster and its gates evolve as agents are added.
