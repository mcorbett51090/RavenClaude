---
id: routine-reserve-errs-toward-a-larger-reserve
title: "Routine reserve: the calibration errs toward a larger reserve"
category: "Inventory — measured mechanisms"
kind: ravenclaude-built
entry_class: inventory
order: 941
summary: "The %-of-cap per dollar rate counts only spend the meter actually saw, so missing spend inflates it and enlarges the reserve held for Routines — the safe direction. Over-counting is what starves them."
last_verified: 2026-09-24
covers:
  - plugins/ravenclaude-core/scripts/routine-reserve.py
  - plugins/ravenclaude-core/scripts/routine-reserve-hook.sh
  - plugins/ravenclaude-core/skills/routine-reserve/SKILL.md
  - plugins/ravenclaude-core/commands/routine-reserve.md
covers_digest: "sha256:906c3893ba369c90a09d98473a2514717062ae04afb7811ef1c52a96a3aab0d9"
nuance: "k = weekly % / metered spend. A session first seen mid-week counts only its growth after that\nsnapshot (unless created inside the window), so unseen spend RAISES k and the reserve —\nthe safe error. Over-counting (double-counted or pre-window cost) is what starves Routines."
nuance_evidence:
  measured: 2026-09-24
  control: "fixture 05-calibrated: three sessions created inside the window count from zero (0.6) while a long session created before it counts only its in-window growth (59.4 - 50.0 = 9.4); total 10.0, k_week = 12 / 10 = 1.2, reproduced exactly by self-test"
  falsifier: "a fixture where a session first seen mid-window contributes its full cumulative cost to window_spend, or where removing spend lowers the recommended reserve"
  probe: "plugins/ravenclaude-core/hooks/tests/test-gate291-routine-reserve.sh"
nuance_source: "plugins/ravenclaude-core/scripts/routine-reserve.py:1-40"
verify:
  tier: "effect"
  strength: "executed"
  class: "script-selftest"
  probe: "plugins/ravenclaude-core/hooks/tests/test-gate291-routine-reserve.sh"
  teeth_exit: 1
sources:
  - label: built and measured in the routine token reserve PR 1 session
    url: https://github.com/mcorbett51090/RavenClaude/blob/main/plugins/ravenclaude-core/knowledge/routine-token-reserve.md
---

## What a reader would have assumed instead

That missing spend makes the reserve too small — the intuitive worry when a meter cannot see every
session (local runs on other machines, the part of a long session before the meter first saw it).
The first draft of this feature's own plan stated exactly that, and an adversarial review caught it.

## The discriminator

The reserve is `k × projected Routine dollars`, and `k = weekly % ÷ metered spend`. Spend sits in the
denominator, so seeing less of it makes `k` — and the reserve — larger. The engine leans into that on
purpose: `window_spend` counts a session from zero only when it was created inside the window, and
otherwise only its growth after the first in-window snapshot. Fixture `05-calibrated` pins the
arithmetic (0.6 + 9.4 = 10.0 → k = 1.2), and Gate 291 fails if it drifts.

## Why it matters

The direction of an estimation error decides which failure you get. Here the cheap error — a reserve
that is too generous, so the warning fires early — is the one the design accepts. The expensive error
— Routines starved because interactive work was allowed to use their share — needs spend to be
*over*-counted, which is why sessions are deduped by id and pre-window cost is never charged to the week.

Probe: `plugins/ravenclaude-core/hooks/tests/test-gate291-routine-reserve.sh`
