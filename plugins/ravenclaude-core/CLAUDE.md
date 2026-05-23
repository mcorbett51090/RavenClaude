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

> Reading a branch needs no isolation (`git show <ref>:<path>` — parallelize freely). Writing a branch (checkout / commit / push) needs Bash, and `isolation: "worktree"` **takes Bash away** in this environment. So: parallel reads yes; for parallel writes, do them in the main agent sequentially, serialize non-isolated agents one-per-branch, or have each agent build its own `git worktree` by hand.

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

## Session-start environment-context load (added 2026-05-22)

The Team Lead reads `.ravenclaude/environment-context.md` at the consumer's project root **as part of session-start orientation**, in the same pass that loads CLAUDE.md and AGENTS.md. The file is OPTIONAL — its absence is informational, not an error. When present, the Team Lead:

1. Parses the active environments + per-environment role + per-environment pre-authorized action categories + forbidden lists
2. Injects a compact summary into the working context (e.g., *"Per `.ravenclaude/environment-context.md`: agent is sysadmin in DEV/TEST, read-only in PROD; pre-authorized for solution import/export + Web API + pac CLI in DEV/TEST"*)
3. Surfaces the summary to dispatched specialists in their focused-task brief when their work might touch one of those environments

When the file is ABSENT, the Team Lead offers auto-discovery via the [`environment-discovery`](skills/environment-discovery.md) skill instead of asking the user to fill in the template by hand. The skill probes installed CLIs (`pac`, `az`, `aws`, `gcloud`, `gh`) with read-only commands, decodes any acquired JWTs, and assembles a draft `.ravenclaude/environment-context.md` for the user to save / edit / skip. Discovery never runs without user confirmation; discovery is read-only by contract; discovery refuses to write any credentials to the file.

This is the load-bearing wiring for the Capability Grounding Protocol's pre-action environment-context check (above). Without the load, the check has nothing to read.

**Consumer-side workflow for creating the file (two paths):**

- **Auto-discovery (recommended)** — at session start when the file is absent, accept the Team Lead's offer to run [`environment-discovery`](skills/environment-discovery.md). One prompt, ~30 seconds of read-only probes, save / edit / skip. Future sessions reuse the saved file.
- **Manual** — copy `plugins/ravenclaude-core/templates/environment-context.md` from the marketplace to `.ravenclaude/environment-context.md`, fill in by hand.

Either way: refresh quarterly OR on env-posture change OR when `/wrap` surfaces a new action category worth pre-authorizing. The Researcher's Weekly Deep Research flags files older than 90 days.

**Privacy boundary:** the file lives in the consumer's project (not in the marketplace plugin) because it contains identifying info (env names, SPN names, tenant slugs). Never commit a marketplace-shipped `environment-context.md` containing real consumer posture. Marketplace ships the **template only**.

## Layout (plugin internal directories)

`ravenclaude-core` uses the standard component directories:

- `agents/` — 14 specialist agent definitions (now includes `data-engineer`)
- `skills/` — dispatch playbook (spawn-team), worktree helpers, structured-output reference, run-full-test-suite, contribution-staging, agent-quality-rubric, knowledge-file-staleness-sweep, prompt-pattern-library, plugin-release-checklist
- `hooks/` — format-on-write, guard-destructive, remind-tests, enforce-layout, guard-recursive-spawn (all registered in `hooks/hooks.json` for plugin-level distribution)
- `rules/` — coding-standards, security, git-workflow, agent-collaboration
- `templates/` — memos, runbooks, design specs, RAID logs, partner-success, plus `agent-ready-repo/` templates used by `/init-agent-ready`
- `commands/` — `/init-agent-ready` slash command shipped to consumers
- `knowledge/` — reference material the Researcher cross-checks

**Convention for future plugins:** every plugin under `plugins/` MUST have `.claude-plugin/plugin.json`, `README.md`, and `CLAUDE.md`. It MAY add purpose-specific directories (e.g. `solutions/`, `flows/` in `power-platform`) — declare any non-default component paths in `plugin.json` (the `agents`, `skills`, `commands`, `hooks` fields all accept arrays) and add a `## Layout` section to that plugin's CLAUDE.md explaining the deviation.

## New skills (v0.13.0)

Four meta-discipline skills added to support agent authoring, knowledge hygiene, and release operations across the marketplace:

- [`skills/agent-quality-rubric.md`](skills/agent-quality-rubric.md) — Score and improve an agent file against a 6-dimension rubric (Mission clarity, Scope sharpness, Capability Grounding alignment, Output-Contract completeness, Escalation paths, Example scenarios) with a remediation PR template. Used by `prompt-engineer` (primary) + `architect`.
- [`skills/knowledge-file-staleness-sweep.md`](skills/knowledge-file-staleness-sweep.md) — Periodic staleness sweep over all `plugins/<plugin>/knowledge/*.md` + decision-tree sections — flags entries past 90/180/365-day thresholds, categorizes by Researcher Tier 1-5 effort, produces a remediation queue with named re-verifiers. Used by `deep-researcher` (primary) + the maintainer.
- [`skills/prompt-pattern-library.md`](skills/prompt-pattern-library.md) — Curated catalog of the 9 already-extant marketplace prompt patterns (decision-tree traversal, alternate-methods, Structured Output, scenario-retrieval, mandatory-phrasing, citation-aware, environment-context, orchestrator-worker, scenario-authoring frontmatter), each with example block + composition checklist. Used by `prompt-engineer` (primary).
- [`skills/plugin-release-checklist.md`](skills/plugin-release-checklist.md) — Pre-release checklist: plugin.json + marketplace.json + architecture.md version-mirror discipline, .repo-layout.json glob coverage, prettier check, audit-gates meta-test, migration-note rule, with bash + PowerShell commands per step and a hot-fix sub-section. Used by the maintainer (primary) + `project-manager`.

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