---
description: "Run a structured fixed-ops optimization: absorption rate gap analysis, ELR waterfall, technician productivity diagnosis, and a ranked action plan with dollar recovery estimates."
argument-hint: "[context, e.g. 'absorption 74%, ELR $112 vs $145 posted, 10 techs, 480 ROs/month CP/warranty/internal split']"
---

You are running `/automotive-dealership:optimize-fixed-ops`. Use the `fixed-ops-analyst`
discipline and the `fixed-ops-service-and-parts` skill.

## Steps

1. **Collect baseline inputs.** Request (or read from context): RO count by pay type,
   total labor sales, hours sold vs hours available, posted labor rate, parts gross,
   total dealership overhead. If inputs are partial, state assumptions clearly.

2. **Calculate absorption rate and gap.** Apply the formula:
   `Fixed gross ÷ Total overhead`. Compare to the benchmark ladder in
   `knowledge/automotive-dealership-decision-trees.md` (Absorption improvement tree).
   Quantify the dollar gap: `(target % − actual %) × overhead`.

3. **Build the ELR waterfall.** Calculate actual ELR (`labor sales ÷ hours sold`),
   then decompose the gap from posted rate: warranty dilution, internal dilution,
   advisor discounting, come-back credits. Identify the largest dilution layer.

4. **Diagnose technician productivity.** Calculate flag rate, efficiency, and
   utilization. Identify which metric is the bottleneck and the root cause
   (scheduling, come-backs, parts availability, shop loading).

5. **Assess RO mix and internal pricing.** Quantify dollars flowing from service to
   variable ops via below-market internal RO rates.

6. **Output ranked action plan.** For each finding: dollar impact (monthly + annualized),
   specific fix, owner, and time horizon (quick-win ≤30 days vs structural ≥90 days).
   Fill `templates/fixed-ops-kpi-dashboard.md` with current-state metrics and targets.
   Emit the Structured Output JSON block with handoffs
   (`dealership-ops-lead` for whole-store context, `inventory-and-desking-analyst`
   for internal recon RO pricing).
