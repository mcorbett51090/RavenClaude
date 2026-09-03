---
id: repo-review-corroboration-bucket-diff
title: "Cross-model corroboration silently missed same-line duplicate findings"
category: "Inventory — measured mechanisms"
kind: ravenclaude-built
entry_class: inventory
order: 918
summary: "findings_merge.py's near-dup detector required bucket-diff == 1, excluding 0 -- two models finding the same bug on the same line, worded differently, got no corroboration flag."
last_verified: 2026-09-02
covers:
  - plugins/ravenclaude-core/skills/repo-review/SKILL.md
  - plugins/ravenclaude-core/commands/repo-review.md
  - plugins/ravenclaude-core/skills/repo-review/reference/dimensions.md
  - plugins/ravenclaude-core/skills/repo-review/scripts/repo_map.py
  - plugins/ravenclaude-core/skills/repo-review/scripts/review_cache.py
  - plugins/ravenclaude-core/skills/repo-review/scripts/findings_merge.py
  - plugins/ravenclaude-core/skills/repo-review/scripts/fix_summary.py
  - plugins/ravenclaude-core/skills/repo-review/scripts/estimate_cost.py
  - plugins/ravenclaude-core/skills/repo-review/workflows/repo-sweep.workflow.js
covers_digest: "sha256:bce3386f7e1414b4be05ad2dd2702abdc27b599f062c1a08c2612baf6502eea7"
nuance: "A dedup key built from each finding's own title tokens misses two models describing
  one bug in different words at the same line -- keys differ, so exact-key merge misses it.
  The near-dup fallback's bucket-diff bound was `== 1` (adjacent only), excluding 0 (the
  identical line) -- the single most common real shape cross-model review exists to catch."
nuance_evidence:
  measured: 2026-09-02
  control: "A live cross-model dispatch (sonnet + opus) against the repo-review skill's own
    fixture repo: both models independently flagged app/services/db.py:21 as SQL injection,
    worded differently (\"SQL injection via %-formatted owner value...\" vs \"SQL injection:
    owner is string-formatted...\"). Before the fix, findings_merge.py's merged.json showed
    both as separate survivors with corroboration: null and near_duplicate: false -- the same
    bug, same line, cross-model agreement, and the pipeline's own corroboration signal never
    saw it. Six such pairs existed in that one proof-run (db.py, scheduler.py, task_service.py,
    plus three resource-leak pairs in file_processor.py)."
  falsifier: "a same-line cross-model pair that DID get flagged near_duplicate before the fix
    (would mean the bucket-diff==1 requirement was not actually excluding 0); none was found --
    every same-line pair in the proof-run's 18 survivors read near_duplicate:false pre-fix and
    near_duplicate:true after changing the bound from `!= 1` to `> 1`."
  probe: "plugins/ravenclaude-core/skills/repo-review/scripts/findings_merge.py"
nuance_source: "plugins/ravenclaude-core/skills/repo-review/SKILL.md \"honest status\""
verify:
  tier: "effect"
  strength: "executed"
  class: "gate-self-test"
  probe: "plugins/ravenclaude-core/scripts/audit-gates.sh --check 258"
  teeth_exit: 1
sources:
  - label: "repo-review build + live proof-run, 2026-09-02 -- cross-model dispatch against the fixture repo caught the defect in findings_merge.py itself"
    url: "plugins/ravenclaude-core/skills/repo-review/SKILL.md"
---

## What a reader would have assumed instead

That a near-duplicate check scoped to "adjacent line buckets" (`abs(a_bucket - b_bucket) == 1`)
was deliberately narrow to avoid double-flagging the exact-key match case -- i.e. that
bucket-difference 0 was excluded ON PURPOSE because same-key findings are already merged
upstream. That assumption is false whenever two findings land in the same bucket but do NOT
share an exact key, which happens constantly in practice: two models describing the same bug
almost never choose the same six sorted title tokens.

## The discriminator

control: a live cross-model dispatch against the repo-review fixture repo. sonnet and opus both
read `app/services/db.py` and both flagged line 21 as SQL injection -- genuine agreement on the
same bug, same file, same exact line (bucket difference 0, not 1). Their titles differed enough
that the exact-key hash (built from each finding's own top-6 sorted title tokens) never matched.
The near-duplicate fallback's `!= 1` bound then also skipped them, because 0 != 1. Both signals
that exist specifically to catch cross-model agreement missed the cleanest possible instance of
it, in the same proof-run, six separate times.

## Why it matters

Falsifier: a same-line cross-model pair that WAS flagged near_duplicate under the old bound --
none was found across the 18-survivor proof-run; every same-line pair read
`near_duplicate: false` before the fix.

Probe: `findings_merge.py --self-test` (`test8`), and Gate 258's teeth check, which reverts the
bound to `!= 1` and asserts the mutant's self-test then fails.

`corroboration` is the field a `/repo-review` user reads to judge whether a finding is a single
model's guess or two models' independent agreement -- exactly the signal cross-model review is
built to produce. A dedup design that silently drops that signal on the most common real shape
doesn't fail loudly; it fails as a quieter, less-trustworthy report that looks identical to a
working one. The bound is now `> 1` (skip only when buckets differ by MORE than 1), which covers
both 0 and 1, with a permanent regression assertion so this cannot silently regress again.
