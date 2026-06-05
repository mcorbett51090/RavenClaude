# Third-party content notice — `microsoft-fabric` plugin

The `agents/`, `knowledge/`, `best-practices/`, `templates/`, `commands/`, `hooks/`,
`scenarios/`, and `scripts/` content of this plugin is original work by Matt Corbett,
released under MIT. The one third-party dependency is the bundled MCP server below.

---

## Bundled MCP server

This plugin's `plugin.json` declares the following Model Context Protocol (MCP) server,
which Claude Code starts automatically when the plugin is enabled.

### `microsoft-learn` — Microsoft Learn MCP Server

**Source:** [`microsoftdocs/mcp`](https://github.com/microsoftdocs/mcp) (official Microsoft Learn MCP Server)
**Endpoint:** `https://learn.microsoft.com/api/mcp` (remote, **streamable HTTP**)
**License:** MIT
**Party:** third-party (first-party *to Microsoft*, third-party *to RavenClaude* — referenced, not vendored)
**What it does:** Grounds answers in **official Microsoft Learn documentation**. Exposes
three **read-only** tools — `microsoft_docs_search` (search docs, up to ~10 chunks),
`microsoft_docs_fetch` (fetch a full doc page as markdown), and
`microsoft_code_sample_search` (search official code samples).

**Why it is BUNDLE-eligible (unusually for a Microsoft server):** it is a **remote, no-auth,
free, read-only** server — there is **no per-consumer URL, no credential, no install, no write
verb, and no metered cost**. That clears the zero-config + read-only + first-party/well-maintained
bar in [`docs/best-practices/bundled-mcp-servers.md`](../../docs/best-practices/bundled-mcp-servers.md)
Step 1 (BUNDLE row). The two *operational* Fabric MCP servers (Fabric MCP, Fabric RTI MCP) are
**credentialed and write-capable**, so they are **recommend-not-bundle** — see CLAUDE.md §11a.
**Verified 2026-06-05** against [Microsoft Learn MCP Server overview](https://learn.microsoft.com/training/support/mcp):
"no authentication required," "publicly available," "no charge," remote streamable HTTP at
`https://learn.microsoft.com/api/mcp`. Re-confirm the endpoint + tool surface at use (`[verify-at-use]`).

**Consumer prerequisite — none.** Because the server is a remote HTTP endpoint with no auth,
there is nothing to `pip install` / `npm install`. Claude Code connects directly when the plugin
is enabled (Claude Code MCP transport `type: "http"`, the streamable-HTTP standard).

**Loud-but-non-fatal failure path.** If the endpoint is unreachable (no network, an egress
proxy, or the consumer's [`.ravenclaude/web-access.yaml`](../ravenclaude-core/templates/web-access.yaml)
denies `learn.microsoft.com`), the server shows `failed` in `/mcp` and the error surfaces in the
`/plugin` Errors tab; **Claude Code and every other tool keep working.** If the Learn tools aren't
responding, check `/mcp` and the `/plugin` Errors tab first, and confirm `learn.microsoft.com` is
reachable / allow-listed. There is no PATH fallback because there is no local binary — the
network endpoint *is* the server.

**No secret is shipped** anywhere in this plugin (the endpoint needs none). This satisfies the
Absolute "reference-not-literal" rule trivially: there is no credential to reference.

**MIT License attribution** — full text per the upstream `LICENSE` at
[`microsoftdocs/mcp`](https://github.com/microsoftdocs/mcp). Reproduced summary:

```
MIT License — Copyright (c) Microsoft Corporation (Microsoft Learn MCP Server / microsoftdocs/mcp)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND…
```

(See the upstream repo for the canonical, year-stamped license text. The Microsoft Learn MCP
Server's use is also governed by the [Microsoft Learn Terms of Use](https://learn.microsoft.com/legal/termsofuse).)
