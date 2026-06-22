# CLI Tooling Engineering Plugin — Team Constitution

> Team constitution for the `cli-tooling-engineering` Claude Code plugin — **4** specialist agents for building command-line tools and TUIs that feel native to the shell: the command surface, the output + exit-code contract, terminal UIs, and distribution. The Team Lead (the top-level Claude session, typically also running `ravenclaude-core`) dispatches the right specialist(s) and integrates their reports.
>
> **Orientation:** this file is **domain-specific**. For the domain-neutral team constitution inherited by every plugin, see [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md). For the meta-repo developer guide, see [`../../CLAUDE.md`](../../CLAUDE.md).

---

## 1. Team roster

| Agent | Owns | When to spawn |
|---|---|---|
| [`cli-architect`](agents/cli-architect.md) | The command/subcommand + flag/positional surface, config precedence, the output + exit-code contract, the CLI-vs-TUI-vs-library decision, the interactive-vs-scriptable boundary, and distribution strategy | "what should the commands/flags be?", "CLI, TUI, or library?", "how should flags/env/config combine?", "what does this tool print + exit?" |
| [`cli-implementation-engineer`](agents/cli-implementation-engineer.md) | The idiomatic parser (Cobra/clap/argparse/Click/oclif/yargs), subcommands, config loading with correct precedence, a clean `--json` mode, exit-code mapping, stdin/TTY/signal handling, completions | "set up subcommands + flags", "make flags override env override the file", "add a clean --json mode", "CI goes green when the tool failed" |
| [`tui-engineer`](agents/tui-engineer.md) | Whether a full-screen TUI is warranted, then the framework (Ink/Bubble Tea/Textual/ratatui), the render-loop + state model, input, resize, non-TTY fallback, accessibility, performance | "should this be a TUI or just flags?", "Ink/Bubble Tea/Textual/ratatui?", "my TUI corrupts on resize / breaks when piped" |
| [`cli-distribution-engineer`](agents/cli-distribution-engineer.md) | The single-binary-vs-runtime decision, cross-compilation, install channels (Homebrew/Scoop/winget/npm/pipx), a build-stamped `--version`, completions packaging, the update path, install scripts/man pages | "how do users install + update this?", "build for the OS/arch matrix", "get this into Homebrew/Scoop", "write a safe curl \| sh installer" |

**Sub-agents do not spawn other sub-agents** — only the Team Lead delegates. If work crosses specialist boundaries, each specialist returns its slice and the Team Lead re-dispatches.

## 2. Cross-cutting house opinions (every agent enforces)

1. **Design the command surface first.** Names, subcommands, flags, and positionals are the hardest things to change once scripts depend on them — decide the shape, the global-vs-local flags, and the defaults before writing commands.
2. **Config precedence is flag > env > project file > user file > default**, resolved into one config object early. Never let a file silently beat an explicit flag.
3. **Human-readable by default, machine-readable (`--json`) on demand** — and never interleave a human log line into the JSON stream.
4. **Data to stdout, diagnostics/logs/prompts/errors to stderr.** This split is what makes a tool composable.
5. **Exit codes are a public API.** `0` only on success; distinct non-zero codes per failure class; `128+signal` when killed. Never exit `0` on a real failure.
6. **Gate color/progress behind `isatty` + `NO_COLOR`/`FORCE_COLOR`**, and read **stdin** when piped — be a good shell citizen.
7. **Confirm destructive actions but honor `--force`/`--yes`** for non-interactive use; on a non-TTY, refuse rather than hang or silently proceed.
8. **Handle SIGINT/SIGTERM and clean up** (temp files, locks, terminal state) on every exit path.
9. **Ship a build-stamped `--version`** (semver + commit), generated **completions**, and a **man page**; prefer a **single static binary** when the language allows.

## 3. Seams (the bridges to neighbouring plugins)

- **The service/business logic the CLI drives** → `backend-engineering` (we own the command-line surface; they own the domain logic).
- **CI release pipeline, code-signing + notarization, secret handling** → `devops-cicd` (we design what the release produces; they wire and sign it).
- **The desktop GUI sibling** → `desktop-app-engineering` — the same "ship to a user's machine" instincts, a windowed runtime instead of a terminal.
- **Man-page authoring / a docs site** → `technical-writing-docs`.
- **Concrete appsec verdicts** (e.g. an install script, secret handling) → `ravenclaude-core/security-reviewer`.

## 4. Inheritance

This plugin **inherits `ravenclaude-core` protocols**: the Capability Grounding Protocol (decision-tree-first + alternate-methods enumeration + honest blocked-reporting), the Structured Output Protocol for handoffs, and the security/review escalations. Domain-specific rules live in each agent file and in `best-practices/`; the knowledge bank carries the decision trees and the dated capability map.

## 5. Knowledge & scenario banks

Two banks back the agents (the dual-bank model — see [`../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../ravenclaude-core/skills/scenario-retrieval/SKILL.md)):

- **Canonical / knowledge** (high trust, follow without disclaimer): [`knowledge/cli-tooling-decision-trees.md`](knowledge/cli-tooling-decision-trees.md) — the command-surface tree, the output/exit-code-contract tree, the parser/framework-choice tree, the distribution tree, a config-precedence prior, and a dated 2026 capability map. **Traverse the relevant Mermaid tree top-to-bottom before choosing** — the proactive complement to the Capability Grounding Protocol. Capability rows are dated and `[verify-at-use]`; re-confirm against the vendor before quoting (Cobra/clap/oclif majors, Typer/Textual majors, exit-code conventions, the `NO_COLOR`/`FORCE_COLOR` semantics).
- **Scenarios** (low/medium trust, surface with the mandatory unverified preamble): [`scenarios/`](scenarios/) — field notes (ANSI color leaking into pipes, an exit-`0` masking a CI failure, `--json` mixed with logs). Secondary source; never replaces the knowledge bank.

## 6. Technical-runtime tier — LSP code intelligence (bundled config, binaries installed separately)

CLI tooling is a **code** domain spanning four mainstream CLI languages, so the plugin ships an [`.lsp.json`](.lsp.json) (referenced from `plugin.json` `lspServers`) giving agents real-time code intelligence:

| Language | Server | `command` | Install (consumer, separate) `[verify-at-use]` |
|---|---|---|---|
| TypeScript/JS (oclif/yargs/Ink) | typescript-language-server | `typescript-language-server --stdio` | `npm install -g typescript-language-server typescript` |
| Rust (clap/ratatui) | rust-analyzer | `rust-analyzer` | `rustup component add rust-analyzer` |
| Go (Cobra/Bubble Tea) | gopls | `gopls` | `go install golang.org/x/tools/gopls@latest` |
| Python (Click/Typer/Textual) | pyright | `pyright-langserver --stdio` | `npm install -g pyright` (or `pip install pyright`) |

**The plugin ships the *config*, not the *binary*.** If a server isn't on `PATH` it shows in the `/plugin` Errors tab and that one language degrades — Claude Code and everything else keep working (loud-but-non-fatal). LSP support landed in Claude Code 2.0.74 `[verify-at-use]`.

## 7. Recommended (not bundled) MCP servers

This plugin **bundles no MCP server**, on purpose. Per [`docs/best-practices/bundled-mcp-servers.md`](../../docs/best-practices/bundled-mcp-servers.md), a bundled server must be zero-config and read-only by default. CLI build/release/publish tooling is per-consumer-environment (package-registry tokens, signing keys, a build toolchain) and write/side-effecting, so it is **evaluate-first, never bundle**. No invented servers.

## 8. Value-add disposition (build-out 2026-06-22, v0.1.0)

| # | Item | Disposition |
|---|---|---|
| 1 | **scenarios/ bank** | **BUILT** — 3 scenarios (ANSI color in pipes, exit-`0` masked CI failure, `--json` mixed with logs) on the 9-field schema. |
| 2 | **Decision-tree knowledge** | **BUILT** — command-surface + output/exit-code + framework-choice + distribution Mermaid trees, a config-precedence prior, and a dated 2026 capability map. |
| 3 | **LSP server** | **BUILT** — `.lsp.json` wires typescript-language-server + rust-analyzer + gopls + pyright, via `plugin.json` `lspServers`. Ships config, not binaries. |
| 4 | **Bundled MCP server** | **N-A (evaluate-first)** — CLI release/publish tooling is per-consumer and write-capable; documented, not bundled. No invented servers. |
| 5 | **Runnable script (`scripts/`)** | **N-A** — the decisions here are qualitative (surface/output-contract/distribution) or live against the consumer's tool (served by the LSP tier + the advisory hook), not arithmetic models. |
| 6 | **skills/hooks/commands/templates** | **BUILT / sufficient** — 5 skills, 4 commands, 4 templates, 1 advisory hook (ungated ANSI color, error/usage on stdout, boolean exit code, secrets as flags). |
| 7 | **CHANGELOG.md** | **BUILT** — top entry for the v0.1.0 initial build. No `NOTICE.md` (nothing third-party is bundled). |
