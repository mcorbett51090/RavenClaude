# `scripts/` — utility scripts

Reusable utility scripts. Keep each script self-documenting (header comment with usage + assumptions) and idempotent where the operation allows.

## Worktree tooling

Helpers for isolating parallel agent work in disposable git worktrees under `.claude/worktrees/<slug>` (each on its own `agent/<slug>` branch), so background agents can't collide on the working tree.

| Script | Purpose |
| --- | --- |
| `worktree-new.sh <slug> [base]` | Create one isolated worktree at `.claude/worktrees/<slug>` on branch `agent/<slug>` (branches off `base`, default `HEAD`). |
| `worktree-clean.sh <slug>\|--status\|--all [--force]` | Safely remove worktrees — refuses a dirty tree without `--force`; `--status` lists each tree clean/dirty; `--all` removes the clean ones. |
| `worktree-swarm.sh <slug>...\|--task "<prompt>"\|--status\|--clean-all` | Fan out N worktrees and print ready-to-paste `claude --bg` dispatch lines for a parallel agent swarm; `--status` / `--clean-all` delegate to `worktree-clean.sh`. |

Each script prints full usage when run with no args or `--help`.
