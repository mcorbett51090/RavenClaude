# State the revenue-recognition policy — when revenue is earned, not when cash arrives

**Status:** Absolute rule
**Domain:** Controllership / revenue recognition
**Applies to:** `finance`

---

## Why this exists

Revenue is the most scrutinized line in the financial statements and the easiest to get subtly wrong, because *when* revenue is earned is a policy decision, not a cash event. Cash collected ahead of delivery is a **contract liability (deferred revenue)**, not revenue; revenue earned ahead of billing is a **contract asset**, not yet cash. The `controller` agent owns "deferred revenue / unearned: subscription / multi-period rev-rec mechanics, contract-liability roll-forward," and the constitution's house opinion #12 is explicit — where GAAP/IFRS and the management view diverge (and revenue-recognition timing is the headline example), **state which you are presenting; don't blend them silently.** The trap is a model or commentary that treats bookings, billings, and recognized revenue as interchangeable — they are three different numbers, and conflating them overstates the period and breaks the deferred-revenue roll.

## How to apply

Pin the recognition policy to the performance obligation, maintain the deferred-revenue roll-forward, and label which basis (GAAP recognized vs. bookings/ARR management view) any figure represents:

```
Recognition trigger:  revenue recognized as the performance obligation is satisfied
  Point-in-time (delivery)  vs  over-time (ratable across the subscription term)
Deferred revenue roll-forward (each period):
  Opening deferred + new billings − revenue recognized = closing deferred
Label every figure's basis:
  "Recognized revenue (GAAP, ASC 606 over-time)"   ≠   "Bookings"   ≠   "Billings"   ≠   "ARR (mgmt view)"
Cutoff:  a sale earned this period but invoiced next still recognizes this period (controller cutoff discipline)
```

**Do:**
- Tie recognized revenue to the **performance obligation** (point-in-time vs. over-time), not to the invoice or the cash receipt.
- Maintain the **deferred-revenue (contract-liability) roll-forward** so opening + billings − recognized = closing ties every period.
- **Label the basis** on every revenue figure — recognized (GAAP) vs. bookings vs. billings vs. ARR — and never blend GAAP and management views silently (house opinion #12).

**Don't:**
- Recognize revenue on cash receipt for a multi-period obligation — that is the deferred-revenue error.
- Carry deferred revenue without a roll-forward (the controller's named anti-pattern).
- Mix bookings/ARR into a "revenue" line, or present a management-view revenue figure as if it were the GAAP number.

## Edge cases / when the rule does NOT apply

- **Point-of-sale / pure transactional revenue** with no future obligation recognizes at the moment of sale — there is no deferral, and the roll-forward is trivial. The rule attaches wherever a performance obligation spans periods.
- **Management-view metrics (ARR, NRR, bookings)** are legitimate and useful — the rule is not to *suppress* them but to **label** them and never present them as recognized GAAP revenue (this is house opinion #12, not a ban).
- **Variable consideration, rebates, and right-of-return reserves** add estimation on top of the trigger; the policy still states the basis, and the estimate carries its own documented assumption.

## See also

- [`./controller-reconcile-the-subledger-to-the-gl.md`](./controller-reconcile-the-subledger-to-the-gl.md) — deferred revenue is a sub-ledger that ties to the GL via its roll-forward.
- [`./link-the-three-statements.md`](./link-the-three-statements.md) — deferred-revenue movement is a working-capital source of cash in the CF bridge.
- [`../agents/controller.md`](../agents/controller.md) — deferred-revenue / contract-liability roll-forward surface area; cutoff discipline.
- [`../skills/kpi-definition/SKILL.md`](../skills/kpi-definition/SKILL.md) — ARR vs. recognized-revenue definition discipline.

## Provenance

Codifies the `controller` agent's deferred-revenue / contract-liability surface area and cutoff discipline and the "deferred revenue without a contract-liability roll-forward" anti-pattern ([`../agents/controller.md`](../agents/controller.md)), plus house opinion #12 (GAAP/IFRS vs. management view — state which, don't blend) in [`../CLAUDE.md`](../CLAUDE.md) §3. The ASC 606 performance-obligation framing is the standard US-GAAP revenue model; specific standard mechanics are stated as a framing, not as engagement advice — verify against the current standard for a live engagement.

---

_Last reviewed: 2026-05-30 by `claude`_
