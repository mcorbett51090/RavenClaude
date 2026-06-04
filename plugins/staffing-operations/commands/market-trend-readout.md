---
description: "Produce a defensible staffing market-trend readout — segment-resolved, SIA-anchored, triangulated across primary sources, with the inflection named (not just the level) and soft numbers marked, then connected to what it means for the client's book."
argument-hint: "[scope, e.g. '2026 read for healthcare + education staffing']"
---

# Build a market-trend readout

You are running `/staffing-operations:market-trend-readout` for `$ARGUMENTS`. Build it the way the `workforce-market-analyst` does — an operator who lives the market will argue with a sloppy one.

## Steps
1. **Resolve to segments** — "healthcare staffing is down" is false for locums. Read each separately ([`../knowledge/staffing-market-trends-2026.md`](../knowledge/staffing-market-trends-2026.md)).
2. **Anchor sizing to SIA**; footnote broad-TAM houses separately.
3. **Triangulate every claim** — a press release is not a trend; corroborate with a SEC filing where possible (AMN FY2025 −8%; Cross Country Nurse & Allied −25%).
4. **Name the inflection** — "−9% YoY but +6% sequential" beats "−9%" alone.
5. **Connect to the client's book** — each trend → a posture (defend / invest / watch).
6. **Mark soft numbers + verification gaps** and **date everything** (§3 #9).

## Output
Fill [`../templates/market-trend-readout.md`](../templates/market-trend-readout.md).

## Guardrails
- SIA editorial/BLS/Becker's often 403 to automated fetch — figures extracted that way are `[unverified]` until re-opened; say which primary source closes each gap.
- The 2021–22 travel-nurse spike is the cautionary tale: a rate or size with no date can be off 30%+.
