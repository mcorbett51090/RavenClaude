---
scenario_id: 2026-06-08-pullthrough-drop-was-a-cycle-bottleneck
contributed_at: 2026-06-08
plugin: mortgage-lending
product: pull-through
product_version: "n/a"
scope: likely-general
tags: [pull-through, fallout, cycle-time, funnel]
confidence: medium
reviewed: false
---

## Problem

A production manager saw pull-through fall and authorized more lead spend to 'fill the top of the funnel.' The risk: pull-through is a funnel, and buying more applications into a leaking funnel wastes spend — the fix is the worst fallout stage, which here sat deep in the funnel, not at the top (§3 #1).

## Context

- Channel: retail purchase + some refi.
- Constraint: funded = apps × the chained stage rates; the worst stage rate is the leak to fix first (§3 #1).
- The manager reasoned from the top-line pull-through number.

## Attempts

- Tried: **broke pull-through into stage fallout** (`mortgage_lending_calc.py pullthrough`). Outcome: app→approved was healthy; approved→clear-to-close had collapsed — the leak was deep, not at intake.
- Tried: **localized the approved→CTC cause.** Outcome: a processing bottleneck — cycle dwell had ballooned in one stage (route to cycle, §3 #2 #4).
- Tried: **back-solved required apps** to show that more apps couldn't fix a mid-funnel leak (§3 #1). Outcome: the math made the case against more lead spend.

## Resolution

The fix was to **clear the processing bottleneck — not buy more applications**. The output was the stage-fallout read, the localized bottleneck, and the back-solve showing why more apps wouldn't help, with no borrower NPI in the deliverable.

**Action for the next consultant hitting this pattern:** **break pull-through into stage fallout before buying more apps.** The leak is usually mid-funnel (a cycle bottleneck or conditions backlog), where more applications can't help. See Tree 1 and the `mortgage_lending_calc.py` `pullthrough` mode.

Benchmark figures are segment-/region-/date-dependent — treat as `[unverified — training knowledge]` and validate against the client's own data before any deliverable (§3 #8).
