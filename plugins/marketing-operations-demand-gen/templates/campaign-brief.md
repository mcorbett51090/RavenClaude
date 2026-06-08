# Campaign Brief

> **Instructions:** fill every section before a campaign enters production. This document is the
> single source of truth for campaign intent, audience, budget, tracking, and success criteria.
> Share with all stakeholders (Marketing, Sales, RevOps) before launch.

---

## Campaign identity

| Field | Value |
|---|---|
| **Canonical campaign name** | `[Year]-[Quarter]-[Segment]-[Motion]-[Name]` (e.g. `2026-Q3-ENT-ABM-Salesforce-Admin-Series`) |
| **Campaign owner** | `[Name, role]` |
| **Campaign type** | `[ABM / Inbound / Outbound / Event / Partner / Nurture / Brand]` |
| **Dates** | Start: `YYYY-MM-DD` · End: `YYYY-MM-DD` |
| **Status** | `[Draft / Approved / Live / Complete]` |

---

## Objective and pipeline target

**Campaign objective (one sentence):**
> `[What does this campaign accomplish? E.g. "Generate 40 MQLs from enterprise Salesforce admins for the integration product line in Q3."]`

| Metric | Target | Notes |
|---|---|---|
| MQLs generated | `[N]` | Based on `[X]`% conversion from `[Y]` responses |
| SQLs from campaign | `[N]` | Based on `[X]`% MQL→SQL rate (bilateral estimate) |
| Pipeline attributed | `$[N]` | Under `[named attribution model]` |
| Pipeline-to-spend ratio | `[N]`× | Target ≥ 3× [verify-at-use] |
| Cost per MQL | `$[N]` | Budget ÷ target MQLs |

> **Attribution model:** `[Name the model — e.g. W-shaped, linear, first-touch. Required.]`

---

## ICP target audience

**Segment:** `[ENT / MM / SMB / PLG]`

| Firmographic | Value |
|---|---|
| Industry | `[e.g. SaaS, Financial Services, Healthcare]` |
| Company size | `[e.g. 200–2,000 employees]` |
| Geography | `[e.g. North America]` |
| Technology signal | `[e.g. uses Salesforce CRM]` |

**Persona / job titles:**
- Primary: `[e.g. Marketing Ops Manager, VP Marketing]`
- Secondary: `[e.g. Demand Gen Manager]`
- Excluded: `[e.g. Competitor domains, current customers (suppress)]`

---

## Channel mix and budget

| Channel | Tactic | Budget | Owner |
|---|---|---|---|
| `[e.g. LinkedIn Ads]` | `[e.g. Sponsored Content]` | `$[N]` | `[Name]` |
| `[e.g. Email Nurture]` | `[e.g. 3-email sequence]` | `$[N]` | `[Name]` |
| `[e.g. Event / Webinar]` | `[e.g. Live webinar]` | `$[N]` | `[Name]` |
| **Total** | | `$[N]` | |

**Cost ledger entry:** `[Confirm entered in campaign cost tracker with GL code: ______]`

---

## UTM parameters

> All external links must carry the full UTM set. Use the URL builder in `templates/utm-taxonomy.md`.

| Parameter | Value |
|---|---|
| `utm_source` | `[e.g. linkedin]` |
| `utm_medium` | `[e.g. cpc, email, social]` |
| `utm_campaign` | `[Canonical campaign name in kebab-case, lowercase]` |
| `utm_content` | `[Creative variant, if A/B testing]` |
| `utm_term` | `[Paid keyword, paid search only]` |

**UTM QA status:** `[ ] All links validated — no spaces, correct casing, all required params present`

---

## Marketing automation setup

**MAP platform:** `[HubSpot / Marketo / Pardot]`

| Setting | Value |
|---|---|
| Program / campaign name in MAP | `[Must match canonical name]` |
| Entry criteria | `[Who enters this program?]` |
| Success criteria | `[What counts as a response? e.g. form fill, demo request]` |
| Suppression list | `[Current customers: Y/N · Active opps: Y/N · Unsubscribes: Y/N · Competitors: Y/N]` |
| Consent / opt-in verified | `[ ] Yes — opt-in status confirmed for all email sends` |
| MQL routing trigger | `[Score threshold or bypass rule that fires when response is recorded]` |

---

## CRM campaign record

**CRM platform:** `[Salesforce / HubSpot]`

| Setting | Value |
|---|---|
| CRM campaign name | `[Must match canonical name]` |
| Campaign type | `[Email / Event / Paid / Content / Webinar]` |
| Budget in CRM | `$[N]` |
| Attribution model enabled | `[Primary Campaign Source / Multi-touch / Named model]` |

---

## Launch checklist

- [ ] Canonical name applied in MAP, CRM, and cost ledger.
- [ ] UTM parameters set on all external links; QA checklist passed.
- [ ] CRM Campaign record created with budget and attribution model enabled.
- [ ] Suppression lists applied (current customers, active opps, unsubscribes, competitors).
- [ ] Consent/opt-in status verified for all email components.
- [ ] Test send / ad preview completed and approved.
- [ ] Sales notified of expected MQL volume and routing logic.
- [ ] Campaign brief signed off by: `[Marketing lead] · [Sales/RevOps counterpart]`

---

## Close-out (fill at campaign end or at 30/60/90 day mark)

| Metric | Actual | vs Target | Notes |
|---|---|---|---|
| Spend | `$[N]` | `[+/- $N]` | |
| MQLs generated | `[N]` | `[+/- N]` | |
| SQLs from campaign | `[N]` | `[+/- N]` | |
| Pipeline attributed | `$[N]` | `[+/- $N]` | Under `[attribution model]` |
| Pipeline-to-spend ratio | `[N]`× | | |
| Cost per MQL | `$[N]` | | |

**Key learnings:**
> `[What worked? What didn't? What should the next campaign do differently?]`
