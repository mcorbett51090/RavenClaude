# Close the product-feedback loop — and measure with developer success, not vanity

**Status:** Absolute rule
**Domain:** DevRel operating model / measurement
**Applies to:** `developer-relations`

---

## Why this exists

DevRel has four motions — advocacy, education, community, and **product-feedback** — and teams reliably skip the fourth because it produces no flashy output. But the friction a developer advocate feels building a sample is the friction *every* developer feels; the DevRel team is the company's most honest source of developer-experience signal. If that signal never reaches PM/eng, the friction stays and activation stays low — and no quickstart can route around a genuinely hard product. The matching failure on the measurement side is the **vanity metric**: a scorecard of followers, stars, and page views can be all-green while activation is zero, because those metrics measure your *reach*, not the developer's *success* ([`../knowledge/devrel-metrics.md`](../knowledge/devrel-metrics.md) §5).

## How to apply

Make developer feedback a standing artifact, and anchor every headline metric in the activation/retention band of the funnel:

```
Feedback loop:   friction (community + sample-building) → DX-feedback digest → PM/eng → shipped
Close condition: a routed friction item ships AND its activation metric moves

Scorecard screen (per metric): does this measure developer SUCCESS or our REACH?
  REACH  (followers / stars / views / impressions)  → leading indicator only, never a headline
  SUCCESS (activation rate / TTFHW / week-4 retention) → headline / north-star
```

**Do:**
- Run the product-feedback loop as a recurring digest to PM/eng with an owner and a cadence — not an anecdote in a thread.
- Track feedback *throughput and action rate* (items routed per cycle, share PM/eng ships).
- Make the north-star metric an activation or retention number; keep vanity metrics only as labeled leading indicators.

**Don't:**
- Treat the friction you found as solved by routing *around* it in the docs — route it *to* product.
- Let any vanity metric (followers, stars, views, signups-without-activation) be a headline KPI (the advisory hook flags goals stated only in vanity metrics).
- Report a quantitative drop ("activation fell") with no qualitative "why" — the loop is what explains it.

## Edge cases / when the rule does NOT apply

- **Pre-launch / tiny audience:** the quantitative funnel may be too sparse to be meaningful — lean *more* on the qualitative loop, not less; the feedback is still the highest-value output.
- **Pure awareness campaigns** legitimately report reach metrics — but as the campaign's *leading* indicator, with a downstream activation metric as the real scorecard, never reach alone.

## See also

- [`../knowledge/devrel-metrics.md`](../knowledge/devrel-metrics.md) — §1 the AAARRP funnel (incl. the product-feedback stage), §5 vanity-metric traps.
- [`../skills/measure-devrel-impact/SKILL.md`](../skills/measure-devrel-impact/SKILL.md) — builds the scorecard and runs the vanity screen.
- [`../knowledge/devrel-strategy-decision-tree.md`](../knowledge/devrel-strategy-decision-tree.md) — when "product is genuinely hard" routes the goal to the product-feedback motion.

## Provenance

Codifies house opinions "the product-feedback loop is a first-class motion" and "vanity metrics measure reach, not developer success" in [`../CLAUDE.md`](../CLAUDE.md) §3. Vanity-vs-actionable distinction from *Lean Analytics* (Croll & Yoskovitz) applied to developer audiences; the advisory hook [`../hooks/flag-devrel-smells.sh`](../hooks/flag-devrel-smells.sh) flags vanity-only goal statements (last reviewed 2026-06-17).

---

_Last reviewed: 2026-06-17 by `claude`_
