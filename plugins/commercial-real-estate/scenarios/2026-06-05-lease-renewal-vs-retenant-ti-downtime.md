---
scenario_id: 2026-06-05-lease-renewal-vs-retenant-ti-downtime
contributed_at: 2026-06-05
plugin: commercial-real-estate
product: leasing
product_version: "n/a"
scope: likely-general
tags: [lease, renewal, net-effective-rent, ti, downtime]
confidence: medium
reviewed: false
---

## Problem

A creditworthy tenant's lease was expiring, and a new prospect was offering a higher **face** rent than the renewal the incumbent would accept. The owner was inclined to take the higher headline rent and re-tenant. But face rent is not what the landlord earns — and a re-tenant carries downtime, leasing commissions, and a fresh tenant-improvement (TI) bill that a renewal mostly avoids. The decision had to be made on net effective rent, not face (CLAUDE.md §3 #5).

## Context

- Segment: commercial space with a single expiring lease (the trade-off is asset-class-agnostic; the TI and downtime magnitudes differ by sector — office TI is heavy, industrial lighter).
- Constraint: comparing a renewal to a re-tenant means converting both to **net effective rent** — face rent minus free rent, minus amortized TI, minus leasing commissions, over the lease term — and charging the re-tenant case with the **downtime** (months of vacancy + carrying costs while re-leasing) and the new TI/LC the renewal avoids. A higher face rent can easily be a lower NER once those are netted.
- The owner was anchored on the face-rent delta and hadn't priced the downtime, the new TI, or the LCs — the costs that live entirely on the re-tenant side.

## Attempts

- Tried: **decomposed both offers to net effective rent** — netting free rent, amortized TI, and LCs over each term — instead of comparing face rents. Outcome: the renewal's lower face rent produced a **higher NER** once the re-tenant's TI and commissions were netted, because a renewal typically needs little to no TI and a reduced commission.
- Tried: charged the re-tenant case with **downtime** — the expected vacant months between the incumbent leaving and a new tenant paying, plus the carrying cost (taxes, insurance, opex the landlord eats while dark). Outcome: the downtime alone closed most of the remaining face-rent gap; the re-tenant only won if downtime was very short and the prospect was as creditworthy as the incumbent.
- Tried: weighed **tenant credit** as part of the underwriting, not a side note (best-practices/tenant-credit-analysis-is-part-of-the-underwriting). A higher face rent from a weaker covenant is not strictly better than a lower rent from a proven, creditworthy incumbent — the renewal also de-risked the income. Outcome: the credit comparison tipped a close call toward retention.

## Resolution

The renewal was selected because on a **net-effective, downtime-and-TI-charged** basis it beat the higher-face-rent re-tenant — retaining a creditworthy tenant with minimal TI and no downtime, rather than chasing a headline rent that netted out lower after concessions, commissions, and vacancy. The output was a dated NER comparison with downtime and TI/LC modeled bottom-up, not a face-rent comparison.

**Action for the next leasing/asset manager hitting this pattern:** **never compare a renewal to a re-tenant on face rent — convert both to net effective rent (net of free rent, amortized TI, LCs) and charge the re-tenant case with downtime + new TI/LC; weigh tenant credit as part of the underwriting.** A higher face rent frequently loses to a lower-TI, zero-downtime renewal. The "Lease Rollover — Renew, Backfill, or Reconfigure" tree in [`../knowledge/cre-decision-trees.md`](../knowledge/cre-decision-trees.md) and the new [`../knowledge/cre-lease-structure-nnn-vs-gross-decision-tree.md`](../knowledge/cre-lease-structure-nnn-vs-gross-decision-tree.md) tree cover the structure choice; the [`decompose-net-effective-rent`](../skills/decompose-net-effective-rent/SKILL.md) skill does the NER math.

**Sources (retrieved 2026-06-05 — `[verify-at-use]`):**
- Holland & Knight — triple net, gross, and modified gross commercial leases (who bears opex; structure affects the rent comparison): https://www.hklaw.com/en/insights/publications/2026/03/who-pays-for-what-understanding-key-differences-in-triple-net
- The Cauble Group — triple net vs gross lease (concession and structure differences that drive NER): https://www.tylercauble.com/blog/triple-net-vs-gross-lease

TI, leasing-commission, free-rent, and downtime norms are market-, sector-, and deal-specific — model each from the actual lease proposals and a current leasing-cost benchmark, not a rule of thumb (§3 #8).
