# Link the three statements — cash flow is derived, never typed

**Status:** Absolute rule
**Domain:** Financial modeling / three-statement integrity
**Applies to:** `finance`

---

## Why this exists

A three-statement model is only trustworthy when the P&L, balance sheet, and cash flow are **mechanically linked**, not three independently-maintained tables that happen to agree this period. The single most common integrity failure is a cash-flow statement whose line items are *typed in* rather than *derived* from the movement in balance-sheet accounts and the P&L. When that happens, the balance sheet appears to balance only because someone plugged a number — and the moment an assumption moves, the model silently lies. The `financial-modeler` agent's rule is blunt: net income flows from the P&L into retained earnings and into the top of the CF; every CF line is the period-over-period change in a BS account; and the cash the CF computes is the cash that lands on the BS. If those links are real, the model balances *because the accounting is right*, not because a reviewer forced it.

## How to apply

Wire the linkages, then prove them with a balance check that returns 0 if and only if A = L + E:

```
P&L:   Net income ───────────────► Retained earnings (BS)  and  top line of CF (indirect method)
CF:    + D&A (from P&L)
       − ΔAR, ± ΔInventory, ± ΔAP   (each = this-period BS balance − prior-period BS balance)
       − Capex (→ PP&E roll on BS)
       ± Δdebt (→ debt schedule on BS),  ± equity issuance
       = Net change in cash
BS:    Ending cash = Beginning cash + Net change in cash (from CF)   # the tie-out
Check: BalanceCheck = TotalAssets − (TotalLiabilities + Equity)      # must equal 0 every period
```

**Do:**
- Derive every CF line from the change in a BS account or a P&L line — never type a working-capital movement directly onto the CF.
- Put a `BalanceCheck` row on every BS column and a cash tie-out row linking CF ending cash to BS cash.
- Route net income through retained earnings, and run interest off the debt schedule (a designed, disclosed circular when interest feeds the cash sweep).

**Don't:**
- Plug the balance sheet — a hardcoded number to "make it tie" hides the broken link instead of fixing it.
- Wrap a non-balancing formula in `IFERROR(formula, 0)`; that masks the integrity failure.
- Maintain the CF as a standalone schedule disconnected from the BS roll-forwards.

## Edge cases / when the rule does NOT apply

- **Direct-method cash forecasts** (the 13-week treasury forecast) are receipts-and-disbursements by source, not a BS-derived indirect CF — a different artifact with its own discipline (`thirteen-week-cash-forecast`). The derive-from-BS rule is for the *model's* indirect CF.
- **Single-statement quick analyses** (a standalone P&L bridge, a margin walk) carry no BS or CF, so there is nothing to link — but the moment a balance sheet or CF is added, the linkage rule attaches.
- **Designed, disclosed circulars** (interest-on-cash-sweep) legitimately loop through the debt schedule; document them on the Documentation tab. The rule bans *undisclosed* circulars and *plugged* balances, not intentional structure.

## See also

- [`../agents/financial-modeler.md`](../agents/financial-modeler.md) — "cash flow is derived from BS + P&L"; balance-check-on-every-BS-tab; designed-vs-accidental circulars.
- [`./inputs-live-in-one-place.md`](./inputs-live-in-one-place.md) — the inputs discipline the linked mechanics read from.
- [`../skills/model-review/SKILL.md`](../skills/model-review/SKILL.md) — the 7-pass review whose *integrity* pass tests these links.

## Provenance

Codifies the `financial-modeler` agent's three-statement / integrity opinions ([`../agents/financial-modeler.md`](../agents/financial-modeler.md) — "P&L, BS, CF fully linked, balancing, with the cash-from-operations bridge wired through"; "a three-statement model where cash flow is not derived from BS + P&L … doesn't actually balance" anti-pattern; "balance check on every BS tab"), and finance house opinions #8 (one source of truth per metric) and #12 (GAAP/management view stated, not blended) in [`../CLAUDE.md`](../CLAUDE.md) §3.

---

_Last reviewed: 2026-05-30 by `claude`_
