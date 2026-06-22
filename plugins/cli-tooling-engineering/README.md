# cli-tooling-engineering

> Build command-line tools and TUIs that feel native to the shell — the **CLI sibling** of the app-craft cluster (`backend` / `frontend` / `mobile` / `desktop-app` / `api`). A 4-agent team for the command surface, the output + exit-code contract, terminal UIs, and distribution.

## What you get

- **4 specialist agents**
  - `cli-architect` — the command/subcommand + flag/positional surface, config precedence, the output + exit-code contract, the CLI-vs-TUI-vs-library call, and distribution strategy.
  - `cli-implementation-engineer` — the idiomatic parser (Cobra / clap / argparse / Click / oclif / yargs), subcommands, config loading, a clean `--json` mode, exit-code mapping, stdin/TTY/signal handling, completions.
  - `tui-engineer` — whether a full-screen TUI is warranted, the framework (Ink / Bubble Tea / Textual / ratatui), the render loop, resize/non-TTY fallback, accessibility.
  - `cli-distribution-engineer` — single-binary vs runtime package, cross-compile matrix, install channels (Homebrew / Scoop / winget / npm / pipx), a build-stamped `--version` + update path.
- **5 skills** — cli-design-and-arg-parsing, output-and-exit-code-contract, tui-design, cli-distribution-and-packaging, shell-completions-and-config.
- **A decision-tree knowledge bank** — command-surface + output/exit-code + framework-choice + distribution Mermaid trees, a config-precedence prior, and a dated 2026 capability map (`[verify-at-use]`).
- **12 best-practices**, **4 templates**, **4 commands**, **1 advisory hook**, a **3-scenario bank**, and an **`.lsp.json`** (TypeScript + Rust + Go + Python).

## Commands

- `/cli-tooling-engineering:design-cli` — design the command/flag surface, config precedence, output + exit-code contract, and the CLI-vs-TUI call.
- `/cli-tooling-engineering:audit-cli-ux` — audit an existing CLI against the output/exit-code + shell-citizenship rules and fix the violations.
- `/cli-tooling-engineering:plan-cli-distribution` — plan single-binary vs runtime, the cross-compile matrix, install channels, and `--version` + updates.
- `/cli-tooling-engineering:add-shell-completions` — generate completions (bash/zsh/fish/PowerShell) and design config discovery + env-var conventions.

## House opinions

1. Design the command surface first — it's the hardest thing to change once scripts depend on it.
2. Config precedence is flags > env > file > default, resolved into one object.
3. Human-readable by default, machine-readable (`--json`) on demand — never interleave logs into the JSON.
4. Data to stdout, diagnostics to stderr; exit codes are a public API — never exit `0` on a real failure.
5. Gate color/progress behind `isatty` + `NO_COLOR`/`FORCE_COLOR`; read stdin when piped.
6. Confirm destructive actions but honor `--force`/`--yes`; handle signals and clean up.
7. Prefer a single static binary; ship a build-stamped `--version`, generated completions, and a man page.

## Seams

Service/business logic → `backend-engineering` · CI release + code-signing → `devops-cicd` · the desktop GUI sibling → `desktop-app-engineering` · man pages/docs → `technical-writing-docs` · appsec verdicts → `ravenclaude-core/security-reviewer`.

## Requirements

Requires `ravenclaude-core@>=0.7.0`. The `.lsp.json` servers (typescript-language-server, rust-analyzer, gopls, pyright) are installed separately by the consumer; the plugin ships the config, not the binaries.

See [`CLAUDE.md`](CLAUDE.md) for the full team constitution and [`CHANGELOG.md`](CHANGELOG.md) for version history.
