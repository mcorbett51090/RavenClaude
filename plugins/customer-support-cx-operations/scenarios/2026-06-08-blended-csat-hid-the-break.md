---
scenario_id: 2026-06-08-blended-csat-hid-the-break
contributed_at: 2026-06-08
plugin: customer-support-cx-operations
product: csat
product_version: "n/a"
scope: likely-general
tags: [csat, segmentation, fcr, quality]
confidence: medium
reviewed: false
---

## Problem

A CX manager reported steady blended CSAT while escalations quietly churned customers. The risk: a blended satisfaction score averages a delighted self-service cohort with a furious escalation cohort, hiding both — and the FCR signal underneath it (§3 #3 #4).

## Context

- Channel: omnichannel with a specialist escalation tier.
- Constraint: CSAT/NPS must be read segmented by channel/tier/issue, and FCR is the master metric (§3 #3 #4).
- Leadership reasoned from the single blended number.

## Attempts

- Tried: **segmented CSAT by channel/tier/issue** (§3 #3). Outcome: self-service CSAT was high and rising while escalation-tier CSAT had collapsed — the blend hid both.
- Tried: **tied the drop to FCR** (§3 #4). Outcome: escalation FCR had fallen and reopens had risen — customers were paying for multiple contacts.
- Tried: **checked QA sample size** on the escalation tier (§3 #6). Outcome: the sample had been too small to catch the quality slide earlier.

## Resolution

The fix was a **tier-specific FCR and QA intervention on escalations**, plus a permanent segmented CSAT view — not a blended dashboard. The output was the segmented CSAT read, the FCR link, and a resized QA sample.

**Action for the next consultant hitting this pattern:** **read CSAT segmented and tie it to FCR.** A blended score is the most reassuring and least informative number; segment by channel/tier/issue and watch FCR/reopens, with a QA sample large enough to detect the slide. See Tree 3 and the `read-satisfaction` skill.

Benchmark figures are segment-/region-/date-dependent — treat as `[unverified — training knowledge]` and validate against the client's own data before any deliverable (§3 #8).
