---
name: improve-diversion-and-recycling-economics
description: Measure the real diversion rate from weigh tickets, diagnose the MRF & recycling commodity economics by grade (OCC/cardboard, PET, HDPE, aluminum, mixed paper — post-National-Sword bale prices), attack the contamination rate that decides the P&L, and set the pricing response (commodity-share vs processing/tip-fee) against the mandates in force (SB 1383 organics, EPR packaging, landfill bans). Reach for this when the user asks "what's our real diversion rate?", "our MRF revenue is underwater", or "contamination is killing single-stream". Used by `route-and-diversion-specialist` (primary).
---

# Skill: improve-diversion-and-recycling-economics

> **Invoked by:** `route-and-diversion-specialist` (primary). Also consulted by `waste-operations-lead` so a disposal plan doesn't undercut a diversion mandate the operation is subject to.
>
> **When to invoke:** "What's our real diversion rate?"; "our MRF/bale economics are underwater"; "contamination is killing our single-stream"; "how do we raise diversion without wrecking the cost?"; any move from "recycle more" to a measured, priced diversion plan.
>
> **Output:** a measured diversion rate (from weigh tickets) + the MRF/commodity exposure by grade + a contamination-reduction plan + the pricing response — against the SB 1383 / EPR / landfill-ban mandates in force, with dated commodity prices and the flip conditions.

## Procedure

1. **Measure diversion from the scale, not the brochure.** Diversion rate = diverted tonnage ÷ total generated, computed from **weigh tickets** — never estimated capture. Name the streams dragging it down: low set-out/capture, organics still landfilled, contamination rejected at the MRF. A ton "collected for recycling" but rejected at the MRF was never diverted.
2. **Attack contamination first — it decides the recycling P&L.** Contamination lowers bale value, raises MRF residual/reject cost, and above a threshold flips a load from revenue to a tipping-fee expense. Measure it as the MRF's **residual/reject rate** and reduce it at the source: cart tagging / "oops" stickers, route audits, targeted customer education, clear accepted-materials lists. This usually beats chasing a marginal bale-price uptick.
3. **Map the commodity exposure by grade.** OCC/cardboard (the volume workhorse), **aluminum (the value anchor — small mass, large revenue share)**, PET/HDPE (real end-markets, value rides resin + cleanliness), **mixed paper (the drag — hit hardest by China's National Sword)**. Traverse [`../../knowledge/waste-recycling-patterns-2026.md`](../../knowledge/waste-recycling-patterns-2026.md). Bale prices are **volatile** — retrieve current and date them.
4. **Respect National Sword's permanent reset.** The offshore outlet for dirty low-grade material is gone; domestic MRF quality + end-markets are the reality. Design for clean, domestically-marketable bales, not a return to shipping unsorted paper offshore.
5. **Set the pricing response to survive a commodity trough.** A **commodity-share** model exposes the program to the market; a **processing/tip-fee** model insulates it. Choose given the contamination and grade mix — and say what a bale-price crash does to the P&L under each.
6. **Bind the mandates in force as constraints.** Organics mandates (California **SB 1383**), **EPR** packaging laws (expanding by state), and landfill bans set the floor: where a stream is compulsorily diverted, "landfill it" isn't a legal option regardless of price. Flag the seam to `waste-operations-lead` when a mandate forces a fleet/disposal change.
7. **Capture it and name the flip conditions.** Record the diversion rate, commodity exposure, contamination plan, pricing response, and mandates in [`../../templates/diversion-and-cost-analysis.md`](../../templates/diversion-and-cost-analysis.md); name the 1-2 facts (a bale-price move, a new mandate) that would change the call.

## Worked example

> User: "Single-stream residential. MRF says our loads are 28% contaminated and our recycling revenue went negative last quarter. What do we do?"

- **Diversion (measured):** pull the weigh tickets — the reported diversion is inflated because ~28% is rejected at the MRF and lands anyway; the *real* diverted tonnage is materially lower.
- **Contamination first:** 28% is deep in flip-to-expense territory — the load costs more to process + dispose of the residual than the clean bales earn. Launch a **source-reduction** program: cart tagging + audits + education on the 3-4 worst contaminants; target the residual rate down first.
- **Commodity exposure:** confirm the grade mix — is **aluminum** (the value anchor) being captured, and is **mixed paper** (the drag) dominating the tonnage? Retrieve current bale prices [date them].
- **Pricing response:** if on a **commodity-share** contract, the trough is hitting the P&L directly — evaluate a **processing/tip-fee** structure to insulate, at least until contamination is under control.
- **Mandates:** check whether **SB 1383** organics or a landfill ban applies — it may compel an organics route that also lifts diversion (hand any fleet/disposal change to `waste-operations-lead`).
- **Flip condition:** if contamination drops below the MRF's acceptance threshold and bale prices recover, commodity-share may beat tip-fee again — revisit.

## Guardrails

- Diversion comes from **weigh-ticket tonnage**, never estimated capture — a rejected-at-MRF ton was never diverted.
- **Contamination is the killer** — reduce it at the source before chasing bale price; it decides whether a load is revenue or expense.
- Know the grade exposure — **aluminum carries the bale, mixed paper is the drag**; National Sword permanently reset the low-grade outlet.
- **Mandates override economics** — SB 1383 / EPR / landfill bans set the floor; never quote the trade-off as pure commodity math when a mandate is in force.
- A fleet/disposal change that a diversion plan implies belongs to `waste-operations-lead` — flag the seam.
- Bale/commodity prices and EPR/SB 1383/landfill-ban statutes are **volatile** — carry a **retrieval date** and re-verify. See [`../../knowledge/waste-recycling-patterns-2026.md`](../../knowledge/waste-recycling-patterns-2026.md).
