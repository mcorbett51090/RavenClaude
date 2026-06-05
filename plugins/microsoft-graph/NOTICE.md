# Third-party content notice — `microsoft-graph` plugin

The `agents/`, `knowledge/`, `skills/`, `templates/`, `best-practices/`, `scenarios/`, `scripts/`, `hooks/`, `commands/`, and `CLAUDE.md` content in this plugin is original work by Matt Corbett, released under MIT. The knowledge bank and scenarios are grounded in (and cite by URL) public Microsoft Learn documentation; no Microsoft documentation text is vendored into the tree — only cited.

---

## Bundled MCP server

This plugin's `plugin.json` declares the following Model Context Protocol (MCP) server, which Claude Code connects to automatically when the plugin is installed:

### `microsoft-learn` — Microsoft Learn MCP Server (Microsoft docs; MIT open-source tooling)

**Source / tooling repo:** [`MicrosoftDocs/mcp`](https://github.com/MicrosoftDocs/mcp)
**Endpoint:** `https://learn.microsoft.com/api/mcp` (remote, HTTP transport)
**Party:** third-party (Microsoft — first-party *to the documentation*, third-party *to this marketplace*; the open-source CLI/tooling is MIT, the served documentation content is CC-BY-4.0 / Microsoft Learn terms).
**What it does:** Brings official, current Microsoft Learn documentation and code samples into the agent's context via three read-only tools — `microsoft_docs_search` (semantic search over Learn docs), `microsoft_code_sample_search` (official code samples, optional language filter), and `microsoft_docs_fetch` (fetch a full Learn page as markdown).

**Read-only / read-write:** **read-only.** It searches and fetches *public* Microsoft documentation. It does **not** read your tenant, your mailboxes, your files, your directory, your code, or any user/profile data, and it writes nothing.

**Why it clears the bundling bar** (per [`docs/best-practices/bundled-mcp-servers.md`](../../docs/best-practices/bundled-mcp-servers.md), Step 1):

- **Zero-config / no per-consumer state** — a fixed public endpoint; no tenant URL, no allowed-directory path, no per-consumer parameter.
- **No authentication / no secrets** — the endpoint requires no auth (verified 2026-06-05 against the [Microsoft Learn MCP overview](https://learn.microsoft.com/training/support/mcp): "No API keys, no logins, no sign-ups required"), so there is no credential to bundle, reference, or leak.
- **Read-only** — search + fetch over public docs only; it never touches the consumer's tenant, so the Gate 25 `mcp.allowed_servers` write-verb concern does not apply.
- **The most fitting grounding companion for this plugin** — a Microsoft Graph plugin's #1 risk is a volatile fact recalled from training (a permission name, a v1.0-vs-beta endpoint, a throttle limit, a subscription max-expiry). This server lets agents re-verify against *current* Learn docs instead of trusting memory (CLAUDE.md §3 #9, §5).

**Consumer prerequisite — none.** Because it is a remote HTTP endpoint with no auth, there is **nothing to install**. If the network can't reach `learn.microsoft.com`, the server shows as `failed` in `/mcp` and the error surfaces in the `/plugin` Errors tab; Claude Code and every other tool still work (**loud-but-non-fatal**). **If the Learn tools aren't responding, check `/mcp` and the `/plugin` Errors tab first** — the usual cause is no network egress to `learn.microsoft.com`, not a broken server. There is no local subprocess and therefore no PATH / `python -m` fallback to configure.

**Override (consumer-side, if needed).** To register it via the CLI instead of the bundled declaration (e.g. to scope it to a different project), the documented command is:

```bash
claude mcp add --transport http microsoft-learn https://learn.microsoft.com/api/mcp
```

(`[verify-at-use]` — Claude Code MCP transport flags and the Learn endpoint are version-volatile; re-confirm against the Claude Code MCP docs and the Microsoft Learn MCP overview before relying on them.)

**License attribution** — the Microsoft Learn MCP open-source tooling/CLI is MIT-licensed; see the upstream LICENSE at [`MicrosoftDocs/mcp`](https://github.com/MicrosoftDocs/mcp). The documentation content served by the endpoint is Microsoft's, governed by the Microsoft Learn terms of use, not redistributed by this plugin.

---

## NOT bundled — credentialed Graph MCP servers (recommend, do not bundle)

A Microsoft Graph plugin invites the question "why not bundle a server that actually *calls* Graph?" The answer is the bundling rule's decision table: any tenant-acting Graph MCP is **per-tenant + Entra-authenticated + write-capable**, which is "recommend, don't bundle" (and write verbs gate through `ravenclaude-core/security-reviewer`).

### Lokka (`@merill/lokka`) — recommend, evaluate-first; NOT bundled

**Source:** [`merill/lokka`](https://github.com/merill/lokka) · **Package:** `@merill/lokka` (npm) · **License:** MIT · **Latest version:** `0.1.7` `[verify-at-use]` (volatile — confirm at adoption).
**Why not bundled:**
- **Per-tenant + authenticated** — requires `TENANT_ID` / `CLIENT_ID` / `CLIENT_SECRET` (client-credentials), or a certificate (`CERTIFICATE_PATH` + `USE_CERTIFICATE`), or interactive (`USE_INTERACTIVE`), or a client-provided token. A connection identity is a secret; you can't hardcode it, and the reference-not-literal rule applies.
- **Write-capable** — the `Lokka-Microsoft` tool calls Microsoft Graph (and Azure RM) with `POST`/`PUT`/`PATCH`/`DELETE` "if permissions are provided." A write-capable, secret-handling server is an **Absolute-rule `security-reviewer` gate before it ships** and interacts with the deterministic `mcp.allowed_servers` allowlist (Gate 25).

**Recommended setup (consumer-configured, secret as a reference, security-reviewer sign-off first):**

```bash
# Interactive (lowest blast radius for exploration; uses the default app):
claude mcp add lokka -- npx -y @merill/lokka@0.1.7   # then set USE_INTERACTIVE=true   [verify-at-use]

# Client-credentials (daemon): pass the secret by REFERENCE (env-var name / vault URI), never a literal.
# TENANT_ID / CLIENT_ID / CLIENT_SECRET sourced from your secret store, not committed.
```

Prefer the **least-privilege, read-only** scope set the task needs; gate any write scope through `ravenclaude-core/security-reviewer` (CLAUDE.md §3 #1, §8). Re-confirm the package version, auth env-var names, and tool surface at adoption — all volatile.

> Sources (retrieved 2026-06-05): [`MicrosoftDocs/mcp`](https://github.com/MicrosoftDocs/mcp) · [Microsoft Learn MCP overview](https://learn.microsoft.com/training/support/mcp) · [`merill/lokka`](https://github.com/merill/lokka) · `@merill/lokka` on npm. Package names, versions, auth env-vars, and endpoint/transport flags are version-volatile — `[verify-at-use]`.
