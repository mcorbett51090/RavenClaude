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
             [--converge [--max-iterations <n>]]
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
- **`--converge [--max-iterations <n>]`** — loop Review→Merge→Verify→Fix until the repo has **0 open
  P0-P3 findings**, or until no further CONFIRMED+fixable finding can be auto-applied (a plateau),
  capped at `<n>` iterations (default 5, hard-capped at 20). Implies `--fix`. See
  [§ Convergence loop](#convergence-loop---converge) below.

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

## P0-P3 priority

Every survivor in the merged findings JSON carries a `priority` field, `P0` through `P3` — a
**deterministic relabeling of `severity`** computed by `findings_merge.py`'s `priority_for()`, never a
second, independently-judged tier a review agent has to decide:

| severity   | priority | meaning |
|---|---|---|
| `blocking` | **P0**   | data corruption, crash, or security-critical on realistic input |
| `major`    | **P1**   | a real bug, not yet catastrophic |
| `minor`    | **P2**   | a real but low-impact issue |
| `nit`      | **P3**   | style / simplification — never blocking, never fixable-in-place-required |

This works because each dimension already **bounds its own severity ceiling** (`performance` never
emits `blocking`; `dead-code-simplification` always emits `nit` — see the per-dimension prompts in
`reference/dimensions.md`), so `severity` already carries the dimension-aware urgency signal — priority
just gives it a name a human, a report, or `--converge`'s stop condition can key off. The merged JSON's
top-level `by_priority` object (`{P0, P1, P2, P3}`, plus `unknown` for an unrecognized severity — never
silently guessed into a tier) is the run's priority breakdown at a glance.

## Convergence loop (`--converge`)

By default `/repo-review --fix` runs the Review→Merge→Verify→Fix pipeline **once**: it applies every
CONFIRMED + fixable-in-place finding it found in that single pass and stops, even if new (or previously
non-fixable-in-place) findings remain. `--converge` instead **loops** the pipeline — Review→Merge→
Verify→Fix, again, and again — until one of three things happens:

1. **Converged** — the repo has **0 open P0-P3 findings** (every survivor was REFUTED or successfully
   applied). The loop stops and the report says so.
2. **Plateaued** — a pass applied **0** new fixes (every remaining CONFIRMED finding is not
   fixable-in-place, was skipped over the fix cap, or a fix agent could not apply it; or every
   remaining finding is PLAUSIBLE/unverified rather than CONFIRMED). Looping further would burn budget
   with no possible progress, so the loop stops and reports the remaining open count as needing
   **human review** — never silently claimed clean.
3. **`--max-iterations` hit** (default 5, hard-capped at 20) — the loop stops and reports the open
   count, same honesty rule.

**Cost stays bounded because of the existing content-hash cache** (`review_cache.py`) — a Fix pass
only ever touches the files it actually edited, so the *next* Review pass gets a cache hit (near-zero
cost) on every file it didn't touch and only genuinely re-reviews what changed. Each iteration's
findings/merged-JSON/fix-receipts land at suffixed paths (`findings-iter2/`, `merged-iter2.json`, …) so
no iteration's artifacts overwrite another's — the final report always cites the last iteration's
paths, and the full history (survivors/confirmed/applied/open-after per iteration) is in the report's
"Convergence" section.

**The convergence-honesty contract** (mirrors this skill's existing coverage-honesty contract): the
report's convergence line is **never omitted** and **never claims 0 open findings unless it's true** —
"CONVERGED — 0 open P0-P3 finding(s)" only when the loop actually reached 0; otherwise "NOT CONVERGED —
plateaued…" or "NOT CONVERGED — hit convergeMaxIterations…", each stating the real remaining count.

⛔ **A convergence loop cannot force a fix a fix agent has already declined.** A finding whose
`fixable_in_place` is `false` (e.g. it needs an architectural decision, a signature change, or a
cross-file coordination the fix agent is deliberately barred from making) will **plateau every run** —
that is by design, not a bug: `--converge` is honest that it converges to "everything auto-fixable is
fixed," not to "every finding is gone." The report's plateau line names this explicitly so a human
knows what's left and why it's theirs.

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
Report, with each survivor carrying a derived P0-P3 priority. A pre-flight cost estimator
([`scripts/estimate_cost.py`](scripts/estimate_cost.py)) implements the `--estimate-only` path and is
also what a normal run consults first to decide whether `--full` at the requested tier is affordable
before dispatching a single review agent. When `--converge` is set, the Review→Merge→Verify→Fix span
loops (see [§ Convergence loop](#convergence-loop---converge) above) instead of running once.

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
| `scripts/findings_merge.py` priority derivation | P0-P3 `priority_for()` map, `by_priority` counts, fixed key order (test9) |

**The `--converge` loop's SAFETY invariants (never its runtime behavior) are gated structurally**, via
[`scripts/check-repo-review-converge.mjs`](../../../../scripts/check-repo-review-converge.mjs) — also
part of [Gate 260](../../../../scripts/audit-gates.sh), the same tier as Gate 51's shell-router checker
and Gate 144's prompt-builder XSS-floor checker: pure text-based assertions over the workflow source
(no `eval`/`new Function`), proving `MAX_ITERATIONS` is clamped to `[1, 20]`, the three loop exits
(converged / plateau / max-iterations) and their honesty-contract report lines are present, `AUTOFIX`
correctly implies `CONVERGE`, `openAfterCount` can never go negative, and the SEVERITY_RANK regression
(below) can't silently reappear — each with a must-fail teeth mutant. **This does NOT prove the loop
converges correctly at runtime** — that needs a real dispatched multi-iteration run, which this build
did not do (see the `Workflow`-tool caveat below; the same honest limit applies).

**A real pre-existing bug was found and fixed while building this:** the workflow's own Verify-phase
severity sort used `{critical:0, high:1, medium:2, low:3}` — a vocabulary that has **never** matched
what dimension agents actually emit (`blocking|major|minor|nit`, per `reference/dimensions.md` and
`findings_merge.py`'s own `SEVERITY_RANK`). Every real finding's severity therefore fell through to the
`?? 9` fallback, so the "severity-sorted verifyCap" was silently unsorted (a stable no-op) on every run
this skill has ever made. Fixed by using the same map `findings_merge.py` already uses; Gate 260 pins
the regression.

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

**`--converge` has NOT been proven end-to-end against a real multi-iteration dispatched run.** Its
safety invariants are gated structurally (Gate 260, above); its actual convergence behavior — does a
real repo's findings genuinely shrink pass over pass, does the content-hash cache actually keep the
re-review cost near-zero on a live run, does a real plateau get correctly detected — has not been
observed. Do not cite this skill's convergence-loop section as proof it has converged a real repo; it
is reasoned-through and structurally gated, not yet measured.

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
- **P0-P3 priority + `--converge` loop (this build):** `findings_merge.py` gained `priority_for()` +
  `by_priority`, exercised by its own `--self-test` (test9). The workflow's Verify-phase severity-sort
  mismatch (found while wiring this) was fixed. `audit-gates.sh` Gate 260 registered (dispatcher + main
  sequence + `Supported:`), with 2 must-fail teeth checks (plateau-detection stripped; the old
  mismatched severity map restored), passing.

**Not yet done, stated explicitly so nobody assumes it silently happened:**

- A real end-to-end run against this marketplace's own repo (or any real, non-fixture repo) — the
  proof-run above is against the 14-file synthetic fixture, not a repo at production scale.
- Execution via the actual `Workflow` tool (see the caveat above) — gated on user opt-in, not a design
  choice.
- The `judge` near-duplicate policy tier's real model-adjudication step (currently: tag + collect only,
  per the merge script's own documented scope).
- **A real multi-iteration `--converge` run** — the loop's SAFETY invariants are gated structurally
  (Gate 260); its actual runtime convergence behavior on a real repo has not been observed (see above).

Do not cite this skill's mechanism section as proof the pipeline has been run at production scale
against a real repo. It has been proven correct on a small, real, live-dispatched run — not yet at
scale, and not yet through the `Workflow` tool specifically.
