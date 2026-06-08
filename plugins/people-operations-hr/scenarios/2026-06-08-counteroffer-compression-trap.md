---
scenario_id: 2026-06-08-counteroffer-compression-trap
contributed_at: 2026-06-08
plugin: people-operations-hr
product: compensation
product_version: "n/a"
scope: likely-general
tags: [compensation, comp-bands, counteroffer, compression, compa-ratio]
confidence: medium
reviewed: false
---

## Problem

A key engineer resigned with a competing offer and the hiring manager wanted to counter above the top of the band "to keep them." The risk: a one-off raise above the band keeps one person but drags every tenured peer's relative position down, creates a precedent the budget can't fund, and sets the next counteroffer's floor — fixing one exit by manufacturing inequity for five who stayed (§3 #2).

## Context

- Scope: a single engineering level inside a defined band (min/mid/max).
- Constraint: comp is a *band* problem, not a negotiation; the counteroffer would push the person well past the band max (compa-ratio > 1.3), green-circling them and compressing peers at midpoint (§3 #2).
- The manager reasoned from the competing offer, not from the band or the market data behind it.

## Attempts

- Tried: **scored the band before reacting** (`people_calc.py comp-band`). Outcome: the band midpoint was below current market on a *dated* survey — the real issue was a stale band, not this one person.
- Tried: **modeled the compression cost** of the above-band counter across the tenured peers at that level. Outcome: keeping one person at compa-ratio 1.3 implied either re-leveling five peers (a large unbudgeted spend) or accepting visible inequity that would surface in the next engagement survey.
- Tried: **re-anchored the band to the current dated survey** and placed the departing engineer within the corrected band. Outcome: a defensible offer that was competitive *and* held the structure — and a band correction that benefited the peers too.

## Resolution

The fix was a **band correction to current market**, not an above-band one-off — the departing engineer got a defensible in-band offer, and the peers were re-anchored in the same cycle. The output was a corrected band (midpoint/spread, dated survey cited), the compa-ratio distribution before/after, and the compression cost the one-off would have created.

**Action for the next consultant hitting this pattern:** **pay to the band, and if the band is wrong, fix the band — never the counteroffer.** Score compa-ratio and range penetration first; a counteroffer above band is a precedent and a compression bill, not a retention strategy. See [`../knowledge/people-ops-economics.md`](../knowledge/people-ops-economics.md) §3 and the [`../scripts/people_calc.py`](../scripts/people_calc.py) `comp-band` mode.

Market comp figures are survey-/date-/geography-dependent — treat as `[unverified — training knowledge]` and cite the dated survey before any deliverable (§3 #8).
