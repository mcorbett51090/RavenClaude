# MCP tool definitions are a context budget — defer or disable, don't connect-and-forget

**Status:** Pattern
**Domain:** Agent design / Context management / MCP

---

## Why this exists

Connecting an MCP server is not free, and the cost lands *before the first
message*. Every connected server loads **all** of its tool definitions
(name + description + JSON schema for every tool) into the model's context
window at session start, as part of the system prompt. With a handful of
chatty servers this is not a rounding error — community measurements in 2026
put a 7-server setup at **~67K tokens of tool definitions, ~34% of a 200K
window, consumed before any conversation begins** (one report hit 66K+ just
loading tools). That budget is gone for the whole session: less room for the
actual code, the files read, and the reasoning — and on long sessions it pulls
auto-compaction forward, which is its own degradation.

The trap is that the cost is **invisible**: nothing prompts you when you add
the eighth server, and a server you used once three weeks ago is still taxing
every session since. "Connect it in case I need it" is the anti-pattern — the
default posture should be the opposite.

This is a **different budget from the agent-description budget**
(the marketplace's ~15K-token cap on subagent `name` + `description`, which
governs orchestrator *routing*). This rule is about **MCP tool definitions
eating the conversation's context window**. They compound — both are paid at
session start — but the levers are different, so don't conflate them.

## How to apply

Treat connected MCP servers as a budget you actively manage, cheapest lever
first:

1. **Defer tool definitions (the biggest single win, often the default now).**
   Modern Claude Code ships **Tool Search**: at session start only tool
   *names* + server instructions load; the full definitions are fetched lazily
   the first time the model actually needs a tool. Community measurements show
   this cutting MCP context ~47% (one report: 51K → 8.5K tokens). For remote
   MCP connectors the equivalent knob is `defer_loading: true`. **If your host
   supports deferral, prefer it** — you keep the capability without paying for
   it up front. (This repo lives the pattern: its MCP tools surface as
   deferred/name-only and are loaded on demand via `ToolSearch` — see the root
   `CLAUDE.md` "MCP tools are deferred + lazy-loaded" note.)
2. **Enable only the servers this session needs.** The bluntest, most reliable
   lever: don't connect a server you aren't using today. A per-session
   enable/disable habit (or a small toggle tool) beats a permanently-mounted
   wall of servers. A server's tools cost the same whether you call them or
   not.
3. **Prune chatty servers.** A single server can expose dozens of tools; if you
   only use two of them, that's the server to scrutinize. Fewer, sharper
   servers cost less context *and* reduce the chance of hitting the host's
   tool-count limit (which forces the model to pick among too many options).

**Do:**

- **Audit the startup tax periodically.** When sessions feel sluggish or
  compact early, count what's loaded before you blame the task — the tool
  surface is a prime suspect.
- **Default to deferral / minimal-connect, opt into more.** The safe posture is
  "few servers, deferred"; reach for "many, eager" only with a reason.

**Don't:**

- **Don't connect-and-forget.** A server mounted "just in case" is a standing
  tax on every future session, paid in the context you most want for the work.
- **Don't confuse this with the agent-description budget.** Tightening a
  subagent's `description` does nothing for MCP tool-definition bloat, and
  deferring MCP tools does nothing for the orchestrator's routing budget. They
  are two separate levers on two separate budgets.

## Edge cases / when the rule does NOT apply

- **A server whose tools you genuinely use every session** is correctly
  always-on — the rule targets the *unused* and the *forgotten*, not the
  load-bearing. Deferral still helps even there (names-only at start).
- **Hosts without deferral / Tool Search** (older Claude Code, some non-Claude
  CLIs) can't lazy-load — there the only lever is lever 2 (connect fewer) and
  lever 3 (prune). The *principle* ports; the deferral mechanism may not.
- **Headless / CI runs** (`claude -p`) should already run a minimal tool
  surface for cost and blast-radius reasons (see the permission-posture rule's
  CI edge case) — there, "few servers" is doubly motivated.

## See also

- [`./permissions-are-deny-ask-allow-not-an-on-off-switch.md`](./permissions-are-deny-ask-allow-not-an-on-off-switch.md) — the other "manage your tool surface deliberately" rule; permissions govern *what a tool may do*, this governs *what a tool costs to have loaded*.
- [`./focused-task-delegation-beats-full-context-dumps.md`](./focused-task-delegation-beats-full-context-dumps.md) — the same context-frugality instinct applied to delegation briefs rather than tool definitions.
- The root [`CLAUDE.md`](../../../CLAUDE.md) § "MCP tools are deferred + lazy-loaded" — the operational corollary: a deferred tool shows name-only until `ToolSearch` loads its schema, so a missing schema is "not loaded yet," never "absent."

## Provenance

Distilled from a recurring Claude-community scan (the [2026-06-18 subreddit
scan](../../../docs/research/2026-06-18-claude-subreddit-scan/README.md)),
cross-checked against the Anthropic [Connect Claude Code to tools via MCP](https://code.claude.com/docs/en/mcp)
doc and the [Context windows](https://platform.claude.com/docs/en/build-with-claude/context-windows)
reference. The token figures (~67K for 7 servers; ~47% reduction via Tool
Search) are 2026 community measurements `[unverified — community
benchmarks]`, cited as order-of-magnitude evidence that the cost is material,
not as exact guarantees. This repo's own deferred-MCP / `ToolSearch`
architecture is the worked example of lever 1.

---

_Last reviewed: 2026-06-18 by `claude`_
