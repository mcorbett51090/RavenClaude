---
id: headless-usage-sidecar-not-verdict
title: "Headless usage metering sits beside the seat"
category: "Inventory — measured mechanisms"
kind: ravenclaude-built
entry_class: inventory
order: 944
summary: "Where a headless call's token and cost envelope goes after the call returns."
last_verified: 2026-10-18
covers:
  - plugins/ravenclaude-core/scripts/headless-usage.py
covers_digest: "sha256:71875d5db313b4113c34755709b17d71c5fcddc4209436761cbe410a6bd4671b"
nuance: "The caller still prints only its own verdict on `stdout`, and record mode returns exit 0 after it writes `.ravenclaude/runs/headless-usage.jsonl`. A missing envelope skips the append rather than replacing that verdict."
nuance_evidence:
  measured: 2026-10-17
  control: "headless-usage.py --self-test writes a row that keeps a present 0, omits an absent field, and drops result text, while record mode itself exits 0"
  falsifier: "a seat whose stdout is no longer the verdict JSON alone, or a record failure that changes the caller exit code"
  probe: "plugins/ravenclaude-core/scripts/headless-usage.py"
nuance_source: "plugins/ravenclaude-core/scripts/headless-usage.py"
verify:
  tier: "effect"
  strength: "executed"
  class: "script-selftest"
  probe: "plugins/ravenclaude-core/scripts/headless-usage.py"
  teeth_exit: 1
sources:
  - label: "2026-10-14 prompt-caching analysis — headless envelopes were not metered"
    url: https://github.com/mcorbett51090/RavenClaude/blob/main/docs/plans/2026-10-14-prompt-caching/analysis.md
---

## What a reader would have assumed instead

That recording token use means the seat's own JSON answer grows a usage object, and that a bad envelope fails the seat.

## The discriminator

control: `headless-usage.py --self-test` writes a derived row and record mode exits 0 even when the envelope is not JSON.

Measured 2026-10-17: the recorder appends a sidecar and leaves the caller to print its own verdict. A missing envelope skips the write.
