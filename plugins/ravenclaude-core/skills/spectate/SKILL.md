---
name: spectate
description: Open Harness Spectate (/spectate loopback livestream) and arm the Claude-only push mirror for permission waits, steer actions, and tool failures. Use when the user wants live loop visibility or native notifications of spectate events.
---

# Skill: spectate

Open the Harness Spectate surface and arm its Claude Code **push mirror**.

## Do this

1. Start or attach the Spectate server and open the UI:

```bash
bash "${CLAUDE_PLUGIN_ROOT:-plugins/ravenclaude-core}/bin/rc" spectate
```

Options the launcher accepts: `--demo`, `--no-open`, `--session <id>`, `--port N`, `--foreground`.

2. Tell the user the URL (`http://127.0.0.1:<port>/spectate?…`). Loopback only — no second UI, no Simple Browser panel.

## What this skill arms

Invoking this skill starts the plugin monitor `spectate-push-mirror` (`monitors/watch-spectate.sh`) for the rest of the session. It tails `.ravenclaude/runs/*/spectate-events.jsonl` and emits **derived-label** notifications only (kind / status / tool name / steer action) — never prompts, args, paths, or note text.

Steer from the browser still requires comfort-posture `spectate_steer: on`.

## Hosts

- **Claude Code** — this skill + monitor push channel.
- **Copilot / Codex / Cursor / terminal** — use `rc spectate` for the pull UI; monitors do not load on those hosts.
