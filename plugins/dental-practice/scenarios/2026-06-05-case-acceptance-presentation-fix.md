---
scenario_id: 2026-06-05-case-acceptance-presentation-fix
contributed_at: 2026-06-05
plugin: dental-practice
product: case-acceptance
product_version: "n/a"
scope: likely-general
tags: [case-acceptance, treatment-presentation, sequencing, financial-options, conversion]
confidence: medium
reviewed: false
---

## Problem

A two-doctor general practice diagnosed plenty of needed treatment but watched large plans walk out the door undone. The owner's instinct was that fees were "too high for the area" and pushed to discount the big cases. But diagnosed-treatment dollars far exceeded scheduled-treatment dollars — the practice was producing a diagnosis it could not convert. The leak was case acceptance, and the reflex (discount) attacks the wrong cause.

## Context

- Segment: general-practice, independent, 2 doctors, mixed PPO/FFS.
- Constraint: treatment was presented as a clinical fact ("you need a crown, an implant, and two fillings — that's $X") at the end of a long appointment, with no sequencing and a single take-it-or-leave-it number. No financial options were offered until the patient flinched.
- The owner was reasoning from "price is the objection" without measuring acceptance by plan size — small plans closed fine; only the large, multi-visit plans stalled.

## Attempts

- Tried: measured **case acceptance by plan size and by treatment type** before changing anything. Found small/basic plans converting near the high end but large restorative plans converting far lower — consistent with the trade pattern that preventive care accepts at ~80–90%+ while implants / full-mouth / ortho land closer to ~60–70% [verify-at-use]. Outcome: confirmed the problem was concentrated in big plans, not a blanket fee problem — reframed away from discounting.
- Tried: re-sequenced the large plans into **phased, prioritized treatment** (urgent/health-first phase, then restorative, then elective) so the patient said yes to a starting step instead of choking on a lump sum, and moved the financial conversation **up front** with concrete payment/financing options rather than surfacing it only after sticker shock. Outcome: more plans started; partial acceptance beat the prior all-or-nothing zero.
- Tried: standardized the **presentation itself** — same-day verbal + written plan, benefit-framed ("here's what this protects / restores"), and a defined follow-up on unscheduled treatment. Outcome: reduced doctor-to-doctor variation in how the same plan was pitched.

## Resolution

The fix was **presentation and sequencing, not price** (CLAUDE.md §3 #3). Phasing large plans, moving financial options up front, and standardizing the presentation lifted acceptance on the cases that were actually leaking, without across-the-board discounting that would have eroded margin. The national average case-acceptance rate sits around 50–60% with healthy practices targeting 65–85% [verify-at-use] — the gap was a communication problem, not a demand or price problem.

**Action for the next consultant hitting this pattern:** before discounting to "close" big cases, **measure acceptance by plan size and treatment type.** If small plans close and large ones stall, the lever is sequencing + up-front financial options + a standardized presentation, not a lower fee. Run [`../skills/lift-case-acceptance/SKILL.md`](../skills/lift-case-acceptance/SKILL.md) and route the sequencing call to [`clinical-treatment-planner`](../agents/clinical-treatment-planner.md) (decision-support for the licensed dentist, never an order — §2).

**Sources (retrieved 2026-06-05):**
- Dentx — Dental Case Acceptance Benchmarks (50–60% average; type-level acceptance): https://dentx.ca/blog/dental-case-acceptance-benchmarks/
- Veritas Dental Resources — Case Acceptance: What's Normal, What's Ideal: https://veritasdentalresources.com/post/case-acceptance-in-dentistry-whats-normal-whats-ideal-and-how-to-improve-it
- Teero — 8 Proven Strategies to Improve Dental Case Acceptance Rates: https://www.teero.com/blog/dental-case-acceptance

Acceptance benchmarks are trade-source rules-of-thumb, not hard rules — treat as `[verify-at-use]` and calibrate to the practice's segment, case mix, and patient base (§3 #8).
