# RavenClaude — this repo's config

This folder holds **this repo's** RavenClaude settings. Editing here affects **only this
repo** — never the marketplace clone.

- `comfort-posture.yaml` — your permission + command-review posture (the dashboard writes this).
- `environment-context.md` — optional: which environments you're authorized in.

## Open the comfort-posture dashboard

A point-and-click editor for the settings above. **Save & apply** writes
`comfort-posture.yaml` and updates `.claude/settings.json` in one step. Use whichever is easiest:

- **VS Code (one click):** Terminal → **Run Task** → **RavenClaude: Comfort-posture dashboard**.
- **Terminal (from this repo):** `bash .ravenclaude/dashboard.sh`
- **From anywhere:** `ravenclaude dashboard --project /path/to/this/repo`

Each starts a small **local** server. Once it's running, the dashboard for **this repo** is at:

➡️ **<__RC_DASHBOARD_URL__>**

That link is filled in for your current environment — the live **Codespace-forwarded** URL in
a Codespace, or `localhost` otherwise — so you don't have to hunt for it. (`ravenclaude setup`
regenerates this file, so a rebuilt Codespace always gets a fresh, working link.) In a
Codespace, open it in a **real browser tab**, not VS Code's Simple Browser (which blocks the
page). Press `Ctrl+C` to stop the server when you're done.

> Scoped & safe: the launcher pins this repo's path, and the server refuses to run if it's
> ever pointed at the marketplace clone — so a consumer dashboard can only edit its own repo.
