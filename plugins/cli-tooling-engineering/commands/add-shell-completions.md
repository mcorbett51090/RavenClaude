---
description: "Generate shell completions (bash/zsh/fish/PowerShell) from the parser and design config-file discovery + env-var conventions."
argument-hint: "[CLI repo + parser/language]"
---

You are running `/cli-tooling-engineering:add-shell-completions`. Use `cli-implementation-engineer` + the `shell-completions-and-config` skill.

## Steps

1. Generate completions from the parser (Cobra `completion` / `clap_complete` / Click-Typer / `@oclif/plugin-autocomplete`) — never hand-write them.
2. Wire a `tool completion <shell>` subcommand (or package the scripts in the release) for bash/zsh/fish/PowerShell.
3. Design config discovery via XDG (`$XDG_CONFIG_HOME/<tool>/` → `~/.config`); document the search path in `--help`.
4. Set env-var conventions (`TOOL_*` prefix; honor `NO_COLOR`/`FORCE_COLOR`/`XDG_*`/`PAGER`/`EDITOR`) and place them in the precedence chain.
5. Emit the completion + config plan + a Structured Output block.
