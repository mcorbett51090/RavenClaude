---
id: workaround-exhaustion-own-deny-never-anchors
title: "The blocked-exhaustion gate must not anchor on its own deny"
category: "Inventory — measured mechanisms"
kind: ravenclaude-built
entry_class: inventory
order: 940
summary: "The gate measures the ledger from the most recent guard deny; if its own block-mode deny counted as that anchor, every block would reset the window to 0 of 3 and it could never be satisfied."
last_verified: 2026-09-17
covers:
  - plugins/ravenclaude-core/hooks/workaround-exhaustion.sh
  - plugins/ravenclaude-core/hooks/tests/test-gate290-workaround-exhaustion.sh
  - plugins/ravenclaude-core/knowledge/workaround-routes.md
covers_digest: "sha256:325e73970b3406c9ac8dfdfc6ba66738593824933ea36ada6607a19c66707fbf"
nuance: "_last_deny reads hook-events.jsonl and returns the newest verdict: deny line whose
  hook is NOT workaround-exhaustion.sh. The gate emits its own deny to the same file in
  block mode, so without that name filter each block would become the newest deny, the
  window would restart behind every row already recorded, and the floor could never be met."
nuance_evidence:
  measured: 2026-09-17
  control: "Gate 290 B4-B6: in block mode the gate denies a hand-back question at 0 rows
    (B4) and that deny lands in hook-events.jsonl (B5); one mcp-api row is then recorded
    and the same question re-run reads '1 of 3' (B6) -- the window is still measured from
    the ORIGINAL guard deny, not from the gate's own. A mutant with the name filter removed
    reads '0 of 3' on B6, because the newest deny is now the gate's, later than the row."
  falsifier: "a hook-events line with hook workaround-exhaustion.sh and verdict deny that
    _last_deny returns as the anchor; the jq select excludes that hook name, so none does."
  probe: "plugins/ravenclaude-core/hooks/workaround-exhaustion.sh"
nuance_source: "plugins/ravenclaude-core/hooks/workaround-exhaustion.sh header, 'our own block must never re-anchor the window it measures'"
verify:
  tier: "effect"
  strength: "executed"
  class: "gate-self-test"
  probe: "scripts/audit-gates.sh --check 290"
  teeth_exit: 1
sources:
  - label: "ravenclaude-core 0.324.0 -- the blocked-exhaustion gate (CHANGELOG + constitution milestone), 2026-09-17"
    url: "plugins/ravenclaude-core/CHANGELOG.md"
  - label: "the route catalog the gate points at"
    url: "plugins/ravenclaude-core/knowledge/workaround-routes.md"
---

## What a reader would have assumed instead

That "the most recent guard deny this session" is simply the last `verdict: deny` line in
`hook-events.jsonl`. It is the obvious query, and it is wrong for this one hook, because this
hook is itself a guard that writes deny lines to that file. A gate that anchors on the newest
deny and also emits denies measures its own output.

## The discriminator

control: Gate 290 B4 drives a block-mode hand-back question against a session with one guard
deny on record and zero ledger rows -> `permissionDecision: deny`; B5 finds that deny in the
session's `hook-events.jsonl` with `hook: workaround-exhaustion.sh`; B6 then records one
`mcp-api` row and re-runs the question -> the nudge reads `1 of 3`. If the gate's own deny were
the anchor, that row (written after the original deny but before the gate's) would fall behind
the window and the count would read `0 of 3`. The `jq` select in `_last_deny` is
`select(.verdict=="deny" and (.hook // "") != "workaround-exhaustion.sh")`; the name test is the
whole mechanism.

## Why it matters

Falsifier: a `hook-events.jsonl` line from this gate that `_last_deny` returns. None can, by the
select above. Without the filter the failure is not loud -- the gate keeps firing, every
re-record looks ignored, and the only exit is `blocked-ok`, which is exactly the escape the
gate exists to make rare. That shape (a guard whose own output feeds its trigger) is the same
class as a runaway brake that counts its own denials as tool calls; the fix is one predicate,
and the test that pins it is the one that records a row *between* the two denies.
