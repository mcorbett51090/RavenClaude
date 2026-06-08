---
scenario_id: 2026-06-08-referrals-stalled-on-access-time
contributed_at: 2026-06-08
plugin: behavioral-health-practice
product: access
product_version: "n/a"
scope: likely-general
tags: [access-time, conversion, intake, marketing]
confidence: medium
reviewed: false
---

## Problem

A clinic was about to increase marketing spend because referrals 'weren't turning into patients.' The risk: pouring more referrals into a slow intake wastes spend — access time (first contact to first kept appointment) is the conversion lever, and a long access time loses referrals regardless of volume (§3 #2).

## Context

- Setting: group practice taking external referrals.
- Constraint: intake-to-first-appointment access time is the strongest predictor of conversion and retention (§3 #2).
- The clinic reasoned from referral count, not access time.

## Attempts

- Tried: **measured access time by referral source** before spending. Outcome: median intake-to-first-appointment ran ~three weeks, far past the point most referrals go cold.
- Tried: **mapped where the delay sat.** Outcome: scheduling capacity at intake, not paperwork — a caseload-staffing gap (route to caseload, §3 #4).
- Tried: **modeled the conversion lift from a shorter access window** instead of more referrals (§3 #2). Outcome: shortening access beat adding volume on expected conversions.

## Resolution

The fix was to **shorten access time by adding intake scheduling capacity — before increasing marketing**. The output was the access-time read by source, the located delay, and the conversion case for fixing access first, with no PHI in the deliverable.

**Action for the next consultant hitting this pattern:** **measure access time before buying more referrals.** A slow intake loses referrals no matter how many arrive; shorten intake-to-first-appointment first. See Tree 2 and the `shorten-access-time` skill.

Benchmark figures are segment-/region-/date-dependent — treat as `[unverified — training knowledge]` and validate against the client's own data before any deliverable (§3 #8).
