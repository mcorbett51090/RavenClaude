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

Each starts a small **local** server and prints a URL. **Open it in a real browser tab** —
in a Codespace use the **Ports** panel → the port → 🌐 **Open in Browser** (not VS Code's
Simple Browser, which blocks the page). Once it's running, the dashboard is at:

➡️ **<http://127.0.0.1:8000/dashboard.html>**

Press `Ctrl+C` in the terminal to stop the server when you're done.

> Scoped & safe: the launcher pins this repo's path, and the server refuses to run if it's
> ever pointed at the marketplace clone — so a consumer dashboard can only edit its own repo.
