# Plan — Auto-provision every new Codespace via a personal dotfiles repo

**Slug:** `codespace-autoprovision` · **Depth:** standard · **Owner:** Matt (mcorbett51090)
**Forged:** G0–G7, two cross-model panels (Opus + Sonnet) + correlated-error critic + red-team.

## Goal
Every new GitHub Codespace Matt opens — **any repo in his account** — arrives with the Claude
Code CLI, the `ravenclaude` marketplace + `ravenclaude-core` plugin, his secondary CLIs, a
recommended VS Code extension set, and non-blocking auth nudges, with **zero** manual hunt-and-install.

## Mechanism (only one that satisfies "every repo, no per-repo edits")
A public personal **dotfiles repo** `mcorbett51090/dotfiles` with a single idempotent `install.sh`
that GitHub Codespaces auto-runs on every codespace once Matt flips one account setting. Alternatives
(devcontainer Feature / prebuild / custom base image) all require per-repo config **and** can't carry
per-user Claude *plugin* state — rejected as the global default (a Feature is a fine *complement*
later for repos Matt owns).

---

## The install.sh contract (incorporates every red-team mitigation)

Single `install.sh` at repo root, functions not separate files (simplest for a personal repo).

```
set -euo pipefail                # first-party logic stays strict
exec > >(tee -a ~/.dotfiles-install.log) 2>&1   # RT#5: stdout AND stderr to a persistent log
export PATH="$HOME/.local/bin:$HOME/.npm-global/bin:$PATH"   # RT#2: fix PATH in THIS process up front
export NPM_CONFIG_PREFIX="$HOME/.npm-global"     # RT#7: env var (survives subshells), not `npm config set`
```

`run_step "<label>" <fn>` — runs the step body so a non-zero exit is **logged and swallowed**;
install.sh **always exits 0** (a broken step can never abort codespace creation). Prints a final
`N ok / M skip / K fail` summary. Each `run_step` emits a `→ [i/total] <label>…` progress marker
(RT#8) so the Codespaces setup spinner shows life.

### Steps (each idempotent, each failure-isolated)
| # | Step | Key decisions (from tiebreaks + red-team) |
|---|------|-------------------------------------------|
| 1 | **Node ≥22** | Guard is **version-aware** (`node major ≥ 22`), not `command -v node` (RT#4). Try nvm → n → apt(sudo); clean skip (rc=75) if no privileged path. |
| 2 | **Claude Code CLI** | **Primary = `claude install` (Node-free native build)** (CE2); fallback `npm i -g @anthropic-ai/claude-code`. Skip if `claude` resolves. |
| 3 | **ravenclaude-core plugin** | `claude plugin marketplace add mcorbett51090/RavenClaude` (PUBLIC repo — unauthenticated clone, CE1) → `claude plugin install ravenclaude-core@ravenclaude`. Idempotency via `claude plugin list \| grep ravenclaude-core`. **+ deferred self-heal:** append a one-shot guard to `~/.bashrc` that re-runs the install on first interactive shell if the plugin is still absent (RT#3 belt-and-suspenders). |
| 4 | **prettier@3** | npm global into `~/.npm-global` (no sudo). Major-pin (not patch-pin). |
| 5 | **actionlint v1.7.7** | Checksum-pinned binary from GitHub Releases → `~/.local/bin`, sha256-verified (matches repo Gate 10). Download authenticated with `$GITHUB_TOKEN` when set (RT#6 rate-limit). |
| 6 | **ruff** | **Pinned, sha256-verified GitHub-Releases binary** → `~/.local/bin` — NOT `curl\|sh` (RT#1) and NOT `pip` (PEP-668). |
| 7 | **Copilot CLI** | `npm i -g @github/copilot` (binary verified = `copilot`, v1.0.66). Gated on Node≥22 integer-compare. |
| 8 | **VS Code extensions** | `code --install-extension` per ID; guard `command -v code` (skip on headless). Default anchors `github.copilot`, `github.copilot-chat` in a clearly-commented array **Matt extends**. |
| 9 | **Auth nudge** | Probe `gh auth status` (verified); for Claude print an **unconditional** login hint (no fragile `claude auth status` dependency). Writes a hint to `~/.bashrc`; **never** runs interactive login. **No secrets in the repo.** |

PATH exports also appended idempotently to `~/.bashrc` **and** `~/.profile` (login shells may source
only `.profile`) — guarded by a marker grep so re-runs don't duplicate.

---

## Dependency DAG
```
[1 Node≥22] ──┬─► [2 claude] ─► [3 ravenclaude-core]      ← CRITICAL PATH (the actual goal)
              ├─► [4 prettier]
              └─► [7 copilot]
(node-independent, parallelizable): [5 actionlint] [6 ruff] [8 vscode-ext]
[9 auth-nudge] last (after gh/claude exist so it can probe).
```
Critical path = Node → claude → plugin. Everything else is optional and isolated; its failure never
touches the critical path. (Optional: background the node-independent binary downloads with `& wait`
to cut cold-start latency — RT#8; deferred as an enhancement to keep logs readable.)

## Alternatives considered
| Approach | Verdict |
|---|---|
| **dotfiles `install.sh`** (chosen) | Only mechanism hitting *every* repo with zero per-repo edits + carries per-user plugin state. |
| devcontainer Feature | Cleaner caching, but per-repo opt-in; can't hold per-user plugin state. Complement, not default. |
| Codespaces prebuild | Per-repo; speed optimization only; never bakes personal Claude auth. |
| Custom base image | High maintenance; per-repo; plugin state still per-user. Overkill. |

---

## Phased build + per-phase acceptance test
1. **Scaffold** — create public `mcorbett51090/dotfiles`; push `install.sh` stub + `README.md` + `.gitignore` (`*.log`). *Accept:* `gh repo view … --json visibility` = PUBLIC; `bash -n install.sh` = 0.
2. **Safety core** — `run_step` wrapper + `exec … tee … 2>&1` + up-front PATH/`NPM_CONFIG_PREFIX` exports + summary. Wire a deliberately-failing fixture step. *Accept:* with the failing fixture, `install.sh; echo $?` prints **0**; summary counts the FAIL. (Proves "can't break a codespace" before any real installer.)
3. **Critical path** — steps 1–3. *Accept:* fresh codespace → `claude --version` works, `claude plugin list` shows **only** `ravenclaude-core`. Re-run = all "already present", zero installs.
4. **Optional tools** — steps 4–7. *Accept:* `prettier --version`, `actionlint --version`, `ruff --version`, `copilot --version` all resolve at pinned versions (or log a clean skip on a minimal/Node<22 image). Checksums verified for actionlint + ruff.
5. **Extensions + nudge** — steps 8–9. *Accept:* `code --list-extensions` contains the defaults; nudge prints on first terminal; `git grep -iE 'ghp_|sk-|token|secret'` finds nothing but nudge text.
6. **Live E2E** — Matt enables the Settings toggle; open a brand-new codespace on an **unrelated** repo. *Accept:* the §"Definition of done" signals all pass.

## Definition of done
- `mcorbett51090/dotfiles` public; `install.sh` executable at root; `bash -n` + `shellcheck` clean.
- Safety proof (Phase 2): an injected failing step leaves exit 0.
- Fresh unrelated-repo codespace: `claude` + `ravenclaude-core` present; secondary CLIs resolve or log a clean skip; default extensions installed; nudge shown.
- Idempotent: second run installs nothing new, exits 0.
- Minimal-image resilient: Node-less image still installs claude (native), actionlint, ruff, extensions; Node-gated tools skip with a clear logged reason.
- Secret-free; this repo's `.devcontainer/post-create.sh` untouched.
- README documents the one-time **Settings → Codespaces → Automatically install dotfiles → select `mcorbett51090/dotfiles`** toggle, the install inventory, the finish-auth steps, and "re-run `~/.dotfiles…/install.sh` and read the summary" troubleshooting.

## Risk matrix (critic + red-team, residual after mitigation)
| Risk | Sev | Mitigation | Residual |
|---|---|---|---|
| RT#2 PATH not in running shell | HIGH | export PATH in script body up front | low |
| RT#1 ruff `curl\|sh` supply chain | HIGH | pinned sha256-verified binary | low |
| RT#3 plugin install pre-auth loop | HIGH | deferred self-heal hook + (plugin ops are git/cache, likely auth-free) | low |
| RT#7 npm prefix lost in subshell | MED | `NPM_CONFIG_PREFIX` env var | low |
| RT#4 Node guard not version-aware | MED | integer-compare guard | low |
| RT#6 shared-IP GitHub rate limit | MED | `$GITHUB_TOKEN` on downloads | low |
| RT#5 stderr not logged | MED | `2>&1` into tee | resolved |
| RT#8 slow cold start / perceived hang | LOW→perceived-HIGH | progress markers now; background downloads = enhancement | accepted |
| Input gap: VS Code extension list | — | default anchors + commented array Matt extends | accepted (Matt's call) |

## Open settling steps carried forward (none block the design)
- claim 3 (clone path) — cosmetic; script uses `$HOME`, re-confirm on first run.
- `claude plugin install` auth-need — covered by the RT#3 self-heal hook regardless of outcome.

## Landing & execution
- **Execution:** `use_local` — small, privacy-clean, research done; buildable here (GitHub MCP can
  create the repo + push files; only the account Settings toggle is Matt's manual one-time step).
- **Landing:** this plan touches **no file in this repo** (the deliverable is an external repo), so
  `plan.md` is a pure design/research doc → commit to **main** under `docs/research/` (docs-only, no
  PR per AGENTS.md), no version bump, no Gate slot, no layout change.
