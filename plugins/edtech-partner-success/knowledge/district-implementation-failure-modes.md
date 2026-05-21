# District implementation failure modes

> **Last reviewed:** 2026-05-21. Status: pre-engagement-draft (synthesis from existing v0.2.0 production-lesson files + practitioner consensus; refresh on first real engagement signal via `/wrap`). Sources: LAUSD/AllHere $6M failure (2024 — already documented in [`ai-in-edtech-2026.md`](ai-in-edtech-2026.md)), CoSN implementation surveys, [`rostering-data-quality-typology.md`](rostering-data-quality-typology.md), [`partner-health-score-drift.md`](partner-health-score-drift.md), [`parent-comms-jurisdictional-bear-traps.md`](parent-comms-jurisdictional-bear-traps.md). Refresh when: (a) a new high-profile EdTech implementation failure becomes public knowledge worth incorporating, (b) the LAUSD/AllHere-driven CIO diligence shift evolves further, (c) live engagement scenarios via `/wrap` surface failure patterns not anticipated here.

This file is the **pre-flight checklist** for implementation. The [`../skills/implementation-90-day-arc.md`](../skills/implementation-90-day-arc.md) skill consults this file in weeks 1-2 (discovery — what to pre-check) and at Day 90 (retrospective — did any patterns slip in). The [`../templates/implementation-90-day-plan.md`](../templates/implementation-90-day-plan.md) template's "Failure-mode checks" section is keyed to this file.

This file complements [`sis-sso-rostering-integration-patterns.md`](sis-sso-rostering-integration-patterns.md) — that file covers TECHNICAL integration patterns; this file covers BROADER failure modes (technical, relationship, calendar, process).

---

## The big picture — why implementations fail

EdTech implementations fail for predictable reasons. The pre-flight check is more valuable than the post-mortem. Most failures fall into one of these categories:

| Category | Frequency (qualitative) | Pre-flight check possible? |
|---|---|---|
| **Technical integration** (rostering, SSO, sync) | High | Yes — see [`sis-sso-rostering-integration-patterns.md`](sis-sso-rostering-integration-patterns.md) |
| **Training cascade collapse** | High | Yes — confirmable in week 5-6 |
| **Calendar misalignment** | Medium-high | Yes — visible in week 1 |
| **Champion departure mid-arc** | Medium | Partial — champion redundancy at discovery |
| **District-internal political shift** | Medium | Partial — surface signals at QBR |
| **Vendor-side failure** (LAUSD/AllHere pattern) | Low but catastrophic when it happens | Yes — vendor financial-diligence at procurement |
| **Compliance / regulatory gap** | Low frequency but high impact | Yes — DPA + sub-processor + state-law check at discovery |

## Failure mode 1: Training cascade collapse

**Symptom:** Trained-trainers attend the train-the-trainer sessions but never run their own waves. By Day 60, the partner's frontline teachers haven't been trained, adoption stalls, the PSM is fielding "how do I do X" tickets that should have routed through the partner-side champion.

**Root causes:**
- Champion was assigned to train-the-trainer by district leadership but never formally tasked with running waves
- Champion's normal workload didn't get reduced to make room for training facilitation
- District PD schedule didn't have follow-up windows for waves 2-N
- Champion attended product depth (Session 1) but no facilitation craft (Session 2) — feels unprepared
- Champion-redundancy of 1; the one champion got reassigned or pulled to other duties

**Pre-flight check (week 5-6):**
- [ ] Has the partner's PD office formally added training waves to champion's calendar?
- [ ] Are there 2-3 champions, not 1? (per the train-the-trainer curriculum)
- [ ] Did the train-the-trainer curriculum cover Session 2 (facilitation craft), not just Session 1 (product depth)?
- [ ] Is there a measurement loop — how will the PSM know if waves are happening?

**Day-90 audit:** Are there documented training waves actually completed? Not just "scheduled."

## Failure mode 2: Calendar misalignment / go-live in dead zone

**Symptom:** Implementation calendar set at contract close; go-live target lands in a known K-12 dead zone (late August setup overload, Thanksgiving week, winter break, state testing window, end-of-year wrap). Engagement signals don't establish because the dead zone suppresses them; the first-30-day measurement window is meaningless.

**Root causes:**
- Standard 60-75-day implementation arc applied without checking the partner's specific school calendar
- Partner pushed for a "we want it live by September 1" target that puts go-live in pre-school-start setup overload
- Partner is in a state with early testing windows that the vendor didn't anticipate

**Pre-flight check (week 1-2):**
- [ ] Has the PSM cross-referenced the target go-live against [`k12-psm-operating-cadence.md`](k12-psm-operating-cadence.md) dead zones?
- [ ] Is the partner's state testing window confirmed?
- [ ] If go-live lands in a dead zone, has the PSM proposed an alternative target?

**Mitigation:** push go-live to a non-dead-zone window even if it's later than the partner's initial target. A successful late go-live beats a failed early go-live.

## Failure mode 3: Champion departure mid-arc

**Symptom:** The named partner-side champion (the curriculum director, principal, or instructional coach who drove the buying decision) leaves the district / is reassigned during the 90-day arc. Implementation continues but the relationship anchor is gone.

**Root causes:**
- K-12 superintendent turnover hit 23% in 500 largest districts 2024-25 (per [`renewal-pricing-conversations-edtech.md`](renewal-pricing-conversations-edtech.md)); curriculum-director turnover is similar
- Champion was the only named decision-maker (champion-redundancy of 1)
- Champion was over-aligned with the buying decision and exited along with leadership churn

**Pre-flight check (week 1-2):**
- [ ] Are there 2+ named decision-makers (champion-redundancy ≥ 2)?
- [ ] Is there a curriculum-director-as-champion AND a technical-lead-as-co-champion, not just one role?
- [ ] What's the named decision-maker's tenure trajectory? (recent appointments at higher risk of being squeezed out)

**Mitigation:** at champion departure, immediately re-confirm the implementation with the named successor (or interim). If no successor exists, the implementation pauses until one is named — going through implementation with no relationship anchor is worse than pausing.

## Failure mode 4: Rostering completeness illusion

**Symptom:** "Sync ran successfully" reports as green. First-30-day adoption signals are weak. Investigation reveals the sync was missing one entire school, or one entire role, or all teachers in a specific grade band.

**Root causes:**
- Clever / ClassLink sharing scope set to limited subset of schools or roles
- OneRoster version skew between SIS export and vendor import (some fields missing silently)
- Class-section mapping drift between SIS and broker
- Family-rostering surface not enabled
- District's SIS itself has data quality issues that don't surface in the broker

**Pre-flight check (week 3-4):**
- [ ] Spot-check 10 users across roles + schools (NOT just "sync succeeded")
- [ ] Compare per-school user counts against the partner's own data
- [ ] Test class-section mapping if product needs class context
- [ ] Test enrollment changes propagate (add a test student, confirm appears in vendor system within sync window)

**Mitigation:** [`rostering-data-quality-typology.md`](rostering-data-quality-typology.md) has the full diagnostic typology.

## Failure mode 5: SSO works for admins but not students

**Symptom:** Admin testing confirms SSO works. Go-live happens. Students can't log in. Implementation immediately becomes a support crisis.

**Root causes:**
- Different IdP routes per role (admins through district AD, students through Clever Instant Login or ClassLink — the student route was not configured or not tested)
- Just-in-time (JIT) provisioning at student login fails because role attribute mapping is wrong
- Student IdP requires a separate metadata exchange the implementation team didn't complete
- Per-grade authentication restrictions (some districts gate student SSO by grade)

**Pre-flight check (week 3-4):**
- [ ] Test SSO **per role**, not just admin
- [ ] Test SSO with a real student account (not a test user with admin privileges)
- [ ] Confirm IdP route for each role is configured + tested
- [ ] Test the error path — what does a failed login look like?

**Mitigation:** mandatory per-role SSO test in the implementation 90-day plan validation gate.

## Failure mode 6: Vendor financial / operational collapse mid-arc

**Symptom:** The vendor (or a key sub-processor) experiences a financial / operational event that disrupts the implementation. The LAUSD/AllHere $6M failure (2024) is the canonical example — AllHere furloughed staff mid-deployment; the CEO was later charged with fraud.

**Root causes:**
- District didn't run financial diligence on the vendor (or sub-processor)
- Vendor's pre-contract claims were misaligned with actual capability
- Sub-processor list wasn't disclosed at the level the district needed to evaluate

**Pre-flight check (PROCUREMENT — before contract):**
- [ ] Vendor financial-health attestation (SOC 2 + recent audit + public filings if available)
- [ ] Sub-processor list disclosed (not just "we use AWS")
- [ ] Pilot-before-scale option offered + considered
- [ ] Reference districts (multiple, independently sourced)

**The CIO posture shift since LAUSD:** vendor financial diligence is now table stakes for any K-12 implementation > ~$500K. The shift is documented in [`ai-in-edtech-2026.md`](ai-in-edtech-2026.md).

**Mitigation:** if mid-arc, the PSM's job is to surface the situation to the partner transparently and honestly. Concealment turns a financial-failure-recoverable event into a trust-failure-unrecoverable one.

## Failure mode 7: Compliance / regulatory gap surfaces post-go-live

**Symptom:** District legal team discovers post-go-live that the implementation doesn't match the contract's data-protection rider, or sub-processor list, or state-law disclosure requirement. Implementation pauses while the gap is closed.

**Root causes:**
- State-specific data-protection rider (NY Ed Law §2-d, IL SOPPA, CA SOPIPA) not attached or out of date
- Sub-processor list at go-live different from contract list
- AI-feature data-flow doesn't match COPPA-amended consent posture (post April 22 2026)
- Family-surface data flow not disclosed to parents

**Pre-flight check (week 1-2):**
- [ ] State-specific data-protection rider attached and current
- [ ] Sub-processor list confirmed current with partner
- [ ] AI-feature data-flow diagram shared with partner (if product has AI)
- [ ] Family-surface data-flow disclosed (if family-facing)

**Mitigation:** these checks should never surface AT go-live; they belong at week 1-2 discovery. Per [`parent-comms-jurisdictional-bear-traps.md`](parent-comms-jurisdictional-bear-traps.md).

## Failure mode 8: District-internal political shift

**Symptom:** Implementation is technically on-track but interpersonal / political signals shift. Champion's enthusiasm wanes; named decision-maker stops responding; expansion conversations get walked back.

**Root causes:**
- District-internal politics (board change, superintendent change, restructure)
- Champion's career trajectory changed (interviewing elsewhere, demoted internally, etc.)
- Competing vendor lobbying inside the district
- External event (parent complaint, news cycle, state policy change) shifts the partner's risk posture

**Pre-flight check (ongoing):**
- [ ] Quarterly "is the named decision-maker still in role, still excited" check
- [ ] Watch for non-technical signals — response delays, less-warm communication, missed touchpoints

**Mitigation:** can't be prevented at pre-flight; only managed when it surfaces. The partner-profile-curator's job is to track political-context signals so the PSM can respond early.

## Summary — the implementation pre-flight checklist (consolidated)

At week 1-2 discovery, confirm:

- [ ] Target go-live NOT in a dead zone
- [ ] Champion-redundancy ≥ 2 (per role: curricular champion + technical lead at minimum)
- [ ] SIS / rostering broker / OneRoster version known + compatible
- [ ] SSO IdP route per role known
- [ ] State data-protection rider attached + current
- [ ] Sub-processor list disclosed
- [ ] AI-feature data-flow disclosed (if applicable)
- [ ] District PD-credit framework confirmed (for train-the-trainer)

At week 3-4 validation:

- [ ] Rostering spot-check 10 users
- [ ] SSO test per role
- [ ] Data-flow validation

At week 5-6 train-the-trainer:

- [ ] 2-3 champions identified + formally tasked
- [ ] Session 1 (product) + Session 2 (facilitation) both delivered
- [ ] Wave-2 schedule confirmed

At week 7-8 go-live:

- [ ] Per-role usage validated Day 3, 7, 14, 21, 30
- [ ] Adoption-baseline established

At week 9-12 stabilization:

- [ ] Retrospective conducted
- [ ] Partner-profile updated
- [ ] First QBR scheduled
- [ ] Implementation-team-to-PSM handoff complete

## Anti-patterns this file flags

- **Skipping pre-flight checks "we'll get to that later."** The implementation is the most-watched moment of the partner relationship. Surfacing problems post-go-live is far worse than catching them at discovery.
- **Treating implementation as "done" at go-live.** Go-live is week 7-8 of a 12-week arc. The 30-day-post-go-live measurement is what actually validates success.
- **Sub-contracting the failure-mode check to "the implementation team will handle it."** The PSM owns the relationship long-term; if the implementation team missed something, the PSM inherits the consequence.
- **One-and-done champion engagement.** Champion needs check-ins through the 90-day arc, not just at week 5-6 train-the-trainer.

## Refresh triggers

- A new high-profile EdTech implementation failure becomes public (the LAUSD/AllHere case shifted the CIO diligence bar; a future similar event may shift it further)
- A new compliance regime (state or federal) adds an implementation-time check
- A new technical integration pattern (new SSO model, new rostering version) creates new failure modes
- `/wrap` slash command surfaces a real-engagement failure pattern this file doesn't anticipate

## References

- [`rostering-data-quality-typology.md`](rostering-data-quality-typology.md) — failure-mode #4 deep dive
- [`sis-sso-rostering-integration-patterns.md`](sis-sso-rostering-integration-patterns.md) — failure-mode #1 + #5 technical reference
- [`parent-comms-jurisdictional-bear-traps.md`](parent-comms-jurisdictional-bear-traps.md) — failure-mode #7 regulatory framework
- [`k12-psm-operating-cadence.md`](k12-psm-operating-cadence.md) — failure-mode #2 calendar reference
- [`ai-in-edtech-2026.md`](ai-in-edtech-2026.md) — failure-mode #6 (LAUSD/AllHere) + COPPA overlay
- [`renewal-pricing-conversations-edtech.md`](renewal-pricing-conversations-edtech.md) — failure-mode #3 (superintendent turnover) data
- [`partner-health-score-drift.md`](partner-health-score-drift.md) — score-vs-reality discipline applies to implementation-time signals too
- [`../skills/implementation-90-day-arc.md`](../skills/implementation-90-day-arc.md) — the playbook this file serves
- [`../templates/implementation-90-day-plan.md`](../templates/implementation-90-day-plan.md) — the per-week checklist artifact
