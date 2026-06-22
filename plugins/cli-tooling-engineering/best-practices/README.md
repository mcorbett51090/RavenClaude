# cli-tooling-engineering — best-practice docs

Named, citable rules for the `cli-tooling-engineering` plugin's specialists. Each file is **one rule**.

---

## Index

_12 rules across the command surface, config, the output/exit-code contract, shell citizenship, and distribution._

| Doc | Status | Use when |
|---|---|---|
| [`design-the-command-surface-first.md`](./design-the-command-surface-first.md) | Pattern | Starting a CLI — design commands/flags/positionals before writing them; they're hard to change later. |
| [`config-precedence-is-flags-over-env-over-file.md`](./config-precedence-is-flags-over-env-over-file.md) | Absolute rule | Any tool with config — resolve flag > env > project file > user file > default into one object. |
| [`human-readable-by-default-machine-readable-on-demand.md`](./human-readable-by-default-machine-readable-on-demand.md) | Absolute rule | Output that serves both people and scripts — human default, --json on demand. |
| [`exit-codes-are-a-public-api.md`](./exit-codes-are-a-public-api.md) | Absolute rule | Every command — map success/failure to stable exit codes; never exit 0 on a real failure. |
| [`data-to-stdout-diagnostics-to-stderr.md`](./data-to-stdout-diagnostics-to-stderr.md) | Absolute rule | Anything a tool prints — data on stdout, logs/progress/prompts/errors on stderr. |
| [`respect-no-color-and-detect-the-tty.md`](./respect-no-color-and-detect-the-tty.md) | Absolute rule | Color or progress output — gate behind isatty + honor NO_COLOR/FORCE_COLOR. |
| [`read-stdin-and-be-pipe-friendly.md`](./read-stdin-and-be-pipe-friendly.md) | Pattern | A tool that processes input — read stdin when piped; compose in pipelines. |
| [`confirm-destructive-actions-honor-force-and-yes.md`](./confirm-destructive-actions-honor-force-and-yes.md) | Absolute rule | Any irreversible operation — confirm interactively, honor --force/--yes for scripts. |
| [`fail-fast-with-actionable-errors.md`](./fail-fast-with-actionable-errors.md) | Pattern | Error handling — fail early with a message that says what to do next. |
| [`handle-signals-and-clean-up.md`](./handle-signals-and-clean-up.md) | Absolute rule | Long-running or stateful commands — handle SIGINT/SIGTERM, restore state, exit 128+signal. |
| [`ship-a-version-flag-and-an-update-path.md`](./ship-a-version-flag-and-an-update-path.md) | Absolute rule | Every distributed tool — a build-stamped --version (semver+commit) and an update story. |
| [`distribute-a-single-binary-and-completions.md`](./distribute-a-single-binary-and-completions.md) | Pattern | Shipping the tool — prefer a single static binary; package generated completions + man page. |

---

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — plugin team constitution.
- [`../../../docs/best-practices/README.md`](../../../docs/best-practices/README.md) — marketplace-wide best-practice docs.
