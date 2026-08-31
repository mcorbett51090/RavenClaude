---
name: spawn-team
description: Team Lead dispatch playbook. Given a feature or task, decide which specialized agents to dispatch, prepare their briefs, allocate worktrees, run them in the right order, and re-route on blockers. Load this skill whenever you (the Team Lead) are about to dispatch more than one agent on a request — and also when you are weighing whether a request warrants delegation at all, since Step 1.5 argues that fork in both directions and the current model under-spawns by default. Keeps routing consistent across sessions and avoids re-deriving the workflow each time.
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

## Step 1.5 — Decide *whether* to delegate at all (this fork runs both ways)

Every other lever in this playbook bounds you from spawning **too much**: the `parallelism` cap (Step 5)
bounds breadth, the runaway brake bounds depth, [`agent-routing.md`](../../knowledge/agent-routing.md)'s
tradeoffs table prices every specialist as a **"spawn cost"** to be justified, `guard-recursive-spawn.sh`
warns on nesting, and the briefs carry reporting caps. Over-delegation is a real failure mode and it is
well covered.

**It is not the failure mode this model has.** *"Claude Opus 4.8 tends to spawn fewer subagents by
default. However, this behavior is steerable through prompting; give Claude Opus 4.8 explicit guidance
around when subagents are desirable"* — [Prompting Claude Opus 4.8](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-4-8),
retrieved 2026-07-15. Stack an under-spawning model on a playbook whose every other lever restrains
fan-out and the two **compound**: the model hesitates and the harness agrees with it. This step is the
counterweight, and it is the only place here that argues *for* dispatch.

**Do it yourself — don't spawn.** You can finish it in a single response: trivial Q&A, a ≤10-line
single-file tweak, a refactor of a function already in your context, or anything where writing the brief
costs more than doing the work. (This is the `(none — Team Lead direct)` row of the tradeoffs table.)

**Spawn — and spawn several in the same turn — when any of these hold:**

- **Fan-out across items.** N independent files, plugins, branches, or findings to read or check.
  Dispatch N subagents in **one turn**. Reading all N into your own context yourself, or looping them
  serially, is the under-delegation tell — not thrift.
- **A gate owns it.** `security-reviewer`, `tester-qa`, `code-reviewer` are gates, not opinions. Doing
  their job yourself doesn't save a dispatch; it removes the gate.
- **Fresh context beats yours.** For verifying work *you* just did, a subagent that never saw you do it
  is the point — self-critique inherits your premises. FORGE's G4a critic exists for exactly this.
- **Context you shouldn't hold.** Bulk reading that would crowd your window is the cheapest thing to
  delegate; the subagent returns the conclusion, not the transcript.

**What this does NOT relax.** The `parallelism` cap still binds (Step 5) — honor the configured breadth.
Sub-agents still never spawn peers (single-orchestrator, [`agent-collaboration.md`](../../rules/agent-collaboration.md)).
The routing tree still decides **which** specialist. This step decides only **whether**, and "spawn more"
is never a licence to skip the cap, the tree, or the shape choice in Step 2.

**Re-check the direction on a model swap.** This counterweight is calibrated to Opus 4.8's under-spawn
default. **Fable 5 inverts it** — it *"dispatches parallel subagents more readily than prior models"*
`[Prompting Claude Fable 5, retrieved 2026-07-15]` — so on Fable the restraining levers do the work and
this step needs re-reading, not copying.

---

## Step 2 — Pick the playbook

**Before you fan out, pick the orchestration *shape*.** A multi-agent request is not automatically a turn-by-turn subagent dispatch. Traverse the table in [`../../knowledge/dynamic-workflows.md`](../../knowledge/dynamic-workflows.md) `## Choosing an orchestration shape` first: if the work is massively-parallel or adversarial, you'll rerun it, or you're coordinating more agents than this conversation can track, it's a **dynamic workflow** (`ultracode`) — not a hand-orchestrated dispatch. If the deliverable is a reviewed *plan* from a raw idea, it's `/forge`. Otherwise the playbooks below (you, the Team Lead, dispatching specialists turn by turn) are the right shape. Say which shape you chose in your summary.

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

## Step 3 — Allocate worktrees (Sleipnir)

For each coder agent, create an isolated worktree using [`new-worktree`](../new-worktree/SKILL.md) — in user-facing prose, "send **Sleipnir** to that branch" (the labeling convention; the mechanism is plain `git worktree`). Naming:

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

## Step 4.5 — Orchestrator routing (non-Claude hosts only)

**Check this before dispatching any agent.** The routing is a single read + branch:

1. **Is the host already Claude Code?** Check `THING_HOST`. If `THING_HOST == claude-code` (or is unset), the host IS Claude — skip this step entirely; orchestrate as today.
2. **Read the knob.** Read `.ravenclaude/comfort-posture.yaml` → `orchestrator:` field. Values: `off` | `decide` | `full`. Absent = `full` (the shipped default — owner choice to route orchestration to Claude under a non-Claude host).
3. **Route:**

| Knob | What to do |
|---|---|
| `off` | Host orchestrates as always. Nothing changes. |
| `decide` | Call `bash plugins/ravenclaude-core/scripts/claude-orchestrate.sh decide` with `RAVENCLAUDE_ORCH_BRIEF="<task>" RAVENCLAUDE_ORCH_ROSTER="<roster json>"`. Get back a JSON dispatch plan `{agents:[...], parallelism, reasoning}`; execute it. Claude planned, host ran. |
| `full` (default) | Call `bash plugins/ravenclaude-core/scripts/claude-orchestrate.sh full` with `RAVENCLAUDE_ORCH_BRIEF="<task>"`. Get back artifact content; write it to the target path. One bounded call; locked intent. |

**FAIL-SAFE:** any non-zero exit from the script means fall back to `off` (host orchestrates). Never hard-block on orchestrator failure.

**Cost note:** `decide` adds one Claude call for planning (+tokens). `full` adds one larger Claude call (+most tokens, bounded). Say the active mode in your summary when it changes routing.

**Scope (`orchestrator_scope: team | all`, default `team`).** The `orchestrator` knob above sets _how_ orchestration routes to Claude; `orchestrator_scope` sets _when_:

- `team` (default) — orchestrate via Claude **only on a team-of-agents dispatch** (i.e. exactly this Step 4.5). This is unchanged behavior.
- `all` — **additionally**, the host relays _every_ prompt to Claude (content-only). That every-prompt relay is **not driven from this skill** — it is the self-gating "Relay mode" directive in the generated [`copilot/AGENTS.md`](../../copilot/AGENTS.md) (Copilot-host only). Team dispatch (this step) is identical under both scopes; `all` only adds the every-prompt surface.

`orchestrator_scope: all` routes client context to a **second processor** (your Claude account) on every turn, so it is guarded by an **egress floor** in `claude-orchestrate.sh` (fails closed unless Bedrock/Vertex, attested ZDR, or a no-PII repo flag) plus an optional pseudonymization layer — see [`knowledge/orchestrator-data-egress.md`](../../knowledge/orchestrator-data-egress.md). Those guards apply to the relay-all path; team-dispatch egress is the pre-existing reviewed path.

**Note:** this step is inert under Claude Code (`THING_HOST == claude-code`). Skip entirely when running in Claude Code.

---

## Step 5 — Run them

- **Independent agents in parallel:** dispatch in a single tool call with multiple Agent invocations.
- **Dependent agents sequentially:** dispatch one, wait for the report, then the next.
- Never spawn the same role twice in parallel on the same branch.
- **Honor the parallelism posture** (see below) before fanning independent agents out in parallel — and when allocating worktrees in Step 3.

### Parallelism posture (`.ravenclaude/comfort-posture.yaml`) — the default is MAXIMUM

**The default is maximum parallelism.** Batch every independent step into ONE message and let them run at once. **The only reason to serialize is a genuine data dependency** — step B literally needs step A's output. Being unsure whether two steps are independent is *not* a dependency; spend one read to find out, then batch them.

The user tunes this from the dashboard's **Pipeline** page (Configure section), which writes a `parallelism:` block into `.ravenclaude/comfort-posture.yaml`. Read it before a parallel dispatch and honor it:

| Posture | Meaning | What you do |
|---|---|---|
| block **absent** (default, v0.273.0+) | **maximum** | Fan out as wide as the independent work allows — no concurrency cap. Same as `enabled: true` + `max_workers: unlimited`. |
| `enabled: false`, or the scalar `parallelism: off` | parallel workers turned off | Run independent agents **sequentially**, one at a time. |
| `enabled: true` + `max_workers: N` | capped fan-out | Dispatch independent agents in **batches of at most N** concurrent workers; queue the rest until a slot frees. |
| `enabled: true` + `max_workers: unlimited` | uncapped | Fan out as wide as the independent work allows — no concurrency cap. |

> **⛔ `absent` changed meaning in v0.273.0** — it used to mean "unchanged / use your own judgment" and now means **maximum**. Every *explicit* setting is unchanged, so a consumer who ever tuned the block sees no difference; only the untouched case moves, and it moves toward more parallelism, never less. See the CLAUDE.md milestone for the migration note.

### The conserve-tokens exception (three triggers, one precedence)

Maximum parallelism has exactly one exception, and it can be engaged three ways. **When it is engaged, read the `parallelism:` posture as `enabled: false` — sequential, one worker at a time.** There is deliberately no fourth mode.

| # | Trigger | Scope | Engages when |
|---|---|---|---|
| 1 | **Prompt phrase** | this session (sticky, either direction) | The user's prompt says *"conserve tokens"* / *"conserve context"* / *"save tokens"* / *"minimise tokens"*. **Releases** on *"maximum parallelism"* / *"full parallelism"* / *"stop conserving"*. |
| 2 | **Posture switch** | persistent | `conserve_tokens: true` (the dashboard's Pipeline **Conserve tokens** checkbox). |
| 3 | **Context pressure** | automatic | Live usage ≥ `conserve_tokens_auto_pct` percent of the context window (default `80`; `0` disables). Measured by `scripts/context-usage-meter.py` — the same live-usage source `handoff-nudge` reads. |

**Precedence (highest first):**

1. **The session phrase wins outright, in BOTH directions.** An explicit human instruction in the live conversation beats standing configuration — including releasing a posture switch that is set to `true`. The release direction is as load-bearing as the engage direction: without it the only exit from a phrase-engaged session would be editing a config file mid-conversation.
2. **The posture switch** engages it. It cannot *dis*-engage it — there is no "never conserve" setting, because that would let a stale config silently suppress trigger 3, and trigger 3 exists precisely for the moments nobody is watching.
3. **Context pressure** engages it.
4. Otherwise: **maximum**.

Formally: `engaged = phrase_override if a phrase fired this session else (posture_switch or context_pressure)`.

Triggers 1 and 3 are resolved by [`scripts/conserve-tokens.py`](../../scripts/conserve-tokens.py), run from the `UserPromptSubmit` hook; it prints a one-line notice **only on a state transition** and writes `.ravenclaude/runs/<session>/conserve-tokens.json`. The SessionStart capability banner states the resolved mode every session.

### Why this is a commitment and not a gate

This is a **behavioral commitment, not a hard gate** — exactly like `design_checkins` and `decision_review`. And it is not an oversight: **a hook cannot compel more parallelism.** A `PreToolUse` hook can *stop* an action; there is no event at which "you should have batched those two dispatches" is a blockable thing, because the second dispatch that never happened emits nothing. So the design is **default + directive + detector**:

- the **default** (this posture) sets the target,
- the **directive** (the SessionStart banner) puts it in front of you every session, on every host,
- the **detector** ([`scripts/parallelism-detector.py`](../../scripts/parallelism-detector.py), riding the `SubagentStart` hook) measures how often work actually ran one-at-a-time and reports the ratio. It never blocks. A high ratio is a **prompt to look**, not a verdict — it infers batching from start-time proximity and cannot tell a needless serialization from a real dependency.

The cap bounds **breadth** (how many workers run at once); the runaway brake bounds **depth** (total tool calls) independently. Say the effective mode in your summary when it changed how you fanned out.

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
| Agent A asserts another agent's prior artifact is wrong (confidence ≥ 0.7, correctness-critical domain) | Contested claim that one orchestrator test can't settle | **deep-researcher in citation-only mode** — apply [Cited-Adjudicator Escalation](../../rules/agent-collaboration.md#cited-adjudicator-escalation) |
| Any agent goes silent for >5 minutes | Blocked or stuck | abort and re-dispatch with a tighter brief |

---

## Step 7 — Reconcile reports

- **⛔ Run the gate yourself after every handoff — build, typecheck and tests — before the work is
  committed, passed on, or described to the user as done.** Not the diff: the gate. Measured on a real
  branch, **twice in one session** a subagent reported its task complete having left a hard compile
  error in the tree (once a symbol referenced but never imported). Both were caught in ~30 seconds by
  running the typecheck. Neither was caught by reading the report, which was confident and detailed.
  A subagent's report is a **claim**, never evidence — see
  [`knowledge/verification-discipline.md`](../../knowledge/verification-discipline.md).
  ⛔ Do not `grep` the gate's output for "error": a filtered warning and an absent warning are
  indistinguishable afterward, and in the same session that filter hid the only evidence a feature had
  never been wired up.
- Read every diff yourself before reporting to the user. Self-reports describe intent, not always reality.
- **Check the seam, not the halves.** Two agents can each finish correctly and leave nothing joining
  them — an endpoint with no caller passes every per-agent check and every per-file review.
- If reports disagree (e.g. tester says ❌, coder says ✅), the test result wins until proven otherwise.
  The disagreement runs both ways: an agent may also report failure on work that is fine. Check the
  tree, not the prose.
- Merge worktrees back via fast-forward or `--no-ff` per the project's branching style.

---

## Step 8 — Close the loop

- Run [`run-full-test-suite`](../run-full-test-suite/SKILL.md) on the integrated branch.
- Run [`cleanup-worktrees`](../cleanup-worktrees/SKILL.md) to remove finished worktrees.
- If shipping, hand to [`create-pr`](../create-pr/SKILL.md).
- Summarize for the user: which playbook ran, what shipped, what didn't, what's open.

---

## Cross-plugin dispatch

When the consumer project has more than one RavenClaude plugin installed — most commonly `ravenclaude-core` **and** `power-platform` — you (Team Lead) are the only agent that routes across plugin boundaries. Specialists stay inside their plugin and escalate via you.

### Detect the domain first

Before picking a playbook, ask: *does this request touch a domain plugin's surface?* Plain English signals for each currently-shipping domain plugin:

| Plugin | Trigger signals |
|---|---|
| `power-platform` | "canvas app", "model-driven", "Power Fx", "Power Automate flow", "Dataverse", "solution.xml", "PBIP", "DAX", "Copilot Studio", "PCF control", "pac CLI", "DLP", anything mentioning `.pbix` / `.msapp` / `*.fx.yaml` / Power Pages |
| *(future)* | finance, EdTech, Salesforce — add rows here as plugins land |

If **no** domain-plugin signal is present, run the standard playbooks above with `ravenclaude-core` specialists only. If signals are present, pick the domain playbook below.

### Domain-led playbooks (when `power-platform` is installed)

These extend — they don't replace — the generic patterns in Step 2. The Team Lead still owns sequencing and gate decisions.

| Request shape | Sequence |
|---|---|
| Build a canvas app that writes to a custom Dataverse table | `power-platform/dataverse-architect` → `power-platform/power-fx-engineer` → `power-platform/solution-alm-engineer`. **Mandatory escalation to `ravenclaude-core/security-reviewer`** if FLS/RLS/sharing or PII fields are involved. |
| Build or fix a cloud flow | `power-platform/flow-engineer`. Pull `power-platform/solution-alm-engineer` for env-var / connection-ref issues; pull `power-platform/power-platform-admin` for DLP / capacity / throttling. |
| PBIP semantic model + DAX + ADO git | `power-platform/power-bi-engineer` → `power-platform/solution-alm-engineer` (only when it must integrate with broader solution pipelines or flows). |
| Tenant audit / governance | `power-platform/power-platform-admin`. Pull `power-platform/dataverse-architect` for schema concerns. |
| Migrate Excel/SharePoint workbook to a real Power App | `power-platform/dataverse-architect` (schema) → `power-platform/solution-alm-engineer` (env strategy) → `power-platform/power-fx-engineer` *or* `power-platform/model-driven-engineer` (UI). |
| Chatbot / Copilot Studio build | `power-platform/copilot-studio-engineer` → `power-platform/flow-engineer` (actions the bot calls) → `power-platform/solution-alm-engineer` (package). |
| Behavioral testing of a Power Platform change before release | `power-platform/power-platform-tester` (Test Studio, flow run history, DAX semantic correctness, `pac solution check`) → `power-platform/solution-alm-engineer` packages. |
| Long-term maintainability review of a Power Platform solution | `power-platform` specialists invoke the `power-platform/maintainability-review` skill; their reports come back to you. |

The complete domain routing table lives in [`plugins/power-platform/CLAUDE.md`](../../../power-platform/CLAUDE.md) §2. Keep that file authoritative; this section summarizes when to *cross* into it.

### Symmetric escalation paths

Both directions are explicitly allowed, but the agent **never** dispatches directly — it returns a report with an `Escalation` line and you decide. Use the table to pick the right specialist:

| Surfacing (in plugin) | Likely cause | Where to route |
|---|---|---|
| Power Platform specialist touched FLS/RLS/sharing/cross-BU/PII/PCI/PHI | Security boundary | `ravenclaude-core/security-reviewer` (mandatory; see `power-platform/CLAUDE.md` §11) |
| Power Platform specialist hit an Azure / identity / non-Power-Platform architecture question | Out-of-domain design | `ravenclaude-core/architect` |
| Power Platform specialist's answer depends on current Microsoft licensing / connector behavior / release-note recency | Knowledge freshness | `ravenclaude-core/deep-researcher` |
| Power Platform delivery needs RAID, status, or stakeholder tracking | PM hygiene | `ravenclaude-core/project-manager` |
| `ravenclaude-core/architect` proposes a design that depends on a Power Platform mechanism (Dataverse table, flow, PBIP layout) | Implementation expertise | `power-platform/dataverse-architect` *or* `power-platform/solution-alm-engineer` (per scope) |
| `ravenclaude-core/security-reviewer` flags a Power Platform-specific concern (DLP, connector auth, premium licensing exposure) | Domain expertise | `power-platform/power-platform-admin` (DLP/governance) or `power-platform/flow-engineer` (connector auth) |
| `ravenclaude-core/code-reviewer` opens a Power Fx / DAX / solution.xml diff | Domain expertise | `power-platform/power-fx-engineer` (Power Fx), `power-platform/power-bi-engineer` (DAX), `power-platform/solution-alm-engineer` (solution metadata) |
| `ravenclaude-core/tester-qa` needs to test a Power Platform app behaviorally | Domain expertise | `power-platform/power-platform-tester` |
| `ravenclaude-core/documentarian` asked to write a runbook for a Power Platform deployment | Domain detail | `power-platform/solution-alm-engineer` provides the technical content; documentarian rewrites for the audience |

### Anti-patterns to avoid

- **No sub-agent dispatches another sub-agent**, ever. Not "the architect spawned a coder," not "the dataverse-architect spawned the power-fx-engineer." The Team Lead is the only orchestrator. Agent files containing `Agent(` calls will be flagged by `plugins/ravenclaude-core/hooks/guard-recursive-spawn.sh`.
- **No silent cross-plugin dispatch.** When you route across plugins, *say so* in your summary so the user can see why the work crossed boundaries.
- **No "Power Platform specialist did the security review."** Security review for FLS/RLS/sharing/cross-BU/PII always goes through `ravenclaude-core/security-reviewer`, even if a Power Platform specialist could plausibly answer.
- **No coder agent reading from another plugin's `CLAUDE.md` directly.** Specialists stay in their plugin. Cross-cutting context flows through you.

### When more domain plugins ship

As new plugins land (finance, EdTech, Salesforce, …), extend the trigger-signal table and the symmetric-escalation table in lock-step. The skeleton is plugin-agnostic; the only thing that grows is which domains the Team Lead can route into.

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
