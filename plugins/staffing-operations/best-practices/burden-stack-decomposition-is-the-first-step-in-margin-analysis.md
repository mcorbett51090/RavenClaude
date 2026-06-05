# Burden Stack Decomposition Is the First Step in Margin Analysis

**Status:** Primary diagnostic
**Domain:** Staffing operations
**Applies to:** `staffing-operations`

---

## Why this exists

A gross margin that is declining may not be a pricing problem. In healthcare and education staffing, the burden stack — taxes, insurance, housing/per-diem stipends, malpractice coverage, credentialing costs, and bench/idle time — is the line that moves first when market conditions shift. A travel-nurse housing allowance that rose 15% in a high-rent market, or a malpractice premium increase for a locums division, compresses margin without touching bill rates or pay rates. Declaring it a pricing problem before decomposing the burden stack results in the wrong fix.

## How to apply

Run a burden stack decomposition before any margin-improvement initiative:

```
Burden Stack Decomposition
───────────────────────────
Period:   ________________
Segment:  [ ] Travel nursing  [ ] Allied  [ ] Per-diem  [ ] Locum  [ ] School-based
Division / desk:  ________________

Bill rate (per hour or assignment):          $______
  Less: pay rate                            ($______)
  Gross spread:                              $______  (__% of bill)

Burden components:
  Payroll taxes (FICA, FUTA, SUTA):         ($______)
  Workers comp insurance:                   ($______)
  Benefits (health, dental, PTO if any):    ($______)
  Housing / per-diem stipend (travel):      ($______)  ← most volatile for travel
  Malpractice / professional liability:     ($______)  ← locums + allied
  Credentialing / compliance cost:          ($______)
  Recruiter commission / bonus:             ($______)
  Bench / idle time allocation:             ($______)
  Other burden:                             ($______)
Total burden:                               ($______)  (__% of bill)

Net margin (contribution per placement):     $______  (__% of bill)

YoY change in burden (component by component):
  [Component most changed]:  $____ / ___% change
  Cause:  ________________
```

**Do:**
- Calculate burden as a percentage of the bill rate, not a percentage of pay rate — bill rate is the revenue denominator; pay rate is not.
- Compare burden components to the prior period to isolate which line moved; a blended margin change explanation is not actionable.
- Route housing/stipend changes to the healthcare specialist — IRS travel-nurse stipend rules and housing allowance calculation are regulatory, not just pricing.

**Don't:**
- Call a margin problem a "bill rate problem" before running this decomposition — the source of the change determines the fix.
- Compare gross spread (bill minus pay) across segments without adjusting for burden differences by segment — travel-nurse burden is structurally higher than per-diem burden.
- Omit bench/idle time from the burden stack — unplaced days between assignments are a real cost that belongs in the margin calculation.

## Edge cases / when the rule does NOT apply

Direct-hire and search-fee work has no burden stack in the traditional sense (no W-2 workers); the margin analysis for those models focuses on revenue-per-search and time-to-fill efficiency rather than a bill/pay/burden decomposition.

## See also

- [`../agents/healthcare-staffing-specialist.md`](../agents/healthcare-staffing-specialist.md) — owns travel/per-diem/locum burden mechanics including stipend compliance.
- [`./decompose-margin-before-calling-it-pricing.md`](./decompose-margin-before-calling-it-pricing.md) — the governing rule on decomposing margin before any repricing action.

## Provenance

Codifies CLAUDE.md §3 #3 (margin is bill-rate minus pay-rate minus burden — name all three) with a structured decomposition instrument. Burden-stack decomposition is a standard healthcare staffing analytics practice and is the methodology underlying gross-margin analysis in staffing P&L reporting [unverified — training knowledge].

---

_Last reviewed: 2026-06-05 by `claude`_
