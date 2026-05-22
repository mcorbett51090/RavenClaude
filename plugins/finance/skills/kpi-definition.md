---
name: kpi-definition
description: Define KPIs that survive cross-team disagreement — single owner, single formula, single source of truth, decay-tested, documented in a KPI dictionary. Reach for this skill when launching a new metric, when two teams cite different numbers for "the same" KPI, when an exec asks "why doesn't this tie?", or when standing up a KPI pack. Used by `fpa-analyst` (primary) and `board-pack-composer`.
---

# Skill: kpi-definition

**Purpose:** Operational KPIs decide hiring, comp, board confidence, and capital allocation. A KPI without a defensible definition is a fight waiting to happen. Used by `fpa-analyst` (primary).

## When to use

- Standing up a new KPI for a business / function
- Resolving "ARR is X" vs "ARR is Y" between two teams
- Standing up a KPI pack or operating cadence
- Pre-audit when a non-GAAP measure is reported externally
- Pre-board / pre-investor cycle to lock the period's definitions
- Annual / quarterly KPI dictionary refresh

## The KPI dictionary entry

Every KPI ships with a dictionary entry. Anything less is folklore.

```markdown
# KPI: <name>

**Definition:** <one-sentence plain English>

**Formula:** <unambiguous arithmetic / SQL>

**Source data:** <system + table + filter + as-of>

**Owner:** <named person + role>

**Refresh cadence:** <daily / weekly / monthly / quarterly>

**Inclusion / exclusion rules:** <what's in, what's out, with reason>

**Effective date / version history:** <YYYY-MM-DD definition v1; YYYY-MM-DD revised to v2 because Z>

**Cross-checks:** <what reconciles to this metric and at what frequency>

**Known limitations:** <what this KPI does NOT tell you>
```

## Six properties of a defensible KPI

A KPI that passes scrutiny has all six:

| Property | Test |
|---|---|
| **Unambiguously defined** | Two analysts with the same source data compute the same number |
| **Strategically relevant** | Ties to a documented company strategy or operating objective — not a vanity metric |
| **Sensitive to action** | Leadership can move this in 1-2 quarters via decisions they control |
| **Trend-readable** | A multi-period view tells a story, not just noise |
| **Reconciled** | Reconciles or cross-checks against at least one other authoritative source (GL, billing system, CRM) |
| **Auditable** | Source query / extract / formula is reproducible without consulting the original author |

KPIs that fail two or more of these are candidates for retirement.

## Canonical KPI definitions: the SaaS set

These are the most-contested KPIs in finance. Each comes with a sharp definition + the common mistake.

### ARR — Annual Recurring Revenue

**Definition:** Annualized contracted revenue from recurring subscriptions at the measurement date.

**Formula:**
```
ARR = Σ (active subscription's monthly recurring revenue × 12) at measurement date
```

**Include:** committed subscription revenue under signed contracts with active service.

**Exclude:** one-time services, set-up fees, professional services, hardware sales, expired contracts not yet renewed, contracts in opt-out / cancellation.

**Common mistake:** counting deferred revenue release as ARR (that's a P&L item). ARR is a snapshot; deferred revenue is a roll. Different things.

**Cross-check:** ARR end-of-period should reconcile to billing-system + CRM contract data; not to GL revenue (which has timing and recognition differences).

### NRR / NDR — Net Revenue Retention / Net Dollar Retention

**Definition:** Trailing-12-month ARR retained + expanded from a fixed customer cohort, divided by the cohort's starting ARR.

**Formula:**
```
NRR_t = (Cohort_ARR_t) / (Cohort_ARR_(t-12))
Where:
  Cohort = customers in the book on the measurement date 12 months prior
  Cohort_ARR_t = current ARR from those same customers (downgrades + churn + expansion all in)
```

**Common mistake:** including new customers acquired during the period. NRR is cohort-locked.

**Industry benchmarks (2026):** > 110% is good, > 120% is excellent, > 130% is unusual.

### Gross Logo Retention

**Definition:** Percent of customers in the starting cohort still active at end of period.

**Formula:**
```
Gross Logo Retention_t = Cohort active customers_t / Cohort customers_(t-12)
```

**Common mistake:** weighting by ARR (that's revenue retention, not logo retention).

### LTV, CAC, LTV/CAC, Payback

**Customer LTV** (subscription):
```
LTV = Gross profit per customer per month × (1 / monthly gross logo churn rate)
```

**CAC**:
```
CAC = (Sales + Marketing expense in period) / (New logos acquired in same period)
```

**Payback period:**
```
Payback (months) = CAC / Monthly gross profit per customer
```

**Common mistake:** including expansion in CAC denominator (expansion isn't customer acquisition). And: claiming LTV/CAC > 5 in early-stage businesses where the LTV horizon assumes 10-year retention before 3-year data exists.

### Magic Number

```
Magic Number = (Net new ARR × 4) / S&M expense in prior quarter
```

A measure of sales efficiency. > 1.0 generally signals investing-mode; < 0.5 signals sales motion stress.

### Cash Burn / Net Burn

```
Net burn = Beginning cash - Ending cash (period)
         (excluding non-operating events like fundraises, M&A consideration)
```

**Common mistake:** including a fundraise inflow in net burn. Separate operating burn from financing flows.

## Operating KPIs by department

### Sales

- **Quota attainment** — sum of attained / sum of assigned, by rep, by team, by period
- **Pipeline coverage** — open pipeline value / quarterly quota target (typical guidance: 3-4× coverage)
- **Win rate** — deals won / deals decisioned (won + lost), with conversion-stage segmentation
- **Sales cycle** — median days from Stage X to Closed-Won, with quartile distribution

### Marketing

- **MQL → SQL conversion rate** — qualified leads passed to sales / total marketing leads
- **CPL by channel** — cost per qualified lead, segmented by acquisition channel
- **Marketing-sourced pipeline %** — pipeline $ attributed to marketing-originated leads / total pipeline $
- **Brand vs demand split** — top-of-funnel awareness investment / total marketing investment

### Customer Success

- **Onboarding TTV** — median days from contract signature to first value-event (defined per product)
- **CSAT / NPS** — survey scores with response-rate context (sub-30% response rates are noisy)
- **Renewal rate** — logos renewed / logos eligible for renewal in the period

### Engineering / Product

- **Velocity** — story points or items shipped per sprint, trended (avoid quarter-to-quarter comp due to org changes)
- **Cycle time** — median time from work-started to production-deployed
- **Reliability** — error rate, uptime %, mean-time-to-recover
- **Adoption** — DAU / MAU, feature-adoption % among eligible users

### Operations / Finance

- **Cash conversion cycle** — DSO + DIO − DPO (lower = better cash discipline)
- **Operating margin** — operating income / revenue
- **Rule of 40** (SaaS) — Revenue growth % + Operating margin %; > 40 is industry-good

## Reconciliation discipline

Every KPI in the dictionary lists at least one cross-check:

| KPI | Reconciles to |
|---|---|
| ARR | Billing-system contract data + CRM closed-won data |
| GAAP revenue | GL revenue accounts |
| Deferred revenue | GL balance + billing-system unrecognized billings |
| Customer count | CRM active accounts |
| Headcount | HR system payroll feed |
| Cash | Bank statements + GL cash |

When two systems disagree, the resolution is documented (not the disagreement papered-over). State which is authoritative for the KPI and why.

## Versioning + change discipline

KPI definitions can change. When they do:

1. Bump the version (e.g., ARR v1 → ARR v2)
2. Document the change, the date, and the reason
3. **Restate prior periods** under the new definition for trend comparability (or footnote the discontinuity prominently)
4. Communicate to dependent reports (board pack, investor update, KPI pack)

**Anti-pattern:** changing a KPI definition silently mid-year. Auditors and boards lose trust faster from definition changes than from bad numbers.

## Common failure modes

- **One KPI, three definitions** — Sales says ARR is X (includes services), Finance says Y (excludes services), Board pack uses Z. Define once; all reports inherit.
- **Vanity metrics** — "Total registered users" with no path to revenue. Strategically irrelevant.
- **Insensitive metrics** — leadership cannot move it in a quarter (e.g., "brand awareness in untested markets"). Useful for tracking, not for OKRs.
- **KPI without an owner** — nobody refreshes it; over time it drifts from reality.
- **No effective date** — when did this definition start applying? Auditors will ask.
- **Missing limitations** — every KPI has limitations. CSAT in a 5% response sample tells you less than the response-weighted average over 5 quarters.
- **Cross-check absent** — the KPI floats; one bad query and the number is wrong forever.

## KPI hygiene checklist

Before a KPI enters the dictionary:

- [ ] Definition written in plain English (one sentence)
- [ ] Formula unambiguous (no "approximately", no "roughly")
- [ ] Source system + table + filter named
- [ ] Owner named (person + role; not "the team")
- [ ] Refresh cadence stated
- [ ] Inclusion / exclusion rules explicit
- [ ] Cross-check identified (at least one)
- [ ] Known limitations stated
- [ ] Effective date + version recorded
- [ ] Reviewed by at least one consumer (sales / marketing / CS / eng) to confirm the definition matches their understanding

## See also

- Skill: [`./variance-commentary.md`](./variance-commentary.md) — KPI commentary uses these definitions
- Skill: [`./board-pack-composition.md`](./board-pack-composition.md) — KPIs on the front 5-7 slides
- Skill: [`./driver-based-forecasting.md`](./driver-based-forecasting.md) — KPI drivers feed the forecast
- Template: [`../templates/kpi-pack-template.md`](../templates/kpi-pack-template.md)
- Agent: [`../agents/fpa-analyst.md`](../agents/fpa-analyst.md)
- Agent: [`../agents/board-pack-composer.md`](../agents/board-pack-composer.md)
