# claude-app-engineering

A specialist team for building **production applications on the Claude API, the Claude Agent SDK, and MCP** — the engineering discipline behind agentic-AI engagements.

## What it is

The hard part of a Claude app is rarely the first prompt — it's the decisions: Messages API or Agent SDK or Managed Agents? which model? how do I make the cache hit? structured output? MCP server or in-process tool? how do I keep the bill sane and the app up under 429s? This plugin encodes those as a team of advisory specialists backed by a 9-doc, retrieval-dated, citation-grounded knowledge bank — important because the platform ships monthly.

The agents are **advisory and interactive**: your app and API keys live outside the repo, so they recommend designs and emit runnable snippets (Python/TS, MCP configs, eval harnesses) you run yourself.

**The marketplace is the worked example** — RavenClaude itself *is* a Claude Agent SDK plugin set (skills + agents + hooks + plugins), so the agents can point at `plugins/*/` as a reference implementation.

## The team

| Agent | Owns |
|---|---|
| `claude-solution-architect` | build-surface (Messages API / Agent SDK / Managed Agents), model right-sizing, deployment target, architecture |
| `prompt-and-context-engineer` | prompts, prompt caching, 1M context, thinking, structured output, in-app tool design + the loop |
| `mcp-and-server-tools-engineer` | MCP server authoring + hosted server tools (computer use, code execution, Files API, memory) |
| `agent-sdk-engineer` | Claude Agent SDK (subagents/hooks/skills/sessions/permissions) + Managed Agents |
| `eval-engineer` | evals — golden sets, programmatic + LLM-as-judge grading, regression deltas |
| `claude-app-ops-engineer` | FinOps (cache hit rate, routing ladder, Batch), reliability (429/backoff), observability |

Plus a 9-doc knowledge bank (build-surface decision tree + dated capability map + caching/tools/MCP/server-tools/Agent-SDK/evals/FinOps playbooks), 6 templates, and 1 advisory hook (14 house opinions).

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install claude-app-engineering@ravenclaude
/reload-plugins
```

Requires `ravenclaude-core@>=0.7.0`.

## Prerequisite

No bundled MCP. The agents emit code against the **Anthropic SDK** (`pip install anthropic` / `npm i @anthropic-ai/sdk`) and the **Claude Agent SDK** (`pip install claude-agent-sdk` / `npm i @anthropic-ai/claude-agent-sdk`); you run it with your own `ANTHROPIC_API_KEY` (or Bedrock/Vertex/Foundry creds).

## How it relates to the other plugins

- **`ravenclaude-core/prompt-engineer`** — improve a prompt/agent-file as an artifact → core; the app's prompt+caching+context+token economics → here.
- **`ravenclaude-core/security-reviewer`** (mandatory) — prompt injection, secrets, sandboxing → core; this plugin supplies AI-app security knowledge, core supplies the verdict.
- **`ravenclaude-core/architect`** — whole-system architecture → core; the Claude-runtime decision → here.
- **`web-design` / `data-platform` / `microsoft-fabric`** — the app's UI shell / data backend.

See [`CLAUDE.md`](CLAUDE.md) §10 for the full seam wording.

## Versioning

Semver; keep `.claude-plugin/plugin.json` in sync with the catalog entry. The dated capability map (`knowledge/model-selection-and-2026-capability-map.md`) is re-reviewed on each Researcher staleness sweep because the Claude platform ships monthly.
