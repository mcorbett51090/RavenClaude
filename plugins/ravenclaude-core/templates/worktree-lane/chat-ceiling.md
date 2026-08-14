# Chat ceiling (not Chat enforcement)

This file is the **one reversible Chat-adjacent artifact** from FORGE
`copilot-chat-worktree-lanes` (G3b owner-gate). It is a probe checklist and an
optional settings snippet. **It is not Chat enforcement.**

VS Code Copilot Chat built-in file tools are **not** OS-sandboxed. Terminal
sandbox (`chat.agent.sandbox.enabled`) does **not** cover those tools. Preview
hooks *may* load `.github/hooks` when org policy / `chat.hooks.enabled` allows
it; live fire on a given machine is `[unverified]` until the probes below run.

Do not claim this file covers the Chat surface. It is not Chat enforcement.

## Owner probes

### CL-3 — sibling Write

In VS Code Copilot Chat Agent mode, with the window opened **only** on worktree
A, ask the agent to Write an **absolute path** under sibling worktree B.

Record keep / undo / approval dialog / no-op (redacted) as
`.ravenclaude/runs/forge/copilot-chat-worktree-lanes/probe-cl3.md`.

### CL-19 — Preview hook fire

With projected `.github/hooks` present and `chat.hooks.enabled` on, does one
Chat tool call produce a PreToolUse stdin payload that `worktree-guard.sh`
understands (`session_id` / `sessionId`, `cwd`, tool name, a file-path field)?

Dump one payload (redacted) as
`.ravenclaude/runs/forge/copilot-chat-worktree-lanes/probe-cl19.md`.

Until both exist, Chat hook teeth stay
`[unverified — premise not disconfirmed: G3b owner-gated 2026-08-14]`.

## Optional settings snippet

`rcwt` merges `chat.agent.sandbox.enabled: true` **only** when
`RCWT_CHAT_CEILING=1`. Default is off. Sandbox still does **not** cover
built-in file tools.

```json
{
  "chat.agent.sandbox.enabled": true
}
```
