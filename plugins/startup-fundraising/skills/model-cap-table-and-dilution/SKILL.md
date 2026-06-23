---
name: model-cap-table-and-dilution
description: Model a startup cap table and the dilution a round causes — including option-pool shuffle, pro-rata, and post-money SAFE conversion — with worked arithmetic. Produces a post-round ownership table and surfaces the post-money-cap dilution gotcha. Reach for this when the user asks "what does my cap table look like after this round?", "how much do I get diluted?", "how does my SAFE convert?", or "what option pool should I set aside?". Used by `fundraising-strategist` (primary).
---

# Skill: model-cap-table-and-dilution

> **Invoked by:** `fundraising-strategist` (primary).
>
> **When to invoke:** "model my cap table after this round"; "how much dilution does this cause?"; "how does my SAFE convert at the priced round?"; "how big an option pool?"; "what's my pro-rata?".
>
> **Output:** a post-round ownership table (fully diluted), the dilution each party takes, and an explicit call-out of the option-pool shuffle and the post-money-cap gotcha when they apply.
>
> **This is founder-side literacy and arithmetic — NOT legal, tax, or accounting advice.** Final numbers belong in a cap-table tool and (for a priced round) with counsel.

## Core mechanics (the math you must get right)

- **Fully diluted shares** = common + options (granted + pool) + as-converted preferred + as-converted SAFEs/notes. Ownership % is always computed on the fully diluted base.
- **Post-money valuation** = pre-money valuation + new money raised. **Investor % (priced round)** = new money ÷ post-money.
- **Option-pool shuffle (the founder tax).** When investors require an option pool (or top-up) created *before* the round, it is carved out of the **pre-money**. Effect: the pool dilutes the *existing* holders (founders), not the new investors. A "$8M pre, $2M raise, 10% post-money pool" is materially worse for founders than the same round with the pool taken post-money — always clarify which.
- **Post-money SAFE (Y Combinator, post-2018).** The cap is a **post-money** number: the SAFE holder's ownership % ≈ investment ÷ post-money cap, and that percentage is **locked**. Consequence — the **post-money-cap gotcha**: every *additional* SAFE, and the option pool created at the priced round, dilute the **founders**, not the earlier post-money SAFE holders. You must sum the SAFE *stack* to see true founder dilution; modeling one SAFE in isolation understates it. (Pre-2018 *pre-money* SAFEs behaved differently — confirm which instrument you hold.)
- **Discount & cap interaction.** A SAFE converts at the **better of** the valuation cap or the discount applied to the priced-round price; MFN gives the holder the best terms granted to any later SAFE.
- **Pro-rata.** A pro-rata right lets an investor buy enough of the *next* round to maintain their ownership %; exercised pro-rata reduces how much of the new round is available to new investors.

## Procedure

1. **Get the starting cap table** (fully diluted): founders, existing options + unallocated pool, prior SAFEs/notes with their caps/discounts.
2. **Identify the instrument** for this round: priced equity, or SAFE(s). For SAFEs, record each one's amount, cap (post- vs pre-money), discount, and MFN.
3. **For a priced round:** compute investor % = new money ÷ post-money. If a pool top-up is required pre-money, add it to the pre-money side first (it dilutes existing holders), then layer the new money.
4. **For SAFEs converting at a later priced round:** for each SAFE, take the **better of** cap-implied price or discounted price; convert to shares; include every SAFE plus the new pool in the fully diluted base before computing final percentages.
5. **Build the post-round fully diluted table:** every party's shares and %, with the **dilution delta** for founders.
6. **Surface the gotchas explicitly:** name the option-pool shuffle (and who bears it) and, for post-money SAFEs, the stack effect on founders.
7. **Sanity-check against the milestone:** is the founder dilution proportionate to what the raise buys? (Typical *single*-round dilution lands roughly **15-25%** at seed/Series A — a range, market-dependent, retrieval-date 2026-06; not a guarantee.)

## Worked example — post-money SAFE conversion + the gotcha

> Pre-round: 10,000,000 fully diluted shares, all founders.
> Raise: a **$2,000,000 post-money SAFE on a $10,000,000 post-money cap.**

- SAFE holder's locked ownership = 2,000,000 ÷ 10,000,000 = **20%**.
- So post-SAFE the founders hold **80%** = the existing 10,000,000 shares; the SAFE will convert to shares equal to 25% of the pre-SAFE count (10,000,000 × 20/80 = 2,500,000), giving 12,500,000 fully diluted, of which the SAFE is 2,500,000 = 20%. ✓

Now a **second** $1,000,000 post-money SAFE on the **same $10M cap** before any priced round:

- Second holder's locked ownership = 1,000,000 ÷ 10,000,000 = **10%**.
- Both SAFEs are locked: SAFE-1 = 20%, SAFE-2 = 10%, together **30%**.
- **The founders now hold 70%, not 80%.** The second SAFE diluted the *founders* — **not** the first SAFE holder, whose 20% is fixed. This is the post-money-cap gotcha: the founder absorbs every later SAFE.

Then at the priced Series A, a **10% post-money option pool** required pre-money dilutes the founders again (carved from the pre-money), and the new lead's % comes out of the post-money — founders end well below a naive "100% − 30%" estimate. **Model the whole stack.**

## Guardrails

- **Always compute ownership on the fully diluted base** — common-only percentages mislead.
- **Always clarify pre- vs post-money** for both the valuation and the option pool — the shuffle is the most common founder surprise.
- **Always sum the SAFE stack** for post-money SAFEs — one-SAFE math understates founder dilution.
- **Confirm SAFE vintage** (post-money YC SAFE vs older pre-money) — the conversion math differs.
- **This is literacy + arithmetic, not advice** — final numbers belong in a cap-table tool; a priced round's docs route to `legal-ops-clm`, model/valuation defensibility to `finance`. See [`../../knowledge/term-sheet-and-safe-essentials.md`](../../knowledge/term-sheet-and-safe-essentials.md).
