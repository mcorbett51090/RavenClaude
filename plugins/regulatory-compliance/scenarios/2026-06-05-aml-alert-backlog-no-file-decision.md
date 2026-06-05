---
scenario_id: 2026-06-05-aml-alert-backlog-no-file-decision
contributed_at: 2026-06-05
plugin: regulatory-compliance
product: aml-kyc
product_version: "n/a"
scope: likely-general
tags: [aml, alert-backlog, sar, no-file, structuring, fincen]
confidence: medium
reviewed: false
---

## Problem

A mid-size institution's transaction-monitoring queue had a 1,400-alert backlog, the oldest alert ~70 days from generation. The MLRO team was treating "clear the backlog" as the goal and was about to bulk-disposition the aged alerts as "no further action" to make the number go down. Two coupled risks: (1) a genuinely reportable pattern buried in the aged alerts could blow the SAR filing clock, and (2) bulk auto-clearing with a one-word disposition is exactly the "looks fine" anti-pattern the team flags (CLAUDE.md §4) — it produces an indefensible audit trail at the next exam. `aml-kyc-analyst` was asked to triage, not to rubber-stamp the cleardown.

## Context

- Sector: deposit-taking institution with a US BSA nexus (so FinCEN SAR rules are the reporting anchor here — but the same shape recurs in any STR regime; the *numbers* differ by jurisdiction).
- Constraint: the backlog had mixed alert types — some were threshold/value alerts, some were behavioral (velocity, sub-threshold patterning). They could not be dispositioned with one rule.
- The team conflated "operational throughput" (clear the queue) with "reporting obligation" (did any of these require a SAR/STR, and is the clock still met). Those are different problems and the second one gates the first.

## Attempts

- Tried: triage by age only (oldest first). Outcome: rejected — age is an *operational* priority signal, not a *risk* one. A fresh alert can be the reportable one; an old alert can be noise. Age sorts the queue, it does not decide reportability.
- Tried: grounded the two volatile facts that gate the decision against the regulator's primary source rather than memory. (a) Under the FinCEN SAR rules a SAR is generally due **no later than 30 calendar days** after initial detection of facts that may form a basis for filing; if no suspect is identified at detection, an institution may take an **additional 30 days (60 total)** to identify a suspect, but no longer. (b) For *continuing* activity, FinCEN's guidance contemplates filing the initial SAR, then a **90-day review** of whether the activity continues, then filing a continuing SAR within **30 days** of the end of that period — i.e. a Day-0 / Day-30 / Day-120 / Day-150 cadence. **October 2025 FinCEN FAQs** clarified institutions need not run a *separate* manual review solely to check for continuation and may rely on risk-based monitoring. All of these are `[verify-at-use]` and **US-specific** — a non-US STR regime has its own clock. Outcome: grounded the clock that decides whether the backlog is merely a productivity problem or a missed-deadline problem.
- Tried (the move that worked): split the backlog into a **suspicion-bearing lane** (any alert where an analyst can name a typology) and a **non-suspicion lane**, then ran the suspicion lane against the reportability decision tree ([`../knowledge/compliance-decision-trees.md`](../knowledge/compliance-decision-trees.md)) *first* — because that lane is the one with a clock. Any sub-threshold-patterning alert was checked for **structuring** before it could be auto-cleared. Each no-file decision in the non-suspicion lane got a documented rationale (the `aml-document-the-no-file-decision` best practice), not a one-word disposition. Outcome: a defensible cleardown with the reportable items pulled out and clock-checked.

## Resolution

The error was treating an *operational* metric (queue depth) as the objective when the binding constraint was a *reporting* obligation with a statutory clock. Sorting by age would have cleared a reportable alert into "no action" and missed the 30/60-day window. The fix: split suspicion-bearing from non-suspicion alerts, run the suspicion lane through the reportability tree first, document every no-file decision, and treat "clear the backlog" as the *output* of correct disposition, not the goal.

**Action for the next analyst hitting this pattern:** never bulk-clear an aged AML queue. Confirm the **filing clock for the actual reporting regime** (the FinCEN 30/60-day and continuing-activity 90/30 cadence above is US-specific and `[verify-at-use]`), pull any suspicion-bearing or structuring-shaped alert into a separate lane and run it through the reportability tree before disposition, and document the *why* on every no-file (CLAUDE.md §4 — a one-word "OK" is not a disposition). SAR/STR drafts and any customer-level content route to `ravenclaude-core` `security-reviewer` and never leave the working directory unencrypted (CLAUDE.md §2). This is compliance analysis, not legal advice — whether to file in a genuinely ambiguous case can need counsel.

**Sources (retrieved 2026-06-05):**
- FinCEN — Frequently Asked Questions Regarding the FinCEN Suspicious Activity Report (SAR): https://www.fincen.gov/resources/frequently-asked-questions-regarding-fincen-suspicious-activity-report-sar
- FinCEN — SAR FAQs (October 2025): https://www.fincen.gov/system/files/2025-10/SAR-FAQs-October-2025.pdf

These describe the **US** SAR regime; STR clocks and structuring rules vary by jurisdiction. Every timeline is `[verify-at-use]` against the current FinCEN rule (or the applicable non-US regulator) and the firm's actual obligations before any deliverable.
