---
description: "Triage a residential work order by safety and habitability first (emergency vs. urgent vs. routine vs. deferred), then route it — flagging warranty-of-habitability as a legal question to counsel."
argument-hint: "[the work-order description + unit/tenant context + season/conditions]"
---

You are running `/property-management-residential:triage-work-order`. Use `maintenance-coordinator` + the `work-order-triage` skill.

## Steps
1. Classify by risk to person and habitability FIRST: emergency (safety / no heat / no water / gas / no lock) → dispatch now; urgent (will worsen) → 24-72h; routine → schedule; deferred → log WITH a reason and revisit date.
2. When in doubt between emergency and routine, treat as emergency and escalate — under-reacting is the unrecoverable error.
3. FLAG any warranty-of-habitability / repair-and-deduct / withholding legality question to counsel — do not adjudicate the law.
4. Route the build: the actual repair / licensed trade work / bid → skilled-trades-contracting; the turn-cost capex-vs-opex → owner-and-portfolio-reporting-analyst / finance; a move-out turn → leasing-and-tenant-ops.
5. Emit the triage classification + dispatch plan + the Structured Output block (with `Fair-housing / habitability flags:` and `Handoff:`).
