# Third-party content notice — `microsoft-365-copilot` plugin

The `agents/`, `knowledge/`, `skills/`, `templates/`, `best-practices/`, `scenarios/`, and `CLAUDE.md` content in this plugin is original work by Matt Corbett, released under MIT. The knowledge bank is grounded in (and cites) public Microsoft Learn documentation; no Microsoft documentation text is vendored into the tree — only cited by URL.

---

## Bundled MCP server

This plugin's `plugin.json` declares the following Model Context Protocol (MCP) server, which Claude Code connects to automatically when the plugin is installed:

### `microsoft-learn` — Microsoft Learn MCP Server (first-party Microsoft, MIT tooling)

**Source / tooling repo:** [`MicrosoftDocs/mcp`](https://github.com/MicrosoftDocs/mcp)
**Endpoint:** `https://learn.microsoft.com/api/mcp` (remote, HTTP transport)
**Party:** third-party (Microsoft — first-party *to the documentation*, third-party *to this marketplace*; the open-source CLI/tooling is MIT)
**What it does:** Brings official, up-to-date Microsoft Learn documentation and code samples into the agent's context via three read-only tools — `microsoft_docs_search` (semantic search over Learn docs), `microsoft_code_sample_search` (official code samples), and `microsoft_docs_fetch` (fetch a full Learn page as markdown).

**Read-only / read-write:** **read-only.** It searches and fetches *public* Microsoft documentation. It does **not** read your tenant, your files, your code, or any user/profile data, and it writes nothing.

**Why it clears the bundling bar** (per [`docs/best-practices/bundled-mcp-servers.md`](../../docs/best-practices/bundled-mcp-servers.md)):

- **Zero-config / no per-consumer state** — a fixed public endpoint; no tenant URL, no allowed-directory path, no per-consumer parameter.
- **No authentication / no secrets** — the endpoint requires no auth, so there is no credential to bundle, reference, or leak. (Contrast the Microsoft MCP Server for Enterprise / Microsoft Graph MCP, which *is* per-tenant + Entra-authenticated → recommend-not-bundle; see CLAUDE.md §11a.)
- **Read-only** — search + fetch over public docs only; it does not interact with the consumer's tenant, the local Gate 25 `mcp.allowed_servers` allowlist concern (write verbs) does not apply.
- **First-party documentation source** — the most fitting grounding companion for a plugin whose #1 risk is the monthly-velocity Copilot surface (manifest schema, connector behavior, plugin-auth schemes). It lets agents verify a volatile fact against current Learn docs instead of recalling a possibly-stale schema from training.

**Consumer prerequisite — none.** Because it is a remote HTTP endpoint with no auth, there is **nothing to install**. If the network can't reach `learn.microsoft.com`, the server shows as `failed` in `/mcp` and the error surfaces in the `/plugin` Errors tab; Claude Code and every other tool still work (**loud-but-non-fatal**). **If the Learn tools aren't responding, check `/mcp` and the `/plugin` Errors tab first** — the usual cause is no network egress to `learn.microsoft.com`, not a broken server. There is no local subprocess and therefore no PATH/`python -m` fallback to configure (the contrast with a local stdio server like `pbix-mcp`).

**Override (consumer-side, if needed).** To register it via the CLI instead of the bundled declaration (e.g. to scope it to a different project), the documented command is:

```bash
claude mcp add --transport http microsoft-learn https://learn.microsoft.com/api/mcp
```

(`[verify-at-use]` — Claude Code MCP transport flags and the Learn endpoint are version-volatile; re-confirm against the Claude Code MCP docs and the Microsoft Learn MCP overview before relying on them.)

**License attribution** — the Microsoft Learn MCP open-source tooling/CLI is MIT-licensed; see the upstream LICENSE at [`MicrosoftDocs/mcp`](https://github.com/MicrosoftDocs/mcp). The documentation content served by the endpoint is Microsoft's, governed by the Microsoft Learn terms of use, not redistributed by this plugin.
