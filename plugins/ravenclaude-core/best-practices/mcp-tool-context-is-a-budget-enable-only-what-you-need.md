# MCP tool context is a budget — enable only what you need

**Status:** Pattern
**Domain:** Agent design / Context management / MCP

**Applies to:** `ravenclaude-core`

---

## Why this exists

Connecting an MCP server is not free, and the cost is paid **before you type
anything**. When a server is enabled, Claude Code preloads _every one of its
tools_ into the context window — the tool name, the description, and the **full
JSON schema** (parameters, types, constraints) for each. That text rides in the
window for the whole session whether or not you ever call the tool.

The mechanic is **count → cost**, and it compounds fast. A widely-shared
community measurement: **seven MCP servers consuming ≈67K tokens — roughly a
third of a 200K-token budget — spent on tool definitions alone, before the first
turn of actual work.** That is a third of the model's working memory gone to
capabilities it may never use this session, leaving less room for the files,
diffs, and reasoning the task actually needs (and pushing the harness toward
compaction sooner — see [`../knowledge/concepts/context-window.md`](../knowledge/concepts/context-window.md)).

The lesson isn't "MCP is bad" — MCP servers are how Claude Code reaches GitHub,
your database, your docs. The lesson is that **the set of enabled servers is a
budget you manage on purpose**, the same way you manage which files you pull into
context. Most of the cost is invisible (it's in the system prompt, not your
prompt), so it goes unmanaged unless you look.

## How to apply

**Enable only what the task needs.** Treat the enabled-server list like a
dependency list, not a junk drawer. A session doing a database migration needs
the Postgres server, not the Figma one. Turn servers off when they're not in
play (`claude mcp remove <name>` / re-add when needed, or toggle in `.mcp.json` /
the `/mcp` UI). The server you don't enable costs zero tokens.

**Prefer lazy-loading / tool-search over preloading.** The structural fix for the
preload tax is to _not_ load every schema up front — load a tool's full schema
only when it's about to be used. Claude Code's **Tool Search** does exactly this
(community reports ~40–50% fewer tool-definition tokens in real use), and it's
the mechanism behind the upstream "lazy-load MCP tool definitions" work
([`anthropics/claude-code#11364`](https://github.com/anthropics/claude-code/issues/11364)).
When a deferred/lazy tool surfaces, you search for it and load its schema on
demand instead of carrying all schemas all session.

**The worked example is this repo's own session model.** RavenClaude runs with a
large fleet of MCP servers available (github, Google-Drive, Microsoft-365,
Postman, …), yet they do **not** all sit in context at once: their tools are
**deferred** — surfaced by name only — and a tool's full schema is fetched with
`ToolSearch` _just before_ it's called. That is the count→cost tax paid down to
near zero by design: the capability is reachable, but the schema is only resident
while it's needed. (It's also why "the tool's schema isn't loaded yet" is a
_not-loaded_ signal, never an _absent-tool_ verdict — see
[`./read-the-error-before-you-reroute.md`](./read-the-error-before-you-reroute.md).)

**Measure it.** Run `/context` to see what's actually consuming the window —
tool definitions are a line item there. If the tool-definition share is large and
you're not using most of those servers, that's the cheapest context you'll ever
reclaim.

**Do:**

- **Right-size the enabled-server set per kind of work**, not once-and-forever.
- **Reach for tool-search / lazy-loading** before you reach for "just add another
  server," so the schema cost scales with _use_, not with _availability_.
- **Audit with `/context`** when a session feels cramped or compacts early — look
  at the tool-definitions line before blaming file reads.

**Don't:**

- **Don't leave every server you've ever configured enabled by default.** Each
  one is a standing tax on every session's budget, paid in capability you're not
  using right now.
- **Don't confuse "available" with "free."** An idle enabled server still costs
  its full schema set in tokens.

## Edge cases / when the rule does NOT apply

- **A genuinely tool-heavy session** (you really are orchestrating across GitHub +
  DB + browser + docs in one task) legitimately carries those schemas — the rule
  is "match enabled servers to the work," not "minimize for its own sake." The
  fix there is lazy-loading, not disabling the servers you actually need.
- **Hosts without tool-search / lazy-loading** can only use the coarse lever
  (enable/disable whole servers); the principle (budget the schemas) ports, the
  fine-grained mechanism may not.
- **The sibling budget on the _authoring_ side** is the agent-_description_ ~15K
  token budget ([`AGENTS.md`](../../../AGENTS.md) § "The agent-description token
  budget"): every _enabled plugin's_ agent `name`+`description` is preloaded for
  routing, the same count→cost shape one layer up. Enabling fewer plugins and
  capping descriptions is that budget's version of this rule.

## See also

- [`../knowledge/concepts/context-window.md`](../knowledge/concepts/context-window.md) — the parent concept: the window is finite, tool schemas ride in it, and it compacts when full. This rule is the MCP-specific, actionable corollary.
- [`./focused-task-delegation-beats-full-context-dumps.md`](./focused-task-delegation-beats-full-context-dumps.md) — the same desk-not-filing-cabinet discipline applied to what you hand a subagent; tool schemas are one more thing competing for the desk.
- [`./read-the-error-before-you-reroute.md`](./read-the-error-before-you-reroute.md) — why a not-yet-loaded deferred tool is a "search for it" signal, not an "it doesn't exist" verdict (the lazy-loading model in practice).

## Provenance

Distilled from a recurring Claude-community scan (the [2026-06-22 subreddit
scan](../../../docs/research/2026-06-22-claude-subreddit-scan/README.md)),
grounded against this repo's own deferred-MCP-via-`ToolSearch` session model and
Anthropic's [Manage context / costs](https://code.claude.com/docs/en/costs) and
[Context windows](https://docs.claude.com/en/docs/build-with-claude/context-windows)
docs, plus the upstream lazy-load signal
([`anthropics/claude-code#11364`](https://github.com/anthropics/claude-code/issues/11364)).
The ~67K-tokens-for-7-servers figure and the Tool Search reduction percentage are
community measurements (verify-at-use — the exact numbers move as Tool Search and
default tool budgets evolve); the **mechanic** (every enabled server preloads its
full schemas) is the durable, load-bearing part.

---

_Last reviewed: 2026-06-22 by `claude`_
