---
scenario_id: 2026-06-05-scope-creep-no-change-control
contributed_at: 2026-06-05
plugin: project-management
product: delivery-predictive
product_version: "n/a"
scope: likely-general
tags: [scope-creep, change-control, baseline, requirements, predictive]
confidence: medium
reviewed: false
---

## Problem

A baselined predictive build was tracking 6 weeks behind by month four, but earned value showed the team was *productive* — they were just delivering a meaningfully larger system than the baseline described. Dozens of "small" enhancements had been accepted verbally by the team's leads during demos and corridor conversations, none logged, none costed. The sponsor believed the original scope was being delivered late; in fact a 20–30%-larger scope `[ESTIMATE]` was being delivered roughly on the original effort rate. The ask was to stop the bleed without halting the team.

## Context

- Track: predictive, approved scope + schedule + cost baseline, formal change control *on paper* but unused in practice.
- Constraint: the change-control process existed but was seen as bureaucratic, so requesters routed around it by asking developers directly; the developers, wanting to be helpful, absorbed the work. No change request had been raised in four months despite obvious scope growth.
- The baseline was real and approved — so every absorbed change was, by definition, an un-baselined deviation.

## Attempts

- Tried: reconstructed the *actual* delivered scope vs the baselined scope from the backlog and demo notes. Surfaced ~18 absorbed changes, of which ~5 were genuinely material. Outcome: quantified the gap — the project wasn't slow, it was silently bigger.
- Tried: ran each material change retroactively through the **Change-request decision tree** in [`../knowledge/pm-decision-trees.md`](../knowledge/pm-decision-trees.md). Two were within-contingency clarifications (logged, no baseline change), one was a must-have that needed a sponsor-funded baseline extension, two were deferrable to a later release. Outcome: converted invisible scope creep into explicit, dispositioned change requests.
- Tried (the move that worked): made the change path *lower friction than the back channel* — a one-page change request with a 48-hour SLA — and instituted a standing rule that **no scope enters via a demo conversation**; the team's answer to "can you also…" became "raise it and I'll get it dispositioned." Outcome: the absorption stopped because the sanctioned path was now easier than the workaround.

## Resolution

The root cause was not a missing process — it was a change-control process **more painful than the workaround**, so scope absorbed silently and the schedule took the blame for work no one had authorised. Re-baselining the genuinely-approved additions and making the change path frictionless converted a 6-week "delay" into an honest, sponsor-visible scope decision.

**Action for the next PM hitting this pattern:** when a baselined project is "behind" but earned value says the team is productive, **suspect silent scope absorption before you suspect slow delivery.** Reconcile delivered-vs-baselined scope, run each delta through the Change-request tree, and — critically — make the sanctioned change path *easier* than the back channel, or the absorption resumes the moment you look away. Scope absorbed with no change request is a defect, not helpfulness (`../best-practices/scope-absorption-is-a-defect.md`); the baseline is what makes the absorption visible (`../best-practices/baseline-before-you-change-control.md`).

**Sources for framings cited:** integrated change control against an approved baseline is the standard PMBOK framing (Perform Integrated Change Control); the Change-request tree in this plugin is built on it. No external numbers are load-bearing here — the scope-growth figure is illustrative for this scenario and must be reconstructed from the project's own backlog and baseline before any deliverable.
