# Timely Filing Deadlines Are Hard Stops, Not Soft Targets

**Status:** Absolute rule
**Domain:** Claims management / revenue cycle
**Applies to:** `medical-revenue-cycle`

---

## Why this exists

Timely filing deadlines — the payer-specific window within which a claim must be submitted after the date of service — are contractual and regulatory hard stops. A claim filed after the timely filing limit is denied, and that denial is generally not appealable with a clinical argument: the deadline passed, and the money is permanently lost. Timely filing deadlines vary by payer and plan (Medicare: 12 months; commercial payers: commonly 90 days to 12 months depending on the contract) and are often shorter for corrected claims and secondary claims. The loss from missed timely filing is 100% of the allowed amount on every affected claim — it is the most complete revenue loss possible.

## How to apply

Build timely filing tracking into the claims management workflow with a mandatory escalation trigger.

```
Timely filing risk management:
1. Maintain a payer timely filing deadline matrix:
   - Column: Payer / Plan
   - Column: Original claim deadline (days from DOS)
   - Column: Corrected claim deadline (days from original remit or denial)
   - Column: Secondary claim deadline (days from primary EOB/remit)
   Update: annually and when a new payer contract is executed

2. Claims age monitoring (run daily or weekly):
   - Flag: any claim approaching 60% of its timely filing window without payment or denial
   - Flag: any claim at 80% of its timely filing window → escalation to billing manager
   - Flag: any claim at 90% of its timely filing window → same-day intervention required

3. Root causes tracked for timely filing denials:
   - Charge capture lag (see charge-capture-lag rule) → upstream fix
   - Claim held for authorization/documentation → release or override and document
   - Wrong payer information → eligibility verification failure at front end
   - Payer credentialing gap (provider not yet credentialed) → credentialing operations issue

4. Timely filing write-off report (monthly):
   - Dollar amount written off for timely filing by payer and root cause
   - Any month with >$5,000 in timely filing write-offs → root cause investigation and
     corrective action plan within 30 days

Proof of timely filing:
   - Keep the claim submission date and clearinghouse acceptance timestamp
   - These are the evidence for a timely filing appeal if the payer erroneously denies
     a claim that was filed on time
```

**Do:**
- File a claim even if documentation is incomplete rather than risk missing the timely filing window — file with available information and correct with an amended claim.
- Retain electronic clearinghouse submission confirmations as the legal evidence of timely filing.
- Configure the PM/billing system to flag claims by remaining timely filing days, not only by age in days.

**Don't:**
- Hold a claim waiting for documentation that may not arrive in time — the timely filing loss is 100%; file and correct.
- Assume that a payer's "grace period" practice equals a policy — only the written contract is legally binding.
- Treat timely filing write-offs as an ordinary adjustment category without root-cause investigation — each write-off is 100% avoidable in principle.

## Edge cases / when the rule does NOT apply

Medicare's timely filing deadline of 12 months is among the most generous in the industry; for most commercial contracts the window is shorter and requires more active management. Some FQHC and Medicaid programs have state-specific rules — confirm the applicable window for each program.

## See also

- [`../agents/denials-management-specialist.md`](../agents/denials-management-specialist.md) — timely filing denials are a denial category with a specific root cause set and a 100% write-off outcome.
- [`./charge-capture-lag-is-a-hidden-revenue-leak.md`](./charge-capture-lag-is-a-hidden-revenue-leak.md) — charge capture lag is the most common upstream cause of timely filing risk.

## Provenance

Grounded in standard payer contract terms, Medicare Claims Processing Manual (CMS Pub. 100-04, Ch. 1), and state Medicaid program claims submission requirements; timely filing deadline windows are [unverified — training knowledge] and must be confirmed against each payer's current contract and provider manual.

---

_Last reviewed: 2026-06-05 by `claude`_
