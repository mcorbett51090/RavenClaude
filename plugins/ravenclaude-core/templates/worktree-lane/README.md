# Worktree-lane templates

`rcwt new` writes these into a **consumer worktree**, not into the marketplace
checkout.

- `settings.json` — parent-walk pin only (`chat.useCustomizationsInParentRepositories: false`). Merged add-absent-keys; never overwrites a key the consumer already set.
- `chat-ceiling.md` — probe checklist. **Not Chat enforcement.** `rcwt` merges the sandbox key only when `RCWT_CHAT_CEILING=1`.
- `.ravenclaude/lane.md` — written by `write-lane-stamp.sh`. Tree-local identity. Gitignored. Do not commit it. Do not rewrite root `AGENTS.md` to name one task.

## Operator layout (the observed Chat close)

1. Open **this folder only** (`code -n <worktree>`).
2. Do **not** `Add Folder to Workspace` a sibling worktree (multi-root = one context pool).
3. Do **not** hop sessions in the Agents window.
4. Start a **new Chat session** per worktree.
5. Sandbox, if you later set it, does **not** cover built-in file tools.
