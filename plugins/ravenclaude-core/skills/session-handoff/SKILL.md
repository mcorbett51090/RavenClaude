---
name: session-handoff
description: "Write a host-paired handoff and start a fresh window before auto-compact — Grok TUI, Copilot Chat new session, or Copilot CLI. Use for /handoff, 'context is full', 'fresh window', or a Stop-hook hot-window nag."
user-invocable: true
allowed-tools: Bash, Read, Write, Edit
---

# Session handoff — fresh window, not a compact

This is a **quality reset**. Write the brief to the existing run-dir contract, then continue in a **new empty** session on the **same host**: Grok TUI → Grok TUI, Copilot Chat → **new** Chat session, Copilot CLI → Copilot CLI. Compaction keeps the transcript on disk; it does not keep quality.

## Gotchas (read these; they are the load-bearing rules)

- **Same `task-id`.** Continue in `.ravenclaude/runs/<task-id>/`. Never invent a parallel id for the same work.
- **The hook cannot write the narrative.** `handoff-nudge` only nags. You fill `<!-- MODEL FILL -->` sections.
- **Seed is host-paired.** Grok: positional `grok "…"`. Chat: `chat-resume.md` + Cmd+N / New Chat + paste. CLI: interactive `copilot` (never a one-shot flag). **A Chat or CLI successor must not launch grok.**
- **Never `grok -p`**, never `--single`, never `--prompt-file`, never `--prompt-json`.
- **Never `/fork`.** Fork copies the bloated history — the opposite of a reset.
- **Never a Grok `SessionStart` injection as the seed.** Grok ignores SessionStart stdout.
- **Never a PreCompact persist hook.** Compaction is append-only.
- **Never encode 40% / 30% / 300K as a trigger.** The compact threshold is ~85%. Soft threshold default 70, always below auto-compact.
- **Do not read `GROK_SESSION_ID` from the agent env.** It is unset here. Detection is hook-only.
- **Never infer Chat from `TERM_PROGRAM=vscode` alone.** That is also Grok-in-VS-Code. Pass `--host grok|cli|chat` from what you actually are.
- **Chat Stop/nudge fire is unverified.** This skill is the Chat path when the **user or the model** invokes it. Copy-paste is always printed. Live Chat URI is owner-flagged best-effort.

## Procedure

1. Resolve `task-id`: user argument → most-recently-touched `.ravenclaude/runs/<id>/` in this repo → else propose a slug and create it. Never a second id for the same task.
2. Resolve **origin host** (you are Chat / Grok TUI / Copilot CLI — do not guess from `TERM_PROGRAM=vscode` alone) → `grok` | `cli` | `chat`.
3. `bash plugins/ravenclaude-core/bin/rc artifacts new <task-id>` (continue-in-place).
4. `python3 plugins/ravenclaude-core/scripts/context-handoff.py write --task-id <id> --host <pair>` to refresh the derive-fill skeleton.
5. **Fill** every `<!-- MODEL FILL -->` section in `.ravenclaude/runs/<id>/handoff.md`. Update `summary.md` / `decisions.md` only when there is real content — never stamp empty files.
6. Spawn: `bash plugins/ravenclaude-core/bin/rc handoff --task-id <id> --host <pair> --recipe same-host`. If spawn is `copy-paste-only` or fails, print the exact copy-paste block. Report which path was taken.
7. If stdout contains `SUCCESSOR_ACK`, the successor has begun. **Stop this session.** You cannot `/quit` — the user closes the tab.

## Out of scope for this skill

- Changing Grok's auto-compact threshold.
- Dashboard dispatch as the spawn path.
- Other-host adapters beyond Grok / Copilot CLI / Copilot Chat.
- A `copilot-chat` marketplace install column.
- Enabling origin `context_handoff`.
- Touching `hooks/compact-anchor.sh` or `scripts/compact-anchor.py`.
