# Triangulate three methods and weight them — one method is an estimate, not a valuation

**Status:** Absolute rule
**Domain:** Valuation / methodology
**Applies to:** `finance`

---

## Why this exists

A valuation built on a single method is fragile: a DCF is only as good as its forecast and discount rate, comparables are only as good as the comp set, and precedents are only as good as how recent and how comparable the deals are. Each method's weakness is a different method's strength, so the `valuation-analyst` rule is blunt — "three methodologies, weighted; if you only have one method, you don't have a valuation, you have an estimate." When the three diverge, **the divergence is the story**: a DCF far above the comps usually means the forecast is heroic; comps far above precedents usually means the public market is hot relative to where deals actually clear. Presenting a single point estimate hides all of this and invites the reader to treat a judgment as a fact.

## How to apply

Run DCF, trading comps, and precedent transactions; show each method's range; assign an explicit weight with a written rationale; present the blended result as a **football field**, range first:

```
Method                 Implied EV range        Weight    Rationale
DCF                    $180M – $240M           50%       Forecast is well-supported; most of value in explicit period
Trading comps          $160M – $210M           30%       4 close comps; trimmed 1 outlier (different margin profile)
Precedent transactions $200M – $260M           20%       3 deals < 18 months old; includes ~20% control premium
Blended (weighted)     ~$195M – $225M          100%      Midpoint $210M — headline; range is the answer
```

**Do:**
- Assign an *explicit* weight to each method with a one-line defense — never "(DCF + comps) / 2" with no stated weights (the agent's anti-pattern).
- Document the comp set: why each comp is in, why each near-miss is out (stage / geography / model / margin profile).
- When methods diverge materially, name *why* in the narrative — the divergence is signal, not noise to average away.

**Don't:**
- Present a single-point valuation as "the answer" — always a range with method weights (`valuation-analyst` anti-pattern).
- Use a DCF alone for a pre-revenue company — that is a methodology mismatch; use VC method / scorecard plus comps.
- Pick comps "that look right" with the selection bias unstated, or carry an exit-multiple terminal value wildly inconsistent with the comp set.

## Edge cases / when the rule does NOT apply

- **Pre-revenue / early-stage** companies where a DCF cannot be calibrated — substitute VC method or scorecard for the DCF leg, but still triangulate (≥ two methods, weighted) rather than collapsing to one.
- **A thin or non-existent comp/precedent universe** (a genuinely novel business) — disclose the gap, widen the range, and lean weight toward the method that *can* be defended, rather than fabricating a comp set.
- **A quick directional read** explicitly labelled as such — but the valuation of record (409A, fairness support, board decision) carries the full triangulation.

## See also

- [`./valuation-build-wacc-from-sourced-components.md`](./valuation-build-wacc-from-sourced-components.md) — the discount rate behind the DCF leg.
- [`./valuation-discipline-the-terminal-value.md`](./valuation-discipline-the-terminal-value.md) — where most DCF value lives; cross-checked against the exit multiple.
- [`./model-present-scenarios-driven-by-one-switch.md`](./model-present-scenarios-driven-by-one-switch.md) — the range-over-point discipline this shares.
- [`../agents/valuation-analyst.md`](../agents/valuation-analyst.md) — "three methodologies, weighted"; comp-set documentation; method-weight anti-patterns.
- [`../skills/dcf-valuation/SKILL.md`](../skills/dcf-valuation/SKILL.md) — the DCF build and football-field cross-check.

## Provenance

Codifies the `valuation-analyst` agent's "three methodologies, weighted" opinion, its comp-set-documentation and method-weight opinions, the related anti-patterns (single-point result, unweighted average, biased comp set), and the constitution §4 anti-pattern "valuation outputs presented as a single point estimate rather than a range with method weights" ([`../CLAUDE.md`](../CLAUDE.md)). New.

---

_Last reviewed: 2026-05-30 by `claude`_
