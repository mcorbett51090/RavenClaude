---
id: preflight-predicate-not-evaluable
title: "Pre-flight rules and post-hoc predicates"
category: "Inventory — measured mechanisms"
kind: ravenclaude-built
entry_class: inventory
order: 913
summary: "A rule about how a command turned out cannot run before the command."
last_verified: 2026-08-25
covers:
  - plugins/ravenclaude-core/scripts/build-outcome-corpus.py
  - plugins/ravenclaude-core/scripts/guard-cause-closure.sh
  - plugins/ravenclaude-core/scripts/guard-remediation-cause.sh
  - plugins/ravenclaude-core/scripts/preflight-command-review.sh
  - plugins/ravenclaude-core/scripts/replay-outcome-rules.py
covers_digest: "sha256:aa8f6c84b60bfc4c21a122a9caa76adc826bd7e24ca34ab4bf2c890915630338"
nuance: "Two of five drafted pre-flight rules name a result that CAME BACK EMPTY — which a `PreToolUse` hook cannot know — so their offline fire rates scored a field absent at fire time; re-measured lexically, one went from 1.43% to 8.28%."
nuance_evidence:
  measured: "2026-08-25"
  control: "the same rule measured post-hoc (with stdout_empty) fired 487 times and lexically (without it) 2,816 times over the same 34,014 evidence-bearing commands, so the gap is the missing field and not a different corpus"
  falsifier: "a PreToolUse payload carrying the tool result"
  probe: "plugins/ravenclaude-core/scripts/replay-outcome-rules.py"
nuance_source: plugins/ravenclaude-core/scripts/preflight-command-review.sh:26-42
verify:
  tier: "effect"
  strength: "executed"
  class: "script-selftest"
  probe: "plugins/ravenclaude-core/scripts/replay-outcome-rules.py"
  teeth_exit: 1
strength_badge: Probed
sources:
  - label: "measured in the verify-before-assert Phase 1 corpus run"
    url: "https://github.com/mcorbett51090/RavenClaude/blob/main/docs/plans/2026-08-19-verify-before-assert/plan.md"
---

## What a reader would have assumed instead

That a pre-flight rule and a post-failure rule are the same rule pointed at a
different moment, so a candidate measured on recorded outcomes can simply be
moved to `PreToolUse` once it clears its ceiling.

## The discriminator

control: the same candidate measured two ways over one 34,014-command corpus —
with `stdout_empty` in the predicate it fires 487 times (1.43%), and with that
field removed it fires 2,816 times (8.28%). One corpus, one rule, two numbers:
the difference is the field, not the sample.

A `PreToolUse` hook runs **before** the command. Any predicate naming the result
— empty stdout, a non-zero exit, a truncated count — is unevaluable there. A
rule written that way does not become noisy at pre-flight; it becomes a
*different rule*, and the offline number that justified it was never a
measurement of the thing that would ship.

## Why it matters

The offline harness will happily report a passing fire rate for a rule that
cannot exist. Both candidates cleared their ceilings on paper. Shipping either
would have put a rule into the pre-flight path whose measured justification
belonged to a predicate the hook could never evaluate — a green number attached
to the wrong mechanism.

The hazard itself was real in both cases and is not lost: it is delivered
post-hoc by `triage-outcome.sh`, which ranks the matching taxonomy members first
at the moment the result IS known. The correction was to move the rule to the
event where its predicate exists, not to widen it until the lexical form passed.

Probe: `replay-outcome-rules.py --rule R-1 --sample 40`, then read whether the
predicate names anything the command has not done yet.
