---
name: build-cash-forecast-and-liquidity-plan
description: "Build a cash position + rolling forecast and a liquidity plan by traversing the treasury decision tree (cash position → forecast method (direct/receipts-and-disbursements vs indirect) → 13-week build & drivers → variance loop → minimum-cash/buffer sizing → committed vs uncommitted facility mix), then return the daily cash position, the 13-week forecast, the buffer target (stress-tested), the facility/revolver plan, and the conditions that resize it. Reach for this when the user asks 'build our 13-week cash forecast', 'how much cash should we hold?', 'what's our liquidity buffer?', 'direct or indirect forecast?', or 'committed vs uncommitted facilities?'. Used by cash-and-risk-operations-specialist (primary) and treasury-strategy-lead."
---

# Skill: build-cash-forecast-and-liquidity-plan

> **Invoked by:** `cash-and-risk-operations-specialist` (primary, for the position + forecast build) and `treasury-strategy-lead` (for the buffer/facility policy the forecast grounds).
>
> **When to invoke:** "build our 13-week cash forecast"; "what's today's cash position?"; "how much minimum cash / liquidity buffer should we hold?"; "direct or indirect forecasting?"; "committed vs uncommitted facilities / how much revolver headroom?"; any "how much cash and where" question.
>
> **Output:** the daily cash position + the rolling 13-week (direct) forecast + a variance loop + the stress-tested minimum-cash/buffer target + the committed vs uncommitted facility mix & revolver headroom + the 1-2 conditions that resize it.

## Procedure

1. **Position cash first — from where the money actually is.** Build today's **cash position** per currency and entity: opening bank balances + confirmed receipts − confirmed disbursements → **closing / available liquidity** (net of holds, minimums, and un-cleared items). This is the anchor; a forecast that doesn't start from the real position is untethered.
2. **Pick the forecast method by horizon.** **Direct (receipts-and-disbursements)** — actual expected cash in/out, driver-based — for the **operating horizon (the 13-week and shorter)**; it's what treasury runs day-to-day. **Indirect** (net income + working-capital changes + non-cash add-backs) — for the **longer, statement-linked** view where you forecast from the P&L/balance sheet. Don't use indirect for the 13-week (too coarse) or direct for the annual (too granular to sustain).
3. **Build the 13-week from drivers, not a straight line.** Lay out 13 weekly columns; populate **receipts** (collections driven by DSO / the AR aging, plus known one-offs) and **disbursements** (AP payment-run timing driven by DPO, payroll, tax, debt service, capex, dividends). Each line is a *driver*, not a plug — so a variance is diagnosable.
4. **Attach a variance loop — every week.** Forecast → actuals → **variance by line** → re-forecast. Tune the drivers from the miss (collections slower than DSO assumed? a payment run slipped a week?). A 13-week without a back-test is a wish, not a forecast.
5. **Size the minimum-cash / buffer against a stress, not the average.** Traverse the buffer-sizing branch in [`../../knowledge/treasury-management-decision-tree.md`](../../knowledge/treasury-management-decision-tree.md): take the forecast's **trough** (the worst intra-period low), then stress it — a receipts shock (a big customer slips), a facility pulled, a covenant tightening, a seasonality low — and set the buffer so the trough-under-stress stays above zero (and above any covenant/minimum-operating-cash floor).
6. **Choose the facility mix — committed over cheap.** Cover the gap between the buffer and on-hand cash with **committed** facilities (a contractually available revolver worth the commitment fee) rather than **uncommitted** lines (withdrawable exactly when you need them). Keep **revolver headroom** you can actually draw when stressed, and check the draw conditions/covenants don't lock it at the wrong moment.
7. **State the resize conditions** — the 1-2 facts that change the buffer or facility plan (e.g., "if a top-3 customer's terms extend, the receipts trough deepens and the buffer must rise"; "if the revolver's covenant tightens, its headroom is not really available and the buffer must absorb it").

## Worked example

> User: "We're a seasonal consumer-goods company with a Q4 build. Build our 13-week and tell us how much cash to hold and whether our $50M revolver is enough."

- **Position:** consolidate the operating accounts to today's available balance per entity — say $18M on hand.
- **Method:** **direct / R&D** for the 13-week — receipts from the AR aging (DSO ~52 days), disbursements from the AP run calendar + the pre-season inventory build (a big **DPO**-timed outflow), payroll, and the interest payment in week 9.
- **13-week:** the inventory build drives a **trough in weeks 6-8** where cumulative cash dips to $6M before Q4 collections arrive.
- **Variance loop:** back-test weekly — if collections run 4 days slower than the DSO assumption, the trough deepens ~$3M; tune the receipts driver.
- **Buffer (stressed):** trough $6M, stress it for a slow-collections + a supplier-prepay demand → the buffer target is **~$12M minimum operating cash**. On-hand at the trough ($6M) is below it → draw is needed.
- **Facility:** the **$50M committed revolver** covers the gap with headroom; confirm the leverage covenant won't be breached by the seasonal inventory swing (which would block the draw exactly when needed).
- **Resize condition:** if the pre-season build grows 30% or the revolver covenant tightens, the trough deepens and the committed headroom must be re-tested.

## Guardrails

- Position cash **first**; a forecast that doesn't start from the real per-currency/entity position is untethered.
- **Direct for the 13-week, indirect for the horizon** — don't mismatch method to horizon.
- Every forecast carries a **variance-to-actual loop**; drivers are tuned from the miss, not left as plugs.
- Size the buffer on the **stressed trough**, not the average month; include any covenant / minimum-operating-cash floor.
- **Committed beats uncommitted** — an uncommitted line can be pulled exactly when you need it; verify draw conditions/covenants don't lock a committed line at the wrong moment.
- Sizing the buffer is a **policy** call (the `treasury-strategy-lead` owns it); the build/variance loop is **execution** (the operations specialist) — keep the seam clean.
- This is **not** the FP&A budget / P&L plan — that's `finance`; treasury forecasts the *cash*, not the earnings.
- Volatile specifics (facility terms, covenant definitions, bank-portal balance feeds) carry a **retrieval date** and are re-verified before a board/bank commitment. See [`../../knowledge/treasury-management-patterns-2026.md`](../../knowledge/treasury-management-patterns-2026.md).
