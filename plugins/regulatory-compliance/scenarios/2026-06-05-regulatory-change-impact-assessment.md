---
scenario_id: 2026-06-05-regulatory-change-impact-assessment
contributed_at: 2026-06-05
plugin: regulatory-compliance
product: regulatory-change
product_version: "n/a"
scope: likely-general
tags: [regulatory-change, horizon-scanning, gap-analysis, applicability, policy]
confidence: medium
reviewed: false
---

## Problem

A compliance team received a stream of regulatory-change alerts from a subscription feed and was treating every alert as an action item — opening a policy-revision task for each. The result was a 40-item change backlog, most of which did not actually apply to the firm's licences or activities, while two changes that *did* materially apply were buried and under-resourced. The team had skipped the **applicability** step: deciding *whether* a change touches the firm before deciding *what to do* about it. `policy-and-procedure-writer` was asked to triage the backlog and stand up a repeatable change-management workflow.

## Context

- Sector: multi-licence financial-services group (so a single change could hit one licence and not another — applicability is per-licence, not firm-wide).
- Constraint: the feed was jurisdiction-broad; many alerts were for regulators/regimes the firm wasn't subject to, or for activities it didn't conduct. Volume was the symptom; missing applicability triage was the cause.
- The team confused "we were notified of a change" with "this change requires us to act." Those are separated by an applicability assessment.

## Attempts

- Tried: open a policy task per alert. Outcome: rejected — this is the backlog-generating behavior, not the fix. It also inverts effort: noise gets the same attention as the two material changes.
- Tried: grounded the workflow shape against the standard regulatory-change-management / horizon-scanning practice rather than inventing one. The widely-described pattern is a **three-stage funnel**: (1) **monitor / horizon-scan** — capture the change; (2) **identify / applicability** — does this change touch *this* firm's licences, activities, or jurisdictions; (3) **impact assessment** — for the changes that pass applicability, evaluate the direct and indirect effect, map to the affected internal policies/controls, and build a dated, owned action plan. Only stage-3 survivors become policy-revision tasks. Outcome: the funnel turned 40 alerts into 2 material change projects + a documented "not-applicable, here's why" record for the rest.
- Tried (the move that worked): for each applicable change, ran a **gap analysis** against the current policy/control set (the `policy-trigger-a-gap-analysis-on-every-regulatory-change` best practice + the [`../skills/regulatory-mapping/SKILL.md`](../skills/regulatory-mapping/SKILL.md) control-to-citation mapping), producing a delta — what the policy says today vs. what the change requires — with an owner and a target date per gap (CLAUDE.md §3 #5: remediation has a date and an owner). Outcome: two scoped, owned, dated change projects instead of a 40-item undifferentiated backlog.

## Resolution

The error was skipping applicability — treating *notification* as *obligation*. The fix is a three-stage funnel (monitor → applicability → impact assessment) where only changes that pass per-licence applicability become impact assessments, and only impact assessments produce dated, owned gap-remediation tasks. The "not applicable" decisions are documented too — at the next exam, "we assessed this change and it doesn't apply because…" is a defensible record; silence is not.

**Action for the next analyst hitting this pattern:** don't open a task per alert. Run each change through applicability **first** (which licence / activity / jurisdiction does it touch — and name the citation that makes it applicable, CLAUDE.md §3 #1), then impact-assess only the survivors, then gap-analyze each against current policy with an owner + date per gap. Document the not-applicable decisions as deliberately as the applicable ones. Jurisdiction is load-bearing: the same headline change can apply under one regulator and not another (CLAUDE.md §3 #12). This is compliance analysis; a genuinely ambiguous applicability call (e.g. whether a new perimeter rule captures the firm's activity) can need counsel.

**Sources (retrieved 2026-06-05):**
- Empowered Systems — What is Regulatory Horizon Scanning: https://empoweredsystems.com/blog/what-is-regulatory-horizon-scanning/
- SafetyCulture — Regulatory Change Management for Compliance: https://safetyculture.com/topics/compliance-management/regulatory-change-management

These are practitioner/GRC-vendor framing sources for the *workflow shape*, not the substance of any specific regulation. The applicability and impact of any actual regulatory change is `[verify-at-use]` against the regulator's primary source and the firm's specific licences before any deliverable.
