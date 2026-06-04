---
description: "Build a staffing operations scorecard where every KPI carries definition, window, baseline, owner, drill-down, and a triggered action — segment-resolved, with paired metrics and soft benchmarks marked."
argument-hint: "[division/segment and the decision it serves, e.g. 'allied division — are we filling fast enough?']"
---

# Build a staffing scorecard

You are running `/staffing-operations:build-staffing-scorecard`. Build the scorecard for `$ARGUMENTS` the way the `staffing-operations-analyst` owns it — every number defined, baselined, and actionable. A scorecard nobody acts on is decoration.

## Steps
1. **Pin the decision** the scorecard serves (one question) — everything flows from it ([`../skills/staffing-scorecard-build/SKILL.md`](../skills/staffing-scorecard-build/SKILL.md) Step 1).
2. **Choose 5–9 KPIs by family** from [`../knowledge/staffing-kpi-glossary.md`](../knowledge/staffing-kpi-glossary.md) — demand/funnel, speed, financial, quality, productivity.
3. **Fill the seven fields per KPI** — definition (name the denominator), formula, window, baseline, owner, drill-down, triggered action. No field, no ship (§3 #1).
4. **Pair the metrics** — fill rate ▸ time-to-fill; margin ▸ bill/pay/burden; rev/recruiter ▸ reqs/recruiter (§3 #2–#4).
5. **Segment the view** — no cross-segment blend as a headline.
6. **Set bands + actions**, and **mark soft benchmarks** `[ESTIMATE]`/`[unverified]` (§3 #9).

## Output
Fill [`../templates/kpi-scorecard.md`](../templates/kpi-scorecard.md). For layout, dispatch the dashboard-design skill; for instrumentation, route to `ravenclaude-core/data-engineer`.

## Guardrails
- A fill rate without time-to-fill, or a margin without bill/pay/burden, gets sent back.
- No candidate/client PII — roles and segments only (§3 #10).
- The client's own data is the baseline; external benchmarks are context, not verdict.
