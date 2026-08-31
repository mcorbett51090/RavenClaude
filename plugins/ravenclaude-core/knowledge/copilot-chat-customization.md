# VS Code Copilot Chat — the customization surface (not Copilot CLI)

**Last reviewed:** 2026-08-14 · **Confidence:** high for docs-verified rows; live Preview hook fire and sibling built-in Write are `[unverified]` until the owner's probes (CL-3, CL-19).
**Owner:** worktree-lane isolation. This file is Chat-only. CLI lives in [`copilot-cli-customization.md`](copilot-cli-customization.md). **Do not merge the two files.**

This is **not** a claim that Chat is protected. CONTENTION (two writers, one tree) is not Chat context isolation.

## 1. Instruction load

VS Code Chat auto-loads workspace always-on instructions from `.github/copilot-instructions.md`, `AGENTS.md` (`chat.useAgentsMdFile`), and `CLAUDE.md` (`chat.useClaudeMdFile`). Path-scoped `.github/instructions/*.instructions.md` apply via `applyTo`. Parent-repo walk (`chat.useCustomizationsInParentRepositories`) is **disabled by default**; `rcwt new` pins that false so a user cannot turn parent-walk bleed back on by accident.

Sources: [custom-instructions](https://code.visualstudio.com/docs/agent-customization/custom-instructions) retrieved 2026-08-14.

Shared committed `AGENTS.md` across worktrees is **intentional**. The leak to stop is the other tree's dirty files, open editors, conversation, or `.ravenclaude/runs/<other-task>/`.

## 2. Preview hooks

Chat **Preview** can load agent hooks from workspace `.github/hooks/*.json` and `.claude/settings.json`, plus `~/.copilot/hooks`. Format is the Claude / Copilot CLI hook format (`PreToolUse` can deny). Orgs can disable it. Matchers are currently **ignored** — hooks run on every tool.

Sources: [hooks](https://code.visualstudio.com/docs/agent-customization/hooks) 2026-08-14.

Live fire of a projected `worktree-guard` on **this** machine is `[unverified — premise not disconfirmed: G3b owner-gated 2026-08-14]` (CL-19). CLI projection is **not** Chat coverage.

## 3. Agents window vs Chat view

Chat view is scoped to the workspace open in **that** window. The Agents window + Agent Host **share sessions across workspaces**. Two windows on two worktrees do **not** share the Chat-view `@workspace` index; they **can** share a session if the Agent Host / Agents window is used.

A **multi-root** window with two worktree folders is one context pool. Do not generate that layout. `rcwt new` opens `code -n <worktree>` (one folder, new window).

Sources: [agents overview](https://code.visualstudio.com/docs/agents/overview), [agents-window](https://code.visualstudio.com/docs/agents/run/agents-window) 2026-08-14.

## 4. Lane workflow

- One VS Code window per worktree.
- New Chat session per window.
- Never continue an Agents-window session started for another workspace.
- `.ravenclaude/lane.md` is tree-local identity (gitignored). Do not rewrite root `AGENTS.md` to name one task.
- See [`isolate-parallel-claude-instances-in-git-worktrees.md`](../best-practices/isolate-parallel-claude-instances-in-git-worktrees.md) operator-layout table. Sleipnir remains a label.

## 5. Ceiling table

| Lane | What we can enforce | What we cannot |
|---|---|---|
| **Write** | FOREIGN-TREE on hooked hosts (Claude, Copilot CLI, Codex, Gemini). Chat built-in Write to a sibling path is `[unverified]` (CL-3). Sandbox does **not** cover built-in file tools. | Shared `~/.copilot`. Agent Host session reuse. |
| **Context** | Operator layout (`code -n`, no multi-root, new session). SessionStart LANE pin when hooks fire. | Agents-window session share. Open-editor / conversation bleed inside one window. |
| **Git** | FOREIGN-TREE on `git -C` / `GIT_WORK_TREE` into a sibling. Git already refuses a branch checked out elsewhere. | A human running git in the wrong window on purpose. |

## 6. Honesty

- Do not write "Chat is protected" or "Copilot is protected" without the Preview qualifier.
- Do not add a `copilot-chat` key to `host-support.json` `hosts` (the dashboard treats every host key as an install column).
- Keep host key `copilot` labeled **GitHub Copilot CLI**.
