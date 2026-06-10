# power-platform — Claude Code plugin

> Microsoft Power Platform specialist team for the RavenClaude marketplace.

Ships 11 specialists covering canvas/Power Fx apps, model-driven apps, Power Automate + connectors, Dataverse modeling, Power BI (PBIP-git + DAX + ADO), pac CLI + ALM, tenant governance/DLP, PCF controls, Copilot Studio + AI Builder, Power Pages, and a Test Studio + `pac solution check` tester. Includes a house-opinions hook covering mechanically-detectable §3/§4 violations, a Mermaid decision-tree knowledge file (Power Automate flow recovery), a scenarios bank from a real customer DEV engagement, and the bundled community `pbix-mcp` server for Power BI `.pbix`/`.pbit` read/write/DAX-eval.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install ravenclaude-core@ravenclaude     # prerequisite
/plugin install power-platform@ravenclaude
/reload-plugins
```

Requires `ravenclaude-core` for the shared protocols (Grounding, Structured Output, orchestrator-worker dispatch). The bundled MCP server needs `pip install pbix-mcp` if you want `.pbix` read/write.

## What's inside

| Component | Count | Where |
|-----------|-------|-------|
| Specialist agents | 11 | [`agents/`](agents/) |
| Skills | 21 | [`skills/`](skills/) |
| Hooks | 1 (house-opinions, advisory) | [`hooks/`](hooks/) |
| Knowledge files | incl. the PA-flow-recovery decision tree | [`knowledge/`](knowledge/) |
| Scenarios | seeded from a real DEV engagement | [`scenarios/`](scenarios/) |

> **Skill format note:** this plugin packages skills as `skills/<name>/SKILL.md` directories (the official Agent-Skills layout), which differs from the flat `skills/<name>.md` used by the other domain plugins. See [`docs/best-practices/`](../../docs/best-practices/) for the canonical-format decision.

See [`CLAUDE.md`](CLAUDE.md) for the full team constitution (roster, routing rules, the §3/§4 house opinions the hook enforces, and the ALM/governance anti-patterns).

## When to dispatch

```text
"This canvas app's delegation is broken"        → canvas/Power Fx specialist
"Model this Dataverse table + relationships"    → dataverse modeler
"This cloud flow keeps failing on retry"        → power-automate specialist
"PBIP git diff is noisy / DAX is slow"          → power-bi-engineer
"Set up solution ALM with pac CLI"              → pac CLI / ALM specialist
"Is our tenant DLP policy sane?"                → tenant governance / DLP specialist
"Build a Copilot Studio topic"                  → copilot-studio engineer
```
