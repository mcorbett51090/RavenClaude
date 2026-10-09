---
description: Open Harness Spectate (live agent loop viewer) in the browser. Host-agnostic entry is `rc spectate`.
---

# /spectate

Opens the Spectate surface served by `serve-dashboards.py` at `/spectate`. On Claude Code, prefer the `spectate` skill — it opens the same URL and arms the v0.6 push mirror (`watch-spectate.sh`).

**Copilot / Codex / Cursor / terminal:** use the host-agnostic launcher instead:

```bash
bash plugins/ravenclaude-core/bin/rc spectate
```

Options: `--demo`, `--no-open`, `--session <id>`, `--port N`, `--foreground`.

Claude Code can use this slash command when the dashboard server is already running; it prints the same URL `rc spectate` would open.
