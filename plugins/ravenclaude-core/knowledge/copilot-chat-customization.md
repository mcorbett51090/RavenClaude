# VS Code Copilot Chat — the customization surface (not Copilot CLI)

**Last reviewed:** 2026-09-01 (§6 added, §2 corrected) · previously 2026-08-14 · **Confidence:** high for docs-verified rows; live Preview hook fire and sibling built-in Write are `[unverified]` until the owner's probes (CL-3, CL-19).
**Owner:** worktree-lane isolation. This file is Chat-only. CLI lives in [`copilot-cli-customization.md`](copilot-cli-customization.md). **Do not merge the two files.**

This is **not** a claim that Chat is protected. CONTENTION (two writers, one tree) is not Chat context isolation.

## 1. Instruction load

VS Code Chat auto-loads workspace always-on instructions from `.github/copilot-instructions.md`, `AGENTS.md` (`chat.useAgentsMdFile`), and `CLAUDE.md` (`chat.useClaudeMdFile`). Path-scoped `.github/instructions/*.instructions.md` apply via `applyTo`. Parent-repo walk (`chat.useCustomizationsInParentRepositories`) is **disabled by default**; `rcwt new` pins that false so a user cannot turn parent-walk bleed back on by accident.

Sources: [custom-instructions](https://code.visualstudio.com/docs/agent-customization/custom-instructions) retrieved 2026-08-14.

Shared committed `AGENTS.md` across worktrees is **intentional**. The leak to stop is the other tree's dirty files, open editors, conversation, or `.ravenclaude/runs/<other-task>/`.

## 2. Preview hooks

Chat **Preview** can load agent hooks from workspace `.github/hooks/*.json` and `.claude/settings.json`, plus `~/.copilot/hooks`. Format is the Claude / Copilot CLI hook format (`PreToolUse` can deny). Orgs can disable it. Matchers are currently **ignored** — hooks run on every tool.

**Eight events**, PascalCase, Claude-compatible: `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `PreCompact`, `SubagentStart`, `SubagentStop`, `Stop`. `[docs-verified 2026-09-01 — code.visualstudio.com/docs/agent-customization/hooks]`

⛔ **`PreCompact`'s `continue`/`stopReason`/`systemMessage` are a verified no-op — do not design anything on them.** The docs' own "all hooks share a common output format" claim is **false for this one event**: `executePreCompactHook()` in `microsoft/vscode`'s shipping `extensions/copilot/src/extension/prompts/node/agent/summarizedConversationHistory.tsx` (source-verified 2026-09-01, `main` branch) never reads `stopReason` or `systemMessage` and never calls the UI-surfacing `hookProgress` — it only logs `resultKind === 'error'` and swallows everything else. `PreCompact` is the *only* one of the eight events with no consumer of its control fields (the other seven route through `processHookResults`, which does honor `stopReason`/block + the doc-claimed `systemMessage` display). It also **does not fire at all on manual `/compact`** — that handler's `promptContext` omits the `request` field the hook check requires (confirmed + corroborated by upstream issue `microsoft/vscode#299566`, closed **unowned**, not fixed). Treat `PreCompact` as fire-and-forget archiving only (its own source comment: "to allow hooks to archive transcripts or perform cleanup") — never as a way to warn the user or shape what survives compaction. `SessionStart` and `UserPromptSubmit` DO have real, working `additionalContext` injection (upstream open feature request `microsoft/vscode#308121` asks for the same on `PreCompact`, unimplemented — its PR `#308297` closed unmerged 2026-07-04).

Sources: [hooks](https://code.visualstudio.com/docs/agent-customization/hooks) + [hooks-reference](https://code.visualstudio.com/docs/agents/reference/hooks-reference) 2026-08-14, corrected/expanded 2026-09-01 against `microsoft/vscode@main` source and the two upstream issues above.

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

## 6. Programmatic compaction — the extension seam (added 2026-09-01)

Repo-level hooks (§2) cannot trigger, gate, or shape Copilot Chat's context compaction — §2's
`PreCompact` finding rules that out. A **VS Code extension** (a real installed/published
extension, not a hooks-JSON contribution) can, using only **stable, public API** — no proposed-API
allowlist, publishable to the Marketplace:

```ts
vscode.commands.executeCommand('workbench.action.chat.open', {
  query: '/compact ' + steeringText,
  preserveInput: true,
});
```

This is verbatim how Microsoft's own Copilot extension implements its own "compact" button
(`extensions/copilot/src/extension/conversation/vscode-node/conversationFeature.ts:277`,
source-verified 2026-09-01). Text after `/compact` flows through `request.prompt` →
`summarizationInstructions` → is injected verbatim into the summarization **system prompt** under
a `## Additional instructions from the user:` heading
(`extensions/copilot/src/extension/intents/node/agentIntent.ts:559`,
`.../prompts/node/agent/summarizedConversationHistory.tsx:192-196`). This is a real,
extension-callable content-injection path into compaction — the only one found.

⛔ **Works only for EXPLICIT/triggered compaction, never automatic/background compaction.**
`summarizationInstructions` has exactly 2 references repo-wide; the auto-compact code path
(`backgroundSummarizer.ts`) has zero, confirmed via a positive-controlled search (the file
downloaded and was searchable — the zero is a real absence). Two Microsoft-maintainer-closed
feature requests (`#289194`, `#319648`) confirm no first-party API for automatic-compaction
influence is planned. Design around triggering compaction *yourself*, proactively — never around
influencing the automatic trigger.

**The proposed-API alternatives are unusable by a third party.** `ChatSummarizer`
(`vscode.proposed.defaultChatParticipant.d.ts`) and `chatContextProvider`
(`vscode.proposed.chatContextProvider.d.ts`, tracked at open issue `microsoft/vscode#271104`,
milestone 1.137.0) both exist, but this machine's own installed VS Code `product.json`
(`extensionEnabledApiProposals`) allowlists them **exclusively** to `GitHub.copilot-chat` —
verified directly against the shipping build, 2026-09-01. Do not design around either.

**No live visibility into an ongoing conversation.** `ChatContext.history` (stable API) is scoped
to an **@-mentioned chat participant only** — a background/non-participant extension cannot
silently observe a session's turns. The viable design is agent-cooperative (register a
`vscode.lm.registerTool` the model itself calls, since it already has full context from inside its
own turn) plus a manual command/status-bar affordance as a human-triggered backstop — never a
heuristic snooping on hidden conversation state.

Implemented in [`../vscode-extension/`](../vscode-extension/README.md) (`ravenclaude-precompact-guard`).

## 7. Honesty

- Do not write "Chat is protected" or "Copilot is protected" without the Preview qualifier.
- Do not add a `copilot-chat` key to `host-support.json` `hosts` (the dashboard treats every host key as an install column).
- Keep host key `copilot` labeled **GitHub Copilot CLI**.
