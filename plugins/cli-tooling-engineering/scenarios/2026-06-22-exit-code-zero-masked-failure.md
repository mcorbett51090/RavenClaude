---
scenario_id: 2026-06-22-exit-code-zero-masked-failure
contributed_at: 2026-06-22
plugin: cli-tooling-engineering
product: generic
product_version: "unknown"
scope: likely-general
tags: [cli, exit-codes, ci, error-handling, stderr]
confidence: high
reviewed: false
---

## Problem

A data-import CLI was run as a step in a nightly CI pipeline. For weeks the pipeline reported green while a downstream dashboard quietly showed stale numbers. The cause: when the import hit a malformed record it caught the exception, printed `Warning: skipped 4,000 rows` and **returned exit code 0**. CI saw `0`, marked the step successful, and the next step (a "data is fresh" assertion that didn't actually re-check freshness) also passed. A real, recurring failure was invisible because the exit code lied.

## Constraints context

- The tool was used both interactively (where the warning text was visible and a human could react) and in CI (where only the exit code is read).
- Some "skips" were legitimately tolerable; others (like 4,000 rows) were not — the tool had collapsed both into a warning.
- Other pipelines already depended on the current (always-0) behavior for a few benign cases, so a blunt "always fail on any skip" would break them.

## Attempts

- Tried: grepping the tool's stdout in CI for the word "Warning". Brittle — message wording drifted, and it coupled the pipeline to log text instead of a stable interface.
- Tried: failing on *any* skipped row. Too blunt — it broke the pipelines that legitimately tolerated a handful of skips.
- Tried (the fix): defined exit codes as an **API** with a threshold, and moved diagnostics to stderr.

## Resolution

**The exit code is the interface CI reads — make it tell the truth, with distinct codes for distinct outcomes.** The shape that worked:

1. **A documented exit-code map.** `0` = clean import; `0` also for skips **below** a configurable threshold (the benign case stays green); a distinct non-zero code (`3`) for "completed with skips above threshold"; `1` for an unexpected error; `2` for usage errors.
2. **Diagnostics to stderr.** The skip summary moved to stderr so stdout stayed clean for the `--json` result other steps consumed.
3. **The pipeline branches on the code, not the text.** CI now fails on `3`, and a `--max-skip` flag lets each caller set its own tolerance.

The mental model: a human can read a warning and decide; a pipeline only ever sees the exit code. If a failure matters, it must change the number.

**Action for the next engineer:** never return `0` from a path that handled a real failure. Decide up front what each non-zero code means, document it, and let callers set the threshold rather than hard-coding tolerance.

Cross-reference: complements [`../best-practices/exit-codes-are-a-public-api.md`](../best-practices/exit-codes-are-a-public-api.md), [`../best-practices/data-to-stdout-diagnostics-to-stderr.md`](../best-practices/data-to-stdout-diagnostics-to-stderr.md), and the output/exit-code tree in [`../knowledge/cli-tooling-decision-trees.md`](../knowledge/cli-tooling-decision-trees.md).
