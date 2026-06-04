---
name: incoterms-2020
description: "Veteran reference for Incoterms 2020 in a sales context — all 11 terms, the cost vs risk transfer point of each, the who-pays-what responsibility matrix, the 7 any-mode vs 4 sea-only split, named-place discipline, and the recurring quoting traps (FCA vs FOB for containers, CIP vs CIF insurance, DDP duty/VAT exposure). Consulted by trade-lane-compliance-advisor."
---

# Incoterms 2020 Skill

**Purpose:** let `trade-lane-compliance-advisor` settle the Incoterm and named place *before* pricing, and explain the cost/risk split to a customer correctly. The Incoterm decides which charges from the surcharge stack land on the seller vs the buyer — get it wrong and the quote is wrong.

> **Source discipline:** the Incoterms® 2020 rules are published by the ICC. The structure below is the standard interpretation; for a binding contractual question, cite the ICC text and flag legal review. Country/contract specifics are `[verify-at-use]`.

## When to use
- Choosing which Incoterm to propose for a deal.
- Settling a "who pays the THC / duty / insurance" question.
- Setting the **quoting scope** for `freight-rate-quoter`.

## The 11 terms — two families

**Any mode of transport (7):**

| Term | Cost transfer (seller pays up to) | Risk transfers | Seller does export clearance? | Notes |
|---|---|---|---|---|
| **EXW** Ex Works | goods at seller's premises | at seller's premises | **No** (buyer's job — awkward) | Maximum buyer responsibility. |
| **FCA** Free Carrier | delivered to carrier at named place | at hand-over to carrier | Yes | **Correct term for containerized cargo.** |
| **CPT** Carriage Paid To | main carriage to named dest | at hand-over to **first** carrier | Yes | Cost ≠ risk point — risk passes early. |
| **CIP** Carriage & Insurance Paid To | main carriage + **all-risks** insurance | at hand-over to first carrier | Yes | Insurance = **ICC (A) all-risks** by default in 2020. |
| **DAP** Delivered At Place | arrival, ready for unloading | at destination | Yes | Buyer handles import clearance + duty. |
| **DPU** Delivered At Place Unloaded | arrival **and unloaded** | at destination after unloading | Yes | Only term where seller unloads. (Was DAT.) |
| **DDP** Delivered Duty Paid | everything incl. **import duty + VAT** | at destination | Yes (+ import) | Maximum seller responsibility; needs importer-of-record. |

**Sea & inland waterway only (4):**

| Term | Cost transfer | Risk transfers | Notes |
|---|---|---|---|
| **FAS** Free Alongside Ship | alongside vessel at load port | alongside the ship | Bulk/breakbulk. |
| **FOB** Free On Board | loaded **on board** at load port | once on board | For goods that cross the ship's rail — **not** ideal for containers. |
| **CFR** Cost and Freight | main carriage to dest port | once on board at origin | Buyer handles destination + import. |
| **CIF** Cost, Insurance & Freight | main carriage + insurance | once on board at origin | Insurance = **ICC (C) minimum** by default (≠ CIP). |

## The traps that change the price

1. **FCA vs FOB for containers.** FOB/CFR/CIF assume the seller bears risk until goods are **on board** — fine for bulk crossing a rail, wrong for containers handed over at a CY/CFS days earlier. Use **FCA/CPT/CIP** for containerized cargo. Customers misuse FOB constantly; flag it, propose FCA, explain the risk-gap.
2. **CIP vs CIF insurance level.** Incoterms 2020 raised **CIP** insurance to **all-risks (ICC A)**; **CIF** stayed at **minimum (ICC C)**. Don't assume they match — it changes the insurance cost and the buyer's protection.
3. **DDP exposure.** Under DDP the **seller** pays import duty + VAT and usually needs to be (or appoint) the importer of record in the destination country — real money and real compliance risk. Don't propose DDP casually.
4. **EXW export-clearance gap.** Under EXW the **buyer** is responsible for export clearance in the seller's own country — often impractical; FCA is usually the better "minimal seller" term.
5. **Named place is mandatory.** "FCA" alone is incomplete — it's "FCA [named place], Incoterms 2020." The named place fixes exactly where cost/risk transfer.

## Cost-allocation cheat (who pays what, by family)

- **E-term (EXW):** buyer pays essentially everything from the seller's door.
- **F-terms (FCA/FAS/FOB):** seller pays to origin hand-over/load; **buyer pays main carriage + destination + import**. (Buyer pays the freight surcharges.)
- **C-terms (CPT/CIP/CFR/CIF):** seller pays **main carriage** (+ insurance on CIP/CIF) to destination port/place, but **risk** already passed at origin; buyer handles import + destination THC (on CFR/CIF).
- **D-terms (DAP/DPU/DDP):** seller pays to destination; DDP also pays **import duty + VAT**.

A quote must match its Incoterm scope: don't include DTHC/destination on an FOB quote the buyer owns; don't omit origin haulage on an EXW quote.

## Recommended resources (read on demand)
- `resources/responsibility-matrix.md` — the full obligation grid (which party does export clearance, main carriage, insurance, unloading, import clearance, duty) per term.

## Hand-offs
- Pricing within the settled scope → `freight-pricing-mechanics` skill / `freight-rate-quoter`.
- A binding legal/contractual interpretation → flag for licensed legal review (not this skill's role).
