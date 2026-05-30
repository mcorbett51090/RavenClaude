# MCP for reuse, an in-process tool for a one-off

**Status:** Pattern — strong default; standing up an MCP server for one app's one function is the named anti-pattern (#12).

**Domain:** Tool use / MCP

**Applies to:** `claude-app-engineering`

---

## Why this exists

A capability Claude can call lives in one of two homes, and picking the wrong one costs either reuse or needless operational weight. An **in-process tool** (a Messages-API tool or an Agent SDK custom tool) is a function in your app's process — fastest to ship, tightly coupled to your app's state, invisible to anything else. An **MCP server** is its own process/service exposing the capability over a protocol — reusable across apps, agents, and clients (Claude Desktop, Claude Code, your app interchangeably), but it's a service you now author, deploy, secure, and version. House opinion #12: build the MCP server when the capability is **genuinely reused across clients**; build the in-process tool when it's app-specific or a one-off. The recurring waste is reaching for MCP's reuse machinery for a function exactly one app will ever call.

## How to apply

Decide by the reuse question first, then the coupling question. If neither pushes you to a server, it's an in-process tool.

```python
# In-process (Agent SDK custom tool) — app-specific, coupled to app state, one-off:
@tool("price_cart", "Total the current user's cart with tax.", {"cart_id": str})
async def price_cart(args):
    return {"content": [{"type": "text", "text": str(_price(args["cart_id"]))}]}

# MCP server — reused across apps/agents/clients, its own process/auth:
#   exposed via Streamable HTTP, consumed by ANY client:
options = ClaudeAgentOptions(
    mcp_servers={"billing": {"type": "http", "url": "https://billing.internal/mcp",
                             "headers": {"Authorization": f"Bearer {token}"}}}
)
# Litmus: "will a second client ever call this?" No -> in-process. Yes -> MCP server.
```

**Do:**
- Build an **MCP server** when the capability is reused across apps/agents/clients, runs as its own service, or you want it usable from Claude Desktop / Claude Code / your app interchangeably.
- Build an **in-process tool** when it's app-specific, tightly coupled to your app's state, or a one-off — ship the function, skip the service.
- Apply the **same contract discipline** either way — name + description-as-prompt + typed schema ([`tools-design-as-a-contract.md`](./tools-design-as-a-contract.md)); the home differs, the contract doesn't.
- When you *do* author a server, keep it narrow and idempotent ([`mcp-author-the-narrow-server.md`](./mcp-author-the-narrow-server.md)).

**Don't:**
- Stand up an MCP server for a single app's single function — the named anti-pattern (#12); the deploy/auth/version overhead buys nothing.
- Couple an MCP server to one app's in-memory state — if it can't run as an independent process, it's an in-process tool.
- Re-implement the same capability as both an in-process tool *and* a server "to be safe" — pick the home, then reuse it.

## Edge cases / when the rule does NOT apply

- **A second consumer arrives later** — promote an in-process tool to an MCP server then, not preemptively; keep the tool logic portable so the move is a lift, not a rewrite.
- **Anthropic-hosted server tools** (computer use, code execution, web search/fetch, Files API, memory) are a third category — neither MCP nor your in-process tool; you request them via the Messages API ([`../knowledge/server-side-tools-and-files.md`](../knowledge/server-side-tools-and-files.md)).
- **The capability is prompt-only** (no external call needed at all) — neither home applies; it's a prompt, not a tool ([`prompt-climb-the-leverage-ladder.md`](./prompt-climb-the-leverage-ladder.md)).
- **Auth/sandboxing of a remote server** is a security design — route it to `ravenclaude-core/security-reviewer`.

## See also

- [`../knowledge/mcp-server-authoring.md`](../knowledge/mcp-server-authoring.md) — MCP capabilities, transports, the MCP-vs-tool decision (house opinion #12)
- [`./mcp-author-the-narrow-server.md`](./mcp-author-the-narrow-server.md) — how to author the server once you've decided to
- [`./tools-design-as-a-contract.md`](./tools-design-as-a-contract.md) — the contract discipline both homes share
- [`../agents/mcp-and-server-tools-engineer.md`](../agents/mcp-and-server-tools-engineer.md) — owns the MCP decision

## Provenance

Codifies house opinion #12 from [`../CLAUDE.md`](../CLAUDE.md) §3 ("MCP for reuse, in-process tools for one-offs") and the §4 anti-pattern ("standing up an MCP server for one app's one function"). Grounded in [`../knowledge/mcp-server-authoring.md`](../knowledge/mcp-server-authoring.md) (modelcontextprotocol.io + Agent SDK MCP docs, retrieved 2026-05-28).

---

_Last reviewed: 2026-05-30 by `claude`_
