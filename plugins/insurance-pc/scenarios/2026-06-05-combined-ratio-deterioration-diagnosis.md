---
scenario_id: 2026-06-05-combined-ratio-deterioration-diagnosis
contributed_at: 2026-06-05
plugin: insurance-pc
product: actuarial-pricing
product_version: "n/a"
scope: likely-general
tags: [combined-ratio, loss-ratio, expense-ratio, catastrophe, attritional]
confidence: medium
reviewed: false
---

## Problem

A multi-line carrier's calendar-year combined ratio jumped ~6 points year over year and the executive team wanted "the rate increase that fixes it." The risk: prescribing a blanket rate action against a number that hadn't been decomposed — when a combined-ratio move can be a cat year, an expense-ratio drift, an attritional-frequency story, or prior-year reserve development, each with a different fix (and a rate filing is the wrong lever for three of those four).

## Context

- Segment: regional carrier, mixed personal + commercial lines, post-active-cat-year.
- Constraint: the headline combined ratio is a calendar-year number — it blends the current accident year, prior-year reserve development, AND catastrophe load. Reading it as one thing misdiagnoses the driver.
- The team was reasoning from the single combined-ratio number, not its components — exactly the §3 #1 / #4 / #5 trap (read loss and expense separately; strip cat; check reserve development).

## Attempts

- Tried: **split loss vs expense first** (§3 #1), then **stripped the catastrophe load** from the loss ratio (§3 #4). Outcome: most of the 6-point jump was an elevated cat load in a heavy-cat year — the attritional loss ratio was nearly flat. Industry context for scale: cat losses ran roughly 7-8 points of the 2025 P&C combined ratio [verify-at-use], so a single bad cat year can swing the headline several points without the attritional book changing.
- Tried: **checked prior-year reserve development** (§3 #5) on the calendar-year figure. Outcome: a portion of the move was modest adverse development on prior accident years, not current-year underwriting — which a rate increase on new/renewal business does nothing to fix.
- Tried: **separated the residual attritional move into frequency vs severity** (§3 #3) for the one line that had genuinely drifted. Outcome: that line was a severity story (large-loss / inflation), not frequency — so the fix was limit/attachment and large-loss handling, not broad risk-selection tightening.

## Resolution

The "6-point problem" decomposed into ~4 points cat (a year-shape artifact, not an underwriting failure), ~1 point prior-year development (a reserving matter), and ~1 point genuine current-year attritional severity on one line. The action plan was line-specific (severity controls + a targeted rate move on the one drifting line), not a blanket rate increase — which would have over-corrected the profitable lines and chased away good business.

**Action for the next consultant hitting this pattern:** **decompose before you prescribe.** Split loss vs expense (§3 #1), strip cat (§3 #4), check prior-year development (§3 #5), THEN separate frequency vs severity (§3 #3) on whatever residual remains. Only the genuine current-year attritional drift is a rate-action candidate; the rest are cat-volatility, reserving, or claims matters. The [`../scripts/pc_calc.py`](../scripts/pc_calc.py) `combined-ratio` mode does the loss/expense + attritional/cat split and reports the underwriting margin; `loss-ratio` does the frequency/severity split. Pair with [`../knowledge/pc-decision-trees.md`](../knowledge/pc-decision-trees.md) "Combined ratio deteriorated".

**Sources (retrieved 2026-06-05):**
- III / Triple-I — 2025 P&C results & combined-ratio commentary: https://www.iii.org/press-release/triple-i-milliman-2025-us-p-c-insurance-outlook-shows-strength-in-personal-auto-ongoing-pressure-in-general-liability-lines-071025
- Reinsurance News — US P&C lowest net combined ratio in over a decade (Triple-I/Milliman): https://www.reinsurancene.ws/us-pc-industry-set-for-lowest-net-combined-ratio-in-over-a-decade-triple-i-milliman/
- OpsDog — Combined Ratio definition & benchmark: https://opsdog.com/products/combined-ratio

The cat-points-of-combined-ratio figure is a recent-year industry datapoint, not a hard rule — treat as `[verify-at-use]` and validate against the book's own cat experience and the relevant accident year (§3 #8).
