# Changelog — cli-tooling-engineering

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.1.0] — 2026-06-22

Initial build — the **command-line-tool** sibling the app-craft cluster (backend / frontend / mobile / desktop-app / api / database / auth-identity) was missing. The #2 candidate on the 2026-06-12 ten-plugin roadmap (after desktop-app-engineering, #1). Mirrors the proven app-craft recipe for a **code** domain.

### Added

- **4 agents** (scenario-authoring schema complete, each description ≤300 chars): `cli-architect` (command surface, config precedence, output/exit-code contract, CLI-vs-TUI-vs-library, distribution strategy), `cli-implementation-engineer` (idiomatic parser, subcommands, config loading, clean `--json`, exit-code mapping, stdin/TTY/signal handling, completions), `tui-engineer` (TUI-warranted check, framework choice, render loop, resize/non-TTY fallback, accessibility), `cli-distribution-engineer` (single-binary vs runtime, cross-compile, install channels, build-stamped `--version`, update path, safe installers).
- **5 skills** — cli-design-and-arg-parsing, output-and-exit-code-contract, tui-design, cli-distribution-and-packaging, shell-completions-and-config.
- **Knowledge bank** — `knowledge/cli-tooling-decision-trees.md`: command-surface + output/exit-code + parser/framework-choice + distribution Mermaid trees, a config-precedence prior, and a dated 2026 capability map (`[verify-at-use]`).
- **12 best-practices** — design-the-command-surface-first, config-precedence, human-readable-by-default/machine-readable-on-demand, exit-codes-are-a-public-api, data-to-stdout/diagnostics-to-stderr, respect-NO_COLOR-and-detect-the-TTY, read-stdin-and-be-pipe-friendly, confirm-destructive-actions/honor-force-and-yes, fail-fast-with-actionable-errors, handle-signals-and-clean-up, ship-a-version-flag-and-an-update-path, distribute-a-single-binary-and-completions.
- **4 templates** (cli-design-spec, output-and-exit-code-contract, distribution-plan, tui-decision), **4 commands** (design-cli, audit-cli-ux, plan-cli-distribution, add-shell-completions), **1 advisory hook** (`check-cli-tooling-anti-patterns.sh` — ungated ANSI color, error/usage text on stdout, boolean exit code, secrets as flags; `CLI_STRICT=1` to block).
- **3-scenario bank** — ANSI color leaking into pipes, an exit-`0` masking a CI failure, `--json` output mixed with logs.
- **`.lsp.json`** — typescript-language-server + rust-analyzer + gopls + pyright; ships config, not binaries.
- **README.md + CLAUDE.md** (team constitution), and registration in `.claude-plugin/marketplace.json` + the `docs/architecture.md` roster.

### Decisions (recorded, not built)

- **No bundled MCP server** — CLI release/publish tooling is per-consumer-environment (registry tokens, signing keys, a build toolchain) and write/side-effecting → evaluate-first, documented not bundled. No invented servers.
- **No runnable `scripts/` calculator** — the decisions are qualitative or live against the consumer's tool (served by the LSP tier + advisory hook), not arithmetic models.

### Verify-at-use

- Cobra/pflag, clap v4, oclif, yargs majors; Click/Typer/Textual majors; the `NO_COLOR`/`FORCE_COLOR` semantics; exit-code conventions (`126`/`127` are shell-owned); the LSP-support Claude Code version (2.0.74). All version-volatile — re-confirm against the vendor before quoting.
