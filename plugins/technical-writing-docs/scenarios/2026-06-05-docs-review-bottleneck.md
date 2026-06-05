---
scenario_id: 2026-06-05-docs-review-bottleneck
contributed_at: 2026-06-05
plugin: technical-writing-docs
product: vale
product_version: "unknown"
scope: likely-general
tags: [docs-as-code, review-bottleneck, vale, ci, style-linter, terminology]
confidence: medium
reviewed: false
---

## Problem

A docs team of one tech writer was the mandatory reviewer on every docs PR, and the queue was the bottleneck: engineers' doc changes sat for days waiting for the writer to hand-check the same things every time — heading capitalization, banned/inconsistent terminology ("log in" vs "login" vs "sign in"), passive voice, "click here" links, the Oxford comma. The writer spent their review time on mechanical style nits instead of structure, accuracy, and whether the doc served the reader. Worse, the standard lived in the writer's head, so engineers couldn't self-correct before submitting and the same nits recurred.

## Constraints context

- The team already practiced docs-as-code (docs in the repo, reviewed in PRs) but had **no automated style gate** — every style rule was enforced by a human, every time (`ci-gate-broken-links-and-examples` was partly in place for links, but not for prose style).
- "Consistent terminology and voice" was an unwritten oral tradition, not a machine-checkable artifact — so it didn't scale past one reviewer and couldn't be enforced before a PR was opened.
- The fix had to **not** add a heavyweight toolchain — the repo was already Node-light, and a slow CI step would just move the bottleneck.

## Attempts

- Tried: a written style guide doc. Helped a little, but a prose style guide nobody runs is enforced by memory — recurrence continued. A guide that isn't executable is advisory.
- Tried: hiring/borrowing a second reviewer. Didn't address the structural problem (mechanical checks done by humans) and wasn't durable when that person was out.
- Tried (the move that worked): encoded the mechanical rules as a **prose linter** (Vale `[verify-at-use]`) with a `.vale.ini` + a small custom style (banned-terms substitutions, heading-case, "click here") and ran it **in CI** as a required check, **plus** wired the same linter as an **LSP in the editor** so engineers see the same diagnostics as they type — self-correcting *before* the PR. The human reviewer was freed to review structure, Diátaxis-kind fit, and accuracy. Traversed the new `knowledge/lint-in-ci-vs-manual-review-decision-tree.md`: mechanical + objective + high-frequency → automate; judgment (is this the right Diátaxis kind? is it accurate?) → stays human.

## Resolution

The fix was to **split the review into machine-checkable vs. judgment**, automate the machine-checkable half (a prose linter in CI **and** in the editor via LSP), and reserve the human for the judgment half. The terminology/voice standard became an executable artifact (`styles/` + `.vale.ini`) instead of oral tradition, so it scaled past one reviewer and engineers self-corrected before submitting. The bottleneck moved from "wait for the writer" to "fix what the linter flags, then a fast human pass."

**Action for the next team with a docs-review bottleneck:** sort what the human reviews into **mechanical/objective** (capitalization, banned terms, link text, passive voice) vs. **judgment** (accuracy, structure, right Diátaxis kind, does-it-serve-the-reader). Automate the first half as a prose linter in CI *and* as an editor LSP so authors self-correct pre-PR; keep the human on the second. Canonical guidance: [`../knowledge/lint-in-ci-vs-manual-review-decision-tree.md`](../knowledge/lint-in-ci-vs-manual-review-decision-tree.md) and the [`docs-as-code`](../best-practices/docs-as-code.md) + [`ci-gate-broken-links-and-examples`](../best-practices/ci-gate-broken-links-and-examples.md) best-practices. The plugin's `.lsp.json` ships the Vale-LS config; the binary installs separately (see CLAUDE.md).

**Sources (retrieved 2026-06-05):**
- Vale — syntax-aware prose linter (Markdown/markup-aware, enforces a style as code): https://vale.sh/ and https://docs.vale.sh/
- Vale-LS — the Vale Language Server (LSP wrapper, editor diagnostics): https://github.com/errata-ai/vale-ls (v0.4.0, 2025-03-14, MIT)

Vale, the LSP, and any specific rule pack are version-volatile — `[verify-at-use]` the package names, versions, and `.vale.ini` schema against the current Vale release before any deliverable.
