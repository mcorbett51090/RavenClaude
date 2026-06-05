# Grant Pipeline Is a 12-Month Calendar, Not a List of Applications

**Status:** Pattern
**Domain:** Nonprofit fundraising — grants management
**Applies to:** `nonprofit-fundraising`

---

## Why this exists

Most organizations manage their grant portfolio as a reactive list — they track applications submitted and decisions received. A pipeline managed as a rolling 12-month calendar treats grant development as a production workflow: LOIs and proposals have defined lead times, reporting deadlines trigger renewal outreach, and funder-fit qualification happens before any writing hours are committed. The difference in cash-flow predictability and win rate is substantial. An organization whose only active funder relationships are "submitted and waiting" has no visibility into where cash is coming from in Q3 or whether the portfolio has a revenue cliff when 3 multi-year grants expire in the same quarter.

## How to apply

**Pipeline stages and their standard lead times:**

| Stage | Definition | Typical Lead Time Before Deadline |
|---|---|---|
| Prospect | Identified but not yet qualified | — |
| Qualified | Funder fit confirmed (mission, geography, size, history) | Research complete |
| LOI / Letter of Inquiry | LOI drafted or submitted | 4–8 weeks before LOI deadline |
| Invited to full proposal | Funder invited full application | Move to proposal stage |
| Proposal in development | Full application being written | 8–12 weeks before deadline |
| Submitted | Application in review | — |
| Awarded | Grant confirmed; first payment received | — |
| Reporting | Active grant; reporting obligations tracked | Report due dates in calendar |
| Renewal research | Active grant nearing end; renewal fit re-qualified | 6 months before grant end |

**12-month pipeline calendar — minimum fields:**

```
| Funder        | Program        | Stage         | Ask Amount | Deadline    | Report Due  | Grant Officer |
| [Name]        | [Program name] | Proposal      | $[Amount]  | [YYYY-MM-DD]| [YYYY-MM-DD]| [Name]        |
```

**Revenue forecasting from the pipeline:**

```
Expected Revenue by Quarter = Sum of (Ask Amount × Win-Probability) by grant

Win-probability by stage:
  Prospect / Qualified:    10–15%
  LOI submitted:           25–35%
  Invited to full:         50–65%
  Proposal submitted:      40–55%
  Renewal (strong history): 70–85%
  (All probabilities are [unverified — training knowledge]; calibrate against the org's own win rate)
```

**Warning signals in the pipeline:**

| Signal | What It Means | Response |
|---|---|---|
| > 40% of grant revenue dependent on 1–2 funders | Concentration risk — a single non-renewal is a budget crisis | Diversify actively; add prospects |
| No qualified prospects for the next 2 quarters | Prospecting has stalled; cash cliff approaching | Allocate research hours now |
| Reporting deadlines clustering in one month | Staff capacity risk; late reports damage relationships | Stagger grant start dates if possible |
| Pipeline shows no renewals — only new applications | Relationship management is weak; renewals are lower cost-to-raise | Prioritize existing funder cultivation |

**Do:**
- Maintain the pipeline in a shared, date-sorted document — not in email threads or one person's head.
- Assign a named grant officer to each funder relationship, not just each application.
- Build the lead time for each stage backward from the deadline — a proposal due February 1 should be in development by November 1.

**Don't:**
- Count a submitted application as "revenue expected" without a probability weight — it inflates the forecast.
- Begin writing a proposal before completing funder-fit qualification — the research investment must precede the writing investment.
- Treat reporting as separate from relationship management — the report is the bridge to the renewal conversation.

## Edge cases / when the rule does NOT apply

Organizations that receive only government grants (federal, state, NOFO-driven) operate on a different cycle where LOIs are rare and proposal deadlines are set externally with little flexibility. The pipeline discipline still applies — the 12-month calendar is equally important — but the lead-time and qualification steps look different (compliance requirements, SAM registration, indirect rate calculation replace funder-fit scoring).

## See also
- [`../agents/grant-writer.md`](../agents/grant-writer.md) — owns the proposal development calendar and funder-fit qualification.
- [`../agents/nonprofit-finance-analyst.md`](../agents/nonprofit-finance-analyst.md) — builds the restricted/unrestricted revenue forecast from the pipeline probability-weighted model.

## Provenance

Codifies standard nonprofit grants management practice; win-probability benchmarks are [unverified — training knowledge] and must be calibrated against the organization's own historical win rate by stage.

---

_Last reviewed: 2026-06-05 by `claude`_
