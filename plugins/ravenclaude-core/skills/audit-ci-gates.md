---
name: audit-ci-gates
description: For any consumer project where a CI workflow is meant to *enforce* a property (lint, format, security scan, manifest validation, version pin, layout allow-list, etc.). When working on a CI file or adding a new check, run this skill — every gate must fail on a known-bad input AND pass on a known-good input. A gate that runs without gating, or gates the wrong thing, is invisible from inside a green CI dashboard. Also triggers on user phrases like "audit the CI", "verify the gates", "is this gate real", "does this lint actually fail".
---

# Skill: audit-ci-gates

You're working in a consumer project that has `ravenclaude-core` installed. A CI workflow exists or is about to be changed. Your job is to make sure every step that claims to be a *gate* actually gates — both directions.

The full rationale lives in [`docs/best-practices/ci-gate-audit.md`](../../../docs/best-practices/ci-gate-audit.md) in the RavenClaude marketplace; the rule was added after the marketplace's own self-review caught two failure modes consecutively: a gate that *ran but didn't gate* (actionlint with no `-exit-code` flag), and a gate that *gated the wrong thing* (a shell-wrapper that tripped on docker pull noise). Both were caught by the same audit-by-fixture practice.

## The pattern, named

**For every CI step that claims to enforce a property, prove it can fail on a known-bad input AND pass on a known-good input.**

## When to invoke this skill

- Before adding a new CI step to any `.github/workflows/*.yml`.
- After changing any existing gate (regex update, tool upgrade, wrapper refactor).
- On any "is this gate real?" / "did the lint actually fail?" question.
- During a code-review of a CI change.
- Periodically as a fitness check — a gate's tool can drift behavior across upstream releases.

## Procedure

### Step 1 — Inventory the gates

List every step in the workflow files that's meant to enforce a property. Skip steps that are explicitly informational (annotation posters, metric publishers — flag those with a header comment so future contributors know they're not gates).

### Step 2 — For each gate, define two fixtures

- **`must_fail_on`** — an input that violates the property the gate enforces. The step must exit nonzero / set the failure signal.
- **`must_pass_on`** — a legitimate input that satisfies the property. The step must exit zero and not emit confusing errors.

Both fixtures should be the *smallest* repro of their target case. A 3-line YAML with a column-0 `**bad` is enough to test an actionlint gate; you don't need a realistic broken workflow.

### Step 3 — Run each fixture against the gate

For each gate-fixture pair, mutate the relevant file temporarily, run the gate's underlying check, capture the exit code (or boolean signal), restore the file, and compare to the expected direction. A reusable pattern (Bash):

```bash
backup=$(mktemp)
cp .github/workflows/<target>.yml "$backup"
trap 'cp "$backup" .github/workflows/<target>.yml; rm -f "$backup"' EXIT INT TERM

# Inject the must_fail_on fixture
sed -i '<line>a\<bad-content>' .github/workflows/<target>.yml

# Run the gate's underlying check
<tool> <args> ; rc=$?

# Assert
if [[ "$rc" -ne 0 ]]; then echo "OK: gate caught the bad input"; else echo "FAIL: gate is paper-tiger"; fi
```

### Step 4 — Wire it as a meta-test

Once every gate has a verified fixture-pair, codify them in a single audit script (e.g. `scripts/audit-gates.sh`) and add a step to the workflow that runs the script. This makes "all gates still gate correctly" a CI-enforced invariant — a gate that loses its teeth gets caught at the next PR, not in the next real incident.

RavenClaude's marketplace ships an example at `scripts/audit-gates.sh` you can use as a starting structure.

### Step 5 — Anti-patterns to flag during review

- **A linter wired as a Docker container action** (`uses: docker://...`) without exit-code semantics — the binary likely exits 0 on findings; needs a shell wrapper.
- **A shell wrapper that captures `2>&1`** when the tool writes findings to one stream — wrapper will trip on incidental stderr (deprecation warnings, image pulls).
- **A grep-based gate that grep-empty returns 0** when the intent was "fail on the absence" — invert the logic or use `! grep`.
- **A test step with `continue-on-error: true`** — that's an "advisory only" flag; the step is not a gate.
- **A custom script that `|| true`s the linter call** — same as above; the `|| true` swallows the failure.

## Output

After running the audit, produce a structured report:

```
## Gates inventoried
<list of gates, with one-line description of what each enforces>

## Fixture-pair verdicts
<table or bullets: gate name | must_fail outcome | must_pass outcome | OK/FAIL>

## Findings
<list of paper-tiger gates or wrong-direction gates that need fixing>

## Recommended fixes
<for each finding: the minimal change to make the gate enforce its target property bidirectionally>
```

Then end with the Structured Output Protocol JSON block per [`structured-output.md`](./structured-output.md):

```
---RESULT_START---
{
  "status": "complete" | "partial" | "blocked",
  "summary": "audited N gates; M failed at least one direction",
  "deliverables": ["audit-report (above)", "<paths to any new audit script>"],
  "handoff_recommendation": {"to_specialist": "backend-coder", "reason": "X gates need wrapper fixes"} or null,
  "confidence": 0.0-1.0,
  "risks_or_open_questions": ["..."],
  "next_actions": ["wire audit script into CI as a meta-test", "..."]
}
---RESULT_END---
```

## Anti-patterns specific to this skill

- **Do not** trust a green CI dashboard as proof of CI correctness. Run the audit.
- **Do not** ship a new CI gate without its fixture-pair in the same PR — paper tigers are easiest to spot at PR time.
- **Do not** count an annotation-only step (one that posts a comment but doesn't fail the build) as a gate. Annotations are signal; gates are enforcement.
