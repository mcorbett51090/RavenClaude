# PSM tools landscape 2026 — CS platforms, adjacent tools, EdTech reality

> **Last reviewed:** 2026-05-21. Research-distilled landscape of customer-success / partner-success tooling as of mid-2026. Sources: vendor press releases, TechCrunch / CX Dive on M&A activity, G2 / TrustRadius practitioner reviews, EDUCAUSE-adjacent K-12 vendor materials. **Pricing figures throughout are from secondary aggregators (Oliv.ai, Custify guides, vendor blogs) — vendors don't publish list prices for enterprise CSPs. Treat all dollar figures as ballpark; verify with vendor in any real procurement.** Refresh when: (a) a major M&A event reshapes the tier-1 landscape, (b) Gartner Magic Quadrant or Forrester Wave publishes a new edition, (c) a meaningful new entrant gains traction, or (d) an EdTech-vertical CSP finally launches.

This file is the **landscape reference** for the PSM team's tooling decisions and for any conversation about what a partner is using on *their* side. Companion to [`customer-success-frameworks.md`](customer-success-frameworks.md) (which names the methodologies these tools implement) and [`psm-metrics-glossary.md`](psm-metrics-glossary.md) (which names the numbers they surface).

**Key 2026 finding:** No K-12-vertical CSP exists. EdTech vendors bolt rostering integration onto generic CSPs. The plugin's value sits in the EdTech-shaped methodology *above* whichever generic CSP a customer happens to use — not in recommending a magic vertical tool.

---

## 1. The "no EdTech vertical CSP exists" finding

Extensive search across vendor sites, EdTech job postings, EdSurge / K-12 Dive coverage, and EDUCAUSE materials turns up **zero K-12-vertical customer-success platforms** as of mid-2026. EdTech vendors that sell into districts use a generic CSP (most commonly Gainsight, ChurnZero, or HubSpot Service Hub) and bolt on rostering-aware tooling (Clever Complete, Ednition RosterStream, ClassLink). The EdTech-vertical CS workflow is built in plugins, configurations, and custom integrations on top of a horizontal CSP, not bought off-the-shelf.

**Implication for PSM teams selling into EdTech:** the value of a plugin like this one (EdTech-shaped playbooks, calendar-aware cadence, rostering-health interpretation) sits in the methodology layer, not the platform layer. There isn't a vertical CSP to recommend — and saying that plainly is more useful than pretending otherwise.

---

## 2. Tier 1 — enterprise CS platforms (Gartner MQ Leaders)

The 2024 and 2025 Gartner Magic Quadrant for Customer Success Management Platforms named the same three Leaders both years: **Gainsight, ChurnZero, and Totango**. The Forrester Wave Q4 2025 also named Gainsight a Leader. These are the platforms enterprise CS teams predominantly evaluate.

### Gainsight

- **Market position.** Leader in 2024 and 2025 Gartner MQ for CSM Platforms; Leader in Forrester Wave Q4 2025. The most widely-deployed enterprise CSP by reach.
- **Corporate status.** Vista Equity Partners majority owner from the $1.1B acquisition closed in 2021. *(A 2024 press release describes a separate "majority investment from Vista" — likely a restructure or secondary, not a new acquisition; verify with primary source if it matters for procurement.)*
- **Product portfolio.** Gainsight CS (core CSM), Gainsight PX (product experience / in-app engagement, MAU-priced), Skilljar by Gainsight (customer education / LMS), Customer Communities (powered by inSided), Staircase AI (conversation and sentiment).
- **Target segment.** Enterprise SaaS predominantly; deployments typically 20+ CSMs with dedicated CS Ops headcount.
- **Pricing (ballpark — secondary aggregator only).** Essentials ~$1,200-$2,400 per user; Enterprise ~$2,400-$4,200 per user; mid-market CS Cloud deployments $60-120K/year. **Confidence: Low** — vendor doesn't publish list prices.
- **AI features.** Agentic copilot features in 2026; reportedly a Model Context Protocol (MCP) server so external LLMs can read/act on Gainsight data. **Confidence: Medium** — found in practitioner blogs, not directly verified on Gainsight docs.
- **Common complaints.** Implementation cost and time (3-6 months in practice). Heavy CS Ops resourcing requirement. Total cost ~1.2-1.5× license once services included. "Complexity tax" for teams without dedicated admins.

> Sources: Gainsight press release on 2025 Gartner MQ (https://www.gainsight.com/press/gainsight-named-a-leader-in-2025-gartner-magic-quadrant-for-customer-success-management-platforms-for-second-consecutive-year/); TechCrunch on original Vista deal (https://techcrunch.com/2020/11/30/vista-acquires-gainsight-for-1-1b-adding-to-its-growing-enterprise-arsenal/); product / pricing overviews via SalesHive and Oliv.ai (https://saleshive.com/vendors/gainsight/, https://www.oliv.ai/blog/gainsight-pricing-cost-per-user).

### ChurnZero

- **Market position.** Gartner MQ Leader 2024 and 2025 (two consecutive years). G2 4.7/5 across 1,400+ reviews. The consensus **mid-market** pick.
- **Target segment.** Mid-market SaaS, typically 50-1,000 employees with dedicated CS Ops headcount.
- **AI Marketplace (launched 2025).** **14 agentic AI teammates** delivered via a marketplace model — sentiment analysis, churn prediction, meeting follow-ups, engagement scoring. ChurnZero uses "AI agents" and "agentic AI teammates" interchangeably. Practitioner consensus treats this as the most production-ready autonomous-agent layer at mid-market price points in 2026.
- **Pricing (ballpark — secondary aggregator only).** Starts ~$12,000/year (basic); HubSpot Marketplace listing $16,000/year + per-user. No free tier. Implementation 4-8 weeks. **Confidence: Low** — single secondary source.
- **Common complaints.** Fewer integrations than Gainsight at the enterprise end. Weaker "platform" extensibility for teams modeling bespoke customer hierarchies (where Planhat has the edge). Reporting / dashboard customization weaker than Gainsight by some users.

> Sources: ChurnZero AI Marketplace press release (https://churnzero.com/press-release/churnzero-extends-industry-leadership-by-reshaping-customer-success-with-ai-teammates/) — 14 agents verified 2026-05-21; ChurnZero AI feature page (https://churnzero.com/features/customer-success-ai/); Oliv.ai review (https://www.oliv.ai/blog/churnzero-reviews-customer-feedback).

### Totango (post-merger entity)

- **Corporate status.** **Totango and Catalyst merged February 28, 2024** in an all-stock deal (no cash changed hands; investors rolled stock into the combined entity). Backed by **Great Hill Partners**. **Co-CEOs Alistair Rennie** (ex-Totango) **and Edward Chiu** (ex-Catalyst). The merger included layoffs.
- **Subsequent moves.** **Acquired the team and IP of Parative AI on October 22, 2024**; launched **"Unison"** — AI-driven churn intelligence engine — with availability targeted December 2024. Keith Frankel (Parative co-founder) joined as CPO.
- **Brand status.** Totango and Catalyst brand names retained "in the near term" but the long-term direction is **unified product, unified brand under Totango**. Catalyst as an independent product is on a sunset trajectory — treat as historical for new evaluations.
- **Target segment.** Mid-market to lower enterprise SaaS; "customer-led growth" positioning.
- **Employees.** ~164 per recent secondary sources.

> Sources: TechCrunch on merger (https://techcrunch.com/2024/02/28/totango-catalyst-merger-customer-success/) — all-stock + co-CEOs verified 2026-05-21; Totango press on Parative AI (https://www.totango.com/press/totango-announces-ai-driven-churn-intelligence-solution-following-acquisition-of-technology-and-team-from-parative-ai); CX Dive on merger implications (https://www.customerexperiencedive.com/news/catalyst-totango-merger-customer-success-teams/709373/).

---

## 3. Tier 2 — credible challengers

### Planhat

- **Corporate.** Stockholm-based, founded 2015 by Kaveh Rostampor and Niklas Skog. ~200 employees, ~$50.9M raised; 2022 SEK 494M round led by Sprints Capital. 2024 revenue SEK 237M (~$22M USD), ~22% YoY growth, targeting $100M ARR.
- **Differentiation.** Unified data model platform — treats CRM data, time-series usage, comm data, tickets, and meeting transcripts as first-class objects with parent-child hierarchies (portfolios, regions, resellers) and auto-aggregation of revenue / health metrics. **Real technical differentiator** vs. Gainsight's playbook-centric, CTA-driven design.
- **Target.** Mid-market and lower-enterprise; teams that want platform flexibility and have technical CS Ops capacity to use it.
- **Common complaints.** Steeper learning curve for non-technical CSMs because the flexibility is exposed in the UI. Smaller partner / integration ecosystem than Gainsight. Admin tooling lags core platform per some reviewers.

> Sources: M&A Insights on Planhat growth (https://www.mainsights.io/ma-news/swedish-ai-based-customer-platform-planhat-targets-rapid-growth-and-potential-capital-raise); Crunchbase (https://www.crunchbase.com/organization/planhat); Planhat features (https://www.planhat.com/features/unified-data-model) — vendor source, aspirational.

### Vitally

- **Corporate.** Brooklyn-based, founded 2017 by Jamie Davidson and Patrick Vatterott. Series B Feb 2023; ~$40.2M total raised from Andreessen Horowitz and Next47.
- **Differentiation.** Go-to for product-led-growth (PLG) CS motions. 2025 "Hubs" feature is positioned as a productivity layer that replaces the Notion / Google Docs glue typical of younger CS teams.
- **Target.** Mid-market SaaS, often PLG or hybrid, smaller CS Ops footprint than Gainsight target.

> Sources: Vitally (https://www.vitally.io/); Tracxn (https://tracxn.com/d/companies/vitally/__DNlUq8LazmHtpnpKOJ-4lIc5jwWm2Gh4QWqJzE9x-PI).

### ClientSuccess

- **Corporate.** Lehi, UT-based, founded 2014. Private; ~36 employees; ~$6M raised. Strategic acquisitions: Status (onboarding) Nov 2023; Baton (onboarding / implementation) 2024; Product Signals (product feedback) Jan 2025.
- **Differentiation.** Long-tenured; SMB to lower-mid-market focus. Built-in onboarding / implementation via Status + Baton — distinct from peers.
- **Gap.** Smaller R&D team than Gainsight / ChurnZero. AI features are catch-up rather than lead.

> Sources: ClientSuccess press on Status acquisition (https://www.clientsuccess.com/resources/clientsuccess-acquires-status-to-merge-the-worlds-of-customer-success-and-onboarding); Tracxn (https://tracxn.com/d/companies/clientsuccess/__JQ42GioQanG6iCJjszVFrvt9EUUFqkZOxC8Qskw98JQ).

### Custify

- **Pricing.** Starts at $899/month; implementation in days, not months.
- **AI.** CustifyAI provides opt-in account summaries, follow-up tasks, conversation summaries.
- **Target.** Teams with 2-10 CSMs ready to leave spreadsheets but not ready for Gainsight-scale spend or implementation.

> Sources: Custify (https://www.custify.com/), Custify pricing comparison (https://www.custify.com/blog/how-to-choose-customer-success-software/).

---

## 4. Adjacent / specialized layers

### Product analytics (input feeds to CS, not CS workspaces)

- **Pendo** — Independent. ~$356M raised, ~$2.6B valuation, last priced round 2021. **Acquired Mind the Product** (Feb 2022). Positioned as a Software Experience Management platform (analytics + in-app guides + roadmapping). Often co-deployed with Gainsight CS — Gainsight's own PX product is a direct competitor.
- **Mixpanel** — Private, ~$210M ARR (2025 secondary), ~$1.1B valuation. Growth analytics specialist. Not a CS platform, but commonly the source-of-truth product-usage feed for a CSP.
- **Heap** — **Acquired by Contentsquare; deal closed December 7, 2023.** "Heap" brand still in use under Contentsquare. Strongest auto-capture retroactive-analytics story; CS teams typically consume via Salesforce / CSP integration.

> Sources: Pendo press on Mind the Product (https://www.pendo.io/news/pendo-announces-acquisition-of-mind-the-product-the-worlds-largest-community-of-product-managers/); Contentsquare on Heap close (https://contentsquare.com/press/contentsquare-completes-acquisition-heap/).

**Where these sit:** these are **input feeds** to the CS team, not the CS workspace. Pendo can substitute partially for Gainsight PX if a customer also runs Gainsight CS; most teams pick one or the other for in-app-guidance.

### CRM-with-CS-extensions

- **HubSpot Service Hub.** Has added a Customer Success Workspace inside Service Hub (health scores, NPS / CSAT / CES feedback, guided playbooks). Reasonable choice for HubSpot-native SMB-to-lower-mid-market; falls short of Gainsight / ChurnZero on health-scoring richness, lifecycle automation depth, and renewals / forecasting tooling.
- **Salesforce Service Cloud (now branded "Agentforce Service" under Salesforce's broader Agentforce push).** Used as system-of-record by many CS organizations; CSPs (Gainsight especially) integrate with it as primary CRM. *Confidence: Medium — rebrand framing surfaced in G2 listing; verify against Salesforce's own materials before relying on the exact "Agentforce Service" name in customer-facing materials.*

> Sources: HubSpot CSM software (https://blog.hubspot.com/service/csm-software); HubSpot comparison page (https://www.hubspot.com/comparisons/hubspot-vs-customer-success-platforms) — vendor-authored, treat as positioning.

**Practitioner consensus on Service Cloud / Agentforce Service:** doable as the CSP itself for enterprises with deep Salesforce admin capacity, but most teams pair Service Cloud (as system-of-record) with a dedicated CSP (Gainsight or ChurnZero) for CS workflows. Complexity tax — slow UI, heavy admin burden, dev-dependent customization — is the common reason teams don't try to build CS in raw Service Cloud.

### Stop-gap stacks (Notion / Coda / Airtable + CRM)

Common pattern for CS teams pre-$5M-ARR or pre-3-CSM headcount: Salesforce or HubSpot as system of record, plus Notion / Airtable for account plans, QBR docs, customer-facing collateral, and an ad-hoc health-score spreadsheet. **This is fine and well-documented** — the failure mode is sticking with it past the point where CSMs are spending >20% of their time on data wrangling. Practitioner consensus, not a single citable source.

---

## 5. The EdTech rostering layer

K-12 EdTech vendors need rostering integration with district SIS. The dominant players:

- **Clever** — Most widely deployed K-12 rostering broker in the US. Sync from district SIS (PowerSchool, Infinite Campus, Skyward, Synergy, etc.) → Clever aggregates → vendor pulls. Daily sync typical. District admin controls sharing scope.
- **ClassLink** — Similar broker pattern + LaunchPad SSO layer. OneRoster-flavored under the hood.
- **Ednition / RosterStream / RosterCare** — Independent rostering and data-integration layer.
- **Direct OneRoster (1EdTech)** — When districts avoid the broker layer; CSV drop to SFTP or REST API; common drift modes are encoding (UTF-8 BOM / Windows-1252), stale cron, version mismatch (v1.1 vs v1.2).

These are **integration infrastructure**, not CS workspaces. A K-12 EdTech vendor's CS workflow typically looks like: rostering integration feeds usage and roster-health data into a generic CSP (Gainsight or ChurnZero); the CSM works renewals against district academic-calendar milestones tracked manually or in custom CRM fields.

See [`rostering-data-quality-typology.md`](rostering-data-quality-typology.md) for the diagnostic typology when rostering breaks.

> Sources: Clever (https://www.clever.com/products/rostering); Ednition (https://www.ednition.com/blog/simplify-k-12-rostering-and-data-integration-with-rosterstream-2); 1EdTech / OneRoster + Ed-Fi (https://www.1edtech.org/blog/the-best-of-both-worlds-how-classlink-bridges-1edtechs-oneroster-and-the-ed-fi-data-standard).

---

## 6. When to graduate off spreadsheets

Practitioner-consensus trigger points (consistent across multiple sources, not a single authoritative survey):

- **3+ CSMs**
- **$1-2M ARR under management per CSM**
- **>100 active accounts**
- **CSMs spending >20% of time on data wrangling**

Below those, a well-organized Salesforce + Notion / Airtable + Pendo or Mixpanel stack is genuinely sufficient. **Premature CSP adoption locks in bad assumptions and costs $60-120K/year for the privilege.** *Confidence: Medium.*

> Sources: Velaris (https://www.velaris.io/articles/building-winning-customer-success-tech-stack-guide-for-cs-teams); CSM Practice (https://csmpractice.com/cs-technology-stack); Customer Success Collective (https://www.customersuccesscollective.com/tools/building-a-customer-success-toolset-with-a-limited-budget/).

---

## 7. Minimum viable stack for a 5-10 PSM EdTech team

Synthesis based on the segment realities and the tool landscape. **Treat as recommendation, not prescription.**

| Layer | Recommendation | Why |
|---|---|---|
| CRM (system of record) | Salesforce or HubSpot (whichever sales is on) | Sales-side consistency; integration burden |
| CSP | **ChurnZero or Custify** for mid-market EdTech; **Vitally** if PLG-tilted | Right mid-market price tier; faster to stand up than Gainsight; capable AI in 2026 |
| Product analytics | Mixpanel or Pendo (Pendo if you also want in-app guides) | Feeds the CSP; in-app guidance for adoption motions |
| Rostering integration (K-12) | Clever Complete or RosterStream | Required infrastructure for K-12 EdTech CS workflows |
| Account-plan / QBR collaboration | Notion or Google Docs early; CSP-native templates once on a CSP | Stop-gap is genuinely fine until book size justifies platform-native |
| Outreach | Email + CSP's email-sequence module | Add Outreach / Salesloft only if running structured outbound expansion |

**Gainsight is correct only when:** the team crosses 20+ CSMs with dedicated CS Ops headcount, the data model is genuinely complex (large account hierarchies, multi-product), or enterprise procurement requirements (a customer's HECVAT or similar) make the security / compliance breadth load-bearing.

---

## 8. Integration patterns

- **Salesforce** is the dominant system-of-record in enterprise CS stacks. Every major CSP has a bi-directional Salesforce sync as table stakes.
- **HubSpot sync** is well-supported by ChurnZero, Custify, Vitally, Planhat.
- **Webhooks, Segment, and Zapier** handle the rest of the integration landscape.

For EdTech specifically, the additional integration is the **rostering data layer** — feeding rostering health and license-utilization-by-school into the CSP so the PSM dashboard surfaces it without manual pull.

---

## 9. AI in CS in 2026 — what's real, what's demoware

Three honest categories:

1. **Production-ready AI.** ChurnZero AI Marketplace agents (14 task-specific agents) for sentiment, churn prediction, meeting follow-ups, engagement scoring. Gainsight's MCP integration enabling external LLM tool use (verify before relying on it). Planhat's announced Claude Code integration. These do useful things on day one.
2. **Demoware needing data maturity.** Churn-prediction models and sentiment-analysis agents that demo well but need ~6 months of clean account data to perform. The honest caveat practitioners share: the AI looks great in vendor decks; in your account, it takes time.
3. **Marketing wrapper.** Generic "AI summary" features on every product page; usually a thin LLM call over CSM notes. Useful, not differentiating.

**PSM rule of thumb for a customer-facing AI conversation:** any vendor promising AI-driven churn prediction without asking about your historical data volume is selling demoware. The math doesn't work without ~6+ months of clean account data.

---

## 10. When staying on CRM + spreadsheets is the right answer

- Small books (<50 accounts / CSM)
- High-touch enterprise CS where every account has a bespoke plan
- A CS team that doesn't yet have agreed-upon health-score logic to encode (premature CSP adoption locks in bad assumptions)

The CSP enables consistent execution at scale. If the team hasn't agreed what consistent execution means, the CSP becomes a $60-120K/year tracking system for guesses.

---

## Refresh triggers for this document

Re-read and update when:

- A material M&A event (acquisition, merger, public listing) changes the tier-1 landscape.
- Gartner Magic Quadrant or Forrester Wave for Customer Success Management Platforms publishes a new edition (typically annual).
- A new entrant gains meaningful market share (>5% of mid-market CSM evaluations).
- An EdTech-vertical CSP finally launches (would be the trigger to materially rewrite this file).
- A major rostering vendor (Clever, ClassLink) changes terms or is acquired.
- A new CS platform's AI feature ships as genuinely production-ready (the Tier-1 list should be re-ranked).
