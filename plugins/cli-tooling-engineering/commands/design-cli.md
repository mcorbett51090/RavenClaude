---
description: "Design a CLI's command/flag surface, config precedence, output + exit-code contract, and the CLI-vs-TUI-vs-library call."
argument-hint: "[tool purpose + audience (humans/scripts/both) + language]"
---

You are running `/cli-tooling-engineering:design-cli`. Use `cli-architect` + the `cli-design-and-arg-parsing` skill.

## Steps

1. Traverse the command-surface tree in `knowledge/cli-tooling-decision-trees.md` (CLI vs TUI vs library; flat vs subcommands; flag vs positional); name the trade.
2. Pick the idiomatic parser for the language (Cobra / clap / argparse / Click / oclif / yargs).
3. Set config precedence (flag > env > project file > user file > default).
4. Define the output + exit-code contract (human default, `--json` on demand, data→stdout/diagnostics→stderr, exit codes as an API).
5. Emit (from `templates/cli-design-spec.md`) + a Structured Output block.
