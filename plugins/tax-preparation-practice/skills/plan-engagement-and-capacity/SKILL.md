---
name: plan-engagement-and-capacity
description: "Plan the client mix, open the engagement, and size busy-season capacity by traversing the practice decision tree (engagement accept/decline & risk screen → client-mix/niche → engagement letter + organizer scope → busy-season volume × preparer-hours vs reviewed-hours → extension policy as load valve → pricing/realization model), then return the accept/decline call, the engagement letter & organizer scope, the capacity/staffing plan, and the pricing model with the conditions that resize it. Reach for this when the user asks 'what client mix should we take?', 'draft our engagement letter / organizer', 'how do we plan busy-season capacity?', or 'how should we price returns?'. Used by tax-practice-lead (primary) and tax-preparation-specialist."
---

# Skill: plan-engagement-and-capacity

> **Invoked by:** `tax-practice-lead` (primary — the client-mix, engagement, capacity, and pricing policy) and `tax-preparation-specialist` (for the engagement letter/organizer that opens a return).
>
> **When to invoke:** "what client mix / niche should we take and who do we decline?"; "draft our engagement letter and client organizer"; "how do we plan busy-season capacity and staffing?"; "an extension policy?"; "how should we price returns / defend realization?"; any "who do we serve and how do we survive the season" question.
>
> **Output:** the engagement accept/decline call + the engagement letter & organizer scope + the busy-season capacity/staffing plan (with the extension as a load valve) + the pricing/realization model + the 1-2 conditions that resize it.

## Procedure

1. **Screen the engagement before you accept it.** Traverse the accept/decline branch in [`../../knowledge/tax-preparation-practice-decision-tree.md`](../../knowledge/tax-preparation-practice-decision-tree.md): does the return sit inside the firm's **competence** (Circular 230 §10.35 competence), its **niche**, and its **risk tolerance** (a client with missing records, aggressive expectations, or a conflict is a decline, not a fee)? A bad client accepted in January is a liability in April.
2. **Set the client mix / niche deliberately.** Decide the segments — **1040** (simple vs complex: Schedule C, rental, multistate, K-1-heavy) vs **business** (1120 / 1120-S / 1065) — and the **complexity band** the staff can prepare and review. A focused niche (a profession, an industry, an entity type) compounds efficiency; an everything-practice compounds review risk.
3. **Open every engagement with a letter and an organizer — before the first keystroke.** The **engagement letter** fixes scope, fee basis, responsibilities (who provides what), the documentation standard, and the limits (what's *not* included) — it is the scope-creep and fee-dispute control. The **organizer** drives document intake and the completeness check. See [`../../templates/client-organizer-and-engagement-letter.md`](../../templates/client-organizer-and-engagement-letter.md). No letter, no return.
4. **Size busy-season capacity on the stressed peak.** Model **return volume × preparer-hours per return** (by complexity band) against **available preparer *and reviewed* hours** across the compressed Jan–Apr window. The binding constraint is usually **review** capacity, not prep — so staff the preparer→reviewer ratio, and don't let review be the step that gets cut when the queue backs up.
5. **Treat the extension as a deliberate load valve, not a failure.** When the peak exceeds reviewed-hours or a client's data lands late, **file an extension** to protect accuracy — a rushed, wrong return filed to beat the date is worse than an accurate one filed on extension. Set the policy: which returns extend by default (late data, high complexity, missing K-1s), and remember an extension is to *file*, not to *pay*.
6. **Choose the pricing model and defend realization.** **Per-return / flat** (predictable, rewards efficiency, needs a tight scope clause), **value-based** (for planning-heavy or high-complexity work), or **hourly** (for open-scope projects and representation). Defend **realization** — billed vs collected vs hours sunk — with the engagement letter's scope clause; the quietly-tripling return is where a practice loses money.
7. **State the resize conditions** — the 1-2 facts that change the mix/capacity/pricing (e.g., "if we add a multistate niche, review-hours per return rise and the reviewer becomes the bottleneck"; "if a top client's business grows into a 1065, it crosses the complexity band we staffed for").

## Worked example

> User: "We're a 3-person firm — one partner, two staff. We did 400 1040s and 30 business returns last season and it nearly broke us. Plan next season and tell us how to price."

- **Accept/decline:** screen out the 20 chronically-late, missing-records 1040s that consumed April — a documented decline (or a firm deadline-to-provide-docs cutoff), not a January yes.
- **Mix / niche:** the two staff prep the standard 1040s and the 1120-S/1065s within their band; the partner **reviews everything** and preps the complex multistate returns — the review capacity is the real ceiling.
- **Engagement:** every client gets the letter + organizer; the organizer's completeness gate stops the "prepared then missing a K-1" re-work loop.
- **Capacity:** 430 returns × avg 3.5 prep-hours ≈ 1,500 prep-hours across two staff, but the partner's **review** hours (≈1 hr/return + 3 hrs on the complex ones) are the binding constraint → **extend the late-data and complex tail** to move ~60 returns past April 15.
- **Extension policy:** any client whose docs aren't complete by mid-March extends by default (pay the estimated balance with the 4868/7004).
- **Pricing:** move the 1040s to **flat per-return** with a scope clause (extra schedules = extra fee), business returns to **value-based**, and representation to **hourly** — defend realization by billing the scope creep the letter reserved.
- **Resize condition:** if the firm adds a fourth preparer but no reviewer, the review bottleneck worsens, not improves.

## Guardrails

- **Screen the engagement before accepting** — a client outside the firm's competence, niche, or risk tolerance is a decline, not a fee (Circular 230 competence).
- **The engagement letter and organizer come before the first keystroke** — scope, fee basis, and the documentation standard in writing protect the client and the preparer.
- **Size capacity on the stressed peak, and review is usually the binding constraint** — staff the preparer→reviewer ratio; don't let review be what gets cut.
- **The extension is a load valve, not a failure** — extend to protect accuracy; it's to file, not to pay (pay the estimated balance with it).
- **Defend realization with the scope clause** — the quietly-tripling return is the leak; per-return / value / hourly is a deliberate choice.
- Setting the mix/capacity/pricing **policy** is the `tax-practice-lead`; opening and preparing the return is the `tax-preparation-specialist` — keep the seam clean.
- This is **not** the books / monthly close — that's `accounting-bookkeeping`; and **not** tax, legal, or accounting advice. Circular 230 specifics, forms, and deadlines are volatile — carry a **retrieval date**. See [`../../knowledge/tax-preparation-practice-patterns-2026.md`](../../knowledge/tax-preparation-practice-patterns-2026.md).
