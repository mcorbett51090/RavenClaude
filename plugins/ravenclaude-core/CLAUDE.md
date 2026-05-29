## Plugin Architecture: Core vs Domain Plugins (Updated)

- `ravenclaude-core` is the **foundational plugin**. It provides the Team Lead, generalist agents (Architect, Coder, Reviewer, etc.), skills, hooks, Capability Grounding Protocol, the Researcher meta-skill, **Structured Output Protocol**, and standardized run artifacts conventions.
- Domain plugins (e.g. `power-platform`) **extend** core. They add specialist agents and domain-specific knowledge.
- The Team Lead is responsible for detecting domain-specific work and dispatching specialists from installed domain plugins.

### House rule: domain plugins extend core via skills and knowledge, not parallel agents (added 2026-05-21)

**Domain plugins extend core via skills and knowledge; they fork core agents only when the domain's review rubric is genuinely incompatible with core's.**

**Test before adding a plugin-specific architect or reviewer:** *could a competent core agent, handed the right skill and knowledge file, produce indistinguishable output?* If yes, ship a skill (with an inline prior on the relevant core agent pointing at it). If no — the domain carries operational craft the core agent genuinely lacks (e.g., `power-platform/dataverse-architect`'s plug-in execution pipeline expertise, cascade-on-high-volume-child gotchas, customer-column polymorphism traps) — ship an agent.

**Precedent (the rule was extracted from this case):** the `data-platform` plugin's v0.1.0 plan originally proposed two parallel agents (`data-platform-architect` and `embed-security-reviewer`). Expert review (prompt-engineer on B2 and B4, 2026-05-21) found both proposals to be wrappers around core's `architect` and `security-reviewer` plus a decision tree's worth of domain priors — exactly what skills + knowledge files are for. Both were deleted; the plan now ships:

- `data-platform/skills/stack-selection.md` — invoked by `ravenclaude-core/architect` via the inline prior on that agent's file
- `data-platform/skills/jwt-embed-issuance.md`, `rls-policy-authoring.md`, `embed-csp-and-iframe-sandboxing.md` — invoked by `ravenclaude-core/security-reviewer` via the inline pointer on that agent's file

The marketplace precedent at the time of the rule's extraction was unanimous: **5 of 5** domain plugins (power-platform, regulatory-compliance, finance, edtech-partner-success, web-design) had **no** plugin-specific security reviewer. All security review escalates to `ravenclaude-core/security-reviewer`. Domain-specific patterns live in skills and knowledge files that core agents invoke.

This rule prevents two specific failure modes: (a) **dispatch ambiguity** on diffs that cross plugin boundaries (Team Lead doesn't know which security-reviewer to dispatch), and (b) **rubric drift** as plugin-specific reviewers diverge from the core review rubric over time.

## Multi-Agent Coordination & Dispatch Rules (Core Principle)

This marketplace follows the **orchestrator-worker / hierarchical** pattern, which is the dominant recommended approach in production multi-agent systems (including Anthropic’s own research architecture and patterns validated in robust agent runtimes).

**Core Rule:**

**Sub-agents should not freely spawn or directly invoke other sub-agents.** Only the Team Lead performs dispatching and orchestration.

**How cross-boundary work is handled:**

1. Each specialist stays focused on their domain and delivers a high-quality slice.
2. When work has clear relevance to another specialist, the agent should complete their portion and include a clear **escalation / recommended handoff** note to the Team Lead (naming the suggested specialist and providing relevant context). **Use the Structured Output Protocol below for all handoff notes.**
3. The **Team Lead** decides whether and how to involve additional agents (in parallel or sequence) and synthesizes the combined output.
4. Limited structured handoff is acceptable when explicitly recommended, but actual dispatch and context management remains the responsibility of the Team Lead.

**Rationale**: This approach provides better observability, easier debugging, reduced risk of loops, and more reliable behavior — especially important when combining generalist agents from core with domain specialists. It mirrors proven task decomposition and session isolation patterns from high-reliability agent frameworks.

### Delegating branch-mutating work (added 2026-05-23)

When the Team Lead fans work out across multiple git branches, **how** the sub-agents are launched determines whether they can do the job at all. See [`knowledge/subagent-isolation-and-tooling.md`](knowledge/subagent-isolation-and-tooling.md) for the full lesson. The load-bearing rule:

> Reading a branch needs no isolation or approval (`git show <ref>:<path>` — parallelize across sub-agents freely). Writing a branch (checkout / commit / push) needs approval that **only the main interactive agent can obtain** — background sub-agents are auto-denied git-writes (confirmed for both worktree-isolated _and_ plain non-isolated agents). So: fan reads out to sub-agents, but do all branch-mutating work in the main session, sequentially. `isolation: "worktree"` only makes it worse — it also strips `Read`.

### Agent-routing decision tree (priors — for the Team Lead)

Before spawning any specialist, traverse the Mermaid graph in [`knowledge/agent-routing.md`](knowledge/agent-routing.md) `## Decision Tree` top-to-bottom against the user's observable request signals — do NOT keyword-match the request to an agent name. The earliest-blocking gate wins (e.g., a UI change that touches auth spawns `security-reviewer` before `frontend-coder`); when multiple branches could apply, default to the leaf with the smaller spawn cost and escalate only if it returns insufficient. Domain plugins (e.g. `power-platform`) with a more-specific routing rule for the request override this tree.

## Structured Output Protocol (Active — required for handoffs)

> **Status as of 2026-05-21:** This protocol is **active and implemented**. All 14 specialist agents in `agents/` (13 from v0.4.0 + the new `data-engineer` added in v0.6.0) declare the Structured Output Protocol block in their Output Contract sections. Every sub-agent that hands off to the Team Lead (or to a downstream specialist) MUST end its report with a `---RESULT_START--- ... ---RESULT_END---` delimited JSON block alongside its human-readable Markdown. The dual-output format is the 2026 norm in production multi-agent systems (pure JSON loses reasoning, pure Markdown is unparseable). The Team Lead enforces the contract at brief time and reads the JSON to drive routing.

The protocol is described below. Agents MUST follow this format for handoff-bearing reports; informational chatter ("file read", "test ran") is exempt.

### Core Rules
1. **Prefer JSON Schema + Delimited Extraction** when the output has clear structure:
   - Define or reference a simple JSON schema in the prompt.
   - Instruct the model to output reasoning/prose first, then:
     ```
     ---RESULT_START---
     {
       "key": "value",
       ...
     }
     ---RESULT_END---
     ```
   - This allows reliable extraction while preserving human-readable reasoning (inspired by robust typed output mechanisms in production agent runtimes).

2. **For complex or narrative outputs** (design docs, reviews, runbooks): Use clear Markdown with explicit sections, checklists, and a final **Structured Summary** block using the delimiter format above (e.g., `{"status": "approved|needs_changes", "confidence": 0.85, "key_decisions": [...], "next_actions": [...]}`).

3. **Handoff Notes (Mandatory Structured Format)**:
   Every escalation to Team Lead must include:
   - Clear context summary (what was done)
   - Structured payload (JSON or delimited)
   - Recommended next specialist + why
   - Any risks or open questions
   - Confidence level

4. **Always include**:
   - Success criteria met (or gaps)
   - Rationale / key decisions
   - Suggested follow-ups

### Example Prompt Pattern (for agents/skills)
```
You are [Role]. Complete the following focused task.

Task: [narrow description]

Success Criteria:
- [bullet 1]
- [bullet 2]

Output Requirements:
1. First, provide your step-by-step reasoning and any code/docs.
2. Then output ONLY the structured result using this exact format:

---RESULT_START---
{
  "status": "complete|partial|blocked",
  "summary": "one sentence",
  "deliverables": [...],
  "handoff_recommendation": { "to_specialist": "...", "reason": "..." },
  "confidence": 0.0-1.0,
  "risks": [...]
}
---RESULT_END---

Use the Researcher skill and Grounding Protocol if any information feels uncertain.
```

Once adopted across the team, this protocol will dramatically improve output quality, handoff reliability, and enable better automation/inspection downstream. The Markdown Output Contract that each agent currently uses is the fallback until the retrofit ships.

## Focused Task Execution (New — Task Decomposition)

When the Team Lead (or a skill) delegates work:

- **Treat delegations as Focused Tasks** (narrow scope, explicit success criteria, minimal unnecessary context).
- Provide the specialist with:
  - Clear, self-contained objective
  - Relevant subset of context (or reference to files)
  - Required output format (use Structured Output Protocol)
  - Any constraints (e.g., "do not modify X")
- Specialists should **not** retain or pollute the full conversation history unless explicitly needed for continuity. Prefer fresh, task-scoped thinking for higher quality results on subtasks.
- For complex work, break into sequential or parallel focused tasks orchestrated by Team Lead.

This reduces context overload, improves focus, and produces cleaner, more ideal outputs per subtask.

## Knowledge Freshness & Researcher (Updated)

The marketplace includes a **Researcher** meta-skill at `plugins/ravenclaude-core/skills/researcher.md`.

**When to invoke the Researcher**:
- On first opening the repo each day (quick check mode)
- Weekly for deep research across all agents and knowledge areas
- After major platform updates or when you notice agents giving outdated advice
- Before producing any high-stakes structured output or handoff

The Researcher is responsible for:
- Checking every agent + its skills and knowledge files
- Researching both official sources and credible community/expert opinions (including divergent views)
- Categorizing information using the defined schema (Consensus / Divergent / Emerging / etc.)
- Proposing specific, justified updates to keep knowledge current
- **Returning findings in Structured Output Protocol format**

This system exists to reduce hallucination and keep the entire agent team intellectually honest and up-to-date, especially in fast-moving domains like Power Platform.

When working with Grok or other models, copy the relevant portable files so they also benefit from the Researcher discipline.

## Capability Grounding Protocol (Updated 2026-05-21)

Before any agent claims it cannot do something or that information is outdated, it must:

1. Check available skills (including the Researcher skill when appropriate).
2. Consider whether partial progress is possible.
3. **Enumerate alternative implementation paths from easiest to most difficult, and try them in that order before declaring the task blocked.** See "Try alternative paths before declaring blocked" below — this is the default behavior, not a step the user has to prompt for.
4. Run the Grounding Protocol checklist.
5. **Produce any limitation statement using the Structured Output Protocol.**
6. Only then state limitations clearly.

The Researcher itself must apply this protocol to its own findings.

Once an agent has confirmed it *can* act, the **Last-Mile Completion Protocol** (below) governs how far it must carry the work before handing back — CGP is the floor (don't falsely claim blocked), Last-Mile is the ceiling (finish everything automatable; tee up and deep-link the human-only residue).

### Try alternative paths before declaring blocked (added 2026-05-21)

When an agent (or the Team Lead) hits a wall on Approach A — a tool fails, an API returns an error, a permission is denied, a CLI command doesn't exist, a library doesn't expose what's needed — the next move is **NOT** to report "this can't be done" or to ask the user to authorize the original approach. The next move is to **enumerate the alternative paths the same outcome could take, rank them from easiest to most difficult, and try them in that order.**

Concretely, before any "blocked" status leaves an agent's report, the agent's working notes (or its inline reasoning, depending on agent type) must answer:

1. **What other ways could this same outcome be achieved?** Different API on the same platform. A lower-level surface (CLI → REST → SDK → database direct). A different tool that solves the adjacent problem. A manual procedure with automation around the boring parts. Brainstorm at least 2–3 alternatives even if you're confident the first failed for good reason.
2. **Rank them by cost** (time to attempt, dependencies needed, permissions to acquire, irreversibility). Easiest first.
3. **Try the next-easiest one** before reporting blocked.
4. **In the eventual blocked report, list the alternatives you tried** (with one-line outcomes) plus the alternatives you considered and ruled out (with the reason). This is what makes the report *useful* — the user shouldn't have to ask "did you try X?" because the report already says "tried X, failed with Y; tried Z, failed with W; the remaining option is escalating to ABC."

Why this rule exists: agents historically default to "this approach didn't work → report blocked → wait for user." Real production work has the user asking "is there another way?" and the agent finding one immediately. That round-trip is wasted — the agent should make the second attempt without being prompted. Confirmed pattern from production: see [`plugins/power-platform/knowledge/programmatic-flow-creation.md`](../power-platform/knowledge/programmatic-flow-creation.md) — the canonical case study, where Approach A (PA Management API) was permission-blocked and Approach B (Dataverse Web API) was sitting right there with the same SPN already authorized.

### Pre-action traversal of decision trees (added 2026-05-21)

The alternate-methods rule above handles the **reactive** case (agent tried A, A failed, enumerate alternates before reporting blocked). It does NOT cover the **wrong-branch-from-the-start** failure mode — where the agent picks the wrong method on first try because the available branches weren't visible.

When a knowledge file in the active plugin contains a `## Decision Tree: <Domain> — <Situation>` section (per the convention in [`docs/best-practices/decision-trees-in-knowledge-files.md`](../../docs/best-practices/decision-trees-in-knowledge-files.md)) and the user's situation matches the tree's entry condition, the agent MUST:

1. **Traverse the Mermaid graph top-to-bottom** before selecting a method
2. **Resolve each condition node against the user's stated context** (not against keyword pattern-matching on their description)
3. **Default to the leaf with the smaller blast radius** when multiple branches could apply
4. **Escalate to a higher-blast-radius leaf only after the smaller one demonstrably failed** (this is where the alternate-methods rule kicks back in)

The decision-tree pre-action traversal and the alternate-methods reactive enumeration compose: the tree prevents picking the wrong method on first try; CGP catches what the tree missed.

### Pre-action environment-context check (added 2026-05-22)

The decision-tree pre-action traversal closes the **wrong-branch-from-the-start** failure mode (the agent picked the wrong method on first try). This clause closes the **agent-forgets-it's-authorized** failure mode (the agent declares "I can't" or asks the user "can you authorize X?" when its environment posture already allows X).

Before any agent (a) declares "I can't do X," (b) asks the user to authorize an action, or (c) walks the alternate-methods enumeration, the agent MUST check whether the **active engagement** has an `.ravenclaude/environment-context.md` at the consumer's project root (see [`templates/environment-context.md`](templates/environment-context.md) for the canonical shape). If the file exists:

1. **Identify the current environment** (DEV / TEST / PROD / sandbox / named) from the user's stated context, the current working directory, recent commands, or by asking explicitly if ambiguous
2. **Look up the environment's role + pre-authorized action categories** in the environment-context file
3. **If the action category is pre-authorized for the current environment, execute** without prompting the user for authorization
4. **If the action is in the "Forbidden" list for the current environment, stop** and require explicit per-action confirmation (regardless of role)
5. **If the file does not exist OR the action category is not listed**, fall through to the existing alternate-methods enumeration

The new failure mode this closes is the **"did you try X?" round-trip on actions the agent could have just done.** Example: the agent is operating in DEV where Matt has sysadmin via an SPN. Without this clause, the agent asks "can you authorize me to import this solution?" — wasting a round-trip on something it's already pre-authorized for. With this clause, the agent imports.

**Anti-patterns this clause prevents:**

- Asking for authorization on actions in the pre-authorized list ("did you try X?" round-trip)
- Treating the environment-context file as a CREDENTIAL store (it isn't; credentials live in env vars / Key Vault)
- Assuming pre-authorization applies cross-environment ("works in DEV → just do it in PROD" — wrong)
- Failing to ask when the file is silent (silence is NOT pre-authorization)

**Anti-patterns this clause does NOT prevent (intentional):**

- Decision-making about HOW to do an action (still bounded by decision trees + capability-grounding alternate-methods)
- Cross-environment leakage (PROD action posture is always restrictive by default)
- Forbidden-action requests (those always require explicit per-action confirmation regardless of role)

**Composition with the other CGP clauses:**

| Failure mode | Clause that catches it |
|---|---|
| Agent forgets it's authorized → asks unnecessarily | **This clause** (pre-action environment-context check) |
| Agent picks wrong method on first try (multiple methods available) | Pre-action decision-tree traversal |
| Agent's chosen method fails → declares blocked without trying alternatives | Alternate-methods enumeration |
| Genuinely blocked after exhausting alternatives | Mandatory-phrasing block (below) |

The four clauses compose into "priors before action, alternatives after failure, honest blockage report" — the unified frame the architect named on 2026-05-21.

### Mandatory phrasing when reporting genuine blockage

If, after exhausting alternatives, the work *is* blocked, the report says so explicitly and lists what was tried:

> "After trying [Approach A — outcome], [Approach B — outcome], and [Approach C — outcome], I am blocked on [specific reason]. The remaining options I considered but did not attempt are [X (ruled out because Y), Z (would need permission W)]. I recommend [escalation / next-best path]."

This phrasing communicates effort, narrows the user's decision space, and protects against the "did you try X?" round-trip.

### Anti-patterns

- **Stopping after one attempt.** "I tried the PA Management API and it returned 401, so this can't be done programmatically." Wrong — the answer was always to try Dataverse Web API.
- **Asking the user to fix the original approach.** "Can you have your Global Admin grant Flows.Manage.All?" — that's a valid escalation, but only after demonstrating the lower-friction paths were tried.
- **Reporting blocked without listing what was tried.** "This isn't possible" with no enumeration is the lowest-value report shape; the user has no idea what's left to consider.
- **Inventing alternatives that don't exist** to look thorough. Better to say "I considered X and Y; neither apply because Z" than to fabricate a third path.

### How this interacts with the Structured Output Protocol

When emitting the SOP JSON block, agents whose final status is `blocked` or `partial` must populate `risks_or_open_questions` with the alternatives ruled out and `next_actions` with the recommended escalation path. The Markdown report carries the human-readable narrative of what was tried.

## Last-Mile Completion Protocol (added 2026-05-28)

The Capability Grounding Protocol governs the **floor** — an agent must not falsely claim it's blocked, and must try alternatives before reporting blockage. This protocol governs the **ceiling**: once an agent has confirmed it *can* act, it carries the work as far toward done as its authority allows before handing anything back. **The human should do as little as possible — ideally only the irreducibly-human residue, reduced to a confirm or a click.**

Before returning work, every agent and the Team Lead applies these five rules:

1. **Do everything automatable.** If a step can be completed with the tools and permissions on hand, complete it — do not hand back a to-do the agent could have executed itself. This is the action-side complement to CGP: CGP says "don't falsely claim you can't"; this says "then actually do it." A "next steps" list whose items the agent could have done is a defect.
2. **Partial-do the partially-automatable.** When only part of a step is automatable, do that part and hand back only the irreducible remainder. Generate the file, the config, the script, the draft, the migration — leave only the action that genuinely needs human credentials, judgment, or authority.
3. **Tee up the human-only residue.** For the steps only a human can do (a click behind their SSO, a signed approval, a payment, a destructive prod action), prepare everything *around* the action: pre-fill the values, draft the message / PR / commit / email, stage the exact inputs, and state the one specific thing to do. The human's job is reduced to **confirm or click**, never **assemble**.
4. **Deep-link, don't narrate.** Whenever the human must go somewhere, give a **direct link to the exact destination** — the specific portal blade, a GitHub "create PR" URL with branch + title + body pre-filled as query params, the precise settings page, the exact dashboard row — not "go to the portal, navigate to X, then click Y." A click beats a recipe. If a deep link genuinely can't be constructed, give the shortest path plus the exact search term to paste.
5. **Report as done vs. your-turn.** The final report separates **✅ done** from **👉 your turn** — and the your-turn list is short, ordered, one action each, each with its deep link. The human sees their entire remaining surface at a glance and finishes it in minutes.

**Composition with the Capability Grounding Protocol:**

| Question | Protocol that answers it |
|---|---|
| "Can this be done at all? Did I try the alternatives?" | Capability Grounding Protocol |
| "I can do it — how much must I actually finish before handing back?" | **Last-Mile Completion Protocol (this section)** |
| "What's the irreducibly-human part, and how do I make it one click?" | **Last-Mile rules 3–4** |

**Anti-patterns this protocol flags:**

- Handing back instructions for something the agent could have executed.
- A "next steps" list that is really automatable work the agent skipped.
- Navigation prose ("open the portal → click Settings → …") where a deep link exists.
- Declaring a task done while leaving assembled-but-unsubmitted work the human now has to figure out how to finish.
- Asking the human to gather inputs the agent already has or could compute.

This protocol is inherited by every plugin via this constitution — the same way the Capability Grounding Protocol and the Structured Output Protocol are; it is not restated in each agent file. Domain plugins add domain-specific deep-link sources to their agents (e.g. `power-platform` → maker-portal solution-import URLs; `azure-cloud` → portal blade deep links; `microsoft-fabric` → workspace item URLs) but do not restate the protocol.

## Auto-mode guardrails — runaway brake + definition-of-done gate (added 2026-05-29, v0.56.0)

Two **deterministic, model-free** hooks port Claude Code's native auto-mode safety to the model-agnostic Copilot-CLI surface (Claude / ChatGPT / Grok routing), where the Anthropic-API-only auto-mode brake is unavailable. Both are **opt-in** (no-op without `.ravenclaude/comfort-posture.yaml` — a single `stat`/`grep`, zero cost for non-adopters), **fail-safe**, and self-limited against deadlock. They are NOT the tribunal: command review (the Thing) gates command *safety*; these gate *runaway behavior* and work *correctness* — the two failure modes a safety reviewer can't see.

- **`runaway-brake.sh`** — `PreToolUse` brake. Counts tool calls per session in `.ravenclaude/runs/thing/runaway/<session_id>` and trips (exit 2 / Copilot deny) when the agent **thrashes** (≥ `max_consecutive` byte-identical calls in a row — the "looping on a fabricated error" rabbit-hole signal, default 8) or blows a generous total-call ceiling (`max_total`, default 200). A new `session_id` starts fresh. The portable equivalent of the native 3-consecutive / 20-total auto-mode block.
- **`dod-gate.sh`** — `Stop` definition-of-done gate. When source files changed this session **and** a `definition_of_done.cmd` is configured, it runs that command (tests / build / lint) on Stop and **blocks the stop until it passes** — turning "looks done" into "is done" without the human being the verification loop (Anthropic best-practices Layer 5). Self-limits to `max_blocks` (default 8) consecutive blocks, then force-allows with a warning (Claude Code force-overrides Stop after 8; Copilot CLI has no such guarantee, so the cap is ours). With no `definition_of_done.cmd` set it exits 0 and the advisory `remind-tests.sh` nudge still fires.

Config (all knobs optional; sensible defaults):

```yaml
# .ravenclaude/comfort-posture.yaml
runaway:
  max_consecutive: 8     # identical calls in a row before tripping (or `runaway: off`)
  max_total: 200         # total tool calls this session before tripping
definition_of_done:
  cmd: "npm test && npm run lint"   # unset -> gate is inert, remind-tests advises instead
  max_blocks: 8          # consecutive Stop-blocks before force-allow (anti-deadlock)
```

Both register in all three wiring paths (plugin `hooks.json`, dev-mirror `.claude/settings.json`, and the Copilot installer `scripts/ravenclaude` via the `stop`/`bash-pretool` adapter modes) and run **unchanged** under Copilot through `copilot-hook-adapter.sh`. **Migration:** none — both default off (absent config = inert), so nothing changes on `/plugin marketplace update` unless a consumer adds the config block.

## Run Artifacts & Observability Standard (Recommended — for multi-step orchestrations)

To enable inspection, debugging, learning, and continuous improvement of the agent team (and to mirror best practices from high-quality agent runtimes), **multi-step workflows orchestrated by the Team Lead SHOULD produce standardized on-disk artifacts**. Single-agent dispatches and one-shot reviews emit the Structured Output Protocol JSON block *inline* in the agent's reply — no on-disk artifact is required for those. The artifact substrate below applies when a run spans 2+ specialist dispatches that benefit from a re-readable record.

### Convention
Store artifacts in a project-local directory:
```
.ravenclaude/runs/<task-or-epic-id>/
```

( Create the directory if it doesn't exist. Use a short descriptive ID or timestamp + slug. )

### Recommended artifacts (use templates from templates/run-artifacts/) — for multi-step runs

- `summary.md` — Human-readable executive summary of what was accomplished, decisions, and outcomes.
- `structured-output.json` or `result.json` — Machine-readable structured result (from the Structured Output Protocol).
- `changes.diff` or `proposed-changes.patch` — Any code/config diffs (if applicable).
- `checks.json` or `validation-results.json` — Results of linting, tests, security scans, etc.
- `decisions.md` or `rationale.md` — Key decisions, trade-offs, and reasoning.
- `handoffs.md` or `escalations.log` — Record of any handoffs and their structured notes.
- `events.jsonl` or `actions.log` — Chronological key actions taken by agents (for observability).
- `agent-instructions.md` — Snapshot of the key prompts/instructions used for this run (for reproducibility).

### Implementation
- The Team Lead (or a dedicated "Artifacts" skill) is responsible for ensuring these are generated at the end of major tasks or workflows.
- Use the provided templates in `templates/run-artifacts/`.
- Hooks can be extended to auto-generate or validate presence of key artifacts on certain events (e.g., after PR creation or task completion).
- **Inspection**: After a run, the Team Lead or user can review `.ravenclaude/runs/latest/` or specific IDs for quality assessment and to feed improvements back into the Researcher or rules.

This creates a powerful feedback loop for making outputs progressively more ideal over time.

## Context & Session Hygiene (New Guidance)

For long-running or multi-turn team collaborations:
- Periodically (or at natural boundaries) create **context summaries** and handoff notes using the Structured Output Protocol.
- Avoid letting full history bloat prompts; reference artifacts and summaries instead.
- When resuming work, load the latest relevant artifacts and structured summaries first.
- The Team Lead should manage overall context; specialists receive focused slices.

This prevents degradation in output quality due to context window pressure and maintains high signal-to-noise in agent reasoning.

## Session-start environment-context load (added 2026-05-22; capability banner added 2026-05-26)

**Enforced injection (added 2026-05-26):** the `SessionStart` hook [`hooks/capability-orientation.sh`](hooks/capability-orientation.sh) now injects a **capability banner** into the session context every session via `hookSpecificOutput.additionalContext` (see [`knowledge/claude-code-permissions.md`](knowledge/claude-code-permissions.md) §"SessionStart hooks"). The banner states the project's detected external surface, the auth it holds (env-var NAMES/presence only — never values; no network calls), the effective `.claude/settings.json` permissions, and a presence/staleness summary of `environment-context.md`. This exists because the behavioral "the Team Lead reads the posture at session start" instruction below is prose the model often skips; the hook makes the summary impossible to miss. **It is a salience boost, not enforcement** — the real gate is the permission rules; the banner just stops the agent acting as if it has no access. The banner is a *pointer*: `environment-context.md` stays the **authoritative** source for per-environment roles/pre-authorized actions, and the agent reads that file for detail.

The Team Lead reads `.ravenclaude/environment-context.md` at the consumer's project root **as part of session-start orientation**, in the same pass that loads CLAUDE.md and AGENTS.md. The file is OPTIONAL — its absence is informational, not an error. When present, the Team Lead:

1. Parses the active environments + per-environment role + per-environment pre-authorized action categories + forbidden lists
2. Injects a compact summary into the working context (e.g., *"Per `.ravenclaude/environment-context.md`: agent is sysadmin in DEV/TEST, read-only in PROD; pre-authorized for solution import/export + Web API + pac CLI in DEV/TEST"*)
3. Surfaces the summary to dispatched specialists in their focused-task brief when their work might touch one of those environments

When the file is ABSENT, the Team Lead offers auto-discovery via the [`environment-discovery`](skills/environment-discovery/SKILL.md) skill instead of asking the user to fill in the template by hand. The skill probes installed CLIs (`pac`, `az`, `aws`, `gcloud`, `gh`) with read-only commands, decodes any acquired JWTs, and assembles a draft `.ravenclaude/environment-context.md` for the user to save / edit / skip. Discovery never runs without user confirmation; discovery is read-only by contract; discovery refuses to write any credentials to the file.

This is the load-bearing wiring for the Capability Grounding Protocol's pre-action environment-context check (above). Without the load, the check has nothing to read.

**Consumer-side workflow for creating the file (two paths):**

- **Auto-discovery (recommended)** — at session start when the file is absent, accept the Team Lead's offer to run [`environment-discovery`](skills/environment-discovery/SKILL.md). One prompt, ~30 seconds of read-only probes, save / edit / skip. Future sessions reuse the saved file.
- **Manual** — copy `plugins/ravenclaude-core/templates/environment-context.md` from the marketplace to `.ravenclaude/environment-context.md`, fill in by hand.

Either way: refresh quarterly OR on env-posture change OR when `/wrap` surfaces a new action category worth pre-authorizing. The Researcher's Weekly Deep Research flags files older than 90 days.

**Privacy boundary:** the file lives in the consumer's project (not in the marketplace plugin) because it contains identifying info (env names, SPN names, tenant slugs). Never commit a marketplace-shipped `environment-context.md` containing real consumer posture. Marketplace ships the **template only**.

## Permission level ≠ design judgment (added 2026-05-25)

**The comfort-posture permission scale governs tool *execution*, not design *judgment*. These are independent.** Setting a category — or every category — to `allow` only removes the click-to-approve on tool calls (file edits, shell, network). It does **not** mean Claude should stop surfacing structural / architectural / design decisions. Those two behaviors are wired to different mechanisms and must not be conflated.

Design judgment is governed by a separate behavioral flag, `design_checkins`, read at session start from `.ravenclaude/comfort-posture.yaml` in the same pass that loads CLAUDE.md, AGENTS.md, and `environment-context.md`. The Team Lead honors it as follows:

| `design_checkins` | Required behavior — at **any** permission level, including all-`allow` |
| --- | --- |
| `true` **or absent** (default) | Before implementing a structural / architectural / design decision, surface it via the Keep / Update / Deny decision flow and wait for the user. Permission level is irrelevant to this pause. |
| `false` (nonstop) | Proceed through design / architectural decisions using best judgment **without** pausing; report the decisions made afterward so the user can review. |

The flag is a **behavioral commitment, not a machine-enforced lock** — Claude Code's permission engine cannot express "auto-run tools but ask about design," so this lives in agent instruction, not in `settings.json`. ON-by-default means a user is never *accidentally* in nonstop mode. The toggle that writes this flag lives in the comfort-posture dashboard (Settings tab), so the user sets it the same place they set permissions — no slash command to memorize.

This closes the failure mode where a user relaxes permissions to move faster and unintentionally also silences design check-ins. The two are now explicitly decoupled.

## Layout (plugin internal directories)

`ravenclaude-core` uses the standard component directories:

- `agents/` — 14 specialist agent definitions (now includes `data-engineer`)
- `skills/` — dispatch playbook (spawn-team), worktree helpers, structured-output reference, run-full-test-suite, contribution-staging, agent-quality-rubric, knowledge-file-staleness-sweep, prompt-pattern-library, plugin-release-checklist, decision-review (route yes/no decisions through the tribunal)
- `hooks/` — format-on-write, guard-destructive, remind-tests, enforce-layout, guard-recursive-spawn, thing-orchestrator, ensure-default-mode, reapply-posture, capability-orientation, route-decision-review, runaway-brake, dod-gate (all registered in `hooks/hooks.json` for plugin-level distribution)
- `scripts/` — apply-comfort-posture.py (`/set-posture` translator), serve-dashboards.py (the consumer dashboard server launched by `/dashboard` — serves the version-matched `dashboard.html` and writes `.ravenclaude/` into the consumer's project; `/__save` + `/__read` + `/__classify` only, no `/__run`, binds 127.0.0.1), thing-decision.py + thing-seat.sh (command-review tribunal — see the `thing` skill), thing-decide.py (decision-review tribunal — see the `decision-review` skill)
- `rules/` — coding-standards, security, git-workflow, agent-collaboration
- `templates/` — memos, runbooks, design specs, RAID logs, partner-success, `agent-ready-repo/` templates used by `/init-agent-ready`, plus `thing.yaml` (command-review seat config)
- `commands/` — slash commands shipped to consumers: `/init-agent-ready`, `/wrap`, `/set-posture`, and `/dashboard` (launches the bundled `serve-dashboards.py` so the consumer gets the fully-functioning comfort-posture dashboard with one-click Save & apply)
- `knowledge/` — reference material the Researcher cross-checks (incl. `concerns-catalog.md`, the tribunal constitution)

### Command review (the Thing) — tribunal T5 (updated 2026-05-26, v0.28.0)

An opt-in command-review tribunal sits on top of the comfort-posture system: when a category's `thing:` toggle is on (set from the dashboard's Command-review switch, stored in `.ravenclaude/comfort-posture.yaml`), the `thing-orchestrator.sh` PreToolUse(Bash) hook convenes a **panel** — up to three reviewer seats (Forseti/`security-reviewer`, Mímir/`code-reviewer`, Heimdall/`prompt-engineer`) run in parallel, with Thor/`architect` convened only on a split or low-confidence panel — that votes **ALLOW / EDIT / DENY** (EDIT rewrites the command; the rewrite is re-validated against the concern catalog before it runs), writes a Sága-log audit entry under `.ravenclaude/runs/thing/`, and emits a Claude Code verdict (with `updatedInput` on EDIT). It can never relax the `security_deny` floor. Seat routing + the pre-LLM screen + the EDIT-safety invariant are deterministic, driven by machine-readable `triggers` in [`knowledge/concerns-catalog.md`](knowledge/concerns-catalog.md) via [`scripts/thing-concerns.py`](scripts/thing-concerns.py). The panel (per-seat models + confidence threshold) is dashboard-configured into a top-level `command_review:` block (precedence: that block > `thing.yaml` > built-in defaults). The skill [`skills/thing/SKILL.md`](skills/thing/SKILL.md) is the operating reference; the design is [`docs/tribunal-review-feature-design.md`](../../docs/tribunal-review-feature-design.md) §B.3/§B.4/§B.11.

T3 is live for `shell_readonly`, `shell_remote_mutate`, and `shell_code_exec` (and, as of v0.36.0, `shell_local_mutate` and `shell_package_install`; as of v0.38.0, `file_edit_project`; as of v0.39.0, `file_edit_global`, `file_read_project`, `file_read_global`, `network_read`, and `mcp_tools` — every non-Bash tool shape, all ALLOW/DENY-only; and, as of v0.40.0, `network_write` — the final category, Bash-shaped so ALLOW/EDIT/DENY — see the milestones below). Every comfort-posture category is now tribunal-reviewable. Fail-closed posture is **per-category**: the high-stakes categories (`shell_remote_mutate`, `shell_code_exec`) DENY on panel timeout/abstention (deny is the only verdict that holds under bypass modes), while `shell_readonly` keeps `ask`. The internal panel deadline (~75 s) stays under the 90 s hook timeout so the orchestrator emits its own verdict before the platform's fail-OPEN-on-timeout fires. The per-seat soft cap defaults to **45 s** (v0.25.1) — parallel `claude -p` cold-starts run ~24-29 s (a single warm seat is ~8 s), so the original 18 s abstained the whole panel on modest machines. The hook short-circuits with a single `grep` when no category is toggled, so it is a no-op for everyone who hasn't opted in. **Migration (T2→T3):** a legacy single-seat `thing.yaml` (`seat:` + `internal_timeout_seconds:`) still works — `seat:` maps to the Mímir seat — but the new `panel:`/`confidence_threshold:`/`timeout_posture:` keys (`schema_version: 2`) are recommended; nothing in a consumer's project breaks on `/plugin marketplace update`.

**T4 — §B.9 injection & self-protection hardening (v0.26.0).** Two load-bearing additions. (1) **The Thing cannot disable itself.** A new cross-cutting concern `xc.tribunal-self-disable` (critical, `pre_llm_deny`, `always_screen`) denies — pre-LLM, no seat — any Bash command that would mutate the Thing's own substrate (the orchestrator, a seat wrapper, `thing-concerns.py`/`thing-decision.py`, the plugin `hooks/`+`scripts/` directories — matched at the directory level so glob / `$var` / whole-dir `rm -rf` forms can't slip past — or `.ravenclaude/thing.yaml`) or write a `thing: off` toggle into `comfort-posture.yaml`. The `always_screen` flag means this guard is evaluated **category-independently** (via `screen_always` in [`scripts/thing-concerns.py`](scripts/thing-concerns.py) → `_screen_always` in [`scripts/thing-decision.py`](scripts/thing-decision.py) → an orchestrator check that runs *before* the per-category enabled gate), so a self-disabling command shaped to classify into a toggled-OFF category is still denied. (2) **Injection hardening:** `xc.injection-attempt` expanded with JudgeDeceiver / role-tag / special-token / verdict-flip shapes; the seat envelope uses the canonical AlignmentCheck "untrusted data, not instructions" framing; and a deterministic **egress secret backstop** in [`scripts/thing-seat.sh`](scripts/thing-seat.sh) denies locally — never transmitting — if a secret reaches a seat. Proven by **Gate 15** (curated adversarial fixtures + the category-independent self-disable case + a negative control + the seat backstop). **Migration (T3→T4):** none — the new concern ships in the catalog and is inert unless a category is toggled on; nothing in a consumer's project breaks on `/plugin marketplace update`.

**T5 — tiered routing & the human gate (v0.28.0).** Risk is now a **blend**: each command's comfort-posture category sets a base tier (`low`→`medium`→`high`→`extreme`, see `category_tier_map`), and a deterministic high/critical concern bumps it up (a high concern +1 tier, a critical concern straight to `extreme`). The TIER — not raw severity — drives the panel. **`low` runs no LLM panel at all**: a clean read is cleared by the zero-cost deterministic screen, so the panel begins at the first mutate tier; seat count and the confidence bar both escalate with the tier; `extreme` carries a mandatory security seat (Forseti). A new **`gate_floor`** knob (`medium`..`extreme`, default `high`, dashboard-configurable) sets the lowest tier whose *confident panel-ALLOW* is surfaced to you as an `ask` — a DENY still blocks and an EDIT still rewrites autonomously, so the tribunal keeps pre-filtering the dangerous/fixable commands before one ever reaches you. Two hard overrides ignore the knob: **reads are never surfaced** (a clean read auto-allows; an escalated read is auto-decided block/allow by the panel, never an ask), and **irreversible high-blast** allows (force-push is denied outright; `rm -rf`, publish, `gh pr merge`, …) always surface. An abstaining / inconclusive panel always fails **CLOSED** (deny) at every tier, retiring the T3 per-category `timeout_posture`. Tiers / `gate_floor` / `category_tier_map` resolve with the same precedence as the panel (`command_review:` > `thing.yaml` > built-in defaults), and `xc.tribunal-self-disable` now also denies a command that writes that tier config (`command_review:` / `gate_floor:`) into `comfort-posture.yaml`. The deterministic screen — including the injection regex — still runs on every reviewed command (Heimdall, the LLM injection seat, convenes from the first mutate tier). Proven by the rewritten **Gate 14** (clean-read short-circuit, tier seat counts, gate_floor, high-blast, reads-never-ask) + new **Gate 15** tier-config self-disable fixtures. **Migration (T4→T5):** none — the defaults reproduce the prior live categories' behavior, a leftover `timeout_posture:` is ignored, and nothing in a consumer's project breaks on `/plugin marketplace update`.

**Cost/ergonomics + model diversity (v0.32.0).** The deterministic pre-LLM screen (hard-rule pre-deny + the self-disable guard) **always runs** — the three knobs below only let you skip the *expensive* panel. (1) **`command_review.bypass`** — regex patterns you trust enough to auto-allow without convening seats; a bypass only fires if the deterministic screen is clean (a bypassed force-push / inline secret / self-disable is still denied, and a match carrying a critical concern is never bypassed). (2) **`cache_ttl_seconds`** — reuse a recent PANEL verdict for an identical command (same category + same effective config) within the window; config-hash-keyed so a rules/catalog change invalidates it, and only allow/edit/deny are cached, never an `ask`. (3) **`fatigue_threshold`** — advisory only: after N `ask`s in a session, the banner nudges toward raising `gate_floor` or adding a bypass; it never auto-allows. Separately, a **model-diversity rule**: whenever ≥2 seats convene, the engine guarantees ≥2 distinct model backbones run (if a `panel:` override collapses them onto one model, one seat is auto-reassigned to a different, equal-or-stronger model) — so a single model's blind spot can't pass the whole panel (anti-correlated-hallucination). All proven by **Gate 22**; full reference [`docs/tribunal-assessment-and-improvement-plan.md`](../../docs/tribunal-assessment-and-improvement-plan.md).

**Live categories expanded — `shell_local_mutate` + `shell_package_install` (v0.36.0).** Two more comfort-posture categories are wired end-to-end and clickable in the dashboard (no longer Preview): `shell_local_mutate` (destructive local mutations — `rm`, `git reset --hard`, force-deleting `main`/`master`, recursive `chmod 000/777`) and `shell_package_install` (supply-chain — global installs, unpinned versions, cred-in-registry-URL, tarball-from-`/tmp`), both base-tier `medium`. Their 14 concerns were authored first (8 deterministic `triggers`, 6 `judgment_only`) and verified Gate-21-#17-clean; this milestone adds the pair to `THING_LIVE_CATEGORIES` (`scripts/generate-dashboards.py`), the Gate 21 #17 hardcoded live list plus an FP/FN regex corpus (`scripts/audit-gates.sh`), and the dashboard/SKILL prose. Still **Bash-only** — no file/network/MCP tool shapes (those ship in a later track). **Migration:** none — both default OFF like every category, so nothing in a consumer's project changes on `/plugin marketplace update` unless they explicitly toggle one on. The design + phasing reference is [`docs/tribunal-tool-review-design.md`](../../docs/tribunal-tool-review-design.md).

**Hard-deny rules made category-independent (v0.36.0, §B.9.3).** A multi-round adversarial review of the live-flip surfaced a pre-existing hole: the unarguable pre-LLM hard-deny rules — **force-push to a protected branch and `curl|sh`** — were only screened for the command's *classified* category, so a wrapped or mis-routed form (`nice git push --force`, `git status && git push --force`, `git --git-dir=/x push --force`, or any form that classified into an untoggled category / `None`) dodged the hard DENY. These two concerns are now flagged **`always_screen`** in the catalog and screened by `thing-concerns.py screen_always` — category-independently, on the raw **and** normalized command — exactly like the `xc.tribunal-self-disable` guard. `always_screen` is reserved for **intent-bearing** triggers (the command *is* doing the dangerous thing). It is intentionally **not** applied to `xc.injection-attempt` (only a threat when a seat is convened) nor to `xc.secret-in-command` (its `--password=…`/`--token=…` triggers are presence-of-substring — they match env-var refs like `--password=$DBPASS` and quoted/grep mentions — so a category-independent, non-overridable hard DENY of those would be too wide a false-positive blast; it stays `pre_llm_deny` within its classified category). **Migration:** once the Thing is on for **any** category, a force-push-to-protected / `curl|sh` is hard-denied regardless of which category the command routes to — so a consumer who had only a read category toggled will newly see those denied. This only ever denies an unarguable hard rule. Proven by new **Gate 15** §B.9.3 fixtures (wrapped/chained/`-C`/`--git-dir` force-push and `curl|sh` denied with only `shell_readonly` toggled; `--force-with-lease` and a benign `--password=$VAR` mention **not** denied).

**Engine Foundation — payload-shaped multi-shape engine (v0.37.0, Track B Phase 0).** The Bash-only engine is extended to the **file (Edit/Write/MultiEdit/Read), network (WebFetch/WebSearch), and MCP** tool shapes — the shared machinery every non-Bash shape needs, **but nothing is LIVE** (`THING_LIVE_CATEGORIES` is unchanged; the dashboard still toggles only the shell categories). Pieces: `classify_payload` (name-keyed, §1) + `reviewed_text` per shape (WebFetch reviews the URL only); a catalog-independent `screen_substrate_path` + single-source `THING_SUBSTRATE` so a **file-shape** mutation of the Thing's own files is denied (the Bash self-disable guard is command-shaped and can't see a `Write` to `thing-orchestrator.sh`); payload caps (`SCREEN_MAX_BYTES`=1 MiB → oversize fails closed; `DECODE_MAX_RUNS`/`DECODE_MAX_BYTES` bound the base64 pass); a payload-shaped seat + full-payload egress backstop (`THING_PAYLOAD`); per-shape Sága + cache identity; and **§EDIT coercion** (file/network/MCP are ALLOW/DENY-only v1 — a seat EDIT is coerced to DENY). The `PreToolUse` matcher widens to `Bash|Write|Edit|MultiEdit|WebFetch|WebSearch|mcp__.*`. **Migration:** the widened matcher is consumer-visible — for anyone with the Thing on for **any** category, the hook now also fires on Write/Edit/WebFetch/MCP calls (a single `grep` short-circuit keeps **opted-out** consumers at zero cost), and a `Write`/`Edit` that mutates the Thing's substrate is now denied category-independently. No new *live* review of file/web/MCP content yet — Phase 1 (`file_edit_project`, ALLOW/DENY-only) flips the first non-Bash category live, rebased on this. Bash behavior is unchanged (Gate 14/15/22 pass with zero fixture edits); proven by **Gate 24** (classify coverage, substrate self-disable incl. hardlink, content hard-rule, oversize fail-closed, EDIT coercion, opt-out, cache non-collision). Full plan: [`docs/track-b-engine-foundation-implementation-plan.md`](../../docs/track-b-engine-foundation-implementation-plan.md).

**First non-Bash category live — `file_edit_project` (v0.38.0, Track B Phase 1).** The engine foundation (v0.37.0) is now switched ON for the first non-shell shape: `file_edit_project` (a `Write`/`Edit`/`MultiEdit` to a path **inside the project tree**) is wired end-to-end and clickable in the dashboard. It is **ALLOW/DENY-only** — there is no machine-checkable `concerns(revised) ⊆ concerns(original)` invariant for free-form file content, so a seat `edit` verdict is coerced to DENY (§EDIT-coercion, already in the v0.37.0 engine). The 7 `file_edit_project` concerns were made Gate-21-#17-detectable: deterministic **`triggers`** for the path/marker-unambiguous ones (writes into `.claude/` or `.ravenclaude/` config, generated/vendored paths, conflict markers — the triggers run against the reviewed text `"<file_path>\n<content>"`, so a `\A[^\n]*…` regex anchors on the path and a `(?m)^…` regex on the body) and **`judgment_only`** for the ones that need live state or would over-block (large-rewrite diff arithmetic, layout-allow-list comparison, literal-secret-vs-env-ref in content — the latter still backstopped by the egress secret scan in `thing-seat.sh`). Triggers are **panel-routed** (not `pre_llm_deny`): a match convenes the seat with the concern cited; the seat decides ALLOW/DENY. **Migration:** none — `file_edit_project` defaults OFF like every category, and the `PreToolUse` matcher already widened in v0.37.0, so nothing changes on `/plugin marketplace update` unless a consumer toggles it on. Proven by **Gate 21 #17 + #17c** (live-list + an FP/FN file-trigger corpus, incl. the `..`/`~` → `file_edit_global` routing guard) and the **Gate 24** `file_edit_project`-ON fixtures (clean write→allow, concerning `.claude/` write→deny, toggle-gating, EDIT-coercion→deny); Bash + engine behavior unchanged (Gate 14/15/22/24 carry zero pre-existing-fixture edits). Phase 2 (`file_edit_global` + reads) is next.

**Every non-Bash shape live — file reads + `file_edit_global` + `network_read` + `mcp_tools` (v0.39.0, Track B Phases 2-4).** The remaining five tool-shape categories flip ON together, all **ALLOW/DENY-only**: `file_read_project` / `file_read_global` (Read), `file_edit_global` (Write/Edit/MultiEdit outside the project), `network_read` (`WebFetch` reviews the URL, `WebSearch` the query), and `mcp_tools` (`mcp__server__verb` + canonical-json args). Their **23 concerns** were made Gate-21-#17-detectable with the same hybrid as Phase 1 — deterministic **`triggers`** on the path / URL / verb (e.g. `~/.ssh`·`~/.aws`·`/etc/shadow` reads, `~/.bashrc`·`/etc`·cron·systemd edits, the `169.254.169.254` metadata SSRF endpoint, localhost, IP-only/IDN domains, MCP write-verbs and `*_all_*` reads) and **`judgment_only`** where detection needs live state or would over-block (git-tracked keys, cross-project reads, secret-in-URL, the three MCP server-identity concerns). **`Read` was added to the `PreToolUse` matcher** (`Bash|Read|Write|Edit|MultiEdit|WebFetch|WebSearch|mcp__.*`) + the orchestrator's shape case — it was deliberately excluded through Phase 1 (reads weren't live). `WebSearch` was added to the `network_read` EMISSIONS (V3-5). **Reads are base-tier `low`** — a clean read convenes no panel (zero cost); only a high/critical concern (a secret/credential read, the metadata endpoint) escalates a read to a seat. **Migration:** the `Read`-widened matcher is consumer-visible (the hook now also fires on `Read`, kept at zero cost for opted-out consumers by the `grep` short-circuit); otherwise none — all five default OFF, so nothing changes on `/plugin marketplace update` unless toggled. **Not yet live (tracked follow-ups):** `network_write` (POST/PUT/DELETE) and the deterministic `mcp.allowed_servers` allowlist (design §MCP identity) — until the allowlist ships, the MCP server-identity concerns are seat-judged. Proven by **Gate 21 #17 + #17d** (live-list + a per-shape FP/FN corpus with routing guards) and **Gate 24** G24L fixtures (a concerning payload of each shape → deny via a seat; a clean low-tier read → not denied). Bash + engine behavior unchanged (Gate 14/15/22 carry zero fixture edits).

**Final category live — `network_write` (v0.40.0, Track B).** The last comfort-posture category flips ON, completing the matrix (12/12 reviewable). Unlike the v0.39.0 tool shapes, `network_write` is reached via **Bash** (`curl`/`wget`/`gh`) — `reviewed_text` is the command string, so it is **ALLOW/EDIT/DENY** like the shell categories (a seat rewrite is re-validated, not coerced to DENY), base tier `medium` (always panels). Its **6 concerns** were made Gate-21-#17-detectable: deterministic **`triggers`** for the DELETE method (`nw.delete-shared-resource`) and webhook-shaped URLs (`nw.webhook-to-unallowed-host` — Slack/Discord/Teams endpoints + a generic `/webhook` path), **`judgment_only`** for the four that need live state or are absence/substring shaped (`nw.body-contains-secret` — backstopped by the egress secret scan, `nw.high-cost-api`, `nw.idempotency-missing`, `nw.cross-tenant-write`). The load-bearing piece is a **flag-aware network-write override in `classify()`** (same routing-only pattern as the `git branch -D` override): the EMISSIONS prefixes catch explicit `curl -X POST` / `gh api POST`, but curl/wget also write via data/upload flags (implicit POST) and `=`-attached method flags the space-delimited prefix matcher can't see — without the override a `curl -d`/`wget --post-data`/`gh api -X POST` would auto-allow as a `network_read` "read" before a write concern could fire. The override touches routing only (NOT the permission EMISSIONS table, exactly like `git branch -D`), so a consumer's emitted deny/ask/allow rules are unchanged. **Migration:** none — `network_write` defaults OFF, Bash was already in the matcher, and EMISSIONS is untouched, so nothing changes on `/plugin marketplace update` unless toggled. Proven by **Gate 21 #17 + #17e** (live-list + a command FP/FN corpus + the routing-override guards, incl. the `curl -X GET` / `wget -d`-debug non-re-route cases) and a **Gate 24 G24L** `network_write`-ON fixture (`curl -X DELETE` → deny via the panel). Bash + engine behavior otherwise unchanged (Gate 14/15/22 carry zero fixture edits). Remaining follow-up: the deterministic `mcp.allowed_servers` allowlist (design §MCP identity).

**MCP server allowlist — engine feature-complete (v0.41.0, Track B §MCP identity).** The last Track B follow-up ships: a deterministic per-server allowlist. Declare trusted servers in `.ravenclaude/thing.yaml` `mcp.allowed_servers: [github, atlassian]` (or `comfort-posture.yaml` `command_review.mcp.allowed_servers`, which wins). When an allowlist **is** configured, `_decision_detail` denies a **write** verb (anything outside the fixed read-verb prefix set `get_`/`list_`/`read_`/`search_`/`describe_`/`fetch_`) from a server **not** on the list **pre-LLM**, citing `mcp.unverified-server`. Implementation reuses the existing `pre_llm_deny` path (set `pre_llm_deny=true` + `deny_concern`), so the orchestrator needs **zero** changes — the deny flows through the same emit + Sága tail as a catalog hard-deny, and (being pre_llm_deny) it beats `bypass`/cache and can't be relaxed. The check is engine config (a server-name membership test on the `mcp__<server>__<verb>` tool name via `mcp_server_name()` + `mcp_verb_is_read()`), **not** a catalog regex, so the three server-identity concerns stay `judgment_only` (Gate 21 #17 unaffected). It is **opt-in**: an absent/empty allowlist denies nothing — the concerns remain seat-judged, so no existing `mcp_tools` user is newly blocked (clean `/plugin marketplace update`). Reads and listed-server writes fall through to the panel unchanged. `mcp.tool-shadowing` stays seat-judged (a name-collision check needs the full live registry, not in the single-call hook payload). The allowlist folds into `config_hash` so a server added/removed invalidates a cached MCP verdict. **Migration:** none — opt-in, defaults off. Proven by **Gate 25** (non-listed write → `pre_llm_deny`; verbless call treated as write; non-listed read + listed write + absent-allowlist NOT pre-denied; `config_hash` invalidation; and end-to-end that a non-listed write denies under `mock=allow` while a listed write is panel-decided). With this, **Track B is feature-complete**: all 12 categories live + the MCP identity layer.

**MCP allowlist dashboard UI (v0.42.0).** The allowlist gets a point-and-click control so it isn't `thing.yaml`-only: the dashboard's **Command-review panel** now has a **Trusted MCP servers** text field (comma-separated server names, validated to the `[A-Za-z0-9._-]` tool-name charset + deduped). It round-trips through the same `state.command_review` object as the seats/gate_floor — parsed back on load from `command_review.mcp.allowed_servers` and serialized into the emitted `comfort-posture.yaml` (which already wins over `thing.yaml`). Engine behavior is unchanged from v0.41.0; this is purely the authoring surface. Verified: generator runs clean, the emitted block drives the engine deny (the dashboard→engine contract), `node --check` on the embedded app JS passes, and the parse/emit string logic round-trips. (No browser click-through was run — there's no dev server for the static generated dashboard.) The freshness gate keeps `dashboard.html` in lockstep with the generator; Gate 25 still covers the engine semantics.

**Convention for future plugins:** every plugin under `plugins/` MUST have `.claude-plugin/plugin.json`, `README.md`, and `CLAUDE.md`. It MAY add purpose-specific directories (e.g. `solutions/`, `flows/` in `power-platform`) — declare any non-default component paths in `plugin.json` (the `agents`, `skills`, `commands`, `hooks` fields all accept arrays) and add a `## Layout` section to that plugin's CLAUDE.md explaining the deviation.

## GitHub Copilot CLI bridge (added 2026-05-26, v0.30.0)

RavenClaude runs under **GitHub Copilot CLI** (GA Feb 2026), not just Claude Code. Copilot CLI is itself a plugin host with the same lifecycle hook events (SessionStart / PreToolUse / PostToolUse / …), Agent Skills (it reads `.claude/skills` directly), AGENTS.md, and MCP — so most of the plugin ports. The pieces:

- **Generated package** — [`scripts/generate-copilot-plugin.py`](../../scripts/generate-copilot-plugin.py) projects the canonical plugin into a Copilot plugin at [`copilot/`](copilot/) (`plugin.json` + `agents/*.agent.md`). It is **generated, never hand-maintained** (single source of truth; `--check` freshness gate, like the dashboard/repo-guide generators). It declares only `agents` — skills + hooks ship via the installer's repo-level surfaces (below), not bundled.
- **Hook adapter** — [`hooks/copilot-hook-adapter.sh`](hooks/copilot-hook-adapter.sh) translates the I/O envelopes so the **existing, unmodified** hook scripts run under Copilot: Copilot's PreToolUse stdin (`toolName` + `toolArgs`-as-JSON-string) ⇄ Claude's (`tool_name`/`tool_input`), and Claude's `hookSpecificOutput.permissionDecision` / exit-2-block ⇄ Copilot's **top-level** `permissionDecision`. Also maps SessionStart `additionalContext`.
- **Enforcement hooks ship as repo-level `.github/hooks/*.json`**, NOT plugin-level — Copilot bug [github/copilot-cli#2540](https://github.com/github/copilot-cli/issues/2540) (plugin `preToolUse` hooks don't fire) forces this; repo-level hooks do fire. Migrate to plugin-level when #2540 closes.
- **Installer / updater** — [`scripts/ravenclaude`](../../scripts/ravenclaude) (`setup` / `install` / `update` / `status` / `init-codespace`) wires skills→`.claude/skills`, hooks→`.github/hooks` (via the adapter), and the bundled MCP→`~/.copilot/mcp-config.json`, and prints an `rc` launch alias. `setup` is the one-shot superset: `install` + seed & apply a balanced comfort-posture + write the `rc` alias.
- **Frictionless update (the design pillar):** we deliberately do **NOT** use Copilot's install-and-cache mechanism (its re-install-to-update flow is the pain point). The plugin loads **live** via `copilot --plugin-dir copilot/`, and every other surface (`.claude/skills`, `.github/hooks`, MCP config, AGENTS.md) is read live from disk — so an **update is just `git pull`** (`ravenclaude update` / the `rc` alias). No re-install, ever.
- **One-click from the dashboard** — `serve-dashboards.py` exposes an allow-listed `POST /__run` (actions `install`/`update`/`status` only — no arbitrary commands), and the dashboard's **Install & Update** tab drives it with buttons (served mode) + copy-to-clipboard commands (everywhere).

**Setup & update — one-click or by hand.** The dashboard's **Install & Update** tab (served via `/dashboard` → `serve-dashboards.py`) drives `install` / `update` / `status` with buttons, so a consumer never has to type them. The equivalent manual commands, run from a marketplace clone (`RC`):

```shell
RC=~/RavenClaude                                                  # the marketplace clone
bash "$RC/scripts/ravenclaude" install --project /path/to/repo    # one-time wiring (idempotent)
bash "$RC/scripts/ravenclaude" status  --project /path/to/repo    # show what's wired
bash "$RC/scripts/ravenclaude" update                             # git pull + regenerate — anytime
copilot --plugin-dir "$RC/plugins/ravenclaude-core/copilot"       # launch live (run in a terminal)
```

`install` and `status` both accept `--project DIR` (default `$PWD`); `status` also takes a bare positional path.

**Zero-command Codespace auto-setup (v0.43.0).** For a brand-new repo there's nothing to type at all: ship the [`templates/codespace-copilot/`](templates/codespace-copilot/) devcontainer into the repo (`ravenclaude init-codespace --project <repo>` stamps it, or make a GitHub _template repo_ out of it). When the Codespace builds, its `postCreateCommand` installs the Copilot CLI if missing, clones the marketplace once (via `gh`), and runs **`ravenclaude setup`** — which wires skills/hooks/MCP, seeds [`templates/comfort-posture-balanced.yaml`](templates/comfort-posture-balanced.yaml) into `.ravenclaude/comfort-posture.yaml` (only if absent — never clobbers an existing posture) and applies it to `.claude/settings.json`, then adds the `rc` alias. Result: open the Codespace → type `rc` → Copilot launches fully wired. The launch stays one word (`rc`) because `postCreateCommand` runs before there's an interactive terminal to take over. The balanced seed allows local dev, prompts on out-of-repo / remote / network-write actions, and always denies the security floor; re-tune it in the dashboard. **Gate 26** proves the seeded posture is valid (applies + emits rules + carries the floor) and that a corrupted seed is rejected.

**Per-repo comfort-posture dashboard (v0.44.0).** `setup` also drops repo-local dashboard launchers into the consumer repo so the point-and-click posture editor is first-class, not a remembered command: `.ravenclaude/dashboard.sh` (self-resolving — derives its own repo root from its location), a one-click **VS Code task**, a `.ravenclaude/README.md` with the link, and a `ravenclaude dashboard [--project DIR]` subcommand. All are **scoped to the consumer repo**: `serve-dashboards.py` gained `--project-root` plus a **hard guard** that refuses to run if `--project-root` resolves inside the marketplace checkout — so a consumer dashboard can only ever edit its own repo, and the marketplace is edited only by *its own* `/dashboard` (which launches without `--project-root`). The dashboard files stay live in the clone (updates arrive via `ravenclaude update`); only the thin launchers live in the repo. **Gate 27** proves the guard (refuses a marketplace `--project-root`, accepts a consumer repo).

Slash commands (`/set-posture`, `/wrap`) don't port (Copilot CLI has no user slash commands yet) — they're documented shell invocations. Live Copilot-CLI behavior is owner-verified (the SDK isn't present in CI); the adapter I/O translation + package freshness are gated (Gate 20).

## New skills (v0.13.0)

Four meta-discipline skills added to support agent authoring, knowledge hygiene, and release operations across the marketplace:

- [`skills/agent-quality-rubric/SKILL.md`](skills/agent-quality-rubric/SKILL.md) — Score and improve an agent file against a 6-dimension rubric (Mission clarity, Scope sharpness, Capability Grounding alignment, Output-Contract completeness, Escalation paths, Example scenarios) with a remediation PR template. Used by `prompt-engineer` (primary) + `architect`.
- [`skills/knowledge-file-staleness-sweep/SKILL.md`](skills/knowledge-file-staleness-sweep/SKILL.md) — Periodic staleness sweep over all `plugins/<plugin>/knowledge/*.md` + decision-tree sections — flags entries past 90/180/365-day thresholds, categorizes by Researcher Tier 1-5 effort, produces a remediation queue with named re-verifiers. Used by `deep-researcher` (primary) + the maintainer.
- [`skills/prompt-pattern-library/SKILL.md`](skills/prompt-pattern-library/SKILL.md) — Curated catalog of the 9 already-extant marketplace prompt patterns (decision-tree traversal, alternate-methods, Structured Output, scenario-retrieval, mandatory-phrasing, citation-aware, environment-context, orchestrator-worker, scenario-authoring frontmatter), each with example block + composition checklist. Used by `prompt-engineer` (primary).
- [`skills/plugin-release-checklist/SKILL.md`](skills/plugin-release-checklist/SKILL.md) — Pre-release checklist: plugin.json + marketplace.json + architecture.md version-mirror discipline, .repo-layout.json glob coverage, prettier check, audit-gates meta-test, migration-note rule, with bash + PowerShell commands per step and a hot-fix sub-section. Used by the maintainer (primary) + `project-manager`.

## Quality gates, Hooks, Rules & Templates (Unchanged Core + Extensions)

The existing 5 hooks, 4 rulesets, and 21+ templates remain foundational. 

**Enhancement Recommendations**:
- Extend `remind-tests` or add output-validation hook elements that check for Structured Output Protocol compliance on critical deliverables.
- Add or evolve rules in `rules/` to reference the new Structured Output Protocol and artifact standards.
- Expand `templates/` with the new run-artifacts templates and handoff templates.

See `plugins/ravenclaude-core/rules/` and `hooks/` for current implementations. Update them to reinforce the new protocols for even higher output quality.

## Team Roster & When to Spawn Agents

(See original team-roster table or agent definitions in `agents/`. The new protocols above apply universally to all specialists and the Team Lead. Update individual agent prompts in `agents/*.md` or equivalent to reference the Structured Output Protocol, Focused Task style, and artifact requirements.)

---

**Summary of Enhancements (from learnings in robust agent runtimes like agentic-harness)**:
- **Structured Output Protocol** → Dramatically improves parseability, reduces errors in handoffs, enables reliable automation.
- **Focused Task Execution** → Better focus, higher quality per subtask, reduced context pollution.
- **Run Artifacts Standard** → Enables inspection, debugging, reproducibility, and continuous improvement of the entire team.
- **Context Hygiene** → Sustains high output quality over long sessions.
- Integrated with existing strengths (hierarchical dispatch, Researcher, Grounding) for a more complete, production-grade system that consistently produces *ideal outputs*.

These changes make RavenClaude agents even more reliable at creating high-quality, consistent, inspectable results while preserving the elegant multi-agent team structure.