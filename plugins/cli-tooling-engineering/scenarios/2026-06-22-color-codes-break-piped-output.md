---
scenario_id: 2026-06-22-color-codes-break-piped-output
contributed_at: 2026-06-22
plugin: cli-tooling-engineering
product: generic
product_version: "unknown"
scope: likely-general
tags: [cli, color, ansi, no-color, isatty, piping, ci]
confidence: high
reviewed: false
---

## Problem

A team's CLI printed nicely colored status output for humans — green checks, red failures, a spinner. The moment it was used in anger (piped into `grep`, redirected to a log file, run in CI) the output filled with raw escape sequences: `\033[32m✓\033[0m service up`. CI logs were unreadable, `grep "service up"` missed lines because of embedded codes, and a downstream parser that split on whitespace broke on the color resets. The colors had been added with a library that emitted ANSI unconditionally.

## Constraints context

- The colored output was genuinely valuable interactively — the team didn't want to drop it.
- The tool was used both ways: a human at a terminal *and* scripts/CI consuming its output.
- Several call sites built colored strings inline, so there was no single choke point.

## Attempts

- Tried: a `--no-color` flag. Helped scripts that *remembered* to pass it, but CI and ad-hoc pipes still got escape soup by default — the safe behavior must be the one you get with no flag.
- Tried: stripping ANSI from the output in a wrapper. A band-aid that every consumer had to apply; the tool was still emitting garbage by default.
- Tried (the fix): made color **conditional on the output being a TTY**, honoring the `NO_COLOR` and `FORCE_COLOR` conventions, and routed all styling through one helper so the decision was made in a single place.

## Resolution

**Color is opt-out-by-environment and gated on a TTY — never emitted unconditionally.** The shape that worked:

1. **One styling helper.** All colored output went through a single function that decided once whether color was on.
2. **The decision rule.** Color on **only if** the stream is a TTY (`isatty`) **and** `NO_COLOR` is unset; `FORCE_COLOR` overrides the TTY check for users who *want* color through a pipe. The default a user never configures (a pipe, a redirect, CI) is plain text.
3. **Same gate for the spinner/progress.** Progress animation was disabled off-TTY too — a spinner in a log file is just thousands of carriage returns.

The mental model: the terminal is one consumer among many. Decorate for it when you can prove you're talking to it; otherwise emit clean bytes the next program can parse.

**Action for the next engineer:** never call a color library directly from scattered call sites — route styling through one helper that checks `isatty` + `NO_COLOR`/`FORCE_COLOR`. The default with no flags must be plain when not a terminal.

Cross-reference: complements [`../best-practices/respect-no-color-and-detect-the-tty.md`](../best-practices/respect-no-color-and-detect-the-tty.md) and the output/exit-code tree in [`../knowledge/cli-tooling-decision-trees.md`](../knowledge/cli-tooling-decision-trees.md).
