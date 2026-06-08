---
description: "Run rent collection and delinquency management: monthly collection cycle, late-fee enforcement, delinquency triage and action ladder (days 1–45+), payment arrangement design, legal notice coordination, and bad-debt write-off. Covers economic occupancy impact, consistent-application rules, and the documentation discipline needed to support eviction filing."
---

# Rent Collection and Delinquency

**Purpose:** collect rent consistently, contact delinquent accounts early and firmly, follow a
documented action ladder, and protect economic occupancy — the real performance metric.

---

## The collection cycle

### Pre-due-date (days -5 to 0)

- PM software auto-charges or sends a payment reminder (depending on configuration).
- Residents on autopay: confirm payment method is active.
- Residents not on autopay: reminder notice via portal / email.

### Due date and grace period

- Rent due on the 1st (or per lease). Most leases provide a 3–5 day grace period.
- **Do not waive the grace period for repeat late payers** — documented, consistent enforcement is
  the baseline for later legal action. If the grace period is waived for one resident and not
  another, apply the same standard to all.

### Day 1 of delinquency (day after grace period expires)

- Late fee assessed automatically in PM software (per lease and per jurisdiction limits).
- Auto-generated late notice delivered via tenant portal + email.
- PM reviews the delinquency report — flag any balance > $500 or any resident with 2+ prior late
  payments for immediate manual follow-up.

---

## The delinquency action ladder

| Day | Action | Owner | Documentation |
| --- | --- | --- | --- |
| **1–3** | Late fee assessed; auto-notice sent; delinquency report reviewed | PM software + PM | Automated log in PM software |
| **3–5** | Manual contact attempt: call + portal message. Inquire about payment or payment arrangement | PM | Log contact attempt in tenant file |
| **5–10** | Second contact if no response. Escalate to property manager if resident contact not made | PM | Log in tenant file |
| **10–14** | Payment arrangement decision: if resident has good history and a credible plan, a written arrangement (amount + date + consequences) may be appropriate. Otherwise proceed to notice. | PM or owner decision | Written payment arrangement agreement in tenant file |
| **14–21** | Issue statutory pay-or-quit notice (timeline varies by jurisdiction — confirm at use). Notice must comply with state law: form, delivery method, cure period. | PM | Copy of notice + proof of delivery in tenant file |
| **21–30** | If unpaid after notice period expires: consult landlord-tenant attorney for filing decision. Prepare documentation package. | PM + counsel | Full tenant file ready for filing |
| **30–45+** | Eviction filing (per attorney direction). Resident may pay in full through this period — accept payment, adjust status, document. | Attorney + PM | Court filing record |

**Key rule:** work the ladder in order. Skipping steps creates documentation gaps that undermine
eviction filings. Every contact, every notice, and every payment arrangement is documented in the
tenant file.

---

## Payment arrangements

A payment arrangement is appropriate when:
- The resident has a payment history of ≤1 prior late payment in the last 12 months, AND
- The total balance is ≤ 1.5 months rent, AND
- The resident provides a specific, credible payment plan (not "I'll get it to you soon").

A payment arrangement must be in writing: amount owed, payment schedule (dates + amounts),
consequence of default (revert to eviction filing with no further arrangements offered).

**Apply payment arrangement criteria consistently.** If arrangements are offered to some residents
and not others with similar histories, document the distinguishing factor or apply the same
standard to all.

---

## Collection tools and integrations

| Tool category | Examples (2026) [verify-at-use] | Use for |
| --- | --- | --- |
| PM software (native collection) | AppFolio, Buildium, Yardi Breeze, Rent Manager | Automated late fees, ACH collection, delinquency reporting, notice generation |
| Online payment portals | PayLease (Zego), PayNearMe, Forte | Resident-facing payment convenience |
| Collections / skip trace | PM-integrated collections modules; third-party collections agencies | 45+ day balances post-move-out |

---

## Economic occupancy impact

Every dollar of uncollected rent reduces economic occupancy:

```
Economic occupancy = (Collected rent) / (Gross potential rent)
```

A 5-unit delinquency situation on a $1,500/month average rent = $7,500/month in gross potential
lost. If the portfolio has 100 units at $1,500 average, gross potential = $150,000/month. Five
delinquent units = 95% physical, but potentially 90–92% economic occupancy. Report the gap to
`pm-ops-lead`.

Use `scripts/pm_calc.py` → `delinquency_rate()` and `economic_occupancy()` for the calculations.

---

## Anti-patterns

- Delinquency not contacted until day 10+ — silent non-payment is not a strategy.
- Payment arrangements offered verbally with no written agreement.
- Inconsistent enforcement: grace-period waivers, late-fee waivers, and payment arrangements
  applied inconsistently create fair-housing and credibility risks.
- Legal notice issued without verifying jurisdiction-specific form, timeline, and delivery
  requirements.
- Tenant file missing contact logs, notice copies, and arrangement agreements — the eviction filing
  will be weak without them.

---

## Output

A delinquency action plan for a specific resident or portfolio segment, a payment arrangement
document, a delinquency report with economic occupancy impact, or an action-ladder process design.
Structured Output Protocol block per `ravenclaude-core`.
