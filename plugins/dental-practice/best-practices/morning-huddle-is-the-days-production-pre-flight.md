# Morning Huddle Is the Day's Production Pre-Flight

**Status:** Pattern
**Domain:** Dental practice operations
**Applies to:** `dental-practice`

---

## Why this exists

The morning huddle is the single highest-leverage 10–15 minute investment in a dental practice's daily production. Practices that run a structured huddle — reviewing the day's schedule, identifying incomplete treatment, confirming outstanding balances, and flagging insurance issues — consistently report higher same-day production and fewer same-day scheduling gaps than those that don't. Without a huddle, the front desk, hygienists, and doctors are each working from a partial picture of the day; the huddle is the only moment all three functions align before patients arrive. A practice producing $600k/year that recaptures one same-day treatment presentation per week can add $40–60k annually with no additional marketing.

## How to apply

**Standard huddle agenda (≤15 minutes, every production morning):**

```
1. Yesterday's recap (2 min)
   - Production vs. goal: $[actual] / $[goal]
   - Collections vs. goal: $[actual] / $[goal]
   - New patients seen: [#]

2. Today's schedule by provider (5 min)
   - Review each provider's chair utilization % (open chair time = production gap)
   - Flag any patients with unscheduled treatment in their chart — "Mrs. Jones has
     an approved crown on D14 — who's presenting it today?"
   - Flag outstanding patient balances > $[threshold] — brief front-desk note
     before patient arrives, not at checkout

3. Insurance / pre-auth flags (3 min)
   - Any patient arriving whose eligibility has not been confirmed → confirm now
   - Any patient needing a pre-authorization that isn't in hand → note at check-in

4. Open chair time / same-day fill (3 min)
   - List any same-day openings: which slot, which provider
   - Assign 1 team member to call the 3 most likely same-day fills from the
     unscheduled-treatment list

5. Action items (2 min)
   - One-line owner and due time for each flagged item
```

**Metrics to track weekly:**
| Metric | Target | How to measure |
|---|---|---|
| Huddle held (yes/no) | 100% of production days | Manual log or scheduler flag |
| Same-day treatment filled | ≥1 presentation/day | PMS report |
| Open chair time at end of day | ≤10% of scheduled slots | PMS fill-rate report |
| Outstanding balance flag acted on | 100% of flagged patients | Front-desk note field |

**Do:**
- Start at the same time every day — set a recurring calendar block.
- Rotate the "flag caller" role so one person doesn't carry same-day fills alone.
- Keep it ≤15 minutes — a huddle that runs long stops happening.

**Don't:**
- Use the huddle as a staff meeting for policy updates — it is a same-day production tool.
- Skip it on "light" days — light days are exactly when the huddle's same-day fill function matters most.
- Rely on memory for outstanding balances or unscheduled treatment — pull from the PMS.

## Edge cases / when the rule does NOT apply

Solo practices with no front-desk staff or hygienist may condense the huddle to a personal 5-minute schedule review; the same-day treatment flag still applies. Practices with multiple providers across rooms should run the huddle provider-by-provider rather than skipping it to save time.

## See also
- [`../agents/dental-operations-analyst.md`](../agents/dental-operations-analyst.md) — builds the same-day production metrics and unscheduled-treatment list.
- [`../agents/dental-practice-lead.md`](../agents/dental-practice-lead.md) — scopes production gaps and routes to operations or clinical.

## Provenance

Codifies standard dental operations practice recognized by practice management consultants; benchmarks are [unverified — training knowledge] and should be compared against the practice's own trailing data.

---

_Last reviewed: 2026-06-05 by `claude`_
