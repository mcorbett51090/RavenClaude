# MCP tool definitions cost context every turn — enable only the servers you need

**Status:** Pattern
**Domain:** Context management / Tooling / MCP
**Applies to:** `ravenclaude-core`

---

## Why this exists

Every connected MCP server loads its **tool definitions** — names, descriptions, and JSON
input schemas for each tool — into the model's context, and they ride along on **every turn**,
not once at startup. A handful of heavy servers can silently consume a large, fixed slice of
the context window before the agent has read a single file. Community reports put a heavy
server's overhead in the **thousands-of-tokens-per-turn** range (one widely-cited figure is
"up to ~18K tokens per turn" for a large server) — `[unverified — community-reported; verify
against your own session with /context]`. The durable, verifiable fact is the **shape**, not
the exact number: tool definitions are per-turn context, they scale with the number of
connected servers/tools, and they are charged whether or not the agent uses the tool.

The cost is two-sided and both sides degrade quality:

1. **Window pressure.** Tokens spent on unused tool definitions are tokens unavailable for the
   actual task, and they push the session toward compaction sooner.
2. **Routing noise.** A larger tool surface is a larger menu the model must disambiguate every
   turn; rarely-used and overlapping tools raise the chance of a wrong or unnecessary tool call.

This is the **exact mirror of this marketplace's own agent-description budget** ([`AGENTS.md`](../../../AGENTS.md)
§"The agent-description token budget (~15K)"): Claude Code loads every *enabled* plugin's agent
`name`+`description` into the orchestrator prompt, and the documented response to crossing the
budget is **"enable only what you need; disable the rest via `/agents`."** The same discipline
applies one layer down, to MCP tool definitions — RavenClaude already *lives* this rule for
agent descriptions; this states it for the tool layer.

## How to apply

- **Connect servers per task, not per "might-need-it."** Enable the MCP servers a session
  actually requires and leave the rest off. A standing always-on set of every server you've ever
  used is the anti-pattern — it taxes every turn of every unrelated session.
- **Measure the overhead.** Run **`/context`** to see how much of the window the connected tool
  definitions occupy before you start work. If servers dominate the budget, that's the signal to
  prune — don't guess the number, read it.
- **Prefer the narrowest surface that does the job.** Between a broad server and a focused one
  that exposes only the verbs you need, prefer the focused one; some servers/hosts let you scope
  which tools load — use that scoping.
- **Audit periodically, the same way you audit agent descriptions.** When the context feels
  tight or the agent starts mis-routing tool calls, the connected-server set is a first place to
  look, alongside the conversation history.

## Edge cases / when the rule does NOT apply

- **A server you use every turn earns its place.** This is a prune-the-*unused* rule, not a
  minimize-at-all-costs rule — a server whose tools are central to the task is paying its way.
- **Bundled-vs-connected is a different question.** *Whether to ship a server with a plugin* is
  governed by [`docs/best-practices/bundled-mcp-servers.md`](../../../docs/best-practices/bundled-mcp-servers.md)
  (recommend-and-evaluate, never auto-bundle). This rule is about *how many servers a consumer
  connects at once* in their own session — the runtime budget, not the packaging decision.
- **Security still leads.** Pruning for budget never overrides the security posture: an
  untrusted or unneeded server should be disconnected for *both* reasons. Trust scoping is the
  primary filter; budget is the secondary one.

## See also

- [`./focused-task-delegation-beats-full-context-dumps.md`](./focused-task-delegation-beats-full-context-dumps.md)
  — the same context-budget discipline applied to sub-agent briefs (don't forward the full
  history); this rule applies it to the connected tool surface.
- [`./permissions-are-deny-ask-allow-not-an-on-off-switch.md`](./permissions-are-deny-ask-allow-not-an-on-off-switch.md)
  — `mcp_tools` is a permission category too; deny the servers you don't trust, prune the ones
  you don't need.
- [`AGENTS.md`](../../../AGENTS.md) §"The agent-description token budget (~15K)" — the
  parent budget this rule mirrors one layer down.
- [`docs/best-practices/bundled-mcp-servers.md`](../../../docs/best-practices/bundled-mcp-servers.md)
  — the packaging-side companion (ship vs. recommend a server).

## Provenance

Surfaced by the [2026-06-17 Claude subreddit scan](../../../docs/research/2026-06-17-claude-subreddit-scan/README.md)
(community reports + practitioner write-ups on MCP context overhead, cross-checked against the
Anthropic Claude Code security/MCP docs and this repo's own `AGENTS.md` budget discipline). The
per-turn-tool-definition mechanism is grounded; the specific ~18K figure is community-reported
and marked unverified — `/context` is the this-session check. Net-new vs. the existing best-practices:
no rule covered the MCP-tool-definition runtime budget (the closest neighbors cover sub-agent
context, the permission taxonomy, and server *packaging*).

---

_Last reviewed: 2026-06-17 by `claude`_
