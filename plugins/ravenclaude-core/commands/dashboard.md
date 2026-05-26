---
description: Launch the fully-functioning comfort-posture dashboard (Save & apply works) in your browser.
allowed-tools: Bash, Read
---

# /dashboard

Open the **fully-functioning** comfort-posture dashboard — the point-and-click editor
for your permission rules and command-review toggles, where the **Save & apply** button
actually writes `.ravenclaude/comfort-posture.yaml` and re-runs the translator for you (no
Copy/Download step).

This launches a small **local** server (`serve-dashboards.py`) bundled inside the plugin.
It serves the version-matched `dashboard.html` and exposes only `/__save`, `/__read`
(allow-listed to `.ravenclaude/` files), and `/__classify` (read-only). It binds
`127.0.0.1` and is single-user/local — there is no `/__run`, no auth, no multi-user mode.

## How to launch it

Run the bundled server **in the background, from the user's project root** (so it writes
`.ravenclaude/` into their project), then give the user the URL. `${CLAUDE_PLUGIN_ROOT}`
resolves to the plugin's install location:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/serve-dashboards.py" --port 8000
```

- Run it with the Bash tool's **background mode** (it's a long-running server).
- If port 8000 is already in use, retry with `--port 8001` (and so on) until one is free.
- Read the server's startup output and relay the exact **URL** it prints to the user.

## What to tell the user

1. **The URL to open** — the `http://127.0.0.1:<port>/dashboard.html` line (and, in a
   Codespace, the forwarded `https://…app.github.dev/…/dashboard.html` line + QR).
2. **Open it in a real browser tab** — *not* the VS Code "Simple Browser" / "Live Preview",
   which sandboxes the page and shows "content is blocked". In a Codespace, use the **Ports**
   panel → port → 🌐 "Open in Browser", or click the forwarded URL and choose "Open in Browser".
3. **Save & apply works here** — picking rules and clicking Save writes
   `.ravenclaude/comfort-posture.yaml` and applies it to `.claude/settings.json` in one step.
4. **Keep the forwarded port Private** (the Codespace default) — `/__save` writes files and
   runs the posture translator, so it must not be public.
5. **To stop it** — Ctrl+C the background process (or end the session).

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
