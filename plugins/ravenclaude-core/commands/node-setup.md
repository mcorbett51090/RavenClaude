---
description: Provision a local Node.js LTS on demand (downloaded into RavenClaude's persistent plugin data dir, checksum-verified, and auto-added to PATH each session). Use when a project needs `node` but it isn't installed — no sudo, no system-wide install.
---

The user wants Node.js available for their work (for example, a project whose test/lint gates are `.mjs` files that need `node`). ravenclaude-core provisions a local Node LTS **on demand** — Claude Code plugins have no install-time step and can't bundle per-platform binaries, so node is fetched into the plugin's persistent data dir instead.

Node is **not** required by ravenclaude-core itself (its own gates are Python + bash); this is a convenience for consumer projects.

## Run the provisioner

```bash
bash "${CLAUDE_PLUGIN_ROOT}/hooks/ensure-node.sh" --install
```

That script:
- detects the OS/arch (`uname`),
- resolves the **latest Node LTS** from `nodejs.org`,
- downloads the static build and **verifies its SHASUMS256 checksum** (refuses to install on mismatch),
- extracts into `${CLAUDE_PLUGIN_DATA}` (which **survives plugin updates**), and
- symlinks `node`/`npm`/`npx` into `${CLAUDE_PLUGIN_DATA}/bin`.

## After it runs
- **New sessions** get `node` on PATH automatically — the `ensure-node.sh` SessionStart hook adds it via `CLAUDE_ENV_FILE`.
- **This shell:** run the `export PATH="…/bin:$PATH"` line the script prints so `node` works immediately without restarting.

Then report the installed `node --version`.

## Platform notes
- macOS and Linux (arm64 / x64) are fully supported.
- On **Windows** (or any unsupported platform) the script exits with guidance to install Node from https://nodejs.org/en/download and put `node` on PATH — relay that rather than retrying.
- Needs `curl` + `python3` (both standard). If offline, the download step fails cleanly — report that and suggest retrying with a connection.
