---
scenario_id: 2026-06-05-production-per-hour-schedule-read
contributed_at: 2026-06-05
plugin: dental-practice
product: practice-operations
product_version: "n/a"
scope: likely-general
tags: [production-per-hour, schedule-utilization, capacity, hygiene-production, doctor-time]
confidence: medium
reviewed: false
---

## Problem

A practice "felt busy" — the schedule looked full and the team felt slammed — yet monthly production was flat and the owner couldn't see why. The owner read production **per day** and concluded the practice was at capacity, so the proposed fix was to add days or a second operatory. But a per-day read hides whether the booked hours are actually producing; a full-but-low-yield schedule looks identical to a genuinely maxed one until you divide by hours.

## Context

- Segment: general-practice, independent, 1 doctor + 2 hygienists, PPO/FFS mix.
- Constraint: doctor time was being spent on procedures a hygienist or assistant could support, low-value short visits filled prime doctor columns, and hygiene was running well below its earning potential. The schedule was full of low-yield blocks.
- The owner was reasoning from "we're booked solid" (a volume signal) instead of production per hour (a yield signal), so the diagnosis pointed at adding supply when the real issue was the mix inside the existing hours.

## Attempts

- Tried: switched the read from per-day to **production per hour for the doctor and per hour for hygiene**, separately. Trade benchmarks put dentist production around ~$475–$575/hr (high performers $700+) and hygiene around ~$145–$175/hr (a healthy hygienist produces ~3–3.5× their hourly wage) [verify-at-use]. Outcome: doctor per-hour was well under benchmark despite a full book — proving the problem was yield, not capacity.
- Tried: read **hygiene as a share of total production** — the ADA baseline is ~25% with high performers at ~30–33% [verify-at-use] — and found hygiene under-running, signaling unbooked margin and missed perio/restorative hand-offs. Outcome: identified the hygiene department as the largest recoverable lever before any expansion spend.
- Tried (the move that worked): **re-mixed the existing schedule** — moved doctor-delegable work off prime columns, blocked high-value restorative time, and raised hygiene yield via perio acceptance and pre-booking — instead of adding days/operatories. Outcome: production per hour rose inside the same calendar; the expansion was deferred because the capacity was already there, mis-allocated.

## Resolution

Production per hour is the **capacity lens** (CLAUDE.md §3 #4), and the **hygiene department is a profit engine, not a loss leader** (§3 #5). The fix was to read yield per hour, find the under-producing hours, and re-mix the existing schedule — not to add supply to a schedule that was full but under-yielding. Adding days would have multiplied a low-yield pattern instead of fixing it.

**Action for the next consultant hitting this pattern:** when a practice "feels busy" but production is flat, **divide by hours before adding any.** Read doctor $/hr and hygiene $/hr separately against benchmark and check hygiene's share of total production; a full-but-low-yield schedule means re-mix, not expand. Run [`../skills/read-production-per-hour/SKILL.md`](../skills/read-production-per-hour/SKILL.md) and route the economics to [`dental-operations-analyst`](../agents/dental-operations-analyst.md). For the capacity-vs-expand call see [`../knowledge/dental-hygiene-capacity-decision-tree.md`](../knowledge/dental-hygiene-capacity-decision-tree.md).

**Sources (retrieved 2026-06-05):**
- Titan Web Agency — Dental Practice Financials: Benchmarks, Overhead, and Profit (production/hr): https://blog.titanwebagency.com/dental-practice-financials
- Dental Economics — The successful hygiene department: Understanding the numbers: https://www.dentaleconomics.com/science-tech/article/16391556/the-successful-hygiene-department-understanding-the-numbers
- Dentx — How Much Should a Hygienist Produce Per Day? (3–3.5× wage, hygiene share): https://dentx.ca/blog/dental-hygiene-production-benchmarks/

Per-hour and hygiene-share figures are trade-source rules-of-thumb, not hard rules — treat as `[verify-at-use]` and calibrate to the practice's procedure mix and segment (§3 #8).
