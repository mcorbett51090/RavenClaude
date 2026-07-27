# Build a capability as CLI + Skill first — reach for MCP only when the state lives in someone else's running system

**Status:** Pattern
**Domain:** Agent design / Integration selection / MCP · Skills

**Applies to:** `ravenclaude-core` (and any plugin author deciding how to add a new capability)

---

## Why this exists

When you want to give an agent a new capability — call an API, run a
report, touch a service — the reflex in 2026 is "stand up an MCP server."
That reflex is often the more expensive answer to the cheaper question. There
is a design-time choice _before_ the runtime one, and it has a clean
discriminator:

- A **Skill** answers **"how do we do X _here_?"** — a repeatable procedure,
  a methodology, a wrapper around a CLI or script. It is knowledge + steps,
  and it costs **~30–50 tokens** of context until it is invoked.
- An **MCP server** answers **"what is true right now _over there_?"** — it
  connects the agent to **live state inside someone else's running system**
  (an open GitHub, a database mid-transaction, a browser session, a ticketing
  backend). Every enabled server preloads its full tool schemas into the
  window for the whole session (the `count → cost` tax — see
  [`./mcp-tool-context-is-a-budget-enable-only-what-you-need.md`](./mcp-tool-context-is-a-budget-enable-only-what-you-need.md)).

The practitioner consensus that hardened through 2026 is: **build everything
you can as CLI + Skill first, and reach for MCP only when the useful state
genuinely lives inside another running system.** Modern models write and run
code reliably, so a thin CLI the agent invokes — open source, read `stderr`,
edit, retry — is a native loop that a Skill can orchestrate without paying the
standing schema tax. Teams routinely run **many Skills and few MCP servers**
for exactly this reason.

This is the **upstream** complement to the MCP-budget rule. That rule prunes
the servers you have **already** enabled; this rule governs whether a new
capability should become a server **at all**. Get this choice right and the
budget problem mostly doesn't arise.

## How to apply

Ask the discriminator question about the capability you're adding:

| The capability is really… | Build it as… | Why |
| --- | --- | --- |
| A repeatable procedure / methodology ("how we lint here", "how we cut a release") | **Skill** (optionally wrapping a CLI/script) | Knowledge that loads on demand; no standing token cost |
| A stateless call the agent could just script (hit a REST endpoint, transform a file, run a report) | **CLI + Skill** | The agent writes/runs code natively; a Skill names the steps and gotchas |
| Access to **live, changing state in an external running system** (GitHub PRs, a live DB, a browser, Sentry/Linear) | **MCP server** | Only MCP gives the agent a live window into another system's current truth |

**Do:**

- **Default to CLI + Skill for anything you can express as "run this, read the
  output, act on it."** Wrap the CLI in a Skill so the _procedure_ and its
  gotchas are captured (see
  [`./a-skills-body-is-the-gotchas-the-model-doesnt-know-not-the-happy-path.md`](./a-skills-body-is-the-gotchas-the-model-doesnt-know-not-the-happy-path.md)).
- **Reach for MCP when — and only when — the agent needs a live view of state
  that lives in another running system**, not a script it could run itself.
- **When you do add an MCP server, keep it thin and pinned** (one server per
  external system) and let Skills orchestrate it. MCP for connectivity, Skills
  for methodology — most real setups use both, weighted heavily toward Skills.

**Don't:**

- **Don't stand up an MCP server for a job a CLI already does.** You pay the
  full schema tax every session for a capability a Skill + one shell command
  would deliver for ~30–50 tokens.
- **Don't push a live-state need into a Skill.** A Skill encodes _how_; it
  cannot tell the agent _what is true over there right now_. That is precisely
  where MCP earns its cost.

## Edge cases / when the rule does NOT apply

- **Genuinely live external state is the MCP case, full stop.** GitHub PR
  status, a database you're mid-migration on, a live browser, an incident
  backend — a script that snapshots them goes stale the instant it returns.
  The rule is "CLI + Skill _first_," not "never MCP."
- **This marketplace ships both.** `ravenclaude-core` bundles MCP servers
  _and_ ~48 skills, and the [`mcp-builder`](../skills/) skill exists for when
  MCP _is_ the right answer — so "which mechanism" is a live authoring
  decision here, not a hypothetical. This rule is the tie-breaker, not a ban.
- **Token figures are directional.** The ~30–50-tokens-per-Skill and
  many-Skills-few-servers shapes are community measurements that move as the
  harness evolves (`verify-at-use`); the **discriminator** — Skill = "how here"
  vs. MCP = "what's true over there" — is the durable, load-bearing part.
- **Non-Claude hosts** (GitHub Copilot CLI, Cursor, Codex) have their own
  skill/MCP surfaces; the _principle_ ports, the exact packaging does not.

## See also

- [`./mcp-tool-context-is-a-budget-enable-only-what-you-need.md`](./mcp-tool-context-is-a-budget-enable-only-what-you-need.md) — the **runtime** sibling: this rule decides whether to add a server; that one prunes the servers you already enabled.
- [`./keep-skill-bodies-lean-let-progressive-disclosure-carry-the-detail.md`](./keep-skill-bodies-lean-let-progressive-disclosure-carry-the-detail.md) — once you've chosen a Skill, keep its body lean.
- [`./scope-a-skill-to-one-workflow-the-description-is-what-triggers-it.md`](./scope-a-skill-to-one-workflow-the-description-is-what-triggers-it.md) — scope the Skill so it triggers reliably.
- [`../knowledge/concepts/context-window.md`](../knowledge/concepts/context-window.md) — the finite window both mechanisms compete for.

## Provenance

Distilled from the recurring Claude-community scan (the
[2026-07-21 subreddit scan](../../../docs/research/2026-07-21-claude-subreddit-scan/README.md)).
Reddit's first-party listings were unreachable this session (the OAuth2
`scripts/reddit-scan.py` route `_die`s without `REDDIT_CLIENT_ID`/`SECRET`,
and the crawler is UA-blocked from `reddit.com`), so the finding was sourced
from practitioner write-ups and Reddit-discussion aggregations via
unrestricted web search — the "Skill = how do we do X here / MCP = what is
true right now over there" discriminator and the "build CLI + Skill first,
reach for MCP only when the state lives in someone else's running system"
heuristic recur across independent 2026 practitioner guides (jngiam;
Verdent; the DEV Community "Skills vs MCP" write-ups; morphllm). Grounded
against this repo's own surface: the runtime
[`mcp-tool-context-is-a-budget`](./mcp-tool-context-is-a-budget-enable-only-what-you-need.md)
rule (the `count → cost` schema tax it complements) and the deferred-MCP-via-`ToolSearch`
session model. Token figures are `verify-at-use`; the discriminator is the
durable part.

---

_Last reviewed: 2026-07-21 by `claude` (automated subreddit scan)_
