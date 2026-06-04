# CI gate audit — every gate must fail on a known-bad input AND pass on a known-good input

**Status:** **Absolute rule** — never break this. Violations are bugs, not preferences.

**Domain:** CI hygiene, cross-domain.

**Applies to:** Any repository where a CI workflow is meant to *enforce* a property (lint check, security scan, manifest validation, format check, regex test, version pin cross-check, layout allow-list, etc.). The rule applies equally to plugin marketplaces, application repos, library repos, and documentation repos.

---

## Why this exists

A CI step that runs is not necessarily a CI step that gates. Worse, a CI step that gates can gate the wrong thing. Both failure modes are invisible from inside a green CI dashboard — the workflow log shows the step executing, the workflow conclusion shows success, and reviewers conclude "the gate held." But:

- A linter with **no `-exit-code` flag** (actionlint 1.7.7, semgrep without `--error`, several SAST tools by default) reports findings to stdout/stderr but exits 0. The workflow stays green. The gate is a paper tiger.
- A shell-wrapper around such a tool can **gate on the wrong thing**: capturing stderr to detect findings will trip on incidental noise (docker pull progress, deprecation warnings) on a fresh runner, even when the underlying tool ran cleanly.
- A gate that does fail on its target violation but **silently rejects legitimate inputs** is just as broken — flaky CI erodes trust faster than no CI.

This rule originated from RavenClaude's PR 9 → PR 12 → PR 13 chain (2026-05-21). The marketplace shipped `rhysd/actionlint:1.7.7` as a Docker container action; CI passed on the first push and the score chain scored it 10/10 on test/verification depth. A researcher dispatched to verify the *behavior* of the step (rather than its *presence*) caught that actionlint exits 0 even on YAML parse errors. The shell-wrapper that replaced it then **false-positive-tripped on docker's image-pull stderr** on the next push — gate that gates the wrong thing. Both bugs were caught by the same audit-by-fixture practice. Codified here so future contributors don't relearn the lesson on every gate they add.

## How to apply

For every CI step that claims to enforce a property, write **two fixtures** and prove the step's behavior on each:

- **`must_fail_on`** — an input that violates the gate's target property. The step must exit nonzero (or set `status=1`, or whatever the failure signal is for that workflow).
- **`must_pass_on`** — a legitimate input that satisfies the property. The step must exit zero AND not surface a confusing error.

Both fixtures live in [`scripts/audit-gates.sh`](../../scripts/audit-gates.sh). Run it from the repo root:

```bash
scripts/audit-gates.sh
```

A clean repo passes every fixture-pair. When you add a new gate, add a corresponding fixture-pair to the script and prove it works **before** wiring the gate into CI.

The same script runs in [`.github/workflows/validate-marketplace.yml`](../../.github/workflows/validate-marketplace.yml) as a meta-test: every PR that touches CI (or anything else) re-verifies that each gate still fails on its known-bad fixture. A gate that quietly loses its teeth gets caught at the next PR, not on the next real incident.

**Do:**

- Add the fixture-pair to `scripts/audit-gates.sh` in the same PR that adds the gate.
- Test the gate locally against both fixtures before pushing.
- After fixing a gate that was discovered to be paper-tiger, re-run the full audit script — the fix may regress an adjacent gate.
- Use **stdout-only or stderr-only capture** when wrapping a tool that exits 0 on findings. Merging streams with `2>&1` will trip on runner noise.
- Pre-pull container images in a separate step so pull progress is out of the capture for any docker-based linter.
- For a **container-based gate, probe real usability** (daemon up AND image present-or-pullable, every probe `timeout`-bounded) before asserting — `command -v docker` is not enough. If the tool can't actually run, the gate must **announce itself loudly, never silently skip or falsely pass**: skip-loud locally ("this is NOT a pass") and treat unrunnable-in-CI (`$CI` set) as a hard audit failure, since the real gate it mirrors already hard-fails there. (This usability-probe + loud-skip pattern is the general rule for any container-based gate.)
- **Prefer a checksum-pinned release binary over a Docker Hub image** when the linter ships one. Gate 10 / actionlint was migrated off `rhysd/actionlint:1.7.7` (a mutable Docker Hub tag, subject to anonymous **pull-rate-limits** — the failure that broke `validate-marketplace` on PR #93) to a sha256-verified `actionlint` binary from the GitHub release. A pinned checksum is also stronger supply-chain integrity than a mutable tag. The same loud-skip-locally / hard-fail-in-CI discipline applies when the binary can't be fetched (offline).

**Don't:**

- Skip the audit because "the gate looks fine in the workflow file."
- Trust a green CI run as proof of CI correctness. CI conclusion is signal, not proof.
- Wire a third-party linter that exits 0 on findings without wrapping it.
- Conflate "the step ran" with "the step gated."

## Edge cases / when the rule does NOT apply

- **Informational-only steps** that explicitly do not gate (e.g., a step that posts metrics or annotations for human review). Mark these with a header comment naming them advisory and exclude them from `audit-gates.sh`. The exclusion is the documentation.
- **Steps that gate on the workflow's *presence*** (e.g., "this workflow must run at all") rather than on a property of the code. The audit-by-fixture pattern doesn't apply because there's no input variable to mutate.
- **Tests inside the gate itself** — the rule applies to the gate's *enforcement* layer, not to every assertion inside a unit test suite. A test suite IS the audit fixture for the code it tests.

### Self-healing artifacts (freshness enforced post-merge, not on PRs)

Some gates enforce that a **committed generated artifact** matches what its generator would produce (a "freshness gate"). For a *repo-wide* artifact that every PR regenerates — e.g. `repo-guide.html`, whose roster/counts change on every plugin add — a PR-time freshness gate becomes a **cross-PR contagion**: concurrent plugin PRs each regenerate the file into their own branch, so they merge-conflict on it, and whichever branch goes stale as a sibling merges fails the gate through no fault of its own diff. The gate punishes parallelism instead of catching a real defect.

The fix is to move freshness from **blocking on PRs** to **self-healing on `main`**: a `push: main` workflow regenerates the artifact and commits it back (`[skip ci]`), PR branches stop touching it, and the PR-time freshness gate is removed. `repo-guide.html` works this way as of 2026-06 — owned by `.github/workflows/regenerate-artifacts.yml`.

When you do this, **the audit-by-fixture rule still applies — the must_pass half just relocates:**

- **Keep the `must_fail` half** in `audit-gates.sh` (mutate the source, assert the detector flags it). The post-merge workflow relies on that same detector both to decide whether to regenerate and to verify it succeeded, so the detector must still be proven to have teeth.
- **Move the `must_pass` (clean-tree) half** into the post-merge workflow's verify step — run the detector after regenerating; a fresh tree must pass. That is the legitimate place to assert "the committed artifact is fresh," because that is the one tree the workflow guarantees is fresh.

Document the relocation with a header comment at the (now-removed) PR gate and at the surviving `must_fail` fixture, so the missing clean-tree assertion reads as *intentional*, not as a gate that quietly lost its teeth. **Not every generated artifact qualifies** — one that other gates structurally depend on (e.g. `dashboard.html`, whose render-test gates extract functions from the committed file) should stay PR-gated, because its freshness gate is also what keeps it in lockstep with generator/schema changes.

## See also

- [`../memory-bank/lessons-learned.md`](../memory-bank/lessons-learned.md) — the 2026-05-21 entry "A step that runs is not necessarily a step that gates" carries the origin trace and the actionlint-specific repro.
- [`./hook-authoring.md`](./hook-authoring.md) — hooks are gates too; the same audit-by-fixture exercise applies to PreToolUse / PostToolUse hooks (a hook that fires but doesn't deny is the moral equivalent of a CI step that runs but exits 0).
- [`../live-dispatch-checklist.md`](../live-dispatch-checklist.md) — Exercise 0 (CI gate audit) — the live-dispatch equivalent of this rule, run on any change to the workflow's gate set.
- [`../../scripts/audit-gates.sh`](../../scripts/audit-gates.sh) — the executable form of this rule. Read it before adding a new gate.

## Provenance

Surfaced 2026-05-21 during the marketplace's R6 self-review chain. Originated from researcher-dispatched verification of actionlint behavior in GitHub Actions, sharpened by the Plan agent's review of PR 12, codified after PR 13 fixed a regression introduced by PR 12. The pattern names itself: **for every CI step, prove it can fail on a known-bad input AND pass on a known-good input.**

---

_Last reviewed: 2026-05-24 by `@mcorbett51090`_
