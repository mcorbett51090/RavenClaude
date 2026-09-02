---
description: "Systematic whole-repo bug sweep across 8 dimensions (correctness, security, concurrency, resource-leaks, error-handling, performance, ci-cd-actions-security, dead-code-simplification), risk-sampled and effort-tiered, with optional cross-model verification and a confirmed-only auto-fix pass. Not a diff/PR reviewer — that's the built-in /code-review."
allowed-tools: Bash, Read, Write, Edit, Task
argument-hint: <effort:high|xhigh|max|ultra> [--only <pathspec>] [--since <ref>] [--fix] [--full] [--cross-model|--no-cross-model] [--risk-floor <n>] [--estimate-only]
---

# /repo-review

Provide a systematic bug review of the **current repository** — every reviewable file, not a diff.

**Disambiguation:** this is a different command from Claude Code's own built-in `/code-review`, which
reviews a diff, a PR, a branch, or a path. `/repo-review` has no PR/diff mode; it is the whole-repo
systematic sweep. If the user wants a change reviewed, point them at `/code-review` instead.

**Load `skills/repo-review/SKILL.md` and follow it.** It owns the mechanism, the dimension prompts
(`reference/dimensions.md`), and the honest build-status statement. This file is the thin entry
point only.

## Flag surface (terse restatement — the skill owns the full contract)

```
/repo-review <effort> [--only <pathspec>] [--since <ref>] [--fix] [--full]
             [--cross-model | --no-cross-model] [--risk-floor <n>] [--estimate-only]
```

`effort` ∈ `high | xhigh | max | ultra`. `low`/`medium` are refused. `--fix` applies confirmed findings
as an uncommitted patch only. `--full` bypasses sampling + the file-count cap and needs confirmation.

## Steps

1. **Parse `effort` first.** If it is `low`, `medium`, absent-and-unclear, or anything not in
   `{high, xhigh, max, ultra}`, **refuse immediately** — do not run a degraded sweep. Tell the user:
   *"`/repo-review` only runs at `high`/`xhigh`/`max`/`ultra` — a shallow pass over a sampled repo
   reports an absence of findings that reads as clean when it means barely looked. Use `high` for the
   cheapest real sweep, or narrow scope with `--only <pathspec>` instead."*
2. **If `--estimate-only` is set,** run only the zero-agent-call planning pass:
   `scripts/repo_map.py` to build the chunked, risk-ranked plan, then `scripts/estimate_cost.py`
   against that plan and the requested effort tier. Report the projected agent-call count and stop —
   do **not** dispatch any review agent, do **not** run the Workflow fan-out.
3. **Otherwise, invoke the `repo-review` skill** and let it drive the full mechanism (chunk → cache →
   Workflow fan-out → merge → verify → fix → report) per its own contract. This command does not
   restate that logic — restating it here means paying for the pipeline's description twice on every
   run, exactly the reason `commands/forge.md` stays a thin entry point over `skills/forge-pipeline/`.
4. **Before reporting done, re-read the skill's honest-status section** and never claim (in this
   session's report) that the pipeline has been run end-to-end against a real repo unless it actually
   was in *this* run — the skill is explicit that it has not been, as shipped.

## Related artifacts

- Skill: [`skills/repo-review/SKILL.md`](../skills/repo-review/SKILL.md)
- Dimension prompts: `skills/repo-review/reference/dimensions.md`
- Chunker: `scripts/repo_map.py`
- Cache: `scripts/review_cache.py`
- Merge: `scripts/findings_merge.py`
- Cost estimator: `scripts/estimate_cost.py`
- Workflow: `workflows/repo-sweep.workflow.js`
- Fixture repo: `tests/fixtures/repo-review/mini-repo/`
- Plan schema: `schemas/repo-review-plan.schema.json`
