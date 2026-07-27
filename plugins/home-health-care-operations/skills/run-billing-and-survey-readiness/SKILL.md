---
name: run-billing-and-survey-readiness
description: "Turn home-health documentation into paid, survey-proof claims by traversing the home-health decision tree (documentation completeness: OASIS / plan of care / visit notes → PDGM 30-day period billing: NOA + final claim, LUPA watch, comorbidity → Medicaid-waiver / private-pay per-unit billing → denial root-cause analysis → conditions-of-participation & survey-readiness checks), then return the completeness gate, the period claim, the denial fixes, and the CoP/survey-readiness gap list. Reach for this when the user asks 'bill this 30-day period', 'why are our claims denied?', 'is our documentation complete?', or 'would our charts pass a survey?'. Used by home-care-operations-specialist (primary) and home-health-agency-lead."
---

# Skill: run-billing-and-survey-readiness

> **Invoked by:** `home-care-operations-specialist` (primary — the documentation-to-claim run and the survey-readiness pass) and `home-health-agency-lead` (the CoP/survey posture and the PDGM billing implications of the payer mix).
>
> **When to invoke:** "bill this 30-day period"; "why are our claims being denied?"; "is our documentation complete enough to bill?"; "check our LUPA risk"; "would our charts pass a survey?"; "map our gaps against the Conditions of Participation"; any "get paid and pass survey" question.
>
> **Output:** the documentation-completeness gate + the PDGM 30-day period claim (or the Medicaid-waiver/private-pay claim) + the denial root-cause analysis & fix + the CoP/survey-readiness gap list — with the audit trail that survives review.

## Procedure

1. **Gate billing on documentation completeness — the documentation is the claim.** Before any claim, confirm the record is complete and defensible: the **OASIS** assessment (accurate — it drives the PDGM case mix and the quality outcomes), the **physician-ordered plan of care** (signed, followed, updated), and the **visit notes** (skilled content, timely, matching the ordered frequency). Incomplete or late documentation is a denial and a citation — the completeness check is a **precondition** to billing, not a cleanup after.
2. **Bill the PDGM 30-day period deliberately.** Traverse the billing branch in [`../../knowledge/home-health-care-decision-tree.md`](../../knowledge/home-health-care-decision-tree.md). Under **PDGM** the **30-day period** is paid on **clinical grouping, functional impairment level, admission source (community vs institutional), and timing (early vs late)** — not visit count. Submit the **NOA (Notice of Admission)** on time (late NOA = payment reduction), then the **final period claim**. Watch the **LUPA** threshold (too few visits flips the period to per-visit payment) and apply **comorbidity adjustments**. _(PDGM rates, weights, and NOA timing are volatile — retrieval date.)_
3. **Bill the non-Medicare paths against the authorization.** **Medicaid waiver / MCO** — bill the **authorized units** per service type, with the **EVV** verification attached (no EVV, no payment). **Private pay / LTC insurance** — invoice the agreed hours/rate, per the agreement. Confirm each claim matches the authorization and the verified visits before submission.
4. **Work denials by root cause, not one-off appeals.** Group denials by source — **eligibility** (homebound/skilled-need), **order/certification** (missing/late signature, face-to-face), **documentation** (incomplete/late notes, OASIS errors), **EVV** (unverified/mismatched visits), **timing** (late NOA), or **authorization** (units exceeded). Fix the **source** so the denial doesn't recur; a rising denial rate in one bucket is a process defect, not a billing-clerk problem.
5. **Run the survey-readiness pass against the Conditions of Participation.** Check the operational record against the **CoP** the way a surveyor would: **QAPI** program active, **patient rights** honored, **plan-of-care and physician-order compliance**, **OASIS accuracy**, **EVV completeness**, **visit-note timeliness**, **competency/supervision** records, **infection control**, and **complaint handling**. Produce the **gap list** — the specific things a surveyor would cite — with the remediation for each. _(CoP interpretive guidance is volatile — retrieval date.)_
6. **Make survey readiness a daily habit, not a scramble.** The same completeness and CoP checks that gate billing are the ones a survey tests — run them continuously (the chart clean every day never needs a pre-survey cram). Tie the readiness pass to the billing run so the two reinforce each other.
7. **State the payment/survey-risk conditions** — the 1-2 facts that would deny payment or trigger a citation (e.g., "the NOA is late → automatic payment reduction for the period → tighten the NOA-submission SLA"; "OASIS coding doesn't match the visit documentation → case-mix and audit risk → reconcile before billing").

## Worked example

> User: "We've got a 30-day PDGM period to bill and our denial rate is climbing. Bill it and tell me what's wrong."

- **Completeness gate:** OASIS complete and internally consistent, plan of care signed, visit notes timely — one visit note is late → hold and correct before billing (a would-be denial caught pre-submission).
- **PDGM period:** community admission, medication-management clinical group, medium functional level, early period; **NOA** submitted on time; visit count is above the **LUPA** threshold → full period payment (not per-visit); comorbidity adjustment applied.
- **Denial root cause:** the climbing denials cluster in the **EVV** bucket — visits delivered but not verified/mismatched → fix the source (the same-day EVV exception procedure), not the appeals.
- **Survey readiness:** CoP pass finds a **supervision-visit documentation** gap (aide supervisory visits not consistently recorded) → remediate now, before it's a citation.
- **Condition:** if NOA submissions keep slipping late, the automatic payment reduction compounds → set and monitor an NOA-submission SLA.

## Guardrails

- **Documentation is the reimbursement** — gate billing on OASIS/plan-of-care/visit-note completeness; if it isn't charted, it wasn't done and it won't be paid.
- **PDGM is not visit-count billing** — the 30-day period pays on clinical group, function, admission source, and timing; watch the **LUPA** threshold and submit the **NOA** on time (late NOA reduces payment).
- **Medicaid/waiver claims need the EVV attached** — no verification, no payment.
- **Work denials by root cause** (eligibility, order, documentation, EVV, timing, authorization) — fix the source so it doesn't recur.
- **Survey readiness is a daily habit, not a scramble** — run the CoP checks continuously and tie them to the billing run.
- Running the claim and the readiness pass is **execution** (the operations specialist); the **CoP posture and quality/VBP strategy** are **policy** (the `home-health-agency-lead`) — keep the seam clean; deep survey-remediation program design → `regulatory-compliance`.
- This is **not** hospital/physician-group RCM — that's `medical-revenue-cycle`; this plugin owns the **home-health agency's** billing and survey record.
- PDGM rates/weights, NOA timing, OASIS versions, and CoP interpretive guidance are **volatile** — carry a **retrieval date** and re-verify before billing or a survey. See [`../../knowledge/home-health-care-patterns-2026.md`](../../knowledge/home-health-care-patterns-2026.md). **Not medical, legal, or reimbursement advice.**
