---
description: Inspect or override the active Agentic Work-Stream — list / set / create / clear / status.
allowed-tools: Bash, Read
---

# /stream

Manage **Agentic Work-Streams** — named logical workstreams under `.ravenclaude/streams/`
that organize streams of agentic work so each session's work is attributed, trackable, and
crash-resumable. This is the **override** surface: the SessionStart banner _suggests_ a
stream (from the branch + recent commits, never your prompts); `/stream` is how you confirm,
switch, create, or clear the active stream.

The engine is the `rc streams` CLI (a thin launcher over `stream-ops.py`). Run it from the
**project root** so it reads/writes that project's `.ravenclaude/streams/`.

## The sticky rule (why an override matters)

When a stream is **active**, this session's prompts are *attributed* to it and the classifier
does **not** re-run — so a "fix it" / "continue" prompt can't spawn a spurious new stream.
Reclassification fires only when **no** stream is active (at session start) or when you ask.
`/stream` is the deliberate way to change which stream is active.

## Usage

Run the matching `rc streams` subcommand with the Bash tool (no `cd` — invoke from the user's
project root). `rc` lives at `${CLAUDE_PLUGIN_ROOT}/bin/rc`; call it by path if it isn't on PATH.

| Ask | Command |
|---|---|
| **Show all streams + which is active** | `rc streams list` |
| **One-line status** (active + count) | `rc streams status` |
| **Set the active stream** | `rc streams set-active <id>` |
| **Create a new stream** | `rc streams create "<name>"` (the name is slugified to the id) |
| **Show a stream's resume state + recent DERIVED history** | `rc streams show <id>` |
| **What's active right now** | `rc streams get-active` |

`/stream set <id>` → `rc streams set-active <id>` · `/stream new "<name>"` → `rc streams create` ·
`/stream list` → `rc streams list` · `/stream status` → `rc streams status`.

## Privacy / safety

- The per-stream `history.jsonl` stores **DERIVED labels/terms/counts only** — never raw
  prompt text (`stream-ops.append_event` refuses a raw-content field by construction).
- Stream ids are slugified and **anti-traversal-checked** — a `..`/`/`/absolute id is rejected
  with a clean error, never a path escape.
- `stream_classify: off | label_only | auto` and `stream_threshold: <0.05–0.95>` in
  `.ravenclaude/comfort-posture.yaml` tune the SessionStart suggestion (default `label_only`:
  suggest, never auto-switch). `auto` opt-in sets the active stream on a confident match.

## Notes

- **Claude Code only as a slash command.** Under GitHub Copilot CLI there are no user slash
  commands — run `rc streams …` directly (it works in any host).
- The dashboard's **Streams** tab (Observe) is the point-and-click view of the same data.
