---
description: "Audit an existing CLI against the output/exit-code contract and shell-citizenship rules; flag and fix the violations."
argument-hint: "[path to the CLI repo or the command]"
---

You are running `/cli-tooling-engineering:audit-cli-ux`. Use `cli-implementation-engineer` + the `output-and-exit-code-contract` skill.

## Steps

1. Check the **streams**: data on stdout, diagnostics/errors/prompts on stderr — flag any error/usage text on stdout.
2. Check **`--json`** (if present): only data, no interleaved log lines.
3. Check **exit codes**: does it ever exit `0` on a real failure? Are failure classes mapped to distinct codes?
4. Check **TTY discipline**: color/progress gated by `isatty` + `NO_COLOR`/`FORCE_COLOR`; no prompts on a non-TTY; reads stdin when piped.
5. Check **signals + destructive actions**: SIGINT/SIGTERM cleanup; destructive ops confirm + honor `--force`/`--yes`.
6. Emit findings (use `templates/output-and-exit-code-contract.md` as the checklist) + a Structured Output block; route appsec verdicts to `ravenclaude-core/security-reviewer`.
