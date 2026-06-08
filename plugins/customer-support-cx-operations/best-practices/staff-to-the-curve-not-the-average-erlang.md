# Staff to the curve, not the average (Erlang C)

**Status:** Absolute rule
**Domain:** Contact center staffing and queue design
**Applies to:** `customer-support-cx-operations`

---

## Why this exists

Staffing a contact center from average daily contact volume and average handle time produces a
systematically under-staffed queue. Contacts do not arrive at an average rate — they arrive in
peaks and valleys by time of day, day of week, and business cycle. A staffing model built on
a daily average smooths away the peaks, where SLA is actually missed.

Erlang C is the industry-standard queueing model for contact centers. It models the probability
that a contact will wait given the number of agents and the arrival rate, and returns the minimum
agents needed to hit a target service level at a given interval. It is not advanced mathematics —
it is the correct arithmetic for a queue. Using averages instead is not a simplification; it is
the wrong calculation.

A staffing plan built on daily averages and presented with interval-level SLA targets is
arithmetically inconsistent. The SLA is a promise about intervals (e.g., "80% of contacts answered
within 20 seconds") — it must be backed by an interval-level staffing model.

## How to apply

- Collect interval-level contact data (15- or 30-minute buckets for voice and chat; hourly for
  email) rather than daily totals.
- Run Erlang C at each interval to find the minimum agents-needed at the target service level.
  Use `scripts/cx_calc.py erlang-c`.
- After finding the minimum agents, verify occupancy: if occupancy at the model's agent count
  exceeds 85% (voice) or 90% (async chat), add agents until occupancy falls within range.
- Apply shrinkage to convert raw agent count to FTE: FTE = raw agents / (1 - shrinkage rate).
  Budget both trained shrinkage (breaks, meetings) and unplanned shrinkage (sick leave, attrition).

**Do:**

- Use 15- or 30-minute interval data as Erlang C inputs, not daily averages.
- Back every customer-facing SLA commitment with an Erlang C model at the stated volume and AHT.
- Re-run the model when volume changes by >20% or AHT changes by >30 seconds.

**Don't:**

- Present a staffing plan calculated from daily-average volume and AHT.
- Publish an SLA commitment before running an interval-level Erlang C model.
- Target occupancy above 85% (voice) as a "cost efficiency" — above that threshold, queue length
  grows nonlinearly and quality degrades.

## Edge cases / when the rule does NOT apply

For a very low-volume async email channel (<20 contacts/day) where contacts are worked in a
batch-processing model rather than a real-time queue, Erlang C is not the right model (there is
no queue dynamic in a pure-batch async workflow). Use a throughput/capacity model instead:
(daily volume × AHT) / (daily agent hours × utilization rate) = agents needed. The no-averages
discipline still applies — use actual daily distribution, not a monthly average.

## See also

- [`../skills/workforce-and-queue-design/SKILL.md`](../skills/workforce-and-queue-design/SKILL.md)
- [`../scripts/cx_calc.py`](../scripts/cx_calc.py) for Erlang C and shrinkage-FTE calculations.
- [`../templates/sla-and-escalation-matrix.md`](../templates/sla-and-escalation-matrix.md) —
  staffing basis column must reference the Erlang C model.

## Provenance

Erlang C is derived from A.K. Erlang's 1917 traffic theory, extended for multi-server queues.
It is the foundation of all major workforce management (WFM) systems (NICE, Verint, Genesys,
Assembled). The discipline of interval-level staffing is standard ICMI and SWPP contact-center
management practice.

---

_Last reviewed: 2026-06-08 by `claude`._
