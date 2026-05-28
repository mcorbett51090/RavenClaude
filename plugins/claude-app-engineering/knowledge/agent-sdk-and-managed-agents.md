# Claude Agent SDK & Managed Agents

**Last reviewed:** 2026-05-28 · **Confidence:** high ([Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview), [Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview), retrieved 2026-05-28).
**Owner:** `agent-sdk-engineer`.

## What the Agent SDK is
The same agent loop, built-in tools, and context management that power Claude Code, as a library in **Python** (`pip install claude-agent-sdk`) and **TypeScript** (`npm i @anthropic-ai/claude-agent-sdk`; bundles a native binary). You give it a prompt + options; Claude reads files, runs commands, edits code, uses tools, and manages context for you.

```python
async for message in query(
    prompt="Find and fix the bug in auth.py",
    options=ClaudeAgentOptions(allowed_tools=["Read", "Edit", "Bash"]),
):
    print(message)
```

## Core concepts
| Concept | What it gives you |
|---|---|
| **Built-in tools** | Read, Write, Edit, Bash, Glob, Grep, WebSearch, WebFetch, Monitor, AskUserQuestion |
| **Hooks** | callbacks at lifecycle points: `PreToolUse`, `PostToolUse`, `Stop`, `SessionStart`, `SessionEnd`, `UserPromptSubmit`, … — validate/log/block/transform behavior |
| **Subagents** | `AgentDefinition` specialized agents, invoked via the `Agent` tool (add `Agent` to allowed_tools); messages carry `parent_tool_use_id` |
| **Permissions** | `allowed_tools` pre-approves; `permission_mode` (e.g. `acceptEdits`); deny/ask/allow control |
| **Sessions** | capture the session id (`SystemMessage` `init`), `resume` to continue with full context, **fork** to branch |
| **Filesystem config** | `.claude/skills/*/SKILL.md`, `.claude/commands/*.md`, `CLAUDE.md`, plugins — loaded from cwd + `~/.claude/` (restrict with `setting_sources`/`settingSources`) |

> **RavenClaude itself is the worked example** — this marketplace *is* a set of Agent SDK skills + agents + hooks + plugins. When designing a consumer's agent, point to the repo's own `plugins/*/` as a reference implementation.

## Agent SDK vs Client SDK vs Managed Agents
- **Client SDK** (Anthropic SDK): you implement the tool loop. Maximum control, most code.
- **Agent SDK:** Claude runs the loop in **your** process, on **your** files/infra; session state is JSONL on your filesystem; custom tools are in-process functions.
- **Managed Agents:** hosted REST API; Anthropic runs the agent **and** a per-session sandbox; session state is an Anthropic-hosted event log; you implement custom tools by returning results to Claude's tool calls. Best for production agents without operating sandbox/session infra, and long-running/async sessions. **Memory** is in public beta (`managed-agents-2026-04-01` header).

Common path: **prototype Agent SDK locally → Managed Agents for production** ([`claude-build-surface-decision-tree.md`](claude-build-surface-decision-tree.md)).

## Deployment / auth
API key (`ANTHROPIC_API_KEY`) or third-party providers: Bedrock (`CLAUDE_CODE_USE_BEDROCK=1`), Claude Platform on AWS, Vertex (`CLAUDE_CODE_USE_VERTEX=1`), Foundry (`CLAUDE_CODE_USE_FOUNDRY=1`). Do **not** offer claude.ai login / subscription rate limits to third-party end users — use API-key auth.

> **Billing note (dated 2026-05-28):** from **2026-06-15**, Agent SDK + `claude -p` on subscription plans draw from a separate monthly Agent SDK credit. Verify when scoping cost.

## When NOT to reach for the Agent SDK
A single classification/extraction call doesn't need an agent loop — use the **Messages API** ([`tool-use-and-structured-output.md`](tool-use-and-structured-output.md)). Reserve the SDK for genuinely agentic, multi-step, tool-using work.
