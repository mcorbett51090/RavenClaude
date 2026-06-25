# Compute LTV before CAC

**Status:** Absolute rule
**Domain:** Studio unit economics
**Applies to:** `fitness-studio-operations`

---

## Why this exists

CAC has no meaning in isolation — "we spend $200 to get a member" is good or terrible depending entirely on what that member is worth and how fast you recover the cost. Setting an acquisition budget before knowing LTV is spending blind, and the most common failure mode is anchoring CAC to *revenue* (ignoring margin) or to an industry-average LTV instead of the studio's own.

## How to apply

- Compute **LTV = revenue per member (net) × average lifetime months (= 1 / monthly churn) × contribution margin** — from your own billing.
- Derive the **CAC ceiling = LTV ÷ target LTV:CAC ratio** (commonly ~3:1 as a floor, not a goal).
- Always check **payback (months) = CAC ÷ (revenue per member × margin)** alongside the ratio — a healthy LTV:CAC with a long payback can still starve cash.
- Hand the CAC ceiling to `marketing-operations` as the number to spend against.

**Do:** compute LTV on net revenue and margin, then set CAC against it.
**Don't:** quote an industry LTV, or set CAC against gross revenue.

## Edge cases / when the rule does NOT apply

Pre-launch with no churn data: use a conservative assumed lifetime, label it an assumption, and re-derive CAC the moment real churn exists.

## See also

- [`./know-your-real-churn-rate.md`](./know-your-real-churn-rate.md)
- [`../skills/compute-studio-unit-economics/SKILL.md`](../skills/compute-studio-unit-economics/SKILL.md)

## Provenance

Standard LTV/CAC unit economics. Codifies the `fitness-studio-operations-lead` house opinion ("LTV before CAC").

---

_Last reviewed: 2026-06-25 by `claude`_
