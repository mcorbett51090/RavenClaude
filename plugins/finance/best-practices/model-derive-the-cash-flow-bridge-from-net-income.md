# Build the indirect cash-flow bridge — start at net income, walk to net change in cash

**Status:** Pattern
**Domain:** Financial modeling / three-statement integrity
**Applies to:** `finance`

---

## Why this exists

`link-the-three-statements.md` establishes the *absolute rule* — every cash-flow line is a balance-sheet movement and the model must tie. This doc is the **constructive companion**: the actual sequence of the indirect-method bridge, so a modeler builds it the same way every time and a reviewer can read it top-down. The most common build error is not a broken link but a **mis-signed** one — adding back a working-capital increase that should be subtracted, or netting capex against D&A. A bridge built in the canonical order, with each sign justified by the direction of the underlying account movement, is self-checking: if the bridge order is right and every sign follows the "use of cash = subtract" rule, the ending cash falls out correctly without a plug.

## How to apply

Build operating, then investing, then financing — in that fixed order — and justify every sign by whether the movement is a *source* (+) or *use* (−) of cash:

```
Cash from operations (indirect):
  Net income (from P&L)
  + D&A                          (non-cash expense added back)
  + stock-based comp             (non-cash add-back)
  − ΔAR        (AR up = cash tied up = use)        # +ΔAR if AR fell
  − ΔInventory (inventory up = use)
  + ΔAP        (AP up = supplier financing = source)
  + ΔDeferred revenue (cash collected ahead of revenue = source)
Cash from investing:
  − Capex                        (PP&E purchase = use; ties to PP&E roll)
  ± Acquisitions / divestitures
Cash from financing:
  ± Δdebt      (draw = source, repay = use; ties to debt schedule)
  + Equity issued / − buybacks / − dividends
= Net change in cash  ->  Beginning cash + this = Ending cash (BS)
```

**Do:**
- Add back **non-cash** P&L items (D&A, SBC, deferred tax) before any working-capital line.
- Sign working capital by direction of movement: an asset increase is a use (−), a liability increase is a source (+).
- Tie investing capex to the PP&E roll-forward and financing Δdebt to the debt schedule — same number, two places, linked.

**Don't:**
- Put a working-capital movement in investing, or capex in operations.
- Net two unrelated movements into one line to "simplify" — it destroys the audit trail.
- Hardcode the net-change-in-cash to force the BS cash tie (that is the plug `link-the-three-statements.md` bans).

## Edge cases / when the rule does NOT apply

- **Direct-method 13-week treasury forecasts** are receipts-and-disbursements, not an indirect bridge — see [`treasury-cash-conversion-cycle.md`](./treasury-cash-conversion-cycle.md) and the `thirteen-week-cash-forecast` skill.
- **Financial-institution models** present cash flow differently (interest received/paid can sit in operating under IFRS election) — state the election on the Documentation tab.
- **A pure P&L or margin walk** with no balance sheet carries no cash-flow bridge; the rule attaches only once a BS exists.

## See also

- [`./link-the-three-statements.md`](./link-the-three-statements.md) — the absolute integrity rule this operationalizes.
- [`./inputs-live-in-one-place.md`](./inputs-live-in-one-place.md) — where the drivers behind each line live.
- [`../agents/financial-modeler.md`](../agents/financial-modeler.md) — "cash-from-operations bridge wired through"; working-capital mechanics (DSO/DPO/DIO).
- [`../skills/model-review/SKILL.md`](../skills/model-review/SKILL.md) — the integrity pass that re-walks this bridge.

## Provenance

Codifies the `financial-modeler` agent's three-statement surface area ("the cash-from-operations bridge wired through") and house opinions #2 and #11 in [`../CLAUDE.md`](../CLAUDE.md) §3. Built adjacent to the existing `link-the-three-statements.md` (the integrity rule) so the *order and signs* of the bridge are a separate, citable artifact.

---

_Last reviewed: 2026-05-30 by `claude`_
