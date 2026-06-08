---
description: "Assess FinOps maturity (crawl/walk/run), name the highest-leverage gap, produce a cost-ownership RACI and the 2-3 moves to the next stage, and emit the structured handoff to the right specialist."
argument-hint: "[context, e.g. 'multi-cloud AWS+Azure, no tagging policy, monthly cost reviews, ~$500K/month cloud spend']"
---

You are running `/finops-cloud-cost:assess-finops-maturity`. Use the `finops-practice-lead`
discipline and the knowledge in `knowledge/finops-cloud-cost-decision-trees.md`.

## Steps

1. **Place the org on the maturity ladder.** Use the crawl/walk/run framework from the knowledge
   bank decision tree. Gather evidence: Is there a tagging policy? Is there showback? Are commitments
   purchased, and at what coverage? Are anomaly alerts in place? Does anyone outside Finance look at
   the bill? Is there a FinOps team or function?

2. **Name the highest-leverage gap.** The one deficiency whose resolution unlocks the most
   subsequent improvement. Common gaps by stage:
   - Crawl → Walk: no tagging policy / no showback / engineers don't see their spend.
   - Walk → Run: commitments unmanaged or over-committed / no anomaly detection / cost not in
     product planning.
   - Run → Optimizing: no unit economics / AI token cost not budgeted / no forecasting discipline.

3. **Produce the cost-ownership RACI.** Three seats: Finance (budget/chargeback/GL), Engineering
   (tagging/optimization/commitment management), Product (unit economics/feature cost accountability).
   Document what each role is Responsible, Accountable, Consulted, and Informed for.

4. **Recommend the 2-3 highest-leverage moves to the next stage.** Each move: what to do, who owns
   it, the success signal (not a feature count — a behavior change), and the estimated time to
   implement.

5. **Build-vs-buy FinOps tooling recommendation** (if tooling is a gap). Traverse the build-vs-buy
   tree in the knowledge bank. Native tools first (Cost Explorer, Azure Cost Management, GCP
   Billing); add a third-party aggregator only after native tooling is configured.

6. **Emit the Structured Output block** with handoffs:
   - `cost-allocation-engineer` if tagging/showback is the gap.
   - `cost-optimization-engineer` if commitments/rightsizing is the gap.
   - `ai-cost-governance-engineer` if AI token cost is unbudgeted.
