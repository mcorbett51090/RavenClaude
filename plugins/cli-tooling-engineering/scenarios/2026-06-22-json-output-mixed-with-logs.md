---
scenario_id: 2026-06-22-json-output-mixed-with-logs
contributed_at: 2026-06-22
plugin: cli-tooling-engineering
product: generic
product_version: "unknown"
scope: likely-general
tags: [cli, json, stdout, stderr, piping, jq]
confidence: high
reviewed: false
---

## Problem

A deploy CLI added a `--json` mode so other tooling could consume its results with `jq`. It worked in a quick test but broke in real use: `deploy --json | jq .status` failed with a parse error. The reason — even in `--json` mode the tool still printed human progress lines (`Connecting...`, `Uploading 3 files...`) to **stdout**, interleaved with the final JSON object. `jq` got `Connecting...{...}` and choked. Consumers had resorted to `deploy --json | tail -1 | jq`, which silently broke the day the JSON spanned multiple lines.

## Constraints context

- The progress lines were useful to humans even during a `--json` run (deploys are slow; people want feedback).
- The JSON result and the progress logging were emitted from the same code paths via a shared `log()` helper that wrote to stdout.
- Some consumers had already hard-coded the `tail -1` workaround, so the fix had to make the clean path obviously correct so they'd drop the hack.

## Attempts

- Tried: suppressing all progress output when `--json` is set. Worked for parsers but blinded humans watching a slow deploy — and operators pushed back.
- Tried: emitting newline-delimited JSON (one object per line) so `tail -1` was "safe". A patch on the symptom; it still mixed logs and data on one stream and assumed the result was always one line.
- Tried (the fix): split the streams — **data to stdout, everything else to stderr** — so progress and the JSON result no longer competed.

## Resolution

**stdout carries only the result; progress and logs go to stderr — so `--json` is clean by construction and humans still get feedback.** The shape that worked:

1. **Two sinks.** The shared `log()` helper was split: `result()` writes the data to stdout; `progress()`/`warn()`/`err()` write to stderr.
2. **`--json` only changes the result renderer.** Progress still streams (to stderr), so `deploy --json | jq` sees a single clean JSON object while a human watching the terminal still sees `Uploading...` on stderr.
3. **One write of the result.** The JSON object is emitted exactly once, at the end, on stdout — no partials, no interleaving.

The mental model: stdout is the machine's channel, stderr is the human's. They can both be active at once precisely because they don't share a stream.

**Action for the next engineer:** when you add `--json`, audit every write that lands on stdout — anything that isn't the result is a bug. Progress is great; it just belongs on stderr.

Cross-reference: complements [`../best-practices/data-to-stdout-diagnostics-to-stderr.md`](../best-practices/data-to-stdout-diagnostics-to-stderr.md), [`../best-practices/human-readable-by-default-machine-readable-on-demand.md`](../best-practices/human-readable-by-default-machine-readable-on-demand.md), and the output/exit-code tree in [`../knowledge/cli-tooling-decision-trees.md`](../knowledge/cli-tooling-decision-trees.md).
