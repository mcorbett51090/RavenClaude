## Plugin Architecture: Core vs Domain Plugins (Updated)

- `ravenclaude-core` is the **foundational plugin**. It provides the Team Lead, generalist agents (Architect, Coder, Reviewer, etc.), skills, hooks, Capability Grounding Protocol, the Researcher meta-skill, **Structured Output Protocol**, and standardized run artifacts conventions.
- Domain plugins (e.g. `power-platform`) **extend** core. They add specialist agents and domain-specific knowledge.
- The Team Lead is responsible for detecting domain-specific work and dispatching specialists from installed domain plugins.

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

## Structured Output Protocol (Active — required for handoffs)

> **Status as of 2026-05-20:** This protocol is **active**. Every sub-agent that hands off to the Team Lead (or to a downstream specialist) MUST end its report with a `---RESULT_START--- ... ---RESULT_END---` delimited JSON block alongside its human-readable Markdown. The dual-output format is the 2026 norm in production multi-agent systems (pure JSON loses reasoning, pure Markdown is unparseable). Agent files in `agents/` are being retrofitted to declare this requirement explicitly in their Output Contract sections; until that retrofit lands across all 13 agents, the Team Lead enforces the contract at dispatch time by including the format in the brief.

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
  "handoff_recommendation": { "specialist": "...", "reason": "..." },
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

The marketplace includes a **Researcher** meta-skill located in `plugins/ravenclaude-core/skills/researcher/`.

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

## Capability Grounding Protocol (Updated)

Before any agent claims it cannot do something or that information is outdated, it must:
1. Check available skills (including the Researcher skill when appropriate).
2. Consider whether partial progress is possible.
3. Run the Grounding Protocol checklist.
4. **Produce any limitation statement using the Structured Output Protocol.**
5. Only then state limitations clearly.

The Researcher itself must apply this protocol to its own findings.

## Run Artifacts & Observability Standard (New — Critical for Ideal Outputs & Inspection)

To enable inspection, debugging, learning, and continuous improvement of the agent team (and to mirror best practices from high-quality agent runtimes), **every significant workflow or task orchestrated by the Team Lead SHOULD produce standardized artifacts**.

### Convention
Store artifacts in a project-local directory:
```
.ravenclaude/runs/<task-or-epic-id>/
```

( Create the directory if it doesn't exist. Use a short descriptive ID or timestamp + slug. )

### Required / Recommended Artifacts (use templates from templates/run-artifacts/)

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

## Layout (plugin internal directories)

`ravenclaude-core` uses the standard component directories:

- `agents/` — 13 specialist agent definitions
- `skills/` — dispatch playbook (spawn-team), worktree helpers, structured-output reference, run-full-test-suite, contribution-staging
- `hooks/` — format-on-write, guard-destructive, remind-tests, enforce-layout (all registered in `hooks/hooks.json` for plugin-level distribution)
- `rules/` — coding-standards, security, git-workflow, agent-collaboration
- `templates/` — memos, runbooks, design specs, RAID logs, partner-success, plus `agent-ready-repo/` templates used by `/init-agent-ready`
- `commands/` — `/init-agent-ready` slash command shipped to consumers
- `knowledge/` — reference material the Researcher cross-checks

**Convention for future plugins:** every plugin under `plugins/` MUST have `.claude-plugin/plugin.json`, `README.md`, and `CLAUDE.md`. It MAY add purpose-specific directories (e.g. `solutions/`, `flows/` in `power-platform`) — declare any non-default component paths in `plugin.json` (the `agents`, `skills`, `commands`, `hooks` fields all accept arrays) and add a `## Layout` section to that plugin's CLAUDE.md explaining the deviation.

## Quality gates, Hooks, Rules & Templates (Unchanged Core + Extensions)

The existing 3 hooks, 4 rulesets, and 21+ templates remain foundational. 

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