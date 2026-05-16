# Enhancement Proposal: Integrating Learnings from agentic-harness into RavenClaude

**Author**: Grok (with analysis of both repos)  
**Date**: 2026-05-16  
**Goal**: Make RavenClaude agents produce even more *ideal outputs* — reliable, structured, high-quality, inspectable, and consistent — by adopting proven patterns from the robust `agentic-harness` runtime (Rust-native agent SDK with strong emphasis on typed outputs, task decomposition, context management, and observability).

## Why These Enhancements?

`agentic-harness` demonstrates excellent engineering for agentic systems:
- Schema-guided + delimited structured outputs for reliable parsing/extraction.
- Clear Task primitives for focused sub-work with fresh context.
- Rich, standardized per-run artifacts for inspection and feedback loops.
- Strong emphasis on workspace context, safety, and reproducible execution.

RavenClaude already has a strong foundation:
- Hierarchical multi-agent orchestration (Team Lead + specialists).
- Researcher for knowledge freshness.
- Capability Grounding Protocol.
- Quality hooks, rules, templates, git worktrees, and CLAUDE.md constitution.

**The enhancements fuse the best of both**: Keep RavenClaude's elegant team-based, Claude Code-native approach while layering on the output reliability, observability, and task hygiene patterns that make harness agents consistently produce high-quality results.

Result: Agents that not only collaborate well but **reliably output ideal, production-ready artifacts** with minimal manual cleanup or parsing issues.

## Key Changes Made

### 1. Enhanced `plugins/ravenclaude-core/CLAUDE.md` (Core Constitution)
Added/expanded sections:
- **Structured Output Protocol** (new flagship addition): Mandates JSON schemas + `---RESULT_START--- / ---RESULT_END---` delimiters for structured deliverables, handoffs, and summaries. Includes example prompt patterns. This is the single biggest lever for "ideal outputs."
- **Focused Task Execution**: Guidance on narrow-scope delegations with explicit success criteria and output formats (prevents bloated context and improves subtask quality).
- **Run Artifacts & Observability Standard**: Defines `.ravenclaude/runs/<id>/` convention + required artifacts (summary.md, structured-output.json, changes.diff, checks.json, decisions.md, events.jsonl, etc.). Creates a feedback/inspection loop.
- **Context & Session Hygiene**: Rules for periodic summarization and focused context slices.
- Integrated all new protocols with existing Researcher, Grounding, and hierarchical dispatch rules.
- Updated rationale to reference validated patterns from robust agent runtimes.

This file is the primary "constitution" that ships with the plugin — updating it immediately elevates behavior across all agents.

### 2. New Supporting Components (Proposed)
- `skills/structured-output.md` (example skill definition) — A reusable skill/playbook for applying the Structured Output Protocol.
- `templates/run-artifacts/` — Ready-to-use templates for standardized artifacts.
- Potential hook/rule extensions to enforce artifact generation and output protocol compliance.

### 3. Benefits for Ideal Outputs
- **Higher reliability**: Structured handoffs reduce miscommunication between specialists and Team Lead.
- **Better parseability**: Downstream automation, inspection tools, or even other agents can reliably consume outputs.
- **Improved focus & quality**: Focused tasks + hygiene keep reasoning sharp.
- **Observability & Iteration**: Rich artifacts enable post-run review, feeding the Researcher, and continuous improvement of the team.
- **Production-grade feel**: Mirrors professional engineering workflows with logs, diffs, checks, and rationales.
- Backward compatible: Existing hooks, rules, and dispatch logic remain; new protocols layer on top as best practices.

## How to Apply These Enhancements

1. **Clone or checkout** your RavenClaude repo locally.
2. **Replace** `plugins/ravenclaude-core/CLAUDE.md` with the enhanced version from this proposal.
3. **Add the new skill and templates** into the appropriate subdirectories under `plugins/ravenclaude-core/`.
4. **Update individual agent prompts** (in `agents/`) and any existing skills to reference the new Structured Output Protocol and artifact requirements (e.g., "Always conclude major deliverables using the Structured Output Protocol...").
5. **Extend hooks** (optional but recommended): Modify `remind-tests` or add an `enforce-artifacts` hook that checks for key files in `.ravenclaude/runs/`.
6. **Test**: Install the updated plugin locally (`/plugin marketplace add /path/to/your/checkout`), reload, and run a multi-agent workflow (e.g., spawn-team + a coding task). Verify structured outputs and artifact generation.
7. **Bump version** in the plugin's `plugin.json` and update marketplace if publishing.
8. **Iterate**: Use the new artifacts + Researcher to further refine prompts/rules.

## Future Opportunities
- Implement a dedicated "Artifacts Generator" skill or hook.
- Add CLI-like inspection commands or a simple script to view latest runs.
- Explore deeper integration with workspace context loading (inspired by harness `.agentic-harness/` conventions).
- Make artifact standards configurable per project.
- Port portable parts (Researcher discipline, Structured Output Protocol) for use with Grok or other models.

These changes position RavenClaude as one of the most robust, output-quality-focused multi-agent setups for Claude Code — combining team intelligence with engineering rigor for consistently *ideal* results.

If you'd like me to generate the additional skill files, full templates, hook examples, or even a diff/patch set, just say the word!