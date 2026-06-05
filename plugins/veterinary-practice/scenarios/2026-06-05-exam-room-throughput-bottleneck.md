---
scenario_id: 2026-06-05-exam-room-throughput-bottleneck
contributed_at: 2026-06-05
plugin: veterinary-practice
product: practice-operations
product_version: "n/a"
scope: likely-general
tags: [capacity, throughput, appointment-template, support-ratio, doctor-bottleneck]
confidence: medium
reviewed: false
---

## Problem

A 3-DVM companion-animal general practice was "booked solid" three weeks out, the owner was working 55-hour weeks, yet revenue had been flat for four quarters. The owner's instinct was to extend hours (open Saturdays) or hire a fourth DVM. Both are expensive, slow moves — the request was to confirm the diagnosis before committing.

## Context

- Segment: general-practice, independent, 3 DVMs + 9 support staff (≈3:1 support-to-DVM ratio).
- Constraint: the owner-DVM was the bottleneck — handling reception escalations, callbacks, and refills between appointments. Two credentialed techs were under-utilized (doing kennel/reception work instead of tech-delegable medicine).
- The schedule was 30-minute slots for every appointment type, including nail trims and tech-appropriate recheck weights.

## Attempts

- Tried: pulled production per DVM and ACT (the §3 #2 read) before any capacity change. Production per DVM was mid-range; ACT was healthy. So this was **not** a revenue-per-visit problem — it was a **throughput/capacity** problem (booked solid + flat revenue is the §3 #3 signature). Outcome: ruled out a fee/ACT intervention.
- Tried: mapped the appointment template against actual visit duration. Found ~25% of doctor-slot minutes were spent on work a credentialed tech could legally do (vaccine boosters, suture removals, nail trims, weight rechecks). Outcome: identified the lever.
- Tried (the move that worked): restructured to (a) tech appointments for tech-delegable work off the doctor template, (b) shortened routine recheck slots from 30→20 min, (c) reassigned the two under-used techs to doctor support so each DVM ran two rooms. This raised the support-to-DVM ratio toward the AAHA-referenced 1:4–5 range and is consistent with the AAHA benchmark that **adding credentialed veterinary technicians per veterinarian can raise gross revenue by ~$161,000** [verify-at-use — AAHA Benchmarking, see source]. Outcome: freed ~6 doctor hours/week/DVM without adding a fourth DVM or opening Saturdays.

## Resolution

The bottleneck was the **doctor's time on tech-delegable work plus a one-size template**, not a shortage of doctors or hours. Fixing the appointment template and leveraging credentialed techs unlocked capacity the practice already owned, deferring a fourth-DVM hire (and its 18–24-month ramp) by an estimated 12+ months.

**Action for the next consultant hitting this pattern:** when a practice is booked-solid-but-flat (§3 #3), do **not** price-shop a fourth-DVM hire first. Run the production/ACT read to rule out a revenue-per-visit problem, then audit the appointment template for doctor minutes spent on tech-delegable work and for one-size slots. Capacity is most often hiding in the template and the support ratio, not in headcount. Cross-reference the in-house lever order in [`../knowledge/vet-add-associate-vs-extend-capacity-decision-tree.md`](../knowledge/vet-add-associate-vs-extend-capacity-decision-tree.md) and the [`../skills/unlock-schedule-capacity/SKILL.md`](../skills/unlock-schedule-capacity/SKILL.md) playbook.

**Sources for benchmarks cited:** AAHA Benchmarking (credentialed-tech revenue lift, staffing ratio) — https://www.aaha.org/american-animal-hospital-association-and-petabyte-technology-unveil-aaha-benchmarking/ ; AVMA staffing-ratio guidance — https://www.avma.org/news/increasing-practice-profitability-requires-benchmarking-defining-core-values (retrieved 2026-06-05). Figures are illustrative for this scenario; validate against the practice's actual data before a deliverable (§3 #8).
