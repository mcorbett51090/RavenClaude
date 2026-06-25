# Claude Code / Anthropic harness — current (2026) facts agents rely on

> Reference sheet of current Claude Code, Claude Agent SDK, and MCP-spec facts that downstream agents treat as load-bearing. Each fact carries a primary-source link with its **retrieved 2026-06-25** date. **Refresh when:** Anthropic ships a new MCP spec revision, renames an SDK package again, changes the sandbox schema, or alters the hooks event/blocking model. Companion to [`claude-code-permissions.md`](claude-code-permissions.md) (the permission/hook deep-dive).

---

## MCP spec 2025-11-25 is the current stable revision

The Model Context Protocol's current stable specification revision is **2025-11-25**, superseding **2025-06-18**. What this revision establishes / adds:

- **JSON Schema 2020-12 is the default dialect.** Tool/resource/prompt schemas are interpreted as JSON Schema draft 2020-12 unless a server declares otherwise. This is the dialect Claude Code's tool definitions and MCP server schemas align to.
- **Elicitation default values** — an elicitation request may carry default values for the fields it asks the user to fill.
- **Titled single-select and multi-select enums** — enum schemas can attach human-readable titles to each option (the basis for the titled single/multi-select prompts a host renders).
- **Tool / resource / prompt icons** — tools, resources, and prompts may declare icons for richer host UIs.
- **Experimental durable tasks** — a task abstraction for long-running / resumable work (marked experimental in this revision).

Source: [MCP specification 2025-11-25 changelog — modelcontextprotocol.io](https://modelcontextprotocol.io/specification/2025-11-25/changelog) (retrieved 2026-06-25).

## The Claude Code SDK is now the Claude Agent SDK (renamed Sept 2025)

The SDK formerly published as the "Claude Code SDK" was **renamed to the Claude Agent SDK** in September 2025. The migration touches both package ecosystems:

| | Old | New |
| --- | --- | --- |
| **Python import** | `claude_code_sdk` | `claude_agent_sdk` |
| **npm package** | `@anthropic-ai/claude-code` | `@anthropic-ai/claude-agent-sdk` |

Beyond the rename, the Agent SDK adds **subagents**, **lifecycle hooks**, and **Skills** as first-class capabilities. Code importing the old package names will not resolve against the new package — update both the import path (Python) and the dependency name (npm) when migrating.

Source: [Claude Agent SDK migration guide — platform.claude.com](https://platform.claude.com/docs/en/agent-sdk/migration-guide) (retrieved 2026-06-25).

## Claude Code's OS-level Bash sandbox (the `sandbox` settings block)

Claude Code can run Bash inside an **OS-level sandbox** configured via a top-level `sandbox` block in `settings.json`. This is a **permission-reduction mechanism distinct from the allow / ask / deny rules** — it constrains what a sandboxed command can do at the operating-system level, where the permission rules only gate the agent's own tool calls (and cannot bound a subprocess — see [`claude-code-permissions.md`](claude-code-permissions.md) §"Read/Edit rules do not protect against subprocess access").

Documented keys:

- `sandbox.enabled` — turn the sandbox on.
- `sandbox.failIfUnavailable` — fail (rather than silently fall back to unsandboxed) if the OS sandbox can't be established on this host.
- `sandbox.autoAllowBashIfSandboxed` — auto-allow Bash calls *because* they run inside the sandbox (the containment substitutes for the prompt).
- `sandbox.filesystem.allowWrite` / `sandbox.filesystem.denyRead` — filesystem write-allow and read-deny scoping for sandboxed commands.
- `sandbox.network.allowedDomains` — restrict the network egress a sandboxed command may reach.
- `sandbox.credentials` (added **2026-06-23**) — blocks sandboxed commands from reading secrets/credentials.

Source: [Sandboxing — code.claude.com/docs/en/sandboxing](https://code.claude.com/docs/en/sandboxing) (retrieved 2026-06-25).

## PreCompact hooks are now blockable; a SessionEnd-on-resume fix

Two hook-model facts current as of this revision:

- **PreCompact hooks can now block compaction.** A `PreCompact` hook may block by returning **exit code 2** or a `{"decision": "block"}` JSON output — the same blocking shape the other gating events use. Previously PreCompact could only observe / annotate.
- **SessionEnd-on-resume fix.** A fix addressed `SessionEnd` hooks **not firing** when switching sessions via an interactive `/resume`. SessionEnd now fires on that interactive session switch.

Source: [Hooks reference — code.claude.com/docs/en/hooks](https://code.claude.com/docs/en/hooks) (retrieved 2026-06-25).

## Citations

- [MCP specification 2025-11-25 changelog — modelcontextprotocol.io](https://modelcontextprotocol.io/specification/2025-11-25/changelog) — primary source for the current stable MCP revision, JSON Schema 2020-12 default, elicitation defaults, titled enums, icons, durable tasks. Retrieved 2026-06-25.
- [Claude Agent SDK migration guide — platform.claude.com](https://platform.claude.com/docs/en/agent-sdk/migration-guide) — primary source for the SDK rename, Python/npm package names, and the subagents/hooks/Skills additions. Retrieved 2026-06-25.
- [Sandboxing — code.claude.com/docs/en/sandboxing](https://code.claude.com/docs/en/sandboxing) — primary source for the `sandbox` settings block, its keys, and the 2026-06-23 `sandbox.credentials` addition. Retrieved 2026-06-25.
- [Hooks reference — code.claude.com/docs/en/hooks](https://code.claude.com/docs/en/hooks) — primary source for blockable PreCompact hooks and the SessionEnd-on-resume fix. Retrieved 2026-06-25.
