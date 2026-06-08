---
description: "Rightsize compute and storage before purchasing commitments; evaluate and size Reserved Instances, Savings Plans, and Committed Use Discounts against the steady-state baseline; eliminate idle and orphan resources; and calculate break-even months and coverage percentage with finops_calc.py."
---

# Rightsizing & Commitments

**Purpose:** maximize cloud cost savings in the optimize phase by eliminating waste before locking
in any commitment, and then buying commitments only at the level the steady-state baseline justifies.

## The operating loop

1. **Pull utilization data.** 14–30 days of CPU and memory utilization at the 90th percentile (not
   peak, not average). Use AWS Compute Optimizer, Azure Advisor, GCP Recommender, or native CloudWatch/
   Monitor/Cloud Monitoring metrics. 14 days is the minimum; 30 days captures more weekly variation.
2. **Rightsize compute first.** Compare P90 utilization against the instance size. Target: CPU P90
   at 40–70%, memory P90 at 50–80% (adjust for your workload's latency/burst tolerance). If P90 CPU
   is ≤25%, the instance is clearly oversized. If memory P90 is ≥90%, it may be undersized. Never
   rightsize memory below P90 usage — OOMs are expensive.
3. **Eliminate idle and orphan resources.** Stopped instances with retained storage, unattached
   volumes/disks, unused Elastic IPs/Public IPs, old snapshots/AMIs, empty load balancers, unused
   reserved capacity. Categorize as: safe-to-delete (no data, no attachment), needs-retention-review
   (data present), or reclaim (re-attach or reassign).
4. **Identify the steady-state baseline.** The minimum hourly resource consumption in your least-
   busy week (not the average — the floor). This is the correct commitment target. Use
   `finops_calc.py commitment_coverage()` to calculate the coverage percentage.
5. **Choose the commitment type.**
   - AWS: Standard RI (highest savings ~40-60%, no flexibility), Convertible RI (~30-45%, can
     exchange instance family/OS/tenancy), Compute Savings Plan (~40-66%, most flexible, covers any
     EC2/Fargate/Lambda), EC2 Instance Savings Plan (~40-60%, specific family). [verify-at-use]
   - Azure: Reserved VM Instances (1-year or 3-year, ~40-60% savings). [verify-at-use]
   - GCP: Resource-based CUDs (specific machine type, deeper discount), Spend-based CUDs (any
     machine type in a region, shallower discount). [verify-at-use]
   - Traverse the commitment-vs-on-demand tree in the knowledge bank before recommending.
6. **Calculate break-even months.** Use `finops_calc.py break_even()` with on-demand hourly rate,
   RI/SP hourly rate, and upfront cost. A 1-year RI typically breaks even in 6–9 months; a 3-year
   in 12–18 months depending on term and payment option. [verify-at-use: rates change]
7. **Commit to the floor, on-demand the peaks.** Never over-commit. The commitment covers the P0
   baseline; everything above that runs on-demand or spot. Use `finops_calc.py blended_vs_effective()`
   to show the blended rate across committed + on-demand hours.
8. **Design storage tiering.** Access frequency → tiering threshold → lifecycle rule. For S3:
   objects not accessed in 30 days → S3-IA or Intelligent-Tiering; 90 days → Glacier Instant
   Retrieval; 180 days → Glacier Flexible or Deep Archive. [verify-at-use: pricing changes]

## Anti-patterns

- Purchasing any commitment before a rightsizing pass — this locks in waste.
- Using peak utilization as the rightsizing target (over-provisions).
- Using the average as the rightsizing target (under-provisions during peaks).
- Committing beyond the steady-state floor.
- "Orphan cleanup" without a data-retention policy check.
- A 3-year RI on a workload without a stability assessment.

## Output

A rightsizing analysis (utilization percentiles, target size, estimated savings), a commitment
recommendation (type, term, coverage %, break-even months via `finops_calc.py`), and an idle-
resource inventory with a safe-to-delete / retention-review / reclaim categorization.
