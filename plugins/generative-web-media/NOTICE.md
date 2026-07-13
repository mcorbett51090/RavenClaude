# Third-party content notice — `generative-web-media` plugin

The `agents/`, `knowledge/`, `skills/`, `templates/`, `best-practices/`, `commands/`, `scripts/`, and `CLAUDE.md` content in this plugin is original work by Matt Corbett, released under MIT. The knowledge bank is grounded in (and cites) public provider documentation and legal/regulatory sources; no third-party documentation text is vendored into the tree — only cited by URL. All provider prices are marked `[unverified — confirm on provider pricing page]`.

---

## Declared MCP server

This plugin's `plugin.json` declares one Model Context Protocol (MCP) server, which Claude Code connects to when the plugin is installed and a key is present:

### `fal` — fal.ai hosted MCP server (third-party, provider-hosted)

**Source / docs:** [`fal.ai/docs/documentation/setting-up/mcp`](https://fal.ai/docs/documentation/setting-up/mcp)
**Endpoint:** `https://mcp.fal.ai/mcp` (remote, HTTP transport)
**Party:** third-party (fal.ai). The server is hosted by fal; this plugin does not vendor or redistribute any fal code.
**What it does:** exposes many hosted image / video / audio / 3D generation models behind one endpoint, plus pricing-introspection tools. The server itself is free; **each model run is billed pay-per-run** to your fal account.

**Read-only / read-write:** **generative (write-ish).** It does not read your repo or files, but it *does* run billable generation jobs against your fal account. Treat it as a spend-incurring tool — this is why per-project generation budgets (`gen-budget.py`, `/check-generation-budget`) exist.

**Authentication — a key is required (the one departure from zero-config).** Unlike a zero-auth public-docs MCP, the fal server needs an `Authorization: Bearer <FAL_KEY>` credential. The plugin **references** the key by env-var name only:

```shell
export FAL_KEY="…"   # your fal API key — NEVER committed to the repo
```

The key is never written into `plugin.json`, any template, or any script — it is read from the environment at call time. If your Claude Code version's declarative `mcpServers` block cannot carry the auth header, use the fallback (below); the plugin's first `/generate-web-asset` run detects an unwired substrate and prints exactly what to set (**loud-but-non-fatal — never a silent dead tool**).

**Consumer prerequisite:** a fal account + `FAL_KEY` in the environment. With no key, the server shows `failed` in `/mcp` and the error surfaces in the `/plugin` Errors tab; Claude Code and every other tool still work.

**Fallback / override (consumer-side).** To register the server via the CLI with the auth header (the `/wire-media-substrate` path):

```bash
claude mcp add --transport http fal https://mcp.fal.ai/mcp --header "Authorization: Bearer ${FAL_KEY}"
```

Or bypass fal entirely with the direct-provider script (e.g. Grok on `api.x.ai/v1`):

```bash
XAI_API_KEY="…" scripts/generate-via-provider.sh --provider xai --prompt "…"
```

(`[verify-at-use]` — Claude Code MCP transport/`--header` flags and the fal endpoint + auth model are version-volatile; re-confirm against the Claude Code MCP docs and the fal MCP setup page before relying on them. The declarative-binding-vs-header-fallback question is the P0 build check recorded in the plan.)

**License attribution** — the fal MCP server is provider-hosted (fal.ai terms of service govern use and billing); it is not redistributed by this plugin. The documentation content is fal's, cited by URL, not vendored.
