# Comfort-posture on Claude Code on the web — setup checklist

**Audience:** the marketplace maintainer + each client who wants to set their permission posture from a browser, without touching git, YAML, or a terminal.

**Goal:** a non-technical client opens a web page, clicks deny/ask/allow per category (and the tribunal toggles), and those choices become active in their Claude Code **web** sessions — where the container is ephemeral and only committed files survive.

This is the web counterpart to the local dashboard server (`scripts/serve-dashboards.py`). On the web there is **no inbound port forwarding**, so a server running inside the session's container is unreachable from the client's browser (verified against the [Claude Code on the web docs](https://code.claude.com/docs/en/claude-code-on-the-web) — the network model is outbound-only). The browser surface therefore has to be **externally hosted (GitHub Pages)**, and persistence rides the **committed project layer** re-applied by a SessionStart hook.

---

## How the pieces fit

```
GitHub Pages (one public URL — same page for every client)
      │  client clicks posture + tribunal choices
      ▼
"Copy" → a YAML block            (the page holds NO client data; it is just the tool)
      │  client pastes it into their Claude chat: "save my posture"
      ▼
Claude writes .ravenclaude/comfort-posture.yaml  +  runs /set-posture  +  commits both
      │                                                   (into THAT client's own repo)
      ▼
SessionStart hook (reapply-posture.sh)  regenerates the project-layer rules from the YAML
      ▼
The client's web sessions start with their posture active. No git seen by the client.
```

Each client's data lives in **their own repo**, so isolation is automatic — there is no shared store to keep separate.

---

## What this PR already ships (maintainer side)

- [x] `reapply-posture.sh` — SessionStart hook that regenerates `.claude/settings.json` (project layer) from `.ravenclaude/comfort-posture.yaml`. Silent no-op when no posture file exists; never blocks a session.
- [x] Registered in both `plugins/ravenclaude-core/hooks/hooks.json` (consumers, via `${CLAUDE_PLUGIN_ROOT}`) and the dev-mirror `.claude/settings.json` (via `${CLAUDE_PROJECT_DIR}`).
- [x] `ravenclaude-core` bumped to **0.26.0**.

## What the maintainer still does once

- [ ] **Confirm GitHub Pages is enabled** for the repo and note the dashboard URL. `dashboard.html` already ships in the plugin and is a static, no-backend page (it emits a live YAML preview + Copy + Download). Link it from the Pages landing (`index.html`) so clients have one address to open.
- [ ] **Send each client the Pages URL** plus the three usage steps below.

## What each client does once (per repo)

- [ ] In their repo's `.claude/settings.json`, declare the RavenClaude marketplace and enable `ravenclaude-core`. Claude Code on the web installs declared plugins at session start, which is what loads the SessionStart hook.

## What each client does to set/change their posture

1. Open the Pages dashboard URL. Click their deny / ask / allow choices and any tribunal toggles.
2. Click **Copy**, paste the block into their Claude chat, and say *"save my posture."*
3. Claude writes the YAML, applies it (`/set-posture`), commits both files, and opens the PR. The client merges it (or you enable auto-merge).

That's the whole loop — no git, no YAML editing, no terminal.

---

## Persistence + timing notes

| Concern | What to do |
|---|---|
| **Only committed files survive a fresh web container** | Commit **both** `.ravenclaude/comfort-posture.yaml` (the source of truth) **and** the generated `.claude/settings.json` (project layer). The current session then loads the right rules natively; the hook keeps the two in sync on later sessions. |
| **User / local layers don't persist on web** | The hook applies `--scope project` only. The machine-wide user layer is ephemeral on web, and `.claude/settings.local.json` is gitignored (absent in a fresh clone), so the project layer is the one that matters. |
| **Does a session pick up its own start-time rewrite?** | Whether settings rewritten at SessionStart affect the *current* session or only the *next* depends on Claude Code's settings-load vs hook-run order. Either way the **next** session is correct; committing the generated `settings.json` guarantees the current one is too. |
| **Bypass modes** | `acceptEdits` / `bypassPermissions` partially or fully ignore these rules; the companion `ensure-default-mode.sh` hook warns when a session loads in one. |

## Optional later upgrade

The "copy → paste to Claude" save step can be replaced by the page committing the YAML **directly via the GitHub API** (one-time client GitHub login, then no paste). That removes the manual step but adds an auth backend to build — defer until the paste step proves annoying.
