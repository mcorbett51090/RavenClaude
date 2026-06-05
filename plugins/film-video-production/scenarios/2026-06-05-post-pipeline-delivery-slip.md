---
scenario_id: 2026-06-05-post-pipeline-delivery-slip
contributed_at: 2026-06-05
plugin: film-video-production
product: post-production
product_version: "n/a"
scope: likely-general
tags: [post-pipeline, picture-lock, vfx, critical-path, delivery, conform]
confidence: medium
reviewed: false
---

## Problem

An indie feature's delivery date was three weeks out and the post supervisor was being told "color is behind, throw more colorist hours at it." But color kept stalling — the colorist would grade a reel, then the edit would change underneath them and the grade was wasted. Everyone was treating it as a color-capacity problem. It wasn't.

## Context

- Segment: indie feature, modest post budget, a hard distributor delivery date.
- Constraint: **picture was not actually locked** (section 3 #5). Editorial was still making creative changes while finishing had started downstream — so color, conform, and the final mix were all keying off a moving target. The "color is slow" symptom was rework, not throughput.
- A handful of VFX shots had been deferred and were also not final, so the conform couldn't close even where the grade was done.

## Attempts

- Tried: mapped the post dependency chain instead of staffing the loudest complaint. Editorial → picture lock → (color | sound mix | conform) → VFX finals fold-in → delivery. The dependency that gated everything was **picture lock** (section 3 #5, #3) — starting color on an unlocked cut guarantees re-grades. Outcome: identified that adding colorist hours against a moving edit would *increase* spend, not recover the date.
- Tried: separated what genuinely could run before lock from what couldn't. Sound design and library work, music to a temp cut, and VFX *non-editorial* build could proceed; online conform, color, and the final mix could not. Outcome: re-parallelized only the lock-independent streams, and stopped the wasteful early color.
- Tried (the move that worked): forced the picture-lock decision — got the director and editor to a hard lock date, froze the cut, and *then* released color + conform + final mix against the locked picture, with the deferred VFX shots given a lock-gated fold-in slot on the critical path. The delivery date was set by the critical path from lock, not by colorist headcount.

## Resolution

The slip was a **picture-lock** problem (section 3 #5) presenting as a color-capacity problem. Post is a dependency chain (section 3 #3) — throwing capacity at a downstream stage while the upstream gate (lock) is still open just buys rework. Protecting the lock and sequencing from it recovered the schedule.

**Action for the next post supervisor hitting this pattern:** when a finishing stage looks "slow," check whether **picture is actually locked** before you add capacity to it. Re-grades, re-conforms, and re-mixes are the signature of finishing started on an unlocked cut. Sequence post as a dependency chain from the lock; run only the genuinely lock-independent streams early (sound design, temp-score, VFX build); and set the delivery date off the critical path from lock, not off the headcount of the loudest stage. Cross-reference the picture-lock and post-dependency best-practice rules in [`../best-practices/`](../best-practices/), the post-pipeline tree in [`../knowledge/production-decision-trees.md`](../knowledge/production-decision-trees.md), and the [`../skills/sequence-the-post-pipeline/SKILL.md`](../skills/sequence-the-post-pipeline/SKILL.md) playbook.

**Sourcing note:** the post-dependency sequencing in this scenario is the team's domain craft (the "What Can Start Before Picture Lock" tree in [`../knowledge/production-decision-trees.md`](../knowledge/production-decision-trees.md), last verified 2026-06-05 against standard dependency-chain practice). No external rate figure is asserted here; any number entering a deliverable carries a source URL + retrieval date or an `[unverified — training knowledge]` mark (section 3 #8).
