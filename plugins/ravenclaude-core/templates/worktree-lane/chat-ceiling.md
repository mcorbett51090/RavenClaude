# Chat ceiling (not Chat enforcement)

This file is the **one reversible Chat-adjacent artifact** from FORGE
`copilot-chat-worktree-lanes` (G3b owner-gate) and leftover
`forge/chat-write-deny` (G3b 2026-08-14). It is a probe checklist and an
optional settings snippet. **It is not Chat enforcement.**

VS Code Copilot Chat built-in file tools are **not** OS-sandboxed. Terminal
sandbox (`chat.agent.sandbox.enabled`) does **not** cover those tools. Preview
hooks *may* load `.github/hooks` when org policy / `chat.hooks.enabled` allows
it; live fire on a given machine is `[unverified]` until the probes below run.

Do not claim this file covers the Chat surface. It is not Chat enforcement.

Hooked hosts (Claude / Copilot CLI / Codex / Gemini) already have FOREIGN-TREE.
Chat gets the **operator lane only** until CL-3 and CL-19b are settled by a
human in VS Code Copilot Chat Agent mode.

## Owner probes

Copy-paste these in a VS Code window. This CLI cannot run Chat Agent mode.

### Procedure — CL-3 sibling Write

1. Open a window on worktree A only: `code -n <A>`. Do **not** add sibling B
   as a second folder (multi-root is one context pool).
2. Start a **new** Chat session. Agent mode.
3. Ask the agent to Write an **absolute path** under sibling worktree B.
4. Record keep / undo / approval dialog / no-op. Do not guess.

Write the redacted result into the **tracked** probe record:

- `docs/research/2026-08-14-chat-ceiling-probes.md` → the **CL-3** table

⛔ Do **not** record the result only under `.ravenclaude/runs/forge/**`. That path is
gitignored (`.gitignore:4`), so it is machine-local and disposable — the previous
run's `probe-cl3.md` / `probe-cl19.md` were lost with their worktree and were never
in the PR. A run-dir copy is fine as scratch; the `docs/` file is the record.
Per `AGENTS.md` § "Where work files go", anything a teammate needs is committed-tier.

Until that table is filled, do not claim Chat can or cannot land sibling Write.

### Procedure — CL-19 Preview hook fire

1. Projected `.github/hooks` present (`ravenclaude install` if needed).
2. `chat.hooks.enabled` on. Org policy allows Preview hooks.
3. One mutating Chat tool call (Write/edit of a path **inside** the opened
   folder is enough).
4. Dump one raw PreToolUse stdin (redact secrets / home paths).
5. Record **which command actually ran** (`argv`):
   `copilot-hook-adapter.sh …` vs a raw `.claude/settings.json` hook.
6. Output channels: **Developer: Show Agent Debug Logs** and
   **GitHub Copilot Chat Hooks**.

Write the redacted dump into the **tracked** probe record:

- `docs/research/2026-08-14-chat-ceiling-probes.md` → the **CL-19b** dump + slot table

⛔ Same rule as CL-3: `.ravenclaude/runs/forge/**` is gitignored and does not survive
the worktree. Redact secrets and home paths **before** the dump reaches a tracked file.

### Observation slots (record; do not map)

Look for these keys on the dump. They are **not** adapter targets.

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

Docs-verified vocabulary to **look for** (VS Code hooks pages, 2026-08-14) —
**not** “put these in the adapter”: `editFiles`, `createFile`, `create_file`,
`replace_string_in_file`, `runTerminalCommand`.

Do **not** invent a sample PreToolUse payload as if it were live-captured.
Do **not** edit `copilot-hook-adapter.sh` from docs alone.
Do **not** flip `host-support.json` `surfaces.chat.supported`.
Do **not** claim Chat is protected after a partial probe.

Until both probe files exist with a dated keep/undo/payload row **or** a dated
`skipped` line, Chat hook teeth stay
`[unverified — premise not disconfirmed: G3b owner-gated 2026-08-14]`.

## Phase 6 (adapter wiring)

Phase 6 (adapter wiring): no-op 2026-08-14 — CL-19b probe skipped; no
dump-derived map. Do not ship RC_CHAT_PREVIEW_MAP.

## Optional settings snippet

`rcwt` merges `chat.agent.sandbox.enabled: true` **only** when
`RCWT_CHAT_CEILING=1`. Default is off. Sandbox still does **not** cover
built-in file tools.

```json
{
  "chat.agent.sandbox.enabled": true
}
```
