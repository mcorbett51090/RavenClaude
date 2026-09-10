---
id: prompt-optimizer-tier0-heuristic-limit
title: "The prompt-optimizer's free pre-filter can never fully close on non-anchored prompts"
category: "Inventory — measured mechanisms"
kind: ravenclaude-built
entry_class: inventory
order: 931
summary: "Tier-0's zero-cost skip rule is a whitelist over sentence shape, not a semantic understanding of triviality — an adversarial reviewer can always construct one more evasive phrasing."
last_verified: 2026-09-10
covers:
  - plugins/ravenclaude-core/commands/optimize.md
  - plugins/ravenclaude-core/scripts/prompt-optimizer-dispatch.sh
  - plugins/ravenclaude-core/scripts/prompt-optimizer-format.py
  - plugins/ravenclaude-core/scripts/prompt-optimizer-gate.sh
  - plugins/ravenclaude-core/scripts/prompt-optimizer-judge-soak.py
  - plugins/ravenclaude-core/scripts/prompt-optimizer-judge-soak.sh
  - plugins/ravenclaude-core/scripts/prompt-optimizer-rewrite.sh
  - plugins/ravenclaude-core/skills/prompt-optimizer/SKILL.md
  - plugins/ravenclaude-core/skills/prompt-optimizer/eval/golden-set.jsonl
covers_digest: "sha256:0cd423848dc86d2a1f3e83a031c27d8d7190a7922b4f3ca69842481db2ba9a66"
nuance: "A whitelist-based zero-anchor skip rule can be adversarially rephrased indefinitely — closing every demonstrated instance never closes the underlying gap, because the gap is a property of matching sentence shape, not meaning."
nuance_evidence:
  measured: 2026-09-03
  control: "the same 3 adversarial strings correctly TIER0_FALLTHROUGH after the cluster_hits==0 + possessive-pronoun tightening, proving the fix closed the demonstrated instances"
  falsifier: "a future Tier-0 rewrite that classifies by parsed intent rather than sentence-shape whitelist, which would not be defeated by a novel third-person or impersonal phrasing"
  probe: "plugins/ravenclaude-core/scripts/prompt-optimizer-gate.sh"
verify:
  tier: "none"
  rationale: "The residual is a structural property of a zero-network-call, zero-cost heuristic (not a coding defect) — closing it fully requires either always paying for a Tier-1 call on every zero-anchor prompt (defeating the whole point of a free tier) or an open-ended keyword arms race. Re-verifying it means adversarially rephrasing a prompt, which is exactly the human judgment call already made and recorded in the SDD fix-loop ruling, not a stageable CI check."
sources:
  - label: SDD fix-loop ledger — round-2 re-review adversarial variants + the controller's ruling to close the loop with a disclosed residual rather than a round-3 fix
    url: https://github.com/mcorbett51090/RavenClaude/pull/1098
---

## What a reader would have assumed instead

That once the reviewer's 3 adversarial paraphrases ("How do we migrate our monolith to microservices with zero downtime and full audit logging for compliance?" and its siblings) were fixed and added as golden-set regression fixtures, the Tier-0 free pre-filter's false-skip problem was closed for good — the same way a fixed bug in ordinary code stays fixed.

## The discriminator

control: the same 3 adversarial strings correctly TIER0_FALLTHROUGH after the `cluster_hits==0` + possessive-pronoun tightening, proving the fix closed the demonstrated instances.

Measured 2026-09-03 (round-2 re-review, agent a49c618f5d3d2c9c6): the reviewer's own three NEW adversarial variants — deliberately avoiding both signals the fix keys on (organizational-possessive pronouns and domain-keyword clusters) — still reproduce `TIER0_SKIP` on genuinely non-trivial prompts: *"Why is the checkout process so confusing?"*, a third-person migration question, and a tradeoffs-summary request. The fix is real (the originally-demonstrated shapes are closed and regression-gated in the 47-entry golden set), but the underlying gap — a zero-cost heuristic distinguishing "trivial" from "non-trivial" by sentence shape rather than meaning — is not closable by patching individual phrasings.

## Why it matters

`prompt-optimizer-gate.sh`'s Tier-0 pre-filter exists specifically so the paid Tier-1 Haiku classifier is never invoked on an obviously-trivial ask. Any whitelist-shaped rule for "obviously trivial" necessarily has an adversarial complement: a prompt built to avoid every signal the whitelist checks. The SDD fix loop closed this at round 2 (not round 3) via an explicit controller ruling rather than continuing to chase phrasings, because the feature ships `prompt_optimizer.enabled: false` by default, is advisory-only (`additionalContext`, never blocking), and the failure direction is a missed optimization (Tier-1 simply never fires on that turn) — identical to the feature's own off-by-default baseline for that narrow prompt shape, not a regression below it. The residual is disclosed in the script's own header comment (search for "HONEST LIMIT").

Falsifier: a future Tier-0 rewrite that classifies by parsed intent rather than sentence-shape whitelist, which would not be defeated by a novel third-person or impersonal phrasing.
