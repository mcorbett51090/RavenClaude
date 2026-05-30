# Discipline the terminal value — cap perpetual growth and reconcile the two methods

**Status:** Absolute rule
**Domain:** Valuation / terminal value
**Applies to:** `finance`

---

## Why this exists

In most DCFs the **majority of present value lives in the terminal value** — the period beyond the explicit forecast — so a small over-reach in terminal-growth assumption swamps every careful year of the explicit build. The `valuation-analyst` agent calls over-confidence in terminal growth "the #1 valuation mistake" and is conservative there by design. Two errors recur: a perpetual growth rate set *above* the long-run growth of the economy (mathematically, the business eventually becomes larger than GDP — impossible), and an exit-multiple terminal value whose implied multiple is wildly inconsistent with the comp set. The discipline is to **cap perpetual growth at long-run GDP**, and to compute terminal value *both* ways — Gordon growth and exit multiple — and reconcile them, because each is a cross-check on the other.

## How to apply

Compute terminal value two ways, force perpetual growth ≤ long-run nominal GDP, and reconcile the implied multiple against the comps:

```
Gordon growth:   TV = FCF_terminal × (1 + g) / (WACC − g)        # require g ≤ long-run nominal GDP growth
Exit multiple:   TV = Metric_terminal × ExitMultiple             # multiple drawn from the comp set
Reconcile:
  implied exit multiple from Gordon  = TV_gordon / Metric_terminal
  implied perpetual g from exit mult = solve g such that Gordon TV = exit-multiple TV
  -> the two should land in a defensible band; a large gap means one assumption is off
Sanity:  TV PV as % of total EV  (flag if > ~75% — value is almost entirely terminal)
```

**Do:**
- Cap perpetual growth at long-run nominal GDP growth; anything higher requires an explicit, written defense (`valuation-analyst` opinion).
- Compute TV by **both** Gordon and exit-multiple and reconcile — the implied exit multiple from Gordon should be consistent with the comp set.
- Run the terminal-growth and WACC sensitivity (these two move the answer most) and disclose the share of EV that is terminal.

**Don't:**
- Set perpetual growth above long-run GDP without defending it — the business cannot outgrow the economy forever.
- Carry an exit-multiple TV whose implied multiple is inconsistent with the comps (the agent's named anti-pattern).
- Let the explicit period end before the business reaches steady state — a terminal value applied to a still-ramping year is unreliable.

## Edge cases / when the rule does NOT apply

- **Finite-life assets** (a single mine, a wasting concession, a contracted PPA) have *no* perpetual terminal value — model the cash flows to end-of-life and a salvage/decommissioning value instead.
- **Declining businesses** legitimately carry a *negative* perpetual growth rate; the cap is an upper bound, not a floor.
- **Cyclical businesses** should base the terminal year on a mid-cycle (normalized) metric, not a peak or trough year, before applying either method.

## See also

- [`./valuation-build-wacc-from-sourced-components.md`](./valuation-build-wacc-from-sourced-components.md) — the discount rate that, with `g`, sets the Gordon denominator `(WACC − g)`.
- [`./valuation-triangulate-three-methods.md`](./valuation-triangulate-three-methods.md) — the comp set the exit multiple is reconciled against.
- [`./model-present-scenarios-driven-by-one-switch.md`](./model-present-scenarios-driven-by-one-switch.md) — the WACC × terminal-growth sensitivity grid.
- [`../agents/valuation-analyst.md`](../agents/valuation-analyst.md) — "conservative on terminal value"; "terminal growth ≤ long-run real GDP growth"; the inconsistent-exit-multiple anti-pattern.
- [`../skills/dcf-valuation/SKILL.md`](../skills/dcf-valuation/SKILL.md) — terminal value (Gordon + exit multiple, reconciled).

## Provenance

Codifies the `valuation-analyst` agent's terminal-value opinions ("conservative on terminal value," "terminal growth ≤ long-run … GDP growth," "exit-multiple … consistent with the comp set") and the related anti-patterns ([`../agents/valuation-analyst.md`](../agents/valuation-analyst.md)), and the `dcf-valuation` skill's "terminal value (Gordon + exit multiple, reconciled)" step ([`../CLAUDE.md`](../CLAUDE.md) §8). New.

---

_Last reviewed: 2026-05-30 by `claude`_
