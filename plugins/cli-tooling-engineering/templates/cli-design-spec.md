# CLI design spec

**Tool:** <name>  **Audience:** <humans / scripts / both>  **Language:** <go / rust / python / node>

## Surface

| Shape | Decision |
|---|---|
| CLI vs TUI vs library | <one-shot CLI / full-screen TUI / library + thin CLI> |
| Structure | <flat flags / `tool <noun> <verb>` subcommands> |
| Parser | <Cobra / clap / argparse / Click / oclif / yargs> |

## Commands

| Command | Positional(s) | Key flags | Output |
|---|---|---|---|
| `<cmd>` | `<what it acts on>` | `<--how>` | <human / --json> |

**Global flags:** `-h/--help` · `--version` · `-v/--verbose` · `-q/--quiet` · `--json` · `--no-color` · `--yes/--force`

## Config precedence (highest wins)

flag → env (`TOOL_*`) → project file → user file (`$XDG_CONFIG_HOME/tool/`) → default

## Output + exit-code contract

- **stdout:** <the data> · **stderr:** logs/progress/prompts/errors
- **Exit codes:** `0` ok · `2` usage · `1` general · `<N>` <domain failure> · `128+sig` signalled

**Decision:** <the shape chosen>  **Trade accepted:** <what we give up>
