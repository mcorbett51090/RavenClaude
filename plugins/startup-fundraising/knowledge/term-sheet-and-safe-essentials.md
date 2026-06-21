# Term-Sheet & SAFE Essentials (Founder-Side Literacy)

> **Last reviewed:** 2026-06 · **Confidence:** mechanics = high; market-standard defaults = medium and **market-dependent**.
>
> ## ⚠️ This is founder-side literacy, NOT legal advice.
> This document explains what the common terms *mean* and *do to you* so you can negotiate and ask good questions. It does **not** tell you what to sign, whether a clause is enforceable, or how it interacts with your specific docs/jurisdiction/tax situation. **Binding review of any term sheet, SAFE, or financing document routes to `legal-ops-clm` (and your actual counsel).** Financial-model and valuation defensibility route to `finance`.

---

## Part 1 — The SAFE (pre-seed / seed)

A **SAFE** (Simple Agreement for Future Equity) is not debt and not equity — it's a right to equity that converts at the next priced round. The current standard is the **Y Combinator post-money SAFE** (post-2018).

| Term | What it is | What it does to the founder |
|---|---|---|
| **Valuation cap** | The maximum valuation at which the SAFE converts. | A lower cap = the SAFE holder gets *more* equity at conversion = more founder dilution. The single most important SAFE term. |
| **Discount** | A % discount to the priced-round price (e.g., 20%). | Rewards the early investor; the SAFE converts at the **better of** cap or discount. More founder dilution than no discount. |
| **MFN (most-favored-nation)** | The holder gets the best terms granted to any *later* SAFE. | A "no cap, no discount, MFN" SAFE is the most founder-friendly *to you* — but later cheaper SAFEs flow back to MFN holders. |
| **Post-money cap (the gotcha)** | The cap is a *post-money* number; the holder's % is **locked** at investment ÷ post-money cap. | **Every later SAFE and the priced-round option pool dilute the FOUNDERS, not the earlier SAFE holder.** You must model the whole SAFE *stack* — see [the cap-table skill](../skills/model-cap-table-and-dilution/SKILL.md). This is the #1 founder surprise. |
| **Pro-rata side letter** | A right to invest in the next round to maintain ownership. | Common; manageable, but track who holds it — it eats into the next round's available allocation. |

**Vintage warning:** older **pre-money** SAFEs convert differently (the cap is pre-money, so additional SAFEs dilute *everyone* including earlier SAFE holders). Confirm which instrument you hold before modeling.

---

## Part 2 — The priced-round term sheet (seed-with-a-lead / Series A)

A priced round issues **preferred stock** and comes with a term sheet split into **economic** terms (who gets what money) and **control** terms (who decides what). The headline valuation is rarely the most important line.

### Economic terms

| Term | What it is | Founder-side note |
|---|---|---|
| **Pre-money / post-money valuation** | Pre-money = company value before the new money; post-money = pre + raise. Investor % = raise ÷ post-money. | The number everyone fixates on. A high price you can't grow into → a future **down round**. |
| **Option pool** | Shares reserved for future hires. | If created/topped-up **pre-money** (the "**option-pool shuffle**"), it dilutes *you*, not the new investors. Negotiate the size and the pre/post-money side. |
| **Liquidation preference** | What preferred holders get back first on an exit. **1x non-participating** is the founder-friendly standard. | **Participating** ("double-dip") preferred takes its 1x *and* shares the rest — much worse for founders. A multiple (2x, 3x) is aggressive. Watch this closely. |
| **Anti-dilution** | Protects investors if a later round prices lower. **Broad-based weighted-average** is standard/fair. | **Full-ratchet** is punitive to founders in a down round. Push for weighted-average. |
| **Dividends** | Accruing dividends on preferred. | Often non-cumulative / waived early-stage; cumulative dividends compound against you. |

### Control terms

| Term | What it is | Founder-side note |
|---|---|---|
| **Board composition** | Who sits on the board (e.g., 2 founders / 1 investor / 1 independent). | Control of the board is control of the company. Guard the seat count carefully — more than valuation, this is the long-game term. |
| **Protective provisions** | Investor veto rights over certain actions (sell the company, raise more, change the option pool). | Standard to a point; over-broad vetoes hamstring you. |
| **Pro-rata rights** | Investors' right to maintain ownership in future rounds. | Standard for lead investors; manageable. |
| **Information rights** | Investors' right to financials/updates. | Standard; satisfied by your [investor update](../templates/investor-update-template.md). |
| **Founder vesting** | Re-vesting of founder shares (often 4-year with a cliff). | Common even for existing founders at a priced round; negotiate acceleration on termination/acquisition. |

---

## What to actually focus on (founder priorities)

1. **Board composition & control** — the longest-lived term.
2. **Liquidation preference** — 1x non-participating or walk; participating/multiples change your exit math materially.
3. **The valuation *and* the option-pool shuffle together** — the effective price after a pre-money pool is lower than the headline.
4. **Anti-dilution** — weighted-average, not full-ratchet.
5. **For SAFEs: the cap, and the post-money stack effect on your dilution.**

## Hard boundary

Everything above is to help you **understand and negotiate**. The moment the question is *"is this enforceable / what should I sign / how does this interact with my docs and taxes?"* — that is **legal advice**, and it routes to **`legal-ops-clm`** and your counsel. Do not treat this doc as a substitute. See the [fundraising-strategist agent](../agents/fundraising-strategist.md) for how the seam is enforced.
