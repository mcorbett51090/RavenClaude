---
description: "Turn reviews and survey verbatims into a ranked comment-to-action list mapping complaints to operational fixes, plus a service-recovery playbook."
argument-hint: "[review/verbatim source + current review score / NPS + the complaint themes or raw text]"
---

You are running `/hospitality-hotel-operations:triage-reviews`. Use `guest-experience-analyst` + the `guest-experience-and-reputation` skill.

## Steps
1. Code the reviews/verbatims into themes + sentiment + frequency. State the current review-score / NPS / GSS baseline and the trend.
2. Map each recurring theme to its operational root cause (an SOP, a maintenance loop, a staffing gap). Mark genuine one-offs separately — respond + recover, don't change the SOP.
3. Rank the comment-to-action list by frequency × score/repeat-rate impact (a rare high-impact defect can outrank a frequent minor one). Assign an owner/handoff to each — operational fixes route to `hotel-operations-lead`.
4. Design or refine the service-recovery playbook: acknowledge → own → fix → follow-up, with comp-authority tiers by severity and the recovery-to-loyalty save path.
5. Define the loyalty/repeat measurement (repeat rate / direct share / CLV, never member count) and the re-measure checkpoint that closes the loop.
6. Route handoffs: the operational fix → hotel-operations-lead, the repeat-value framing → revenue-manager, the dashboard → data-platform, significance tests → applied-statistics.
7. Emit the ranked action list + the playbook + the Structured Output block (with `KPI impact:` and `Handoff to neighbours:`).
