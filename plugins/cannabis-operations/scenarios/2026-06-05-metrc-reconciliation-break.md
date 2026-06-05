---
scenario_id: 2026-06-05-metrc-reconciliation-break
contributed_at: 2026-06-05
plugin: cannabis-operations
product: seed-to-sale
product_version: "n/a"
scope: likely-general
tags: [metrc, track-and-trace, reconciliation, discrepancy, audit, package-tag]
confidence: medium
reviewed: false
---

## Problem

A vertically-integrated operator's monthly physical count of flower no longer matched the state track-and-trace system (Metrc). The system showed ~4 lbs more on-hand than the vault held. The operator treated it as a counting error and re-counted three times. It was not a counting error — it was an accumulated **reconciliation break**: small per-transaction drifts (un-recorded sample pulls, mis-weighed package adjustments, a few sales rung in the POS but never decremented in Metrc via the integration) compounded over a quarter. Left unresolved this is a **compliance event** (a physical-vs-system discrepancy the regulator can read as diversion), not a bookkeeping rounding issue (CLAUDE.md §3 #1) — and **seed-to-sale-compliance-specialist** must frame the corrective steps as decision-support for the licensed operator, never as a legal opinion (CLAUDE.md §2).

## Context

- Segment: vertically-integrated (cultivation + retail), single-state, Metrc state.
- Constraint: the break is a **reconciliation discipline** gap, not (on the evidence) actual diversion — but the inability to explain the delta is exactly what turns a routine inspection into an investigation. The plugin stores no records and is not a track-and-trace platform (CLAUDE.md §2); it standardizes the operator's reconciliation cadence as decision-support.
- The team had been reconciling **monthly** and relying on the POS↔Metrc integration to "just sync," with no daily exception report.

## Attempts

- Tried: re-counting the physical vault repeatedly. Outcome: confirmed the physical number was stable; the delta was real, not a miscount.
- Tried: confirmed the two load-bearing facts against authoritative sources rather than memory — (a) Metrc is the mandated track-and-trace system in ~30 regulated markets and the system of record the regulator audits against [verify-at-use — state list and Metrc's footprint move; New York and Illinois both transitioned toward Metrc in 2025]; (b) the corrective steps and discrepancy-reporting window are **state-specific** — never generalize one state's reconciliation rule to another (CLAUDE.md §3 #3). Outcome: grounded the framing before recommending.
- Tried (the move that worked): rebuilt the trail package-tag by package-tag for the affected items over the quarter, isolating the drift to (1) sample pulls logged in the POS but not as Metrc package adjustments and (2) a stretch where the integration silently failed and sales didn't decrement. Then instituted a **daily** physical-spot-vs-system exception report on high-velocity SKUs plus a written reconciliation SOP with a named owner. Outcome: the delta was explained, documented, and corrected in-system per the state's adjustment procedure; the daily cadence stopped the next drift before it compounded.

## Resolution

The break was **cadence and integration-trust**, not theft — monthly reconciliation let small drifts compound past the point where they could be explained. Daily exception reporting on high-velocity SKUs, package-tag-level trail rebuilding for the affected items, and a written SOP with a named owner converted an unexplainable delta into a documented, in-system correction.

**Action for the next consultant hitting this pattern:** reconcile **daily** on high-velocity SKUs, not monthly (a small drift you can explain today is an investigation you can't explain next quarter). Never assume the POS↔track-and-trace integration is decrementing — verify it with an exception report. Confirm the **state's** discrepancy-reporting window and adjustment procedure before recording any correction (`[verify-at-use]` — these vary by state and by track-and-trace system). Frame every output as decision-support for the licensed operator; route anything that looks like actual diversion, PII, or regulated records to `ravenclaude-core` `security-reviewer` (CLAUDE.md §2).

**Sources (retrieved 2026-06-05):**
- Metrc — Metrc/BioTrack strategic partnership (Metrc footprint, ~30 markets): https://www.metrc.com/news/metrc-and-biotrack-announce-strategic-partnership/
- CRB Monitor — Metrc and BioTrack Form Partnership (state coverage context): https://news.crbmonitor.com/2025/09/metrc-and-biotrack-form-partnership/
- Distru — New York's Metrc integration / compliance framework: https://www.distru.com/cannabis-blog/new-yorks-cannabis-compliance-framework-guide-to-metrc-integration

Track-and-trace system, discrepancy windows, and adjustment procedures are **state-specific and volatile** — `[verify-at-use]` against the operator's specific state regulator and track-and-trace system before any deliverable (CLAUDE.md §3 #3, #8).
