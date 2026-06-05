# NOTICE — third-party content bundled in `aws-cloud`

This plugin declares one third-party MCP server in `.claude-plugin/plugin.json`. The server's **source is referenced, not vendored** — nothing of its code is copied into this repo. This file is the attribution required by `docs/best-practices/bundled-mcp-servers.md` (Step 5) and is the target of the `x-mcpAttribution.aws-documentation.notice` field (CI-checked by `scripts/check-mcp-attribution.py`).

## `aws-documentation` — AWS Documentation MCP Server (awslabs/mcp)

- **Server name (in `plugin.json`):** `aws-documentation`
- **Source:** https://github.com/awslabs/mcp/tree/main/src/aws-documentation-mcp-server
- **Package (PyPI):** `awslabs.aws-documentation-mcp-server`
- **License:** Apache-2.0 (the `awslabs/mcp` suite is Apache-2.0) — verified 2026-06-05.
- **Party:** third-party (AWS Labs — first-party to AWS, third-party to RavenClaude).
- **What it does:** read-only access to **AWS public documentation** — search the docs, fetch a doc page (converted to markdown), and read doc sections / recommendations. It reads **only the public documentation site**; it does **not** touch any AWS account, and it requires **no AWS credentials**. This is what clears the bundling bar (zero-config + read-only + first-party-to-AWS / well-maintained Apache-2.0): per `docs/best-practices/bundled-mcp-servers.md` Step 1, a zero-config, no-auth, read-only server may be bundled.

### Consumer prerequisite (run once)

The server runs via `uvx`, so the prerequisite is **`uv`** on `PATH`:

```bash
# install uv (the uvx launcher) — see https://docs.astral.sh/uv/
curl -LsSf https://astral.sh/uv/install.sh | sh
# then uvx fetches and runs the pinned server on demand:
uvx awslabs.aws-documentation-mcp-server@latest
```

The `@latest` tag is what `plugin.json` declares. To pin a tested version instead, replace `@latest` with `==<tested-version>` in both `plugin.json` and the command above (keep the two identical) and re-confirm at each plugin version bump. `[verify-at-use]` the current published version on PyPI before pinning.

### PATH fallback (loud-but-non-fatal)

If `uv`/`uvx` is not installed, the server shows `failed` in `/mcp` and the binary error surfaces in the `/plugin` Errors tab — **Claude Code and every other tool keep working** (the same loud-but-non-fatal posture as any missing MCP prerequisite). MCP subprocesses get a minimal shell env, so if `uvx` is visible in your terminal but missing to the child process, use the **absolute path** to `uvx` in `plugin.json`'s `command` (e.g. `~/.local/bin/uvx`). If the tools aren't responding, check `/mcp` and the `/plugin` Errors tab first.

---

**No other third-party content is bundled.** The bundled `scripts/aws_cost_estimator.py` is original, stdlib-only, first-party RavenClaude code (versioned with the plugin). All knowledge-bank and scenario sources are **cited inline by URL**, not vendored.
