---
description: "Fallback substrate wiring when the declarative fal MCP binding can't carry the Authorization: Bearer FAL_KEY header. Registers the fal server via claude mcp add with the auth header, or points at the direct-provider script. Keys stay env-referenced, never committed."
argument-hint: "[optional: --provider fal|xai to target a specific path]"
---

You are running `/generative-web-media:wire-media-substrate`. This is the **fallback** — the plugin already declares the fal MCP in `plugin.json` so it auto-wires on install. Use this only when the declarative binding can't carry the auth header in your Claude Code version (the P0 build check).

> Keys are read from the environment by name and NEVER written to the repo. See [`../NOTICE.md`](../NOTICE.md).

## Steps

1. **Probe what's wired:**

   ```shell
   scripts/generate-via-provider.sh --check   # reports curl + FAL_KEY + XAI_API_KEY readiness
   ```

   If a key is missing, instruct the user to `export FAL_KEY=…` (fal) and/or `export XAI_API_KEY=…` (direct Grok) first.

2. **Wire fal via the CLI with the auth header** (the fallback the declarative block may not support):

   ```bash
   claude mcp add --transport http fal https://mcp.fal.ai/mcp \
     --header "Authorization: Bearer ${FAL_KEY}"
   ```

   `[verify-at-use]` — the `--header` / `--transport` flags and the fal endpoint are version-volatile; confirm against the current Claude Code MCP docs and the fal MCP setup page.

3. **Or use the direct-provider path** (off fal entirely — keeps Grok reachable):

   ```bash
   XAI_API_KEY="…" scripts/generate-via-provider.sh --provider xai --prompt "…" --out asset.png
   ```

4. **Verify** — re-run `--check`, and confirm the fal server shows healthy in `/mcp`. If it shows `failed`, the usual cause is a missing/expired `FAL_KEY`, not a broken server (loud-but-non-fatal).

## Output

The wiring that succeeded (declarative already-wired / `claude mcp add` header path / direct-provider), the readiness report, and the exact env-var(s) the user must keep set. Never print a key value.
