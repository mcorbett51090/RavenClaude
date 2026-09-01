---
id: analog-closeness-quality-bar-is-independent-of-score
title: "A high closeness score can still fail the quality bar"
category: "Inventory — measured mechanisms"
kind: ravenclaude-built
entry_class: inventory
order: 914
summary: "analog-closeness-scorecard's weighted score and its observed-vs-inferred quality bar are scored independently — a row can rank high on arithmetic and still be dropped."
last_verified: 2026-08-30
covers:
  - plugins/ravenclaude-core/skills/analog-closeness-scorecard/SKILL.md
  - plugins/ravenclaude-core/skills/analog-closeness-scorecard/score_closeness.py
covers_digest: "sha256:ab0fb7dd893151b6c78de30fd20be77d1dcd09e9825eb01d9b6a7408992f2bf9"
nuance: "A row scoring M=H=G=0 (arithmetic weighted >=18 via O/E/I/T/V alone) with every dimension inferred, not observed, still fails the quality bar — the two checks are independent, not one gate."
nuance_evidence:
  measured: 2026-08-30
  control: "compute({M:0,H:0,G:0,O:2,E:2,I:2,T:2,V:2}, all-inf) returns weighted>=18 AND quality_bar_pass=False with 2 named reasons in the self-test"
  falsifier: "the same high-arithmetic row passing quality_bar_pass"
  probe: "plugins/ravenclaude-core/skills/analog-closeness-scorecard/score_closeness.py"
verify:
  tier: "effect"
  strength: "executed"
  class: "script-selftest"
  probe: "plugins/ravenclaude-core/skills/analog-closeness-scorecard/score_closeness.py"
  teeth_exit: 1
sources:
  - label: Q2 of the analog-repos-gap-fill leftovers, unparked on owner request
    url: https://github.com/mcorbett51090/RavenClaude/pull/1047
---

## What a reader would have assumed instead

A single weighted-score threshold decides closeness — a row that scores high enough on the
`3M+3H+3G+2O+2E+2I+2T+1V` arithmetic passes.

## The discriminator

control: `compute()` on `{M:0,H:0,G:0,O:2,E:2,I:2,T:2,V:2}` with every dimension `kind:"inf"`
returns a weighted score >= 18 (well into the closeness-4 band) AND `quality_bar_pass: False`,
with both failure reasons named (`none of M/H/G scored >= 1` and the observed-count shortfall).
Measured 2026-08-30: the survey's own quality bar — at least one of M/H/G >= 1, and at least 3 of
8 dimensions actually observed — is checked independently of the arithmetic total, exactly
mirroring the 2026-08-14 survey's own `dropped.md` discipline.

## Why it matters

Falsifier: the same high-arithmetic, all-inferred row passing `quality_bar_pass`.

Probe: `plugins/ravenclaude-core/skills/analog-closeness-scorecard/score_closeness.py`
