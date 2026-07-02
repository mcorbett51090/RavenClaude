# dotfiles

Personal **GitHub Codespaces** dotfiles. When enabled, GitHub runs [`install.sh`](install.sh)
automatically on **every new Codespace I open — in any repo** — so the tools below are already
there, with zero manual install.

## One-time setup (do this once)

1. Go to **GitHub → Settings → [Codespaces](https://github.com/settings/codespaces)**.
2. Under **Dotfiles**, check **“Automatically install dotfiles.”**
3. Select the repository **`mcorbett51090/dotfiles`**.
4. Save. The next Codespace you create (or rebuild) runs `install.sh` automatically.

## What it installs

| Tool | How | Skipped when |
|------|-----|--------------|
| **Claude Code CLI** | native installer (`https://claude.ai/install.sh`), npm fallback | already present |
| **ravenclaude-core** plugin | `claude plugin marketplace add mcorbett51090/RavenClaude` → `claude plugin install ravenclaude-core@ravenclaude` | already installed |
| **prettier** (v3) | npm global (`~/.npm-global`, no sudo) | already present / no npm |
| **actionlint** (v1.7.12) | checksum-verified GitHub-Releases binary → `~/.local/bin` | already present |
| **ruff** (0.15.20) | checksum-verified GitHub-Releases binary → `~/.local/bin` | already present |
| **GitHub Copilot CLI** | `npm i -g @github/copilot` | already present / Node < 22 |
| **VS Code extensions** | `code --install-extension` (list in `install.sh`) | `code` CLI absent |

## Design guarantees

- **Can’t break a Codespace.** Every step is failure-isolated; `install.sh` always exits `0`. A
  failed step is logged and skipped, never fatal.
- **Idempotent.** Re-running installs nothing already present.
- **Minimal-image tolerant.** On an image without Node, Claude (native), actionlint, ruff, and
  extensions still install; Node-gated tools skip with a logged reason.
- **No secrets.** This is a public repo. Authentication is never automated.

## Finishing authentication (the one thing that can’t be scripted)

After a new Codespace starts, `install.sh` prints an auth checklist. If it lists items, run them in
the terminal:

```bash
gh auth login     # if GitHub CLI isn't already authenticated
claude            # then complete the browser login if prompted
```

If `ravenclaude-core` wasn’t installed at create time (e.g. it needed a login first), a small hook
retries automatically on your next terminal and removes itself once it succeeds.

## Logs & re-running

- Full timestamped log: **`~/.dotfiles-install.log`** (stdout *and* stderr).
- Re-run manually any time:

  ```bash
  bash /workspaces/.codespaces/.persistedshare/dotfiles/install.sh
  ```

  Read the summary line (`N ok, M skipped, K soft-failed`) and the log to see what happened.

## What it deliberately does NOT do

- Edit any repo’s `devcontainer.json`.
- Store secrets or tokens.
- Install Claude plugins other than `ravenclaude-core`.

---

<sub>Built with the RavenClaude FORGE pipeline (two cross-model panels + correlated-error critic +
red-team). Plan: `RavenClaude/docs/research/2026-06-30-codespace-autoprovision/plan.md`.</sub>
