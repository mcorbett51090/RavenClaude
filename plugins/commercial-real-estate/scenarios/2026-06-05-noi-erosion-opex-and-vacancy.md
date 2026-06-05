---
scenario_id: 2026-06-05-noi-erosion-opex-and-vacancy
contributed_at: 2026-06-05
plugin: commercial-real-estate
product: asset-management
product_version: "n/a"
scope: likely-general
tags: [noi, opex, recovery-ratio, vacancy, variance]
confidence: medium
reviewed: false
---

## Problem

An owned asset was tracking below its acquisition-underwriting NOI, and the owner's first instinct was "rents are soft — re-tenant." But a same-rent-roll asset can miss NOI from three different drivers, and the fix for each is different. Treating an opex/recovery problem as a leasing problem would have spent capital on the wrong lever.

## Context

- Segment: owned commercial asset with a mix of expense-recovery and gross leases (the variance decomposition is asset-class-agnostic).
- Constraint: NOI is not a single line — it is gross potential rent − vacancy/credit loss + expense recoveries − operating expenses. A miss can come from **occupancy/NER** (a rent problem), **opex creep** (an expense problem), or a **falling recovery ratio** (a reimbursement problem — opex rose but wasn't passed through), and the three look identical on the NOI line until you decompose them (CLAUDE.md §3 #7, opex is an underwriting input, not a plug).
- The owner was about to greenlight a leasing/concession budget to "fix occupancy" before checking whether occupancy was actually the driver.

## Attempts

- Tried: **decomposed the NOI variance** into the three components before recommending any fix — actual vs underwritten for (a) effective rent at actual occupancy, (b) operating expenses line by line, (c) the recovery ratio (recoveries ÷ recoverable opex). Outcome: the largest piece of the miss was a **falling recovery ratio** — opex had risen (taxes/insurance/CAM) but the lease structure and reconciliation weren't capturing the pass-throughs, so the landlord was absorbing expense growth that should have flowed to tenants.
- Tried: checked the lease structures (recovery-ratio analysis precedes opex benchmarking — best-practices/recovery-ratio-analysis-precedes-opex-benchmarking.md). On NNN leases the operating-expense growth (taxes, insurance, maintenance/CAM) is contractually the tenant's; on gross leases the landlord absorbs it. The recovery gap was concentrated in the gross / modified-gross leases and in a CAM reconciliation that hadn't been issued. Outcome: the fix was a **reconciliation + lease-structure** action, not a leasing-up action.
- Tried: only after the recovery and opex pieces were isolated did the residual rent/occupancy variance get sized — and it was small enough that a re-tenant would have been an expensive answer to a minor part of the problem.

## Resolution

The NOI miss was correctly attributed to a recovery-ratio erosion (un-passed-through opex growth) rather than soft rents, so the fix was a CAM reconciliation and a lease-structure review — cheap, fast, and NOI-accretive — instead of a leasing-and-concession spend that would have addressed the smallest slice of the variance. The output was a dated three-way NOI bridge (rent / opex / recoveries), not a single-cause story.

**Action for the next asset manager hitting this pattern:** **decompose an NOI miss into rent vs opex vs recovery-ratio BEFORE picking a fix — the three look identical on the NOI line and have different, differently-priced remedies.** Run the recovery-ratio analysis first; on a rising-opex asset, a falling recovery ratio (not soft rent) is the common hidden driver. The [`../scripts/cre_calc.py`](../scripts/cre_calc.py) `noi-cap` mode shows the full GPR → vacancy → recoveries → opex → NOI build-up so each line can be compared to underwriting; the "This asset missed NOI" tree in [`../knowledge/cre-decision-trees.md`](../knowledge/cre-decision-trees.md) sequences the decomposition.

**Sources (retrieved 2026-06-05 — `[verify-at-use]`):**
- Holland & Knight — who pays for what: triple net, gross, and modified gross commercial leases (which party bears opex growth): https://www.hklaw.com/en/insights/publications/2026/03/who-pays-for-what-understanding-key-differences-in-triple-net
- NAIOP — benefits and risks of triple net leases (NNN shifts opex risk to the tenant; protects landlord NOI): https://www.naiop.org/research-and-publications/magazine/2017/summer-2017/marketing-leasing/the-benefits-and-risks-of-triple-net-leases/

Lease-structure norms vary by market, asset class, and negotiation — verify the actual recovery terms in each lease abstract before acting (§3 #8).
