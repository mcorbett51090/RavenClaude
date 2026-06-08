---
description: "Diagnose the leasing funnel (inquiry → tour → application → approval → signed), identify the conversion drop-off stage, and produce 3 prioritized fixes with expected impact on days-to-lease and occupancy."
argument-hint: "[context, e.g. '80-unit complex, 20 inquiries/wk, 8 tours, 3 applications, 1 signed, asking $1,800/mo, market avg $1,750']"
---

You are running `/property-management-residential:optimize-leasing-funnel`. Use the
`leasing-strategist` discipline and the `leasing-and-tenant-lifecycle` skill.

## Steps

1. **Map the funnel** — list the current conversion rates at each stage (inquiries → tours,
   tours → applications, applications → approvals, approvals → signed). If exact numbers aren't
   provided, ask for them or use the context provided.

2. **Identify the drop-off stage** — the stage with the lowest conversion rate is the primary
   lever. Name it explicitly: "The biggest leak is inquiry → tour at X%."

3. **Diagnose probable causes** — for the identified drop-off stage, enumerate 3–5 probable causes
   (pricing, listing quality, response time, showing experience, screening friction, market
   conditions).

4. **Produce 3 prioritized fixes** — rank by expected impact × ease of implementation:
   - Fix 1: the highest-impact, fastest-to-implement change
   - Fix 2: medium impact, medium effort
   - Fix 3: structural / longer-term change
   Each fix includes: what to change, how to measure it, and the expected impact on the relevant
   conversion rate.

5. **Flag fair-housing review** — if the diagnosis touches listing language or screening criteria,
   note that `pm-compliance-advisor` should review before changes go live.

6. **Run the economics** — use `scripts/pm_calc.py` to estimate the NOI impact of improving
   days-to-lease by X days (days-vacant × daily rent recovered).

7. **Emit the Structured Output Protocol block** with `handoff_recommendation` to
   `leasing-strategist` (ongoing execution) and `pm-ops-lead` (NOI impact).
