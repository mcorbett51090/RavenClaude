---
scenario_id: 2026-06-05-irb-submission-gaps
contributed_at: 2026-06-05
plugin: clinical-trials
product: regulatory-submission
product_version: "n/a"
scope: likely-general
tags: [irb, ind, informed-consent, submission-readiness, clinical-hold]
confidence: medium
reviewed: false
---

## Problem

A first-in-human sponsor wanted to begin screening "as soon as we file." Their start-up plan compressed the IND submission, IRB approval, and the first screening visit into nearly the same week. Two structural misunderstandings drove the plan: (a) they treated the IND as a green light on submission, and (b) they were assembling the informed-consent and IRB package as a final-month task. The ask was a submission-readiness read before the plan locked — as decision-support, not a regulatory determination (CLAUDE.md §2).

## Context

- Segment: Phase I, first-in-human, single sponsor-investigator at start-up.
- Constraint: the submission is built **throughout**, not at the end (CLAUDE.md §3 #7), and two hard regulatory facts gate the timeline: after an IND is submitted the sponsor must **wait 30 calendar days** before initiating the trial (the FDA review window), and during that hold **study-specific activities — advertising, eligibility screening, and seeking informed consent — are prohibited** [verify-at-use]. The compressed plan violated both.
- The plugin is not an IRB, not a regulatory authority, and makes no approvability determination — it inventoried the package and flagged the gaps for the sponsor's regulatory lead (CLAUDE.md §2). Anything touching PHI routes to `ravenclaude-core` `security-reviewer`.

## Attempts

- Tried: grounded the two timeline anchors rather than asserting from memory — confirmed the **30-day IND review window** and the **prohibition on advertising/screening/consent during the hold** against current FDA framing before touching the schedule (volatile regulatory facts → date + `[verify-at-use]`, CLAUDE.md §3 #8). Outcome: the "screen the week we file" plan was off the table on a hard rule, not an opinion.
- Tried: inventoried the **submission package** against the IND content areas (nonclinical pharm/tox, CMC manufacturing, and the clinical protocol) plus the IRB requirements (protocol, informed-consent document, investigator commitments). Found the gating gap was the **informed-consent document and the IRB package**, assembled last — and incomplete-consent documentation is a recurring deviation and inspection finding downstream, so a weak consent process is a cost that compounds. Outcome: a prioritized gap list with the consent/IRB package as the critical path.
- Tried (the move that worked): re-sequenced start-up so the **IRB submission and the consent document run in parallel with the IND wait**, not after approval — using the 30-day window productively for everything *except* the prohibited activities (advertising, screening, consent-seeking). Built a submission-readiness checklist tracked throughout, so the filing wasn't a final-month scramble. Outcome: a realistic start-up timeline that respected the hold and put the long-pole consent/IRB work on the critical path early.

## Resolution

The plan failed on two structural points: the IND is a 30-day **wait**, not a green light, and screening/advertising/consent are **prohibited during the hold** — so the "file and screen" compression was impossible. And the consent/IRB package, treated as a final-month task, was the real critical path. The fix sequenced the IRB + consent work into the IND wait window and tracked submission readiness throughout.

**Action for the next consultant hitting this pattern:** confirm the **30-day IND review window** and the **screening/advertising/consent prohibition during the hold** (`[verify-at-use]` — confirm against current FDA guidance and the sponsor's regulatory counsel). Inventory the submission package early and put the **informed-consent document + IRB package** on the critical path — they are the usual long pole and a weak consent process compounds into deviations later (CLAUDE.md §3 #7). Frame as decision-support; this plugin is not an IRB or regulatory authority (CLAUDE.md §2). Cross-reference [`../skills/read-submission-readiness/SKILL.md`](../skills/read-submission-readiness/SKILL.md).

**Sources (retrieved 2026-06-05):**
- FDA — *Investigational New Drug (IND) Application* (30-day window, content areas): https://www.fda.gov/drugs/types-applications/investigational-new-drug-ind-application
- Advarra — *How the IND 30-day Hold Impacts Clinical Trial Activities* (prohibited activities during hold): https://www.advarra.com/blog/how-the-ind-30-day-hold-impacts-clinical-trial-activities/
- UCSF HRPP — *Investigational New Drugs and Biologics* (IRB + IND interaction): https://irb.ucsf.edu/investigational-new-drugs-and-biologics

IND/IRB timing rules are volatile and jurisdiction-specific — every figure carries a retrieval date and a `[verify-at-use]`; confirm against current FDA guidance and the sponsor's regulatory counsel before any deliverable (CLAUDE.md §3 #8).
