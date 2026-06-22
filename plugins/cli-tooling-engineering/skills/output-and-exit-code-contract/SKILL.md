---
name: output-and-exit-code-contract
description: "Define a CLI's output contract — human by default, --json on demand, data to stdout, diagnostics to stderr — and an exit-code map treated as a public API. Use when a tool must serve both humans and scripts, or CI keeps passing on real failures."
---

# Output & Exit-Code Contract

## Two streams, never crossed

- **stdout = the program's data/result.** This is what `tool | next` and `tool > file` consume.
- **stderr = everything else** — logs, progress, prompts, warnings, errors.

This split is what makes a tool composable: `tool 2>/dev/null` shows only data; `tool >/dev/null` shows only diagnostics.

## Two output modes, one switch

- **Human-readable by default** — formatted, possibly colored (gated, see below).
- **`--json` on demand** — emit **only** structured data on stdout, with **no human log lines interleaved**. Keep the two renderers separate so a stray log never corrupts the JSON stream.

## Exit codes are an API

| Code | Meaning |
|---|---|
| `0` | Success |
| `1` | General/unexpected error |
| `2` | Usage error (bad args/flags) |
| `3`+ | Distinct **domain** failure classes (document them) |
| `128 + N` | Killed by signal N (e.g. SIGINT → 130) |

**Never exit `0` on a real failure** — every downstream CI step trusts the code and keeps going. Print the error + a remediation hint to **stderr**, then exit a non-zero code.

## Color & TTY discipline

Gate color/progress behind **`isatty(stderr)`** *and* honor **`NO_COLOR`** (any non-empty value disables) and **`FORCE_COLOR`** (overrides a non-TTY). Emitting ANSI codes into a pipe or redirected file turns logs into escape-code soup.

## Pipe friendliness

Read **stdin** when piped (treat `-` as "read stdin" where sensible). Don't prompt interactively when stdin/stdout isn't a TTY — require a flag instead.

See the output/exit-code tree in [`../../knowledge/cli-tooling-decision-trees.md`](../../knowledge/cli-tooling-decision-trees.md).
