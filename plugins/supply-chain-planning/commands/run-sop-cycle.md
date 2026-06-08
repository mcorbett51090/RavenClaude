---
description: "Facilitate a monthly S&OP cycle: run the five-step gate sequence (product review, demand review, supply review, pre-S&OP reconciliation, executive S&OP), produce the gap analysis and scenarios, and close with a decision record."
argument-hint: "[cycle month and scope, e.g. 'July S&OP, North America finished-goods, 18-month horizon']"
---

You are running `/supply-chain-planning:run-sop-cycle`. Use the `sop-process-lead` discipline and
the `sop-process` skill.

## Steps

1. Confirm the cycle gate calendar: data cutoff → demand review → supply review → pre-S&OP →
   executive S&OP. Confirm all inputs exist (demand plan, supply plan, inventory position).
2. **Product review:** confirm active/NPI/EOL SKU list. Flag any NPI without an analogue demand
   assumption.
3. **Demand review:** present the statistical baseline with MAPE/bias KPIs. Review and document
   commercial overrides. Produce the consensus demand plan.
4. **Supply review:** run the demand plan through capacity/MRP. Identify gaps. Quantify each gap
   (units, periods, root cause, lead time to relieve, options).
5. **Pre-S&OP reconciliation:** for each gap, generate options (supply acceleration, demand
   prioritization, demand shaping, inventory draw-down). Score options by lead time, cost, and
   margin impact. Recommend a scenario.
6. **Executive S&OP:** produce the one-page performance summary + top-3 decisions. Close with a
   decision record: approved scenario, conditions, action owners, triggers.
7. Distribute the decision record within 24 hours. Log the S&OP KPIs (forecast accuracy,
   plan attainment, on-time completion).
8. Use `templates/sop-deck.md` for the exec pack. Emit the Structured Output block.
