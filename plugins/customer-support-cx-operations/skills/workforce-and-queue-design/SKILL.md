---
name: workforce-and-queue-design
description: "Apply Erlang C to size a contact center queue for a target service level, model occupancy and shrinkage, design schedule adherence programs, forecast demand by interval, and produce shrinkage-adjusted FTE counts for headcount planning."
---

# Workforce and Queue Design

**Purpose:** produce staffing models grounded in queue mathematics (Erlang C), not averages — so
service level targets are backed by a model, occupancy is bounded to a quality-safe range, and
shrinkage is budgeted before it becomes a surprise.

## The operating loop

1. **Gather interval-level inputs.**
   Never use daily averages for Erlang C. Required inputs per channel:
   - Contact volume by interval (15- or 30-minute buckets for voice/chat; hourly for email).
   - Average Handle Time (AHT) in seconds: average talk time + average after-call work.
   - Target service level: X% of contacts answered within Y seconds (e.g., 80% within 20s = "80/20").
   - Number of available intervals per day (operating hours).

2. **Run Erlang C.**
   Use `scripts/cx_calc.py erlang-c` for the calculation.
   
   Key Erlang C outputs:
   - **Agents needed (N):** minimum agents at the interval to hit target service level.
   - **Occupancy at N:** occupancy = (AHT × call rate) / N. If occupancy > 85%, add agents until
     occupancy falls within range — service level hits target, but occupancy is the quality governor.
   - **Service level at N:** verify the model's output matches the target (sanity check).
   
   Erlang C assumptions: Poisson arrivals, exponential service times, no caller abandonment.
   For high-abandonment queues, Erlang A (with abandonment rate) is more accurate; use it when
   abandonment > 8%.

3. **Model shrinkage.**
   Raw agent count from Erlang C → shrinkage-adjusted FTE.
   
   FTE = raw agents / (1 - total shrinkage rate).
   
   Shrinkage budget (components):
   - **Trained shrinkage** (predictable, schedulable): paid breaks, lunch, scheduled meetings,
     training sessions, QA coaching time. Typical range: 12–18%.
   - **Unplanned shrinkage** (variable): sick leave, no-shows, attrition lag. Typical range: 5–10%.
   - **Total shrinkage:** 17–28% is a standard operating range. Above 30%: investigate retention
     and scheduling practices.
   
   Use `scripts/cx_calc.py shrinkage-fte` for the calculation.

4. **Check occupancy.**
   Use `scripts/cx_calc.py occupancy` to verify: occupancy = (AHT × contacts/interval) / (agents × interval_duration).
   Target ranges by channel:
   - Voice: 80–85%. Above 85%: queue dynamics degrade non-linearly; agent burnout risk rises.
   - Async chat (multi-session): 85–90%. Agents handle concurrent sessions; occupancy ceiling is higher.
   - Email: 85–90%. Non-real-time; intervals are longer.
   
   If occupancy is above target: model the deflection-first option (`deflection-and-knowledge-strategy`)
   before adding headcount.

5. **Design schedule adherence program.**
   Adherence = (time in queue as scheduled) / (scheduled time in queue). Target: ≥90%.
   
   Adherence levers: shift schedule alignment to interval-level demand curve (not flat 9-5 schedules),
   staggered start times, break scheduling to fill low-volume valleys, real-time adherence alerting.

6. **Demand forecasting.**
   For a new channel or peak-season plan:
   - Decompose historical contact volume into trend + seasonality + event effects.
   - Project forward: apply expected growth rate, seasonality index by week/month, and planned event
     multipliers (product launches, billing cycles, marketing campaigns).
   - Run Erlang C at each projected volume level → agents-needed curve by week.
   - Model flex options: overtime capacity, contractor burst, deflection buffer (KB improvement
     projected to deflect N% of contacts), and hiring lead time against the demand curve.

7. **SLA and abandonment monitoring.**
   SLA attainment: % of contacts answered within threshold / total contacts offered.
   Abandonment rate: contacts abandoned / total contacts offered. These are correlated — model both.
   Benchmark: voice abandonment ≤5%; chat ≤2%; email (age-based SLA) ≤1% past SLA.

## Anti-patterns

- Staffing from daily-average volume rather than interval-level Erlang C inputs.
- Publishing an SLA commitment before running the Erlang C model to know the agent count required.
- Targeting occupancy above 85% as an "efficiency" measure — it is a quality risk.
- A shrinkage budget that includes breaks and lunch but not meetings, coaching, and sick leave.
- A headcount plan that doesn't model deflection-first options.

## Output

An Erlang C staffing model (agents by interval, occupancy at staffing level), a shrinkage-adjusted
FTE count with budget breakdown, an SLA and abandonment model, and a demand forecast with
scenario sensitivity. Use [`../../scripts/cx_calc.py`](../../scripts/cx_calc.py) for all
calculations and [`../../templates/sla-and-escalation-matrix.md`](../../templates/sla-and-escalation-matrix.md)
for the SLA commitment artifact.
