# Output & exit-code contract

**Tool:** <name>

## Streams

| Stream | Carries |
|---|---|
| stdout | <the primary data/result only> |
| stderr | logs, progress, prompts, warnings, errors |

## Output modes

| Mode | Switch | Shape |
|---|---|---|
| Human (default) | (none) | <formatted text; color gated by isatty + NO_COLOR> |
| Machine | `--json` | <documented JSON schema; data only, no log lines> |

## Exit codes

| Code | Meaning |
|---|---|
| 0 | Success |
| 2 | Usage error (bad args/flags) |
| 1 | General/unexpected error |
| <N> | <domain failure class> |
| 128+N | Killed by signal N |

## Checklist

- [ ] No human log line ever lands on stdout in `--json` mode
- [ ] Never exits `0` on a real failure
- [ ] Color/progress gated by `isatty` + `NO_COLOR` / `FORCE_COLOR`
- [ ] Reads stdin when piped; doesn't prompt on a non-TTY
- [ ] Errors go to stderr with an actionable message
