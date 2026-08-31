---
name: session-handoff
description: "Write a run-dir handoff and start a NEW interactive session (unbounded TUI — never a headless print-flag). Use for /handoff, context full, fresh window, quota host-switch, 'pass remaining work to Grok'. NOT for one bounded Grok/Copilot job → cheap-lane-delegation."
user-invocable: true
allowed-tools: Bash, Read, Write, Edit
---

# Session handoff — fresh window, not a compact

Write the brief to the existing run-dir contract, then continue in a **new empty** session on the **same host**: Grok TUI → Grok TUI, Copilot Chat → **new** Chat session, Copilot CLI → Copilot CLI.

## ⛔ FIRST: do you need this at all? Default is `/compact`.

**`/compact` by default. `/handoff` for three specific cases it structurally cannot cover.**

This skill used to open with *"compaction keeps the transcript on disk; it does not keep
quality."* That framing is **overstated, and this repo retracted the harder version of it after
measuring** (see the marketplace CLAUDE.md, v0.244.1): **compaction APPENDS.** Measured on real
transcripts — 44 `compact_boundary` records; a 12,398-line transcript with its first boundary at
line 4031 and **1,942 pre-boundary turns still present**; **939 `thinking` blocks** retained.
`compact-anchor.sh` exists precisely because the post-compaction agent does not lack the *data* —
it lacks the **addressability**, which is one injected line, not a new session.

So the burden is on `/handoff` to earn the reset. It earns it here:

| Reach for | When | Why `/compact` cannot do it |
|---|---|---|
| **`/compact`** | **default** — context is hot and you are mid-task | keeps the process, the tools, and the thread |
| **`/handoff`** | a **plugin/hook change must go live** | the plugin cache is **version-keyed** and hooks load at **SessionStart**. `/compact` is the SAME process, so a merged hook fix stays inert no matter how much context you free |
| **`/handoff`** | the **next reader is not this session** — a different CLI, a later day, a teammate | `handoff.md` is the **cross-CLI contract**. Nothing in a compacted transcript is readable by Copilot or Codex |
| **`/handoff`** | the **task is genuinely done** | a fresh window starts on the finished state instead of carrying a completed task's history |

⛔ **The two halves of this skill are INDEPENDENT — do not conflate them.** *Writing the brief*
is durable and always worth it; *opening the window* is the expensive half. You may run steps
1–5 (write `handoff.md` + `summary.md` + `decisions.md`), then **`/compact` and keep going**. The
run dir banks the expensive knowledge either way, and it survives compaction, a crash, and the
session ending. **Skipping step 6 is a supported outcome, not an abandoned handoff.**

## Gotchas (read these; they are the load-bearing rules)

- **Same `task-id`.** Continue in `.ravenclaude/runs/<task-id>/`. Never invent a parallel id for the same work.
- **The hook cannot write the narrative.** `handoff-nudge` only nags. You fill `<!-- MODEL FILL -->` sections.
- **Seed is host-paired.** Grok: positional `grok "…"`. Chat: `chat-resume.md` + Cmd+N / New Chat + paste. CLI: interactive `copilot` (never a one-shot flag). **A Chat or CLI successor must not launch grok.**
- **Never `grok -p`**, never `--single`, never `--prompt-file`, never `--prompt-json`.
- **Cheap-lane is a different product.** One well-defined job with `cheap_lane: advise|agent` is `cheap-lane-delegation` (bounded, returns) — **do not spawn**. Quota escape, leftover multi-item work, plugin-cache reload, or "the next reader is not this session" is this skill. When `cheap_lane` is on and you still hand off, state in one clause why.
- **Never `/fork`.** Fork copies the bloated history — the opposite of a reset.
- **Never a Grok `SessionStart` injection as the seed.** Grok ignores SessionStart stdout.
- **Never a PreCompact persist hook.** Compaction is append-only.
- **Never encode 40% / 30% / 300K as a trigger.** The compact threshold is ~85%. Soft threshold default 70, always below auto-compact.
- **Do not read `GROK_SESSION_ID` from the agent env.** It is unset here. Detection is hook-only.
- **Never infer Chat from `TERM_PROGRAM=vscode` alone.** That is also Grok-in-VS-Code. Pass `--host` from what you actually are: `claude-code` | `grok` | `cli` | `chat` each have their own recipe; `codex` | `cursor` | `gemini` | `aider` | `windsurf` | `other` get a host-neutral block. ⛔ **Never substitute a host you are not.** An agent that read an older, shorter list here passed `--host chat` from a Claude Code session and produced a Copilot-Chat seed for a Claude Code successor (2026-08-18).
- **Chat Stop/nudge fire is unverified.** This skill is the Chat path when the **user or the model** invokes it. Copy-paste is always printed. Live Chat URI is owner-flagged best-effort.

## Procedure

1. Resolve `task-id`: user argument → most-recently-touched `.ravenclaude/runs/<id>/` in this repo → else propose a slug and create it. Never a second id for the same task.
2. Resolve **origin host** (you are Claude Code / Grok TUI / Copilot CLI / Copilot Chat — do not guess from `TERM_PROGRAM=vscode` alone) → `claude-code` | `grok` | `cli` | `chat`. On any other host, pass its `host-support.json` name (`codex` | `cursor` | `gemini` | `aider` | `windsurf`) or `other`; you will get a host-neutral block, which is correct.
3. `bash plugins/ravenclaude-core/bin/rc artifacts new <task-id>` (continue-in-place).
4. `python3 plugins/ravenclaude-core/scripts/context-handoff.py write --task-id <id> --host <pair>` to refresh the derive-fill skeleton.
5. **Fill** every `<!-- MODEL FILL -->` section in `.ravenclaude/runs/<id>/handoff.md`. Update `summary.md` / `decisions.md` only when there is real content — never stamp empty files.
6. Spawn: `bash plugins/ravenclaude-core/bin/rc handoff --task-id <id> --host <pair> --recipe same-host`. The script prints a `PRODUCT` line (`NEW interactive session` / `not cheap-lane-delegation`) **before** it launches — that line is the product label; do not treat a launch as cheap-lane. If `cheap_lane` is `advise`/`agent`, it also prints that the spawn is a host-switch. If spawn is `copy-paste-only` or fails, print the exact copy-paste block. Report which path was taken.
7. If stdout contains `SUCCESSOR_ACK`, the successor has begun. **Stop this session.** You cannot `/quit` — the user closes the tab.

## Out of scope for this skill

- Changing Grok's auto-compact threshold.
- Dashboard dispatch as the spawn path.
- A per-host **launch recipe** beyond Claude Code / Grok / Copilot CLI / Copilot Chat. The other `host-support.json` hosts are accepted and answered host-neutrally; inventing a launch command for them is what is out of scope.
- A `copilot-chat` marketplace install column.
- Enabling origin `context_handoff`.
- Touching `hooks/compact-anchor.sh` or `scripts/compact-anchor.py`.
