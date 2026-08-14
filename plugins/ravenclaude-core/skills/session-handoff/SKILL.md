---
name: session-handoff
description: "Write a host-agnostic handoff and start a fresh Grok window when context is hot — a quality reset before auto-compact, also fired by the Stop-hook nudge. Use when the user says /handoff, 'context is full', 'fresh window', or the Stop hook reports the window is hot."
user-invocable: true
allowed-tools: Bash, Read, Write, Edit
---

# Session handoff — fresh window, not a compact

This is a **quality reset**. The current window is (or will be) a detriment. Write the brief to the existing run-dir contract, then continue in a **new empty** Grok TUI. Compaction keeps the transcript on disk; it does not keep quality. This skill writes a **legible** brief so the successor does not need that transcript.

## Gotchas (read these; they are the load-bearing rules)

- **Same `task-id`.** Continue in `.ravenclaude/runs/<task-id>/`. Never invent a parallel id for the same work.
- **The hook cannot write the narrative.** `handoff-nudge` only nags. You fill `<!-- MODEL FILL -->` sections.
- **Seed is positional `grok "…"`.** Never `grok -p`, never `--single`, never `--prompt-file`, never `--prompt-json`.
- **Never `/fork`.** Fork copies the bloated history — the opposite of a reset.
- **Never a Grok `SessionStart` injection as the seed.** Grok ignores SessionStart stdout. Compact-anchor stays the Claude/post-compact pointer; do not replace it.
- **Never a PreCompact persist hook.** Compaction is append-only.
- **Never encode 40% / 30% / 300K as a trigger.** The compact threshold is ~85%. The soft handoff threshold is owner-tunable (default 70), always below auto-compact.
- **Do not read `GROK_SESSION_ID` from the agent env.** It is unset here. Detection is hook-only.

## Procedure

1. Resolve `task-id`: user argument → most-recently-touched `.ravenclaude/runs/<id>/` in this repo → else propose a slug and create it. Never a second id for the same task.
2. `bash plugins/ravenclaude-core/bin/rc artifacts new <task-id>` (continue-in-place).
3. `python3 plugins/ravenclaude-core/scripts/context-handoff.py write --task-id <id>` to refresh the derive-fill skeleton.
4. **Fill** every `<!-- MODEL FILL -->` section in `.ravenclaude/runs/<id>/handoff.md` from what you actually know. Update `summary.md` / `decisions.md` only when there is real content — never stamp empty files.
5. Spawn: `bash plugins/ravenclaude-core/bin/rc handoff --task-id <id>` (or `handoff-spawn.sh`). If spawn is `copy-paste-only` or fails, print the exact copy-paste block from stdout. Report which path was taken.

## Out of scope for this skill

- Changing Grok's auto-compact threshold.
- Dashboard dispatch as the spawn path.
- Other-host auto-spawn adapters.
- Touching `hooks/compact-anchor.sh` or `scripts/compact-anchor.py`.
