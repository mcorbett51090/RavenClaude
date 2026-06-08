---
description: "Select, implement, and maintain a multi-touch attribution model: traverse the attribution-model decision tree, configure CRM campaign influence or a dedicated attribution tool, define marketing-sourced vs marketing-influenced pipeline, build the channel ROI report, and document model limitations for every consumer of the output."
---

# Attribution Modeling

**Purpose:** produce a defensible, model-named measurement layer that tells the demand-gen team
which channels and programs are contributing to pipeline — with honest limitations stated at every
step.

## Step 1 — Select the attribution model

Traverse the attribution-model selection tree in
[`../../knowledge/marketing-ops-decision-trees.md`](../../knowledge/marketing-ops-decision-trees.md).
Key decision dimensions:

| Dimension | Implication |
|---|---|
| Sales cycle < 30 days | Last-touch or time-decay captures the decision-moment well |
| Sales cycle > 90 days | U-shaped or W-shaped; multiple influence points matter |
| Top-of-funnel investment is large | First-touch or U-shaped; protect awareness-channel credit |
| Bottom-of-funnel investment is large | Last-touch or W-shaped |
| Data volume ≥ 1,000 conversions/period | Data-driven is viable; below this, use a named heuristic model |
| Multi-stakeholder B2B (buying committee) | Account-level attribution (Dreamdata, HockeyStack) over person-level |

**Never use a model without naming it.** Every report states: "Under [model], marketing contributed
X% of pipeline." If presenting multiple models, label each column.

## Step 2 — Define marketing-sourced vs marketing-influenced

Before building reports, lock the definitions in a shared glossary with Sales and RevOps:

- **Marketing-Sourced (MS):** the first known touch on a contact/account was a marketing program,
  with no prior Sales-initiated contact on record. MS% = MS pipeline ÷ total pipeline created.
- **Marketing-Influenced (MI):** at least one marketing touch occurred before the opportunity
  closed, regardless of source. MI% = MI pipeline ÷ total pipeline created.
- **Neither is "better"** — they answer different questions. MS measures Marketing's independent
  origination; MI measures its reach across the funnel.

Document the lookback window (typically 90 or 180 days before opportunity creation) and the touch
types that qualify (form fills, email clicks, events, ad clicks — not email opens alone).

## Step 3 — Instrument the data pipeline

### UTM → CRM campaign flow

1. Every campaign asset carries UTM parameters (per the UTM taxonomy).
2. The MAP captures UTM values on form fill and writes them to contact/lead fields.
3. The CRM creates a Campaign Member record (Salesforce) or Contact Activity (HubSpot) linking the
   contact to the campaign program.
4. Opportunity creation: the CRM's campaign influence model attributes pipeline to the campaign(s)
   that touched the contact before opp creation.

### Tool options (2026) [verify-at-use]

| Tool | Best for | Notes |
|---|---|---|
| **GA4** | Session/traffic-level reporting; top-of-funnel view | Not person-level in B2B; good for channel mix overview |
| **Salesforce Campaign Influence** | CRM-native, multi-touch across campaign members | Requires clean Campaign Member data; multiple models available |
| **HubSpot Revenue Attribution** | HubSpot-native; contact-to-deal attribution | Simpler model set than Salesforce; good for SMB/mid-market |
| **Dreamdata** | B2B account-level multi-touch; revenue attribution | Connects CRM + MAP + paid channels; strong for complex B2B [verify-at-use] |
| **HockeyStack** | B2B attribution + analytics; cookieless options | Combines attribution with behavioral analytics [verify-at-use] |

## Step 4 — Build the channel ROI report

Required columns:

| Column | Notes |
|---|---|
| Channel | utm_source / utm_medium combination |
| Spend (period) | From the campaign cost ledger — one source of truth |
| MQLs attributed | Under the named model |
| SQLs attributed | Under the named model |
| Pipeline attributed ($) | Under the named model |
| CAC (pipeline-to-spend ratio) | Spend ÷ new customers attributed [verify-at-use for industry benchmarks] |
| Pipeline-to-spend ratio | Pipeline attributed ÷ spend |
| Attribution model | Named, in every row header or table caption |

Add a "Model caveats" section below every report: what the model over-credits, what it under-credits,
and the data quality limitations (% of pipeline with unknown source, UTM coverage rate).

## Step 5 — Maintain the model

- **Quarterly model review:** validate that the model still reflects the actual sales cycle.
  If the average deal cycle has lengthened from 60 to 120 days, re-run the tree.
- **UTM hygiene check:** monthly audit of untracked traffic % and UTM coverage rate (% of
  form fills with all required UTM parameters populated).
- **Definition drift check:** confirm that MS/MI definitions haven't changed in the CRM due to a
  Salesforce admin update or MAP integration change.

## Anti-patterns

- Attribution reports without the model named — ever.
- Comparing two channels' ROI figures from different attribution models in the same table.
- Presenting attribution output as causal proof ("paid social caused this deal").
- Using data-driven attribution with fewer than ~1,000 conversions in the period.
- Building attribution on top of UTM data with >20% unknown-source traffic.
- A channel ROI report without a "Model caveats" section.

## Output

An attribution model selection document (model chosen, rationale, decision tree leaf), MS/MI
definition glossary, CRM campaign influence configuration spec, channel ROI report template
(with model named), and a quarterly model maintenance checklist. All benchmark figures and
tool capabilities marked `[verify-at-use]`.
