# MCP server authoring

**Last reviewed:** 2026-05-28 · **Confidence:** high ([modelcontextprotocol.io](https://modelcontextprotocol.io), [Agent SDK MCP](https://code.claude.com/docs/en/agent-sdk/mcp), retrieved 2026-05-28).
**Owner:** `mcp-and-server-tools-engineer`.

## What MCP is
The **Model Context Protocol** is an open standard (JSON-RPC) for connecting Claude (and other clients) to external systems. A **server** exposes capabilities; a **client** (Claude Code, the Agent SDK, Claude Desktop, your app) consumes them.

## Capabilities a server can expose
| Capability | What it is |
|---|---|
| **Tools** | callable functions (the most common) — like Messages-API tools but reusable across any MCP client |
| **Resources** | readable data/context the client can fetch (files, records, docs) |
| **Prompts** | reusable prompt templates the user can invoke |
| **Sampling** | the server asks the *client* to run a model completion (server-initiated LLM calls) |
| **Roots** | the client tells the server which filesystem/URI roots are in scope |
| **Elicitation** | the server asks the client to collect structured input from the user |

## Transports
- **stdio** — local subprocess (the default for local servers; the Agent SDK launches it via `command`/`args`).
- **SSE** — server-sent events over HTTP (legacy remote).
- **Streamable HTTP** — the current remote transport; supports auth + horizontal scaling.

## Connecting from the Agent SDK
```python
options=ClaudeAgentOptions(
    mcp_servers={"playwright": {"command": "npx", "args": ["@playwright/mcp@latest"]}}
)
```
Remote servers add a URL + auth (OAuth-style for Streamable HTTP). Hundreds of community servers exist ([servers repo](https://github.com/modelcontextprotocol/servers)).

## MCP server vs in-process tool (house opinion #12 — the recurring decision)
- **Build an MCP server** when the capability is **reused across apps/agents/clients**, runs as its own process/service, or you want it usable from Claude Desktop / Claude Code / your app interchangeably.
- **Build an in-process tool** (Messages-API tool or an Agent SDK custom tool) when it's **app-specific**, tightly coupled to your app's state, or a one-off. Don't stand up an MCP server for a single app's single function.

## Security (escalate to core/security-reviewer)
A remote MCP server is an attack surface: authenticate every request, honor the client's roots (don't read outside scope), validate/parameterize all inputs, and treat tool arguments as untrusted. Server responses are untrusted content downstream (injection) — see [`tool-use-and-structured-output.md`](tool-use-and-structured-output.md). Route the auth + sandboxing design to `ravenclaude-core/security-reviewer`. Never ship secrets in the server's source ([`claude-app-finops-reliability-and-security.md`](claude-app-finops-reliability-and-security.md)).

## Note
For **Anthropic-hosted server tools** (computer use, code execution, web search/fetch, the Files API, the memory tool) — distinct from MCP — see [`server-side-tools-and-files.md`](server-side-tools-and-files.md).
