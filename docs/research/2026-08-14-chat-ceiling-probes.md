# Chat ceiling — owner probe records (CL-3, CL-19b)

**Status: UNFILLED.** Both probes need a human in **VS Code Copilot Chat Agent mode**;
no CLI can drive that surface. Until the tables below carry real observations,
`surfaces.chat.supported` stays `false` and Chat is the **operator lane only** —
do not claim Chat is protected.

Procedure: `plugins/ravenclaude-core/templates/worktree-lane/chat-ceiling.md`.
Plan: `docs/plans/2026-08-14-chat-write-deny.md`.

⛔ **This file is the record, not the run dir.** `.ravenclaude/runs/forge/**` is
gitignored (`.gitignore:4`); the previous session's `probe-cl3.md` / `probe-cl19.md`
were written there and were lost with their worktree — they were never in PR #941.
Per `AGENTS.md` § "Where work files go", evidence a teammate needs is committed-tier.
Redact secrets and home paths before anything lands here.

---

## CL-3 — sibling Write

Window opened on worktree **A** only (`code -n <A>`, not multi-root); new Agent-mode
Chat session; ask the agent to Write an **absolute path** under sibling worktree **B**.

| Field | Observation |
|---|---|
| Date run | |
| VS Code version | |
| Copilot Chat version | |
| Outcome (keep / undo / approval dialog / no-op) | |
| Did the file appear under sibling B? | |
| Notes (redacted) | |

**Do not guess.** An unrun probe stays blank — a blank row is honest, a filled-in
guess is a false premise the next build phase would rest on.

---

## CL-19b — Preview hook fire

Projected `.github/hooks` present (`ravenclaude install` if needed); `chat.hooks.enabled`
on; org policy allows Preview hooks. One mutating Chat tool call (a Write/edit **inside**
the opened folder is enough). Channels: **Developer: Show Agent Debug Logs** and
**GitHub Copilot Chat Hooks**.

| Field | Observation |
|---|---|
| Date run | |
| Did a PreToolUse hook fire at all? | |
| Which command actually ran (`argv`) | |
| `copilot-hook-adapter.sh` vs raw `.claude/settings.json` hook | |

### Observation slots (record; do not map)

These are **not** adapter targets — record what is present, do not build a map from it.

| Slot | Present? | Value (redacted) |
|---|---|---|
| `session_id` / `sessionId` | | |
| `cwd` / `workspaceRoot` | | |
| `tool_name` / `toolName` | | |
| path field name(s) | | |
| `toolArgs` present? | | |
| `tool_input` object? | | |
| `files[]` shape (string / object / absent) | | |
| argv / which hook file ran | | |

### Raw PreToolUse stdin (one dump, redacted)

```json
```

---

## What filling these unblocks

A dump-derived adapter map is a **later PR**, not this one. Phases 6–7 stay a
documented no-op: a docs map without proven fire is a shim, and a pre-commit snippet
is not a write-deny. Hooked hosts (Claude / Copilot CLI / Codex / Gemini) already have
FOREIGN-TREE (`db114e93`, v0.268.0, #933) — Chat is the gap this reserves, not
unfinished wiring.
