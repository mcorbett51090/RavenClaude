---
description: Launch the fully-functioning comfort-posture dashboard (Save & apply works) in your browser.
allowed-tools: Bash, Read
---

# /dashboard

Open the **fully-functioning** comfort-posture dashboard — the point-and-click editor
for your permission rules and command-review toggles, where the **Save & apply** button
actually writes `.ravenclaude/comfort-posture.yaml` and re-runs the translator for you (no
Copy/Download step).

> **Disambiguation:** an unqualified "open the dashboard" resolves to **this** RavenClaude
> comfort-posture dashboard (the `rc dashboard` front door). Don't surface a chooser unless the
> user *named* a different dashboard (e.g. a Power Platform admin / maker portal) — guessing wrong
> there cost a needless menu prompt in a prior session.

This launches a small **local** server (`serve-dashboards.py`) bundled inside the plugin.
It serves the version-matched `dashboard.html` and exposes only `/__save`, `/__read`
(allow-listed to `.ravenclaude/` files), `/__saga` (read-only Review-log feed from
`.ravenclaude/runs/thing/`), and `/__classify` (read-only). It binds
`127.0.0.1` and is single-user/local — there is no `/__run`, no auth, no multi-user mode.
The server **self-expires after 120 minutes idle** (`--max-idle N`; `--max-idle 0`
disables) so a forgotten, detached background server does not sit on the loopback
`/__save` write surface indefinitely — reopen it with the same command if it has expired.

## How to launch it

`rc dashboard` is the one-verb front door — a real launcher shipped at
[`${CLAUDE_PLUGIN_ROOT}/bin/rc`](../bin/rc). It runs the bundled server, and on a
local/desktop machine **the browser opens automatically**. In a Codespace, VS Code's
`onAutoForward: openBrowser` wiring opens the forwarded URL in a real browser tab the
moment the port comes up — no copy-paste required in either case.

`rc` works the same in **any host** (Claude Code, GitHub Copilot CLI, a bare terminal) —
it preserves your cwd as the project root, so `.ravenclaude/` is written where you run it.
To call it as a bare `rc dashboard`, put the plugin's `bin/` on your PATH:

```shell
export PATH="$PATH:<your-ravenclaude-clone>/plugins/ravenclaude-core/bin"
```

Otherwise run it by path: `bash <clone>/plugins/ravenclaude-core/bin/rc dashboard`. In a
**Copilot** session you don't need either — just ask Copilot to "open the dashboard" and
its `AGENTS.md` grounding ([`copilot/AGENTS.md`](../copilot/AGENTS.md)) tells it the command.

To launch it manually (e.g. from Claude with the Bash tool), run the bundled server
**in the background, from the user's project root** (so it writes `.ravenclaude/` into
their project). `${CLAUDE_PLUGIN_ROOT}` resolves to the plugin's install location:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/serve-dashboards.py" --port 8000
```

- Run it with the Bash tool's **background mode** (it's a long-running server).
- **If port 8000 is already in use**, the server recovers on its own — it never dies with
  an "address already in use" traceback, and it never signals a process it hasn't
  positively identified as one of its own:
  - held by a **stale RavenClaude dashboard** (the usual case — you relaunched) → it stops
    that server and rebinds **8000**, so the URL stays stable;
  - held by **anything else** → it leaves that process alone and binds the next free port
    (**8001–8010**).
- Pass `--no-open` to suppress the browser auto-open in scripts/CI.
- The server **self-expires after `--max-idle` minutes idle** (default 120; `--max-idle 0`
  disables) — an idle background server reaps itself instead of lingering on the `/__save`
  write surface. A tab left open across the expiry re-checks on focus and shows the exact
  relaunch command; just run this command again.
- Read the server's startup output and relay the exact **URL** it prints to the user — on a
  fallback bind the port is *not* 8000.

## What to tell the user

1. **Browser auto-opens** on a local machine, straight to `/dashboard.html`; in a Codespace
   the forwarded tab opens automatically via `onAutoForward`. If it doesn't, use the URL the
   server prints. Bare `/` **302-redirects** to the dashboard, so a hand-typed
   `localhost:8000` lands on the dashboard rather than a file listing.
2. **Open it in a real browser tab** — *not* the VS Code "Simple Browser" / "Live Preview",
   which sandboxes the page and shows "content is blocked". In a Codespace, use the **Ports**
   panel → port → "Open in Browser", or click the forwarded URL and choose "Open in Browser".
3. **Save & apply works here** — picking rules and clicking Save writes
   `.ravenclaude/comfort-posture.yaml` and applies it to `.claude/settings.json` in one step.
4. **Keep the forwarded port Private** (the Codespace default) — `/__save` writes files and
   runs the posture translator, so it must not be public.
5. **To stop it** — Ctrl+C the background process, or let it **self-expire** (`--max-idle`,
   default 120 min idle). On the marketplace clone, `bash scripts/open-dashboard.sh --stop`
   stops this checkout's server (it never signals an unrelated one).

## Marketplace developer: `scripts/open-dashboard.sh`

Working *on this marketplace repo*? `bash scripts/open-dashboard.sh` opens **this repo's**
unified portal (`index.html`, served by the **root** `serve-dashboards.py` so its live
`/__*` fetches run same-origin). It is worktree-correct — run it from a worktree and it
edits **that** worktree's `.ravenclaude/comfort-posture.yaml`.

- **Probe-then-reuse:** if a dashboard is already serving *this* checkout it is **reused**,
  not duplicated — a second run adopts the live server and prints its URL.
- **Never kills an unrelated server:** it only ever stops a `serve-dashboards.py` whose
  process cwd is this checkout (a fail-closed `ps` command + cwd match). Another project's
  live dashboard is left alone; the server walks to the next free port instead.
- **`--stop` / `--stop-all`:** stop this checkout's server(s) — `--stop` scans the 8000 walk
  range, `--stop-all` any port. Both signal only *your* checkout's servers.
- **Explicit `--bind 127.0.0.1`** off-Codespace (the loopback C2 floor); in a Codespace it
  lets the server default to `0.0.0.0` so the forwarded port is reachable.
- **Prints the actually-bound URL every run** (a fallback bind means the port is not
  necessarily 8000). `--no-open` suppresses the browser open (the devcontainer
  `postStartCommand` uses it).

## When to use which path

| You want… | Use |
|---|---|
| The full point-and-click experience with one-click Save & apply | **`/dashboard`** (this command) |
| To just look / pick rules and copy the YAML yourself | the hosted dashboard link in the plugin README, then save the YAML and run `/set-posture` |
| To apply an already-saved `.ravenclaude/comfort-posture.yaml` headlessly (CI) | `/set-posture` |

## Related artifacts

- Dashboard UI: `${CLAUDE_PLUGIN_ROOT}/dashboard.html`
- Server: `${CLAUDE_PLUGIN_ROOT}/scripts/serve-dashboards.py`
- Translator (what Save & apply calls): `${CLAUDE_PLUGIN_ROOT}/scripts/apply-comfort-posture.py` (also `/set-posture`)
