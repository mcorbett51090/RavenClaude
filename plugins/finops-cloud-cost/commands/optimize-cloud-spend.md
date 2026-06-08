---
description: "Run the rightsize → eliminate idle → commit discipline: pull utilization analysis, identify idle and orphan resources, calculate the steady-state commitment baseline, recommend the right RI/SP/CUD type and term with break-even months, and output the sequenced optimization plan."
argument-hint: "[context, e.g. 'AWS EC2 fleet, ~200 instances, no RIs, P90 CPU ~30%, $80K/month compute']"
---

You are running `/finops-cloud-cost:optimize-cloud-spend`. Use the `cost-optimization-engineer`
discipline, the `rightsizing-and-commitments` skill, and `scripts/finops_calc.py`.

## Steps

1. **Gather the utilization baseline.** Request or read 14–30 days of CPU and memory P90 utilization
   data by instance/VM. If the data is not available, explain how to obtain it (AWS Compute
   Optimizer, Azure Advisor, GCP Recommender, or native CloudWatch/Monitor metrics). Do not proceed
   to recommendations without utilization data — estimating without it produces unreliable results.

2. **Rightsizing pass.** For each instance type or cluster of similar instances: compare P90 CPU
   and memory to the target thresholds (CPU P90 40–70%, memory P90 50–80%). Flag instances below
   the lower threshold as oversized. Calculate the estimated savings from downsizing. Document the
   phased migration approach: resize one instance, monitor 48 hours, roll out to the fleet.

3. **Idle and orphan cleanup.** Identify: stopped instances with retained storage, unattached
   volumes/disks, unused Elastic IPs/Public IPs, old snapshots (>90 days), empty load balancers.
   Categorize each type as safe-to-delete / needs-retention-review / reclaim. Estimate monthly
   savings per category.

4. **Identify the steady-state baseline.** From the utilization data, find the P0 floor (the
   minimum consistent hourly usage). This is the commitment target. Use `finops_calc.py
   commitment_coverage()` to calculate what percentage of current usage this represents.

5. **Commitment recommendation.** Traverse the commitment-vs-on-demand tree in
   `knowledge/finops-cloud-cost-decision-trees.md`. Select the right type (Standard RI / Convertible
   RI / Compute SP / EC2 SP / Azure RVI / GCP CUD) based on the workload's stability and flexibility
   profile. Use `finops_calc.py break_even()` to calculate the break-even in months for the 1-year
   and 3-year terms. Mark all price inputs `[verify-at-use]`.

6. **Sequenced savings summary.** Produce a table: (1) rightsizing savings, (2) idle-cleanup
   savings, (3) commitment savings after rightsizing — in that order. The total is the sum, not each
   in isolation (they overlap if you commit before rightsizing).

7. **Emit the Structured Output block** with handoffs:
   - `cost-allocation-engineer` if tagging gaps are blocking accurate attribution.
   - `finops-practice-lead` if the commitment purchase requires governance sign-off.
   - `ai-cost-governance-engineer` if AI/inference spend is a material line item.
