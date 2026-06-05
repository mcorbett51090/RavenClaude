# Underwriting Guideline Exceptions Need a Documented Reason and a Named Approver

**Status:** Absolute rule
**Domain:** Underwriting governance
**Applies to:** `insurance-pc`

---

## Why this exists

Underwriting guidelines are the distillation of the actuarial pricing model and the portfolio strategy into a set of risk-selection rules. An exception to a guideline — binding a risk outside the stated appetite or above the stated limit — is a deliberate departure from the expected-loss basis on which the rate was set. Undocumented exceptions are invisible to portfolio management until they appear in the loss run; by then, the premium has been collected and the risk is fully bound. Documented exceptions, by contrast, create an audit trail that lets portfolio managers identify patterns (are exceptions concentrated in one broker? one class of risk? one underwriter?), measure their loss emergence, and decide whether the exceptions represent a desirable expansion of the book or a systematic guideline failure.

## How to apply

Every risk written outside the underwriting guidelines generates a documented exception record at binding.

```
Underwriting Exception Record — Required Fields
──────────────────────────────────────────────────────
Policy number / account:   <ID>
Binding date:              YYYY-MM-DD
Guideline violated:        <Quote the specific guideline language or reference number>
Nature of exception:       <e.g., "TIV exceeds per-location limit by $X" / "Adverse
                            loss history — 3 losses in 5 years vs 0-loss guideline">
Underwriter's rationale:   <Why this risk is still acceptable despite the exception:
                            offsetting credits, relationship value, rate adequacy buffer,
                            specific mitigation applied>
Pricing adjustment applied:<Rate loaded by X% to account for exception; or "no adjustment
                            — justify">
Approval authority:        <Named individual + title> (must be senior underwriter or manager
                            if exception exceeds a defined materiality threshold)
Date of approval:          YYYY-MM-DD
Aggregate tracking:        <Note whether this exception type is tracked in the
                            exception log for portfolio review>
```

**Do:**
- Set materiality tiers for approval authority: minor exceptions approved by the underwriting supervisor; major exceptions (above a threshold TIV/premium or adverse loss history) require chief underwriting officer approval.
- Review the exception log quarterly in portfolio management; a rising exception rate in a class signals that the guideline may need revision or the book is drifting out of appetite.
- For programs or delegated authorities, include exception-rate reporting as a standard performance metric in the MGA oversight framework.

**Don't:**
- Allow verbal approvals without a written record; a verbal exception approval disappears when the approver leaves the organization.
- Treat guideline exceptions as routine; if more than ~10–15% of accounts in a class require exceptions, the guidelines are wrong, not the risks.
- Allow an underwriter to approve their own exceptions without a second-level review for exceptions above the materiality threshold.

## Edge cases / when the rule does NOT apply

- **Manuscript / bespoke large-risk accounts** where the guidelines explicitly permit underwriter discretion — the exception framework is replaced by a bespoke account-approval memo; the documentation requirement is the same, the process differs.
- **Market-capacity situations** where no carrier writes within standard guidelines — document the market context and the rate adequacy analysis that supports binding; the exception is the market, but the analysis must still be on record.

## See also

- [`../agents/pc-underwriter.md`](../agents/pc-underwriter.md) — owns the account-level underwriting decision and the exception documentation.
- [`./underwrite-to-the-loss-ratio-not-the-competitors-rate.md`](./underwrite-to-the-loss-ratio-not-the-competitors-rate.md) — the underwriting guideline is the operationalization of loss-ratio targeting; an exception is a departure from that target.

## Provenance

Codifies the pc-underwriter's exception-documentation discipline from the insurance-pc plugin's CLAUDE.md §3 #2 (underwrite to the loss ratio) and §3 #1 (combined ratio is loss plus expense — read both). The tiered approval authority structure and aggregate exception-rate monitoring reflect standard carrier underwriting governance practice.

---

_Last reviewed: 2026-06-05 by `claude`_
