---
name: manage-case-logistics-and-fulfillment
description: Read and manage the funeral-home case-flow pipeline (first call → removal/transfer → arrangement → preparation → services → billing → aftercare), find the constraint stage that gates throughput, size staffing and on-call/removal capacity against call volume, decide build-vs-contract for removals or preparation, and produce the fulfillment plan for the arranged services — all while protecting the family experience, not just the margin. Reach for this when the user asks "why are families waiting?", "are we staffed right for our volume?", "where's the bottleneck in our case flow?", or "can we fulfill these services on our capacity?". Used by `funeral-operations-lead` (primary). Not legal/financial advice — verify licensing and benchmarks.
---

# Skill: manage-case-logistics-and-fulfillment

> **Invoked by:** `funeral-operations-lead` (primary). Also consulted by `funeral-arrangement-and-compliance-specialist` to confirm an arranged disposition is fulfillable before a service date is committed.
>
> **When to invoke:** "Why are families waiting between first call and arrangement?"; "are we over/under-staffed for our call volume?"; "where's the bottleneck in our case flow?"; "can we fulfill these services on our current capacity?"; any operational read of the pipeline or a fulfillment plan.
>
> **Output:** the case-flow read (the constraint stage + why), a staffing/on-call/removal capacity read against volume, the build-vs-contract call with its volume threshold, and the fulfillment plan — with a family-experience check. **Not legal/financial advice.**

## Procedure

1. **Map the full pipeline before naming a bottleneck.** Walk [`../../knowledge/funeral-operations-patterns-2026.md`](../../knowledge/funeral-operations-patterns-2026.md)'s stages: **first call → removal/transfer → arrangement → preparation → services → billing → aftercare.** Read it as a system — the constraint stage is rarely where the complaint is voiced.
2. **Locate the constraint stage.** A "slow arrangement" often traces upstream to an under-staffed removal or a prep-room/embalmer backlog. Find the stage that *gates* throughput (the one others queue behind), not the loudest symptom.
3. **Read call volume and disposition mix.** Annual call volume and the burial : cremation : aquamation : green-burial split drive staffing load, facility use, and blended revenue-per-call. A cremation-majority mix changes the fulfillment shape (more memorial/celebrant services, urns, scattering coordination; fewer full-casket burials).
4. **Size staffing against real load.** Licensed funeral directors (arrangements/services), embalmers (preparation), and **on-call/removal coverage** against volume and after-hours frequency. Flag burnout risk on a thin on-call roster — it degrades the family experience, not just cost.
5. **Decide build-vs-contract at the threshold.** Removals and, sometimes, embalming/preparation can be contracted to a trade service below a volume threshold and brought in-house above it. Name the threshold that flips it rather than defaulting either way.
6. **Produce the fulfillment plan for the arranged services.** Schedule the visitation/funeral/memorial/graveside against facility, vehicle, and staff availability; sequence preparation to the service date; coordinate the graveside *with the cemetery* (out of scope to run, in scope to coordinate); confirm livestream/recording if offered.
7. **Run the family-experience check and route the seams.** Confirm the plan preserves dignity, not just margin (§3 #1). Route regulatory items to [`ensure-deathcare-compliance-and-pricing`](../ensure-deathcare-compliance-and-pricing/SKILL.md), the books to `accounting-bookkeeping`, clinical grief to `behavioral-health-practice`, and cemetery interment out of scope.

## Worked example

> User: "Families keep telling us the arrangement conference is booked three days out. We're a 350-call-a-year home with two directors. What's wrong?"

- **Map the pipeline** — the complaint is at *arrangement*, but at 350 calls/year two directors aren't the obvious constraint. Look upstream.
- **Locate the constraint** — the removal is on a single on-call rotation and the prep room has one embalmer; decedents back up in transfer/prep, so the *arrangement* can't be scheduled until care-status is confirmed. The bottleneck is **removal + prep capacity**, not the arrangement desk.
- **Volume/mix** — 350 calls with a rising cremation share means less prep-room load per case *on average*, but the burial cases still queue on the one embalmer.
- **Staffing** — the on-call roster is too thin for the after-hours first-call frequency; burnout risk is real.
- **Build-vs-contract** — at 350 calls, contracting overflow removals to a trade service (rather than a second full-time on-call hire) likely pencils out; name the volume above which the in-house hire wins.
- **Fulfillment + family-experience check** — smoothing removal/prep lets arrangements book within a day, which the family experiences as responsiveness. Route the pricing of any new package to compliance; the cost model to `accounting-bookkeeping`.

## Guardrails

- Map the whole pipeline before naming a bottleneck — the constraint stage is rarely where the complaint is.
- Never optimize a stage in isolation; a downstream fix on an upstream constraint just moves the queue.
- Family-experience check on every plan — a margin move that degrades dignity is rejected (§3 #1).
- Build-vs-contract is a threshold decision — name the volume that flips it, don't default.
- Coordinate *with* the cemetery for graveside; running interment/grounds is **out of scope**.
- Licensing requirements and benchmark figures (cremation rate, revenue-per-call) are **state-specific / volatile** — carry a retrieval date and route the books to `accounting-bookkeeping`. **Not legal/financial advice.**
