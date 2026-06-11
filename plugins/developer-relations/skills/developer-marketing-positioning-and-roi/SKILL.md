---
name: developer-marketing-positioning-and-roi
description: "Position to developers and prove DevRel ROI — write job-to-be-done positioning that earns a technical audience's trust, segment by adopting role, rank channels by reach-to-activation efficiency, and report cost-per-activation instead of vanity reach."
---

# Developer Marketing, Positioning & ROI

**Purpose:** make developers want to try (positioning), reach the right ones efficiently (channels),
and prove it paid off (ROI) — all measured by activation, not reach.

---

## Steps

### 1. Write job-to-be-done positioning

State the developer's job, the alternative they'd otherwise use, the differentiated path you offer,
and the proof. Lead with specificity; a technical audience distrusts superlatives ("seamless",
"blazing-fast") and trusts numbers, constraints, and honest tradeoffs
(see [`positioning-precedes-content`](../../best-practices/positioning-precedes-content.md)).

### 2. Segment by adopting role

| Role | Adopts because… | Channel | Message emphasis |
|---|---|---|---|
| IC builder | it solves their task fast | docs, search, communities | time-to-first-value |
| Tech lead | it fits the architecture & team | deep guides, ref architectures | integration, maintainability |
| Platform owner | it's safe, governed, supported | security/compliance, case studies | risk, support, ecosystem |

A single blended message under-serves all three.

### 3. Rank channels by reach-to-activation efficiency

Don't rank by impressions. Use [`../../scripts/devrel_calc.py`](../../scripts/devrel_calc.py)
`content_roi` and `funnel_conversion` to compute activations per channel and expose high-reach,
zero-activation channels for cutting.

### 4. Wire attribution from reach to first success

Connect channel touch → sign-up → first success so each channel carries an activation number, not just
a reach number. Where attribution is imperfect, state the assumption rather than over-claiming.

### 5. Report cost-per-activation

The headline DevRel-marketing metric is cost-per-activation (and per-adoption), not impressions or
followers. Vanity reach appears only paired with the activation it drove (constitution rule 2).

---

## Output

A positioning statement, a role-based segmentation with channels, a channel ranking by
reach-to-activation, and a cost-per-activation report. Deepen with the
[`devrel-metrics-and-roi-reference`](../../knowledge/devrel-metrics-and-roi-reference.md).
