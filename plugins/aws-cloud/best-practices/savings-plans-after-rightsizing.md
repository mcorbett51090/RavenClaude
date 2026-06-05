# Buy Savings Plans only after rightsizing

**Status:** Pattern
**Domain:** AWS FinOps / cost
**Applies to:** `aws-cloud`

---

## Why this exists

Savings Plans and Reserved Instances lock in a commitment for 1–3 years. Committing before rightsizing locks in waste: you pay the discounted rate on oversized resources. The correct order is: (1) establish a baseline of actual usage, (2) rightsize to the correct instance family/size, (3) then commit with a Savings Plan on the stable baseline. Skipping step 2 is the most common way organizations discover they saved 40% on something they never needed at that size.

## How to apply

**Rightsize first checklist:**

| Signal | Tool | Action |
|---|---|---|
| CPU ≤ 10% sustained | AWS Compute Optimizer | Downsize or switch instance family |
| Memory ≤ 20% sustained | CloudWatch + Compute Optimizer | Downsize |
| EC2 never peaks above `t3.small` equivalent | Compute Optimizer | Move to Graviton/t-series |
| Lambda memory vastly over-allocated | Lambda Power Tuning (Step Functions) | Reduce memory; reduce cost |
| RDS Multi-AZ with < 5% CPU and tiny DB | Compute Optimizer | Downsize; evaluate Aurora Serverless |

**Then commit:**

```
# Recommended Savings Plan purchase order:
# 1. Compute Savings Plan (most flexible — covers EC2 any family/region, Lambda, Fargate)
# 2. EC2 Instance Savings Plan (deeper discount, family-locked)
# 3. RDS Reserved Instances (for stable DB fleets)

# Use the Savings Plans purchase recommendation in the AWS Cost Explorer console:
# Cost Explorer → Savings Plans → Recommendations
# Set: "Look-back period: 30 days", "Coverage target: 70–80%" (not 100% — leave burst on On-Demand)
```

Aim for 70–80% commitment coverage, not 100%. On-Demand covers burst; over-committing 100% of peak leaves you paying for Savings Plan hours you can't use.

**Do:**
- Run Compute Optimizer and act on its recommendations before opening a Savings Plan console.
- Use Compute Savings Plans over EC2 Instance Savings Plans unless you have a very homogeneous, stable EC2 fleet — the flexibility is worth the slight discount reduction.
- Set a budget alert on Savings Plan utilization — low utilization means you over-committed.
- Review commitment coverage quarterly; adjust as the workload grows.

**Don't:**
- Buy Savings Plans on day one of a new workload before you have 30 days of usage data.
- Commit 100% of On-Demand spend — leave 20–30% for burst.
- Treat Savings Plans as a substitute for rightsizing: savings on waste is still waste.
- Use RIs for Fargate or Lambda (Savings Plans are the correct vehicle).

## Edge cases / when the rule does NOT apply

- **Event-driven / bursty-only Lambda workloads**: Lambda Compute Savings Plans still apply if there's a sustained baseline; purely spiky traffic has no committal baseline to lock.
- **Short-lived projects** (< 6 months): On-Demand is cheaper than a 1-year Savings Plan for temporary workloads.

## See also

- [`../agents/aws-ops-finops-engineer.md`](../agents/aws-ops-finops-engineer.md) — owns rightsizing, Savings Plans, and cost optimization.
- [`./tag-and-watch-cost-from-day-one.md`](./tag-and-watch-cost-from-day-one.md) — cost allocation tags are the prerequisite for knowing what to rightsize.
- [`./budget-alarms-before-the-bill.md`](./budget-alarms-before-the-bill.md) — budget alerts detect commitment drift early.

## Provenance

Codifies the `aws-ops-finops-engineer` remit from `CLAUDE.md` §1: "rightsizing and Savings Plans/RIs" with the explicit ordering constraint. Derived from AWS FinOps best practices (AWS Cost Optimization Pillar, Well-Architected Framework) and the standard cloud FinOps community guidance on commitment sequencing.

---

_Last reviewed: 2026-06-05 by `claude`_
