---
name: spawn-team
description: Team Lead dispatch playbook. Given a feature or task, decide which specialized agents to dispatch, prepare their briefs, allocate worktrees, run them in the right order, and re-route on blockers. Load this skill whenever you (the Team Lead) are about to dispatch more than one agent on a request. Keeps routing consistent across sessions and avoids re-deriving the workflow each time.
---

# Skill: spawn-team

You are the **Team Lead** — the top-level Claude session. This skill is your dispatch playbook. Use it whenever a request needs more than one specialist.

The dependency graph stays a tree: **you** dispatch all sub-agents directly. No sub-agent spawns peers.

---

## Step 1 — Decompose the request

Write down, in your own words:
- The user's goal (one sentence).
- The deliverable (what artifact lands in the user's hands at the end).
- Hard constraints (deadlines, perf, compatibility).
- What's *out* of scope (explicit, to prevent drift).

If you can't write these in three minutes, the request is unclear — ask the user before spawning anyone.

---

## Step 2 — Pick the playbook

These are the standard dispatch patterns. Pick the one that matches the request, adapt as needed, and *say which playbook you're running* in your final summary.

### Software change (feature, bugfix, refactor)
Default sequence — gates between phases are mandatory:

1. **architect** — produce design plan. Output: structured plan with files to touch, sequencing, risks, open questions.
2. **architect → coder hand-off:** if open questions exist, resolve with the user before dispatching the coder.
3. **backend-coder / frontend-coder / fullstack-coder** — implement per plan. Pick by surface area; default to backend-coder for server-only, frontend-coder for UI-only, fullstack-coder only when the change is one cohesive cross-boundary unit.
4. **tester-qa** — write or extend tests, run them. If tests fail in unexpected ways → re-dispatch architect (design issue) or coder (impl issue) based on root cause.
5. **architect** — short consult if testing surfaced anything that contradicts the plan or expands scope. Skip if the test phase was clean.
6. **code-reviewer** — pre-merge review. Blockers → back to coder.
7. **security-reviewer** — mandatory if the change touched auth, crypto, secrets, untrusted input, file upload, deserialization, SQL, shell, network egress, or third-party integrations. Skip otherwise.
8. **architect** — final pass on iterative changes from review. Skip if review was clean.

The architect is the technical conscience for the whole lifecycle. Pull them back in whenever a phase boundary surfaces a question that exceeds a coder/tester/reviewer's authority.

### Research-only
Single specialist, no sequencing.

1. **deep-researcher** — produce brief with citations and confidence labels. Done.

### Stakeholder document (memo, exec summary, runbook, release notes, partner brief)
1. **deep-researcher** — *only* if the document needs verified facts the user/system doesn't already have. Skip when the user supplies the inputs.
2. **documentarian** — drafts the document from inputs. Saves under `docs/deliverables/<type>/`.

### Visual artifact (UI screen, dashboard layout, slide deck, infographic)
1. **architect** — only if the artifact is part of a code change with structural implications. Skip for standalone slides / handouts.
2. **designer** — produces the design spec under `docs/design/`.
3. **frontend-coder** — implements (only when the artifact is code). For non-code artifacts (Power Apps, slides, etc.), the user owns production; the spec is the deliverable.

### PM hygiene (RAID, status, tasks, activity log, stakeholder register)
1. **project-manager** — single specialist. Done.

### Partner success work (profile, success plan, QBR prep, health score, onboarding, AI workflow library)
1. **partner-success-manager** — single specialist. Done.
2. **documentarian** — *only* if a partner-facing re-cut of a PSM artifact is needed (warmer voice, less internal candor). The PSM artifact is read-only input; documentarian produces a *new* file under `docs/deliverables/partner-briefs/`.

### Prompt library work (new agent, new skill, prompt critique, library refactor)
1. **deep-researcher** — *only* if Anthropic ships new guidance worth absorbing. Skip otherwise.
2. **prompt-engineer** — authors / critiques / refactors. May edit `.claude/agents/`, `.claude/skills/`, `.claude/rules/`.

### Ambiguous prompt
The user's request doesn't map to any playbook above. Don't guess.
1. Ask the user one tight clarifying question.
2. Once disambiguated, pick the right playbook.

### Quick-look signal table

| Signal | First specialist |
|--------|------------------|
| Multi-file design choice, schema/API change | architect |
| Server-side implementation | backend-coder |
| UI implementation | frontend-coder |
| One vertical slice, no stable contract yet | fullstack-coder |
| Research / verification / unfamiliar error | deep-researcher |
| Stakeholder prose / memo / runbook | documentarian |
| Visual / UX / accessibility | designer |
| RAID, status, tasks, stakeholder register | project-manager |
| Partner profile, QBR, health score, onboarding | partner-success-manager |
| New agent, prompt critique, library refactor | prompt-engineer |
| Auth, crypto, secrets, untrusted input | security-reviewer (mandatory) |
| Any non-trivial diff | tester-qa, then code-reviewer |

---

## Step 3 — Allocate worktrees

For each coder agent, create an isolated worktree using [`new-worktree`](./new-worktree.md). Naming:

```
.claude/worktrees/<role>-<short-slug>/
branch:  agent/<role>/<short-slug>
```

Two coder agents must **never** share a worktree.

---

## Step 4 — Brief each agent like a new colleague

A bad brief is the most common cause of bad agent output. Every brief includes:

1. **Goal** — one sentence the agent could repeat back.
2. **Context** — file paths, excerpts, prior agent reports relevant to *this* phase. The agent has no prior conversation memory.
3. **What's been tried / ruled out** — saves wasted work.
4. **Success criteria** — concrete, testable.
5. **Boundaries** — what's out of scope.
6. **Reporting cap** — word / line limit ("under 300 words").
7. **Playbook context** — which playbook step this is, what the previous step produced, what the next step expects.

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

## Playbook context
Step <N> of <playbook name>. Previous step produced <X>. Next step expects <Y>.

## Reporting
Return your standard structured report. Cap your response at <N> words.
```

---

## Step 5 — Run them

- **Independent agents in parallel:** dispatch in a single tool call with multiple Agent invocations.
- **Dependent agents sequentially:** dispatch one, wait for the report, then the next.
- Never spawn the same role twice in parallel on the same branch.

### Parallel reviewer fan-out (standard pattern)

After the build phase produces a diff, dispatch `code-reviewer` and (if the change touches auth/crypto/secrets/untrusted-input/SQL/shell/network/third-party-integration) `security-reviewer` **in parallel, in a single tool call**. They review the same diff independently — independent reviewers mitigate self-agreement bias. Ideally use diverse models (one Claude, one Codex/Gemini) for the reviewer stage when the change is high-stakes.

## Step 5.5 — Artifact-based handoff (the primary substrate)

Reports flow back to the Team Lead **as pointers to artifacts on disk**, not as inline pasted content. This mirrors Anthropic's own multi-agent research architecture: agents write artifacts to a shared filesystem and return lightweight references. The Team Lead loads only what the next dispatch actually needs.

### Convention

Every multi-agent run writes to:

```
.ravenclaude/runs/<run-id>/
  01-design.md           ← architect's plan (human-readable)
  01-design.json         ← architect's plan (structured, next agent's input)
  02-plan.md / .json     ← project-manager or architect, sequencing
  03-impl.json           ← coder's diff manifest (worktree path + files touched)
  04-review-code.json    ← code-reviewer verdict
  04-review-security.json ← security-reviewer verdict (when run)
  events.jsonl           ← chronological action log (optional)
  summary.md             ← Team Lead's final summary back to the user
```

The `<run-id>` is a short slug or timestamp + slug. The Team Lead creates `.ravenclaude/runs/<run-id>/` before the first dispatch and includes the path in every brief.

### What goes in each brief

Add to the standard brief template (Step 4):

```
## Artifacts
- Read prior artifacts: <list of paths under .ravenclaude/runs/<run-id>/>
- Write your output to: .ravenclaude/runs/<run-id>/<your-phase-name>.{md,json}
- Return only: a path + the Structured Output Protocol JSON block.
```

### Why this matters

Without on-disk artifacts, every handoff is "telephone game" — each successor sees a summary of a summary, decisions degrade, and rework compounds. With artifacts, the orchestrator (Team Lead) can re-read source material directly when synthesizing, and any agent can be re-dispatched with the exact same input.

---

## Step 6 — Re-routing protocol

When an agent surfaces a problem, route by the *type* of problem, not by which agent surfaced it:

| Surfacing | Likely cause | Where to route |
|-----------|--------------|----------------|
| Tester finds a bug in coder's diff | Implementation error | back to **coder** with the failing test attached |
| Tester finds behavior that contradicts the design | Design assumption was wrong | back to **architect** to re-plan; coder waits |
| Reviewer flags a structural issue | Design didn't anticipate this concern | **architect** adjudicates; coder revises after |
| Reviewer flags style / nit | Quick fix | back to **coder** |
| Reviewer flags a security concern | Threat model issue | **security-reviewer** (if not already run); architect if structural |
| Researcher returns "no source found" for a load-bearing claim | Knowledge gap | surface to the user — do not have another agent guess |
| Designer needs information about a constraint | Scope question | ask the user |
| PSM surfaces a partner risk during work | New RAID item | **project-manager** to log it; PSM continues |
| Documentarian surfaces a fact gap | Source insufficient | **deep-researcher** if external; ask the user if internal |
| Agent A asserts another agent's prior artifact is wrong (confidence ≥ 0.7, correctness-critical domain) | Contested claim that one orchestrator test can't settle | **deep-researcher in citation-only mode** — apply [Cited-Adjudicator Escalation](../rules/agent-collaboration.md#cited-adjudicator-escalation) |
| Any agent goes silent for >5 minutes | Blocked or stuck | abort and re-dispatch with a tighter brief |

---

## Step 7 — Reconcile reports

- Read every diff yourself before reporting to the user. Self-reports describe intent, not always reality.
- If reports disagree (e.g. tester says ❌, coder says ✅), the test result wins until proven otherwise.
- Merge worktrees back via fast-forward or `--no-ff` per the project's branching style.

---

## Step 8 — Close the loop

- Run [`run-full-test-suite`](./run-full-test-suite.md) on the integrated branch.
- Run [`cleanup-worktrees`](./cleanup-worktrees.md) to remove finished worktrees.
- If shipping, hand to [`create-pr`](./create-pr.md).
- Summarize for the user: which playbook ran, what shipped, what didn't, what's open.

---

## Output Contract (your summary back to the user)

```
## Playbook
<which playbook ran, with deviations noted>

## Sequence executed
1. <agent> — <one-line outcome> — Status: ✅/⚠️/❌
2. <agent> — <one-line outcome> — Status: ✅/⚠️/❌
3. …

## Re-routes
- <when / why> — <where it went>
(or "none — clean run")

## Verified vs. self-reported
- <what you actually checked yourself, vs. what came from agent self-reports>

## Final state
- Files changed: <paths>
- Gates passed / failed: <list>
- Artifacts produced: <paths>

## Open questions for you
- <question>
```
