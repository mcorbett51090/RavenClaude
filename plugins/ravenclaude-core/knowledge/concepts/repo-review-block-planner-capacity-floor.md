---
id: repo-review-block-planner-capacity-floor
title: "A capacity floor masked the guard it was supposed to let fire"
category: "Inventory — measured mechanisms"
kind: ravenclaude-built
entry_class: inventory
order: 939
summary: "block_planner.py's _capacity() unconditionally floored its result at 1, so the 'even a 1-batch finalize block does not fit' guard could never actually raise."
last_verified: 2026-09-16
covers:
  - plugins/ravenclaude-core/skills/repo-review/scripts/block_planner.py
  - plugins/ravenclaude-core/skills/repo-review/workflows/repo-sweep.workflow.js
  - plugins/ravenclaude-core/skills/repo-review/SKILL.md
covers_digest: "sha256:9b7b9f447605fa72915be31351bfcdc8f633c9b87eca2e37c3ec32006b3c5c83"
nuance: "_capacity() clamps every result to max(1, ...) so a block always covers at least
  one batch once it exists. The finalize-capacity guard read that ALREADY-CLAMPED value,
  so 'nothing fits at all' could never be observed -- the clamp and the check that needs
  the unclamped truth were reading the same variable."
nuance_evidence:
  measured: 2026-09-16
  control: "block_planner.py's own --self-test fixture 6 calls plan_blocks(huge_plan,
    tier='ultra', safe_ceiling=1) and expects BlockPlanError. Before the fix this
    silently returned a 1-batch finalize block instead of raising -- the fixture
    itself was the first thing to demonstrate the guard was unreachable, on its
    first real run, before any manual review caught it."
  falsifier: "a safe_ceiling value that reached the raise branch through the OLD
    (already-clamped) check; none exists, because max(1, x) for any real x is >= 1,
    so `finalize_capacity < 1` is a tautological false regardless of how small
    safe_ceiling is set."
  probe: "plugins/ravenclaude-core/skills/repo-review/scripts/block_planner.py"
nuance_source: "plugins/ravenclaude-core/skills/repo-review/SKILL.md \"honest status\""
verify:
  tier: "effect"
  strength: "executed"
  class: "gate-self-test"
  probe: "plugins/ravenclaude-core/scripts/audit-gates.sh --check 258"
  teeth_exit: 1
sources:
  - label: "repo-review block-mode build, 2026-09-16 -- block_planner.py's own --self-test caught the defect on first run"
    url: "plugins/ravenclaude-core/skills/repo-review/SKILL.md"
---

## What a reader would have assumed instead

That `if finalize_capacity < 1: raise BlockPlanError(...)` was a live, reachable guard against
an impossibly small `--safe-ceiling` -- the self-test even had a fixture asserting exactly that
("an impossibly small safe_ceiling raises BlockPlanError"). Reading the guard in isolation gives
no reason to doubt it; the defect is only visible by reading it alongside the helper that feeds
it.

## The discriminator

control: `_capacity(available, per_batch_cost, cap)` returns `max(1, min(cap, int(available //
per_batch_cost)))` -- for `safe_ceiling=1` against an "ultra" tier plan, `available` (the budget
left after reserving verify/fix/overhead) goes deeply negative, `int(available // per_batch_cost)`
is a large negative number, `min(cap, negative)` stays negative, and then `max(1, negative)`
clamps it back up to exactly `1`. The guard that follows, `if finalize_capacity < 1`, is checking
a value that can never be less than 1 by construction -- the clamp and the check were reading the
same post-clamp number.

## Why it matters

Falsifier: a `safe_ceiling` value, however small, that made the old check raise. None exists --
`max(1, x) >= 1` for every real `x`, so the branch was dead code that looked live. Fixed by
computing the raw `finalize_available` budget and comparing it against the real per-batch cost
`r` **before** calling `_capacity()`'s clamp: `if r > 0 and finalize_available < r: raise
BlockPlanError(...)`. `_capacity()` itself is unchanged -- clamping to a minimum of 1 is correct
for every OTHER caller, since a block that exists should always cover at least one batch; the fix
is moving the "does anything fit at all" question to before the clamp runs, not removing the
clamp.

This is the same shape as this repo's own recorded `guard-premise.sh` bare-`mkdir` incident and
the `srm.force-push`/`sce.curl-pipe-shell` unscoped-`.*` incidents: a guard whose input has
already had its failure signal smoothed away is a guard that can pass every review and still
never fire. It was caught here the cheapest possible way -- the tool's own `--self-test` failed
on its very first run, before the module shipped, rather than surviving to become a silent gap
in a later release.
