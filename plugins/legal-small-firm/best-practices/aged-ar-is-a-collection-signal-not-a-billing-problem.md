# Aged A/R Is a Collection Signal, Not a Billing Problem

**Status:** Primary diagnostic
**Domain:** Small-firm legal practice
**Applies to:** `legal-small-firm`

---

## Why this exists

When A/R ages past 90 days, the instinct is to re-invoice or send reminders — a billing-desk fix. But aging A/R almost always traces to one of three upstream causes: a client who disputed the work, a client who can't pay, or an engagement that lacked clear payment terms. Treating aged A/R as a billing-process problem without diagnosing its cause wastes collection effort and delays the intake or fee-structure fix that would prevent the next one.

## How to apply

Run an A/R aging cut at 30/60/90/120+ days at least monthly. For every balance over 90 days, document one of three root causes before any collection action:

```
A/R Aging Root-Cause Triage
────────────────────────────
Matter:         [name / number]
Balance:        $___
Days aged:      ___
Root cause:
  [ ] Client dispute — scope, billing error, or fee disagreement
  [ ] Client liquidity — client can't pay (documented)
  [ ] Engagement terms — no payment terms or retainer requirement at intake
Action:
  Dispute → invoice review + attorney conversation
  Liquidity → payment plan or write-off decision
  Terms → fix intake for future matters
```

**Do:**
- Triage root cause before sending a demand letter or re-invoicing.
- Flag any balance aged 90+ that is not on an agreed payment plan as a potential write-off candidate.
- Use aging patterns to audit intake — a recurring "no retainer" root cause means the intake template is broken, not the client.

**Don't:**
- Auto-send collection letters without confirming the invoice isn't in dispute.
- Carry a disputed balance as collectible A/R in the realization calculation.
- Let aging run past 120 days without a documented decision (pursue, plan, or write-off).

## Edge cases / when the rule does NOT apply

Contingency matters have no A/R until settlement; the aging framework applies only to hourly and flat-fee matters with billed balances.

## See also

- [`../agents/legal-operations-analyst.md`](../agents/legal-operations-analyst.md) — owns the A/R aging analysis and triage.
- [`./collections-and-a-r-are-part-of-the-matter-not-after-it.md`](./collections-and-a-r-are-part-of-the-matter-not-after-it.md) — the upstream rule on treating collections as part of the matter.

## Provenance

Codifies the `legal-operations-analyst`'s diagnostic discipline from CLAUDE.md §3 #7 (collections are part of the matter) and standard small-firm practice management: the three root causes map to the standard collection-failure categories identified in ABA practice-management guidance [unverified — training knowledge].

---

_Last reviewed: 2026-06-05 by `claude`_
