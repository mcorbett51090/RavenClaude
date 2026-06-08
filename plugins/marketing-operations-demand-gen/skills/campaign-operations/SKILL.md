---
description: "Run campaign operations end-to-end: apply the campaign taxonomy, enforce UTM parameter standards, set up the campaign in the MAP and CRM, manage the campaign cost ledger, execute the launch checklist, and close out with a campaign performance report."
---

# Campaign Operations

**Purpose:** give every campaign a clean operational spine — taxonomy, tracking, cost accounting,
and a documented launch/close-out process — so that attribution, reporting, and budget reconciliation
work without heroics.

## Step 1 — Apply the campaign taxonomy

Every campaign has a canonical name before any asset is created. Use the taxonomy:

```
[Year]-[Quarter]-[Segment]-[Motion]-[Name]
Example: 2026-Q3-ENT-ABM-Salesforce-Admin-Series
```

| Dimension | Values |
|---|---|
| Year / Quarter | 2026-Q3 (ISO format) |
| Segment | ENT (Enterprise), MM (Mid-Market), SMB, PLG (Product-Led) |
| Motion | ABM, Inbound, Outbound, Event, Partner, Nurture |
| Name | Short human-readable label (kebab-case) |

This name seeds the `utm_campaign` value, the CRM campaign record, and the cost ledger line.

## Step 2 — Set up UTM parameters

Every external campaign link carries the full UTM string. Mandatory parameters:

| Parameter | Convention | Example |
|---|---|---|
| `utm_source` | Channel origin, lowercase | `linkedin`, `google`, `newsletter` |
| `utm_medium` | Traffic type, lowercase | `cpc`, `email`, `social`, `organic` |
| `utm_campaign` | Campaign name from taxonomy, kebab-case | `2026-q3-ent-abm-salesforce-admin-series` |
| `utm_content` | Creative variant (optional but required for A/B) | `headline-v1` |
| `utm_term` | Paid keyword (paid search only) | `salesforce-crm-integration` |

Use the URL builder in `templates/utm-taxonomy.md`. Validate all links before launch with the QA
checklist: no spaces (encode as `%20`), no mixed case, no missing source/medium on any tracked link.

## Step 3 — Create the campaign record in the MAP and CRM

### MAP setup (HubSpot / Marketo / Pardot)

1. Create a Campaign / Program in the MAP with the canonical name.
2. Set the campaign type (Email, Paid, Event, Content, Webinar).
3. Configure the success criteria (form fill, registration, attendance, demo request).
4. Wire the UTM capture fields to the MAP form or landing page.
5. Set the campaign member status progression (Sent → Opened → Clicked → Responded → MQL).

### CRM setup (Salesforce / HubSpot)

1. Create the Campaign record in Salesforce or the equivalent HubSpot Deal object association.
2. Set start/end dates, campaign type, and expected response.
3. Set the campaign budget line (link to cost ledger).
4. Enable Campaign Influence (Salesforce: Primary Campaign Source + multi-touch influence model).

## Step 4 — Maintain the campaign cost ledger

One source of truth for spend — typically the finance system or a dedicated campaign cost tracker:

| Field | Required |
|---|---|
| Campaign name (canonical) | Yes |
| Channel | Yes |
| Budget approved | Yes |
| Spend to date | Yes (updated weekly) |
| Vendor / publisher | Yes |
| Invoice date | Yes |
| Finance GL code | Yes |
| Notes | Optional |

**Reconcile weekly against paid-channel dashboards (Google Ads, LinkedIn Campaign Manager).**
Discrepancies > 5% require investigation before the next budget cycle. Never use paid-channel
dashboard spend as the source of truth without reconciling to the invoice.

## Step 5 — Execute the launch checklist

Before any campaign goes live:

- [ ] Canonical name applied in MAP, CRM, and cost ledger (consistent across all three).
- [ ] UTM parameters set on all external links; URL builder used; QA checklist passed.
- [ ] CRM Campaign record created with budget and influence model enabled.
- [ ] Suppression lists applied: current customers, active opportunities (if appropriate), competitors, unsubscribes.
- [ ] Consent / opt-in status verified for email sends (CAN-SPAM, GDPR, CASL [verify-at-use]).
- [ ] Test send / preview completed (MAP) or ad preview reviewed (paid).
- [ ] Sales notified of any campaign that will surface MQLs (pipeline alignment).

## Step 6 — Campaign close-out and performance report

At campaign end (or at the 30/60/90 day mark for always-on campaigns):

| Metric | Notes |
|---|---|
| Spend vs budget | Variance; explain if >10% |
| MQLs generated | Count and MQL conversion rate |
| SQLs from this campaign | CRM Campaign Influence data |
| Pipeline attributed | Under named attribution model |
| Pipeline-to-spend ratio | ≥ 3× is a common B2B target [verify-at-use] |
| Cost per MQL | Spend ÷ MQLs |
| Cost per SQL | Spend ÷ SQLs |

Always name the attribution model in the close-out report.

## Anti-patterns

- Campaign names set ad hoc without taxonomy — breaks UTM → CRM matching.
- Missing `utm_source` or `utm_medium` on any external link.
- Two cost sources for the same campaign (dashboard spend vs invoice vs spreadsheet).
- No suppression list applied to email sends.
- Campaign records in MAP and CRM with different names — breaks campaign influence reporting.
- Close-out report without the attribution model named.

## Output

A campaign operations checklist (taxonomy, UTM, MAP/CRM setup, cost ledger entry, launch QA,
close-out report) — usable as a repeatable runbook for every campaign launch.
