---
name: design-ancillary-services-and-scope
description: Decide an urgent-care center's ancillary services and scope of service by modeling each ancillary (on-site x-ray/imaging, POCT/on-site labs, procedures) as a capex-and-throughput decision with a payback — weighing capex, staffing, scope, and the door-to-door-time cost against the revenue-per-visit lift and in-house retention — and by framing the scope-of-service line (acuity ceiling, procedure menu, pediatric age floor, transfer protocol) as a clinical-and-operational decision drawn WITH the medical director, returning the recommended additions/scope with the payback and the throughput impact and flagging the clinical decision to the medical director. Reach for this when the user asks "should I add on-site x-ray or a POCT lab?", "is a procedure line worth it?", "what acuity should we treat?", or "what's our pediatric age floor?". Used by `urgent-care-operations-lead` (primary).
---

# Skill: design-ancillary-services-and-scope

> **Invoked by:** `urgent-care-operations-lead` (primary). Also consulted by `urgent-care-revenue-and-payer-specialist` for the ancillary-capture side of visit economics (the operations lead owns the capex/scope decision; the *revenue* per ancillary is the specialist's).
>
> **When to invoke:** "Should I add on-site x-ray / a POCT lab / a procedure line?"; "what's the payback on imaging?"; "what acuity should we treat / what's our pediatric age floor?"; any ancillary-services or scope-of-service decision.
>
> **Output:** the ancillary-services read (each service as capex/staffing/throughput cost + payback) + the scope-of-service line (acuity ceiling, procedures, pediatric floor, transfer protocol) drawn **with the medical director** + the throughput impact + the 1-2 flip conditions.

> ⚠️ **Scope of service is a clinical-and-operational decision — the acuity ceiling, procedure menu, and pediatric floor are set WITH the medical director, never as an operations solo call.** This skill frames the operational and economic trade-offs; the clinical line is the medical director's. **Not clinical advice.**

## Procedure

1. **Name the sub-branch — ancillary add, or scope line.** Traverse [`../../knowledge/urgent-care-operations-decision-tree.md`](../../knowledge/urgent-care-operations-decision-tree.md): is the question *should we add an ancillary service* (x-ray/POCT/procedures) or *where is our scope of service drawn* (acuity/procedures/pediatric floor)?
2. **Model each ancillary as a capex-and-throughput decision with a payback.** For **on-site x-ray/imaging**, **POCT/on-site labs**, or a **procedure line**, weigh: **capex** (equipment), **staffing** (e.g. a rad tech, trained MA), **scope** (what it commits the center to clinically), and the **door-to-door-time cost** (the added provider-to-discharge turnaround) against the **revenue-per-visit lift** and **in-house retention** (visits kept rather than referred out). See [`../../knowledge/urgent-care-patterns-2026.md`](../../knowledge/urgent-care-patterns-2026.md).
3. **Route the revenue side to the specialist.** The revenue-per-visit lift and the **ancillary capture** (an x-ray/POCT delivered but not recorded is lost revenue) belong to `structure-payer-and-occmed-contracts` — this skill owns the capex/staffing/throughput decision; the specialist owns what the ancillary *earns*.
4. **Draw scope of service WITH the medical director.** The **acuity ceiling** (upper bound before transfer/referral), the **procedure menu**, the **pediatric age floor**, and the **transfer/EMTALA-adjacent protocol** set staffing, malpractice, equipment, and clinical protocol. Frame the operational and economic trade-offs; **flag the clinical decision to the medical director** — never set it solo.
5. **Cost the throughput impact explicitly.** Each ancillary adds provider-to-discharge time (turnaround) — feed that back into `optimize-throughput-and-staffing` so the door-to-door plan accounts for it. A payback that ignores the added wait is incomplete.
6. **State the flip conditions.** Name the 1-2 facts that would change the add/scope call (e.g. "if a new occ-med contract requires DOT physicals and drug screens, the POCT payback improves and the scope shifts").

## Worked example

> User: "Should I put in an on-site x-ray? The nearest imaging is 15 minutes away and we refer a lot of ankles out."

- **Sub-branch:** ancillary add (x-ray) — with a scope implication.
- **Capex/staffing:** x-ray unit + install, plus a rad tech (or trained/licensed staff per state) — a real fixed cost and a scope commitment.
- **Payback:** model the **retained** imaging-needing visits (the ankles/wrists/chest complaints currently referred out) × the revenue-per-visit lift (route the exact per-visit revenue and ancillary capture to the specialist), against the capex + staffing. In-house retention also improves the **door-to-door experience** (no 15-minute referral detour) — a review/demand benefit.
- **Throughput cost:** x-ray adds provider-to-discharge turnaround — feed that into the throughput plan so the demand-curve staffing absorbs it.
- **Scope flag:** treating more musculoskeletal/imaging-needing acuity raises the **acuity ceiling** — confirm the expanded scope, protocols, and staffing **with the medical director** before committing. **Not a clinical call this skill makes.**
- **Flip condition:** if an imaging center opens next door, the retention benefit shrinks and the payback lengthens.

## Guardrails

- Every ancillary is a **capex-and-throughput decision with a payback** — model the revenue-per-visit lift *and* the door-to-door-time cost; never add for prestige.
- The **revenue** per ancillary and the ancillary-capture leakage route to `structure-payer-and-occmed-contracts` — this skill owns the capex/scope decision, not the revenue diagnosis.
- The added provider-to-discharge turnaround routes back into `optimize-throughput-and-staffing` — a payback that ignores the added wait is incomplete.
- **Scope of service (acuity ceiling, procedures, pediatric floor, transfer protocol) is drawn WITH the medical director** — flag the clinical decision; never set it solo. Not clinical advice.
- Volatile claims (equipment/reagent costs, reimbursement, EMR/PM POCT-workflow features, state staffing/licensure rules) carry a **retrieval date** — re-verify before a client commitment; the licensure/legal question routes to counsel.
