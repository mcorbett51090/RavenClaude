---
name: shell-completions-and-config
description: "Generate shell completions (bash/zsh/fish/PowerShell) from the parser and design config-file discovery + env-var conventions (XDG, TOOL_* prefixes). Use when adding tab completion or a config/env layer to a CLI."
---

# Shell Completions & Config

## Completions — generate, don't hand-write

Every idiomatic parser can emit completion scripts; never maintain them by hand (they rot the moment a flag changes):

| Parser | Completion generation |
|---|---|
| Cobra (Go) | `cmd.GenBashCompletion` / built-in `completion` subcommand (bash/zsh/fish/pwsh) |
| clap (Rust) | `clap_complete` |
| Click/Typer (Python) | built-in completion install |
| oclif (Node) | `@oclif/plugin-autocomplete` |

Ship a `tool completion <shell>` subcommand (or package the scripts in the release) so users can wire `bash`, `zsh`, `fish`, and `PowerShell`.

## Config-file discovery

Follow the **XDG Base Directory** convention on Linux/macOS:

- User config: `$XDG_CONFIG_HOME/<tool>/config.<ext>` → fallback `~/.config/<tool>/config.<ext>`.
- Project config: a `.<tool>rc` / `<tool>.toml` discovered by walking up from the cwd.
- On Windows use the platform equivalent (`%APPDATA%`).

Prefer one documented format (TOML/YAML/JSON); document the search path in `--help`.

## Env-var conventions

- Prefix every env var with the tool name: `TOOL_TIMEOUT`, `TOOL_CONFIG`.
- Env vars sit **below flags, above config files** in precedence (see the config-precedence prior in [`../../knowledge/cli-tooling-decision-trees.md`](../../knowledge/cli-tooling-decision-trees.md)).
- Honor the cross-tool standards you don't own: `NO_COLOR`, `FORCE_COLOR`, `XDG_*`, `PAGER`, `EDITOR`.

Resolve flags + env + files into **one config object** early, and make `--help` state where settings come from.
