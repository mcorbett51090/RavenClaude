# ravenclaude-core — Claude Code plugin

> The domain-neutral Team Lead + specialist-agent foundation for the RavenClaude marketplace.

Ships the orchestrator-worker dispatch model, 14 generalist specialist agents (architect, backend/frontend/fullstack coders, code-reviewer, security-reviewer, tester-qa, data-engineer, deep-researcher, designer, documentarian, project-manager, partner-success-manager, prompt-engineer), 20 skills, 5 hooks, 4 rule-sets, working templates, slash commands (`/init-agent-ready`, `/wrap`, `/set-posture`), and a knowledge bank the Researcher cross-checks. Every other plugin in the marketplace extends this one.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install ravenclaude-core@ravenclaude
/reload-plugins
```

This is the prerequisite plugin — domain plugins (`power-platform`, `finance`, …) require it for the shared protocols below.

## What's inside

| Component | Count | Where |
|-----------|-------|-------|
| Specialist agents | 14 | [`agents/`](agents/) |
| Skills | 20 | [`skills/`](skills/) |
| Hooks | 5 | [`hooks/`](hooks/) |
| Rule-sets | 4 | [`rules/`](rules/) |
| Slash commands | 3 (`/init-agent-ready`, `/wrap`, `/set-posture`) | [`commands/`](commands/) |
| Knowledge files | see [`knowledge/`](knowledge/) | [`knowledge/`](knowledge/) |

## The protocols it provides to the whole marketplace

- **Orchestrator-worker dispatch** — only the Team Lead spawns specialists; sub-agents hand back, they don't fan out.
- **Capability Grounding Protocol** — pre-action environment + decision-tree checks, alternate-methods enumeration, and honest blocked-phrasing before any "I can't."
- **Structured Output Protocol** — every handoff ends with a `---RESULT_START--- … ---RESULT_END---` JSON block alongside human-readable Markdown.
- **Comfort-posture** — `/set-posture` translates a per-category YAML into `.claude/settings.json` permission rules, with an always-on `security_deny` baseline.
- **Per-plugin dashboard** — `generate-dashboards.py` renders an interactive settings/activity dashboard.

See [`CLAUDE.md`](CLAUDE.md) for the full team constitution (dispatch rules, agent-routing decision tree, knowledge-freshness discipline, run-artifacts standard).

## When to dispatch

```text
"Design the approach before we build X"        → architect
"Implement this API handler / this UI"          → backend-coder / frontend-coder
"Review this diff before I merge"               → code-reviewer (+ security-reviewer if auth/crypto)
"Is this library claim actually true?"          → deep-researcher
"Set up this repo so agents behave"             → /init-agent-ready
"Capture what we just learned"                  → /wrap
"Tune how autonomous Claude is here"            → /set-posture
```
