---
name: spawn-team
description: Team Lead helper. Given a feature or task, decide which specialized agents to dispatch, prepare their briefs, allocate worktrees, and run them in the right order (sequential vs. parallel). Use this for any change that needs more than one role.
---

# Skill: spawn-team

You are the Team Lead. This skill is your dispatch playbook.

## Step 1 — Decompose the request
Write down, in your own words:
- The user's goal (one sentence).
- The deliverable (what artifact lands in the user's hands at the end).
- Hard constraints (deadlines, perf, compatibility).
- What's *out* of scope (explicit, to prevent drift).

If you can't write these in three minutes, the request is unclear — ask the user before spawning anyone.

## Step 2 — Choose the team

| Signal | Spawn |
|--------|-------|
| Multi-file design choice, schema/API change | architect (always first) |
| Server-side implementation | backend-coder |
| UI implementation | frontend-coder |
| One vertical slice, no stable contract yet | fullstack-coder (instead of backend+frontend) |
| Any non-trivial diff | tester-qa, then code-reviewer |
| Auth, crypto, secrets, untrusted input, deserialization | security-reviewer (mandatory) |

Default flow for a feature:

```
architect
  ↓
backend-coder  ⟂  frontend-coder    (parallel, separate worktrees)
  ↓
tester-qa
  ↓
code-reviewer  ⟂  security-reviewer (parallel; security only if applicable)
  ↓
Team Lead opens PR via /create-pr
```

## Step 3 — Allocate worktrees
For each coder agent, create an isolated worktree using [`new-worktree`](./new-worktree.md). Naming:

```
.claude/worktrees/<role>-<short-slug>/
branch:  agent/<role>/<short-slug>
```

Two coder agents must **never** share a worktree.

## Step 4 — Brief each agent like a new colleague
Bad brief: *"Implement the auth refresh endpoint."*
Good brief: includes (a) the goal, (b) the architect's design link, (c) what's been tried / ruled out, (d) success criteria, (e) response-length cap.

Template:
```
## Goal
<one sentence>

## Context
<links to architect plan, related files, prior commits>

## What's already done / ruled out
<so the agent doesn't redo it>

## Success criteria
<concrete, testable>

## Out of scope
<explicit list>

## Reporting
Return your standard structured report. Cap your response at <N> words.
```

## Step 5 — Run them
- **Independent agents in parallel:** dispatch in a single tool call with multiple Agent invocations.
- **Dependent agents sequentially:** dispatch one, wait for the report, then the next.
- Never spawn the same role twice in parallel on the same branch.

## Step 6 — Reconcile reports
- Read every diff yourself before reporting to the user. Self-reports describe intent, not always reality.
- If reports disagree (e.g. tester says ❌, coder says ✅), the test result wins until proven otherwise.
- Merge worktrees back via fast-forward or `--no-ff` per the project's branching style.

## Step 7 — Close the loop
- Run [`run-full-test-suite`](./run-full-test-suite.md) on the integrated branch.
- Run [`cleanup-worktrees`](./cleanup-worktrees.md) to remove finished worktrees.
- If shipping, hand to [`create-pr`](./create-pr.md).
- Summarize for the user: what shipped, what didn't, what's open.
