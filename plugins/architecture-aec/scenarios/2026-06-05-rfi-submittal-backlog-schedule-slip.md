---
scenario_id: 2026-06-05-rfi-submittal-backlog-schedule-slip
contributed_at: 2026-06-05
plugin: architecture-aec
product: construction-documents
product_version: "n/a"
scope: likely-general
tags: [rfi, submittal, turnaround, schedule, coordination, ca]
confidence: medium
reviewed: false
---

## Problem

A mid-size commercial project hit construction administration with an RFI and submittal backlog: the contractor was claiming the design team's slow RFI responses were delaying the schedule (and teeing up a delay claim), while the architect's team felt buried in a flood of RFIs that should never have been asked. Both "we're too slow" and "they're asking too much" were being asserted with no data. The firm wanted to know whether this was a staffing problem on their side, a document-quality problem, or a contractor-tactics problem — before negotiating the delay claim.

## Context

- Segment: commercial, ~$30M [ESTIMATE] construction value, design-bid-build, architect under direct owner contract providing CA.
- Constraint: under most standard contracts (AIA, ConsensusDocs) the RFI response window is **7-14 calendar days** [verify-at-use]; the contractor's schedule narrative assumed near-instant turnaround and counted every day past day 3 as "architect delay."
- No single issue log — RFIs lived in the contractor's PM platform, submittals in a spreadsheet, and the coordination history in email. Nobody could see the pattern in one place.

## Attempts

- Tried: pulled the actual RFI turnaround distribution before arguing the claim. Measured median response days against the contract window, not against the contractor's "day 3" expectation. Found the team's median was **inside the contractual 7-14 day window** but a handful of structural/code-interpretation RFIs had stretched past it — consistent with the industry reality that ~30% of RFIs are simple clarifications answered fast while the complex 70% (structural, code, owner-decision) run a week to months [verify-at-use]. Outcome: separated the genuine slow responses (a few, defensible) from the contractor's inflated narrative (most).
- Tried: classified the RFI corpus by root cause — clarification vs. genuine document gap vs. contractor-convenience vs. substitution. A high share traced to a few under-coordinated detail areas (the §3 #3 coordination signal), not to a staffing shortfall. Outcome: identified that fixing ~5 detail conditions would have prevented a disproportionate share of the RFIs.
- Tried (the move that worked): stood up a single RFI + change-order issue log (one place, every entry — the §3 #3 discipline), tracked turnaround against the contract window weekly, and triaged incoming RFIs so simple clarifications were answered in 48h while complex ones got a dated "response expected by" commitment. Each RFI cost the firm meaningful review time — reviewing/responding to an RFI runs an industry-cited average of **~$1,080 each** [verify-at-use] — so cutting the avoidable ones was real money, not just schedule.

## Resolution

The schedule narrative was mostly a **measurement-baseline dispute** (contractor measuring against day-3, contract saying 7-14) plus a **small real coordination tail**. With the turnaround data and a single issue log, the firm defended the delay claim down to the few genuinely-late responses, fixed the under-coordinated details for the next bid package, and set up a CA cadence that kept turnaround inside the window for the rest of the job.

**Action for the next consultant hitting this pattern:** before conceding (or fighting) a delay claim, **measure RFI turnaround against the contract window, not the contractor's expectation**, and classify the RFI corpus by root cause. A backlog is usually part baseline-dispute, part a small coordination tail — both are addressable, neither is "we're just slow." Stand up one issue log for RFIs + change orders (§3 #3), triage simple-vs-complex, and feed the coordination tail back into the next set. See [`../knowledge/aec-decision-trees.md`](../knowledge/aec-decision-trees.md) and the [`../skills/read-rfi-pattern/SKILL.md`](../skills/read-rfi-pattern/SKILL.md) playbook.

**Sources (retrieved 2026-06-05):**
- SubmittalLink — *RFI Best Practices* (response windows, regional turnaround averages): https://www.submittallink.com/post/rfi-best-practices
- Layer App — *The Complete Guide to RFIs in Construction Administration* (~$1,080/RFI, response-time distribution): https://layer.team/blog/the-complete-guide-to-rfis-in-construction-administration

Turnaround figures and per-RFI cost are industry rules-of-thumb, not hard rules — treat as `[verify-at-use]` and validate against the project's actual contract window and the firm's real review cost (§3 #8).
