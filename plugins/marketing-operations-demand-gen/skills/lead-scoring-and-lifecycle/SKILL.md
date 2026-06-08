---
description: "Design and implement a lead scoring model and lifecycle stage framework: demographic/firmographic fit scoring, behavioral engagement scoring, recency decay, negative scoring, the MQL threshold, and the lifecycle stage model (Subscriber → MQL → SAL → SQL → Opportunity) with entry/exit criteria."
---

# Lead Scoring and Lifecycle

**Purpose:** turn an undifferentiated contact database into a scored, staged funnel where Sales
receives only leads that meet a bilateral MQL definition — with scoring that reflects current
intent, not historical noise.

## Step 1 — Agree on the lifecycle stage model

Define stages, entry criteria, and exit criteria before touching any scoring configuration.

| Stage | Entry criteria | Exit criteria |
|---|---|---|
| **Subscriber** | Any opted-in contact (source agnostic) | Meets fit threshold (Score-A or Score-B) OR a qualifying behavior |
| **Lead** | Fits ICP minimally (industry, company size) | Score reaches MQL threshold OR hand-raise |
| **MQL** | Score ≥ MQL threshold (bilateral) OR bypass rule met | SAL accepted by Sales (→ SAL) OR rejected with taxonomy reason |
| **SAL** | Sales has accepted and is working the lead | Sales converts to opportunity (→ SQL/Opp) OR recycles (→ Lead) |
| **SQL / Opportunity** | Sales has qualified: budget, authority, need, timeline | Closed-Won, Closed-Lost, or Nurture/Recycle |

Jointly document bypass rules (direct Sales request, event lead, executive referral) and the
recycling path (rejected MQL → back to nurture, not discarded).

## Step 2 — Design the scoring model

### Demographic / firmographic fit score (who they are)

Score the lead's fit against the ICP:

| Attribute | Score range | Notes |
|---|---|---|
| Job title / seniority | 0–20 | Decision-maker vs influencer vs user vs irrelevant |
| Company size | 0–10 | Sweet-spot band gets max score |
| Industry | 0–10 | Tier-1 ICP industry vs adjacent vs out-of-ICP |
| Geography | 0–5 | Serviceable region vs out-of-territory |
| Technology (technographic) | 0–10 | Complementary stack signal (e.g., uses Salesforce) |

**Ceiling at 50 points.** Fit score rarely exceeds this; behavior drives MQL graduation.

### Behavioral engagement score (what they did)

Score actions that signal purchase intent:

| Action | Score | Decay |
|---|---|---|
| Pricing page visit | +15 | 30-day half-life |
| Demo request (form submit) | +25 | No decay (hand-raise) |
| Product trial start | +25 | No decay |
| High-intent content download (ROI calculator, comparison guide) | +10 | 60-day half-life |
| Webinar/event attendance | +8 | 90-day half-life |
| Email click | +3 | 90-day half-life |
| Email open only | +1 | 120-day half-life |
| Website visit (non-pricing) | +2 | 90-day half-life |

### Negative scoring (who became cold or disqualified)

| Signal | Score |
|---|---|
| No email activity in 90 days | −10 |
| No website activity in 120 days | −15 |
| Unsubscribe attempt | −25 (+ suppress) |
| Competitor email domain detected | −50 (+ flag) |
| Bounce (hard) | Remove from scoring; suppress |

### Composite score and MQL threshold

`Composite Score = Fit Score + Behavior Score + Negative Adjustments`

- MQL threshold: typically 50–75 composite (bilateral negotiation with Sales — do not set unilaterally [verify-at-use]).
- Review the threshold quarterly in the scoring committee. If Sales rejects >30% of MQLs as unqualified, lower the threshold or tighten fit criteria.

## Step 3 — Implement recency decay

Behavioral scores decay over time. Implement either:

- **Time-based decay:** each behavioral point has a half-life (see table above). Recalculate nightly.
- **Activity-reset decay:** inactivity for N days triggers a score reduction (see negative scoring).

In HubSpot, use Workflows + calculated properties. In Marketo, use the Scoring Program with periodic
decay Smart Campaigns. In Pardot, use Automation Rules for recency adjustments [verify-at-use].

## Step 4 — Wire the MQL trigger

When composite score ≥ MQL threshold:
1. Change lifecycle stage to MQL.
2. Assign to the correct Sales owner (round-robin, territory, or account-based routing).
3. Trigger the speed-to-lead SLA timer (alert Sales if unworked after the SLA window).
4. Notify the SDR/AE via Slack/email with the contact's score composition and recent activity.

## Anti-patterns

- A MQL threshold set by Marketing without Sales buy-in.
- Behavioral scores that never decay — rewarding contacts for activity from 18 months ago.
- No negative scoring — the score only ever goes up.
- Lead scoring in the MAP with no CRM sync — Sales sees the lead but not the score context.
- Demographic-only scoring — job title gets a contact to MQL with zero behavioral signal.

## Output

A lead scoring configuration document (attribute table, score values, decay rules, MQL threshold,
bypass rules) ready for implementation in the MAP, plus the lifecycle stage model with entry/exit
criteria. Use the scoring review cadence (quarterly) and the Sales rejection taxonomy to maintain
the model after launch.
