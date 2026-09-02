---
name: repo-review
description: "Whole-repo systematic bug sweep — deterministic chunking + a content-hash cache + a Workflow-orchestrated multi-dimension review fan-out (correctness / security / concurrency / resource-leaks / error-handling / performance / ci-cd-actions-security / dead-code-simplification), cross-model-checked at higher tiers, merged and verified before any fix is proposed. Distinct from Claude Code's own built-in /code-review, which reviews a diff/PR/branch — this skill reviews the whole tree, including GitHub Actions workflows and CI gate definitions."
---

# Skill: repo-review

> **Build-in-progress — read the Honest status section (§6) before trusting this skill's own
> description of itself.** The mechanism below is the design this skill implements; the section at
> the bottom states plainly which parts have been mechanically self-tested and which have not yet
> been run end-to-end. Do not let the confident prose above outrun that section.

## What this is, and what it is not

`repo-review` is a **whole-repository systematic bug sweep** — given a repo (or a `--only` slice of
one), it walks every reviewable file, dimension by dimension, and reports findings with an optional
confirmed-only auto-fix pass. It is invoked via **`/repo-review`** (see
[`commands/repo-review.md`](../../commands/repo-review.md), the thin entry point).

**This is not Claude Code's built-in `/code-review`.** That command reviews a diff, a PR, a branch, or
a path — a *changed-code* reviewer. `/repo-review` has **no PR/diff mode at all**; it is the whole-repo
systematic reviewer, built for a periodic or on-demand sweep of a tree that may have accumulated bugs
no single diff-scoped review ever saw. Reach for `/code-review` to review a change; reach for
`/repo-review` to review the repo.

## Command surface

```
/repo-review [effort] [--only <pathspec>] [--since <ref>] [--fix] [--full]
             [--cross-model | --no-cross-model] [--risk-floor <n>] [--estimate-only]
```

- **`effort`** — `high | xhigh | max | ultra`. See the ladder below. `low`/`medium` are **refused**,
  not silently degraded.
- **`--only <pathspec>`** — narrow the file set to a glob/pathspec before chunking.
- **`--since <ref>`** — narrow the file set to what changed since `<ref>` (still a whole-repo-shaped
  run over that narrower set — this is not a diff review; it is repo-review scoped to recently-touched
  files).
- **`--fix`** — apply CONFIRMED, fixable-in-place findings as a reviewable, **uncommitted** patch.
  Never auto-commits or pushes. Gated by its own file-touch cap (default 25) and an upfront one-line
  confirmation before any file is touched.
- **`--full`** — bypass risk-floor sampling and the file-count hard cap. Requires confirmation (this
  can be expensive on a large repo).
- **`--cross-model` / `--no-cross-model`** — override the effort tier's cross-model default (see the
  ladder).
- **`--risk-floor <n>`** — override the sampling percentile that decides which batches get reviewed at
  a given effort tier.
- **`--estimate-only`** — run only the zero-agent-call chunk/score pass (`repo_map.py` +
  `estimate_cost.py`) and print the projected agent-call count. No review agent is dispatched.

## Why `low`/`medium` are refused, not degraded

A shallow pass over a sampled subset of a whole repo produces an **absence-of-findings report that
reads as "clean" when it actually means "barely looked."** That is a worse outcome than declining to
run: a clean-looking whole-repo sweep invites trust a `low`/`medium` effort cannot earn. So the command
refuses those tiers outright, with a message pointing at `high` (the cheapest tier that still does a
real sampled sweep) or suggesting `--only <pathspec>` to narrow scope instead — a small, thoroughly
reviewed slice beats a large, thinly-sampled one.

## Effort-tier ladder

| effort | allowed | dimensions | cross-model | sampling | auto-fix |
|---|---|---|---|---|---|
| low / medium | refused | — | — | — | — |
| high | yes | 4 | off | risk-floor sampled | opt-in (`--fix`) |
| xhigh | yes | 8 | opt-in (`--cross-model`) | sampled, wider floor | opt-in (`--fix`) |
| max | yes | 8 | on by default | sampled, wider floor | opt-in (`--fix`) |
| ultra | yes | 8 | always | fullest, still hard-capped | opt-in (`--fix`) |

`--full` bypasses the sampling column (and the file-count hard cap) at any allowed tier, at its own
confirmation cost.

## The 8 dimensions

Full prompts live in [`reference/dimensions.md`](reference/dimensions.md) — this file does not inline
them, so paying for the dimension text happens once, at the tier that actually needs it. One line each:

1. **correctness** — logic errors, off-by-one, wrong conditionals, incorrect state transitions.
2. **security** — injection, auth/authz gaps, unsafe deserialization, secret handling, unsanitized
   input at a trust boundary.
3. **concurrency** — races, deadlocks, unsynchronized shared state, incorrect async/await usage.
4. **resource-leaks** — unclosed handles, connections, file descriptors, listeners; missing
   cleanup on an error path.
5. **error-handling** — swallowed exceptions, wrong error propagation, a caught error that silently
   continues, missing fail-closed defaults.
6. **performance** — quadratic-or-worse hot paths, N+1 queries, unnecessary re-computation,
   unbounded growth.
7. **ci-cd-actions-security** — GitHub Actions / CI-pipeline specific issues: script injection via
   untrusted `${{ github.event.* }}` data, `pull_request_target` combined with checking out and running
   the PR's head ref, unpinned third-party Actions, overly broad `permissions:` grants, and a CI gate
   that can be silently skipped, never invoked, or made to report success without asserting anything.
   Distinct from the generic `security` dimension above — CI/CD trust boundaries have their own attack
   shapes, and this repo's own history has been burned by more than one of them.
8. **dead-code-simplification** — unreachable code, redundant abstraction, a simplification that
   preserves behavior. **This dimension defaults single-model even under `--cross-model`** — it is the
   cheapest cost lever (a near-deterministic dimension gains little from a second model's vote) and is
   the first thing trimmed when `--estimate-only` shows the run running hot.

`high` runs the first 4 (correctness / security / concurrency / resource-leaks); `xhigh`/`max`/`ultra`
run all 8, including `ci-cd-actions-security`.

## Mechanism

Deterministic **chunking** ([`scripts/repo_map.py`](scripts/repo_map.py)) partitions the reviewable
tree into directory-major, token-budget-packed batches ranked by churn, recency, size, and path
sensitivity — this is the zero-agent-call planning pass `--estimate-only` runs alone. A **content-hash
cache** ([`scripts/review_cache.py`](scripts/review_cache.py)) keys prior verdicts by file content
hash, so a repeat sweep of an unchanged repo costs near-zero review-agent calls — only the batches whose
files actually changed since the last run get re-dispatched. A **`Workflow`-orchestrated fan-out**
([`workflows/repo-sweep.workflow.js`](workflows/repo-sweep.workflow.js)) runs
Map (assign batches) → Review (dimension-sharded, cross-model-checked per the tier) → Merge
(deterministic dedup — [`scripts/findings_merge.py`](scripts/findings_merge.py)) → Verify
(batched by file, a third model verifies a sampled subset of findings per this repo's cross-model
anti-correlated-error pattern) → Fix (batched by file, confirmed-findings-only, never committed) →
Report. A pre-flight cost estimator ([`scripts/estimate_cost.py`](scripts/estimate_cost.py))
implements the `--estimate-only` path and is also what a normal run consults first to decide whether
`--full` at the requested tier is affordable before dispatching a single review agent.

## §6 — Honest status (read this before trusting the mechanism section above)

Modeled on this repo's own precedent for stating gate scope honestly — see `/wireframe`'s "HONEST
GATE-SCOPE STATEMENT" in this repo's `CLAUDE.md`.

**Mechanically self-tested, with real assertions (each via its own `--self-test` flag), and registered
as [Gate 258](../../../../scripts/audit-gates.sh) in `audit-gates.sh` (dispatcher + main sequence +
`Supported:` string — verified by Gate 195, the gate-introspection meta-gate):**

| Component | What `--self-test` actually asserts |
|---|---|
| `scripts/repo_map.py` | determinism (same commit → byte-identical plan), exclusion counts, budget/coverage honesty, `--only` narrowing |
| `scripts/review_cache.py` | content-hash hit/miss/invalidation |
| `scripts/findings_merge.py` | dedup, corroboration, severity-merge, cap, near-dup collapsing, determinism |
| `scripts/fix_summary.py` | row-count == applied-count invariant, anomaly handling |
| `scripts/estimate_cost.py` | tier refusal (low/medium), cardinality formula, the >3000-file hard cap for `--full` |

**Proven end-to-end against a real, live-dispatched run — not just self-tests against synthetic
fixtures.** The full pipeline (Map → Review, single-model then cross-model → Merge → Verify → Fix →
Report) was actually executed against the synthetic fixture repo at
[`tests/fixtures/repo-review/mini-repo/`](../../../../tests/fixtures/repo-review/mini-repo/) via direct
`Agent`-tool dispatch (not yet via the `Workflow` tool — see the caveat below), with every step measured
rather than asserted:

- **Recall: 7/7 planted defects found (100%)**, on the correct file, correct dimension, correct line —
  across all 7 code dimensions the fixture covers (the 8th, `ci-cd-actions-security`, correctly reported
  nothing, since the fixture has no `.github/workflows/` files — a true negative, not untested).
- **Precision: 0 false positives** on the 4 clean control files.
- **A genuine organic bug found beyond the planted set:** the cross-model (opus) pass flagged a real bug
  in `id_utils.py`, a file the fixture's manifest had labeled clean — independently verified by the
  Verify step (CONFIRMED, with a traced code path) and fixed. The fixture's ground truth was simply
  incomplete; this is the pipeline doing its job.
- **A real defect in `findings_merge.py` itself was caught and fixed by this run**, not by a synthetic
  test: the near-duplicate detector required line-bucket difference `== 1`, excluding `0` — so two
  models finding the identical bug on the identical line with differently-worded titles got neither an
  exact-key match nor a near-dup flag, and `corroboration` silently read `null` for the single most
  common real case. Fixed to `> 1`; a permanent regression assertion (`test8`) was added to
  `findings_merge.py`'s own `--self-test`, and Gate 258 carries a must-fail teeth check reverting the
  fix and confirming `test8` then fails.
- **Verify: 17 CONFIRMED, 1 PLAUSIBLE, 0 REFUTED**, across all 18 survivors, third-model rule honored
  (haiku verified findings sourced from sonnet+opus).
- **Fix: 17/17 confirmed+fixable findings applied**, 8 files touched, `fix_summary.py`'s row-count
  invariant held, nothing committed/staged — verified afterward with `git status`, `py_compile`, and
  hand-written functional smoke tests (not just "it compiles") confirming three of the fixes are
  actually, behaviorally correct (the off-by-one page slice, the hyphenated-prefix id validator, the
  slugify delegation).
- **A verify-agent silently failed to write its output file** despite reporting a complete, correct
  analysis — caught by checking the filesystem rather than trusting the report, and recovered by writing
  the already-produced content directly. Left here as a documented instance of "trust but verify."

**Known, honest limitation — not fixed, not hidden:** two real cross-model duplicate pairs
(`notifier.py`, `report_generator.py`) still evade both the exact-key match and the widened near-dup
check, because the two models' titles share only 2-3 tokens, under the 4-token near-dup threshold. This
is an inherent limitation of a pure lexical heuristic, not a bug in the bucket-diff sense above —
correctness is unaffected (Verify re-confirms every survivor independently regardless of corroboration
tagging), but the `corroboration` field will read `null` for some real duplicate pairs. Chasing this
further via threshold-tuning risks overfitting to two examples; the plan's own `judge` policy tier
(deferring marginal near-dup calls to a real model) is the principled fix, not yet built.

**`workflows/repo-sweep.workflow.js` is an authored, complete Workflow script**, following this repo's
own `rc-deep-research.js` conventions — but **it has NOT itself been executed via the real `Workflow`
tool.** The proof-run above used direct `Agent`-tool dispatch to exercise the identical orchestration
shape (cache-check-then-maybe-review, dimension-sharded cross-model fan-out, third-model verify,
per-file fix), which is a faithful functional proof of the *pipeline*, but is not a proof that this
specific `.js` file runs correctly when handed to the `Workflow` tool — invoking that tool requires an
explicit user opt-in ("use a workflow", the `ultracode` keyword, or equivalent) that this build session
did not receive. Treat the file the way `rc-deep-research`'s own SKILL.md treats its bundled `.js`: *"a
reference shape... Claude adapts it to the task at hand."*

**Done in this build, stated explicitly:**

- Plugin version bumped, `sync-plugin-versions.py` + `generate-copilot-plugin.py` + `generate-dashboards.py`
  + `generate-index-dashboard.py` all regenerated and verified fresh.
- `audit-gates.sh` Gate 258 registered (dispatcher + main sequence + `Supported:`), with a must-fail
  teeth check, passing.
- `.repo-layout.json` — no change needed (already covers every path this skill and its siblings touch).

**Not yet done, stated explicitly so nobody assumes it silently happened:**

- A real end-to-end run against this marketplace's own repo (or any real, non-fixture repo) — the
  proof-run above is against the 14-file synthetic fixture, not a repo at production scale.
- Execution via the actual `Workflow` tool (see the caveat above) — gated on user opt-in, not a design
  choice.
- The `judge` near-duplicate policy tier's real model-adjudication step (currently: tag + collect only,
  per the merge script's own documented scope).

Do not cite this skill's mechanism section as proof the pipeline has been run at production scale
against a real repo. It has been proven correct on a small, real, live-dispatched run — not yet at
scale, and not yet through the `Workflow` tool specifically.
