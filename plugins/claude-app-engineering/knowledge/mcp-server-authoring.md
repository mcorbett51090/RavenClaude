# MCP server authoring

**Last reviewed:** 2026-08-05 · **Confidence:** high ([modelcontextprotocol.io](https://modelcontextprotocol.io), [Agent SDK MCP](https://code.claude.com/docs/en/agent-sdk/mcp), retrieved 2026-05-28; **2026-07-28 spec note added, retrieved 2026-08-05**).
**Owner:** `mcp-and-server-tools-engineer`.

## What MCP is
The **Model Context Protocol** is an open standard (JSON-RPC) for connecting Claude (and other clients) to external systems. A **server** exposes capabilities; a **client** (Claude Code, the Agent SDK, Claude Desktop, your app) consumes them.

> **⚠️ Spec update — the 2026-07-28 revision makes MCP stateless (forward-looking; verify against YOUR client/SDK version).** The [2026-07-28 specification](https://modelcontextprotocol.io/specification/2026-07-28) ([announcement](https://blog.modelcontextprotocol.io/posts/2026-07-28/), retrieved 2026-08-05) is a **protocol-level rewrite** — the most substantial change since authorization:
> - **Stateless core.** The `Mcp-Session-Id` header and the `initialize`/`initialized` handshake are **removed**; each request now carries its protocol version, client identity, and client capabilities in `_meta`, so any request can land on any server instance behind an ordinary load balancer.
> - **Multi Round-Trip Requests (MRTR)** replace server-initiated requests that needed a held-open stream: when a tool needs mid-call input, the server returns `resultType: "input_required"` and the client **retries the original call** with the answers in `inputResponses`.
> - **Extensions framework.** **Tasks** (long-running operations) moved out of core into the `io.modelcontextprotocol/tasks` extension, joining **MCP Apps** (a server ships interactive HTML the host renders in a sandboxed iframe) and **Enterprise Managed Authorization**.
> - Also: header-based routing (`Mcp-Method`/`Mcp-Name`), cacheable `tools/list`/`prompts/list`/`resources/list` (`ttlMs`/`cacheScope`), and auth hardening (RFC 9207 issuer validation; Dynamic Client Registration → Client ID Metadata Documents).
>
> **What to do now:** this is *spec published, SDKs/clients still catching up* — **author against the version your client/SDK negotiates** (Claude Code and the Agent SDK MCP client target the pre-stateless model until they adopt the revision). A **12-month minimum deprecation window** covers **Roots, Sampling, and the legacy HTTP+SSE transport**, so the capabilities and transports below stay valid for your negotiated version — but some cross-version changes are **not** backward-compatible, so verify the client/SDK support before relying on either the old or the new shape. `[verify-at-use — spec 2026-07-28; per-client/SDK adoption varies; deprecation-window dates are moving targets]`

## Capabilities a server can expose
| Capability | What it is |
|---|---|
| **Tools** | callable functions (the most common) — like Messages-API tools but reusable across any MCP client |
| **Resources** | readable data/context the client can fetch (files, records, docs) |
| **Prompts** | reusable prompt templates the user can invoke |
| **Sampling** | the server asks the *client* to run a model completion (server-initiated LLM calls) — *on the 12-month deprecation window per the 2026-07-28 stateless spec; verify your client's negotiated version `[verify-at-use]`* |
| **Roots** | the client tells the server which filesystem/URI roots are in scope — *on the 12-month deprecation window per the 2026-07-28 stateless spec; verify your client's negotiated version `[verify-at-use]`* |
| **Elicitation** | the server asks the client to collect structured input from the user |

## Transports
- **stdio** — local subprocess (the default for local servers; the Agent SDK launches it via `command`/`args`).
- **SSE** — server-sent events over HTTP (legacy remote; **on the 12-month deprecation clock per the 2026-07-28 spec** — see the spec note above).
- **Streamable HTTP** — the current remote transport; supports auth + horizontal scaling. (The **2026-07-28 revision makes the protocol layer stateless** — requests carry identity/version/capabilities in `_meta` instead of a session; see the spec note above. Verify your client/SDK's negotiated version.)

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
