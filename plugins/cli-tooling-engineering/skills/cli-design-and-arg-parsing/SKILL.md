---
name: cli-design-and-arg-parsing
description: "Design a CLI's command/subcommand surface, flags vs positionals, and config precedence (flags > env > file > default), then pick the idiomatic parser for the language. Use when starting a CLI or reworking a messy one."
---

# CLI Design & Argument Parsing

## The command surface

| Tool shape | Use |
|---|---|
| `tool [flags] <input>` (flat) | Single-purpose tool (one operation) |
| `tool <noun> <verb> [flags]` (subcommands) | Multi-feature tool — `git`, `docker`, `kubectl` style |
| Library + thin CLI | Logic other programs should call |

- **Positional** = *what* the command acts on (required input). **Flag** = *how* it behaves (optional, with a sensible default).
- Separate **global** flags (apply to all subcommands) from **command-local** ones.
- Reserve the conventional flags: `-h/--help`, `--version`, `-v/--verbose`, `-q/--quiet`, `--json`, `--no-color`, `--force`/`-y/--yes`.
- Make the common case need **no flags** — good defaults beat required configuration.

## Config precedence (highest wins)

`flag > env var > project config file > user config file > built-in default`

Resolve all sources into **one config object** early; pass it down. Never let a file silently beat an explicit flag. Discover user config via XDG (`$XDG_CONFIG_HOME` → `~/.config`).

## Pick the idiomatic parser (never hand-roll argv)

| Language | Parser |
|---|---|
| Go | Cobra + pflag |
| Rust | clap (derive) |
| Python | argparse (stdlib) / Click / Typer |
| Node/TS | oclif (multi-command) / yargs / commander |

The parser gives you help generation, value validation, and shell completions for free — losing those is the cost of hand-rolling.

See [`../../knowledge/cli-tooling-decision-trees.md`](../../knowledge/cli-tooling-decision-trees.md) for the command-surface and framework-choice trees.
