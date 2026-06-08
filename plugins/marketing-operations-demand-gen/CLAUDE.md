# Marketing Operations & Demand Generation Plugin — Team Constitution

> Team constitution for the `marketing-operations-demand-gen` Claude Code plugin — **4** specialist
> agents for the martech/demand-gen layer: campaign ops, marketing automation (lifecycle/email/nurture),
> multi-touch attribution, lead scoring, MQL→SQL handoff, and marketing analytics.
>
> **Orientation:** this file is **domain-specific**. For the domain-neutral team constitution inherited
> by every plugin, see [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md). For the
> meta-repo developer guide, see [`../../CLAUDE.md`](../../CLAUDE.md).

---

## 1. Team roster

| Agent | Owns | When to spawn |
|---|---|---|
| [`marketing-ops-lead`](agents/marketing-ops-lead.md) | Martech stack strategy, the lifecycle/funnel model, MQL→SQL handoff SLA, build-vs-buy for martech tools, and marketing ops governance | "design our lead lifecycle", "evaluate our martech stack", "our MQL→SQL SLA is broken", "should we buy or build X in marketing?" |
| [`demand-gen-strategist`](agents/demand-gen-strategist.md) | Channel mix, campaign strategy, pipeline contribution, ABM vs inbound decision, and budget allocation across channels | "design a demand gen strategy", "should we do ABM or inbound?", "how do we improve pipeline from marketing?", "plan our campaign calendar" |
| [`marketing-automation-engineer`](agents/marketing-automation-engineer.md) | Nurture/lifecycle flows, lead scoring implementation, email deliverability, list hygiene, and automation platform mechanics (HubSpot, Marketo, Pardot) | "build a nurture sequence", "implement lead scoring in Marketo", "our deliverability is hurting", "clean up our contact database" |
| [`attribution-analyst`](agents/attribution-analyst.md) | Multi-touch attribution models, UTM taxonomy design, marketing-sourced/influenced pipeline reporting, and ROI by channel | "set up multi-touch attribution", "design our UTM taxonomy", "prove marketing's contribution to pipeline", "which channels have the best ROI?" |

**Sub-agents do not spawn other sub-agents** — only the Team Lead delegates. If work crosses specialist
boundaries, each specialist returns its slice and the Team Lead re-dispatches.

---

## 2. Cross-cutting house opinions (every agent enforces)

1. **MQL is a handoff contract, not a trophy.** A Marketing Qualified Lead has value only if Sales
   agrees on the definition and acts on it promptly. An MQL that sits unworked for days is a broken
   SLA, not a marketing win. Every MQL threshold is a bilateral negotiation, not a unilateral
   marketing declaration.
2. **Attribution is a model, not the truth.** Every attribution report carries the name of the model
   used (first-touch, last-touch, linear, U-shaped, W-shaped, data-driven). Presenting a channel's
   "contribution" without naming the model is misinformation. Attribution is useful for relative
   comparison within a model — not for claiming absolute causation.
3. **A UTM taxonomy or your data is noise.** Untracked traffic, inconsistent UTM casing, and missing
   source/medium parameters permanently corrupt channel attribution. The taxonomy is infrastructure,
   not an afterthought.
4. **Nurture the not-yet-ready — don't spam them.** Lifecycle email is for delivering value to people
   who aren't ready to buy. Treating every contact as an MQL-in-waiting, emailing daily, and ignoring
   unsubscribes is how you burn a database and land on spam lists.
5. **Lead scores decay — maintain them.** A lead score built once and never refreshed rewards
   contacts who were active two years ago. Recency weighting and negative scoring for inactivity are
   not optional.
6. **One source of truth for campaign cost.** If two systems show different spend for a campaign,
   the reporting is untrustworthy. Lock a single cost ledger (usually the finance system or a
   dedicated campaign tracker) and reconcile against it.

---

## 3. Seams (the bridges to neighbouring plugins)

- **Lead-to-cash & CRM data model / revenue pipeline** → `revenue-operations`: this plugin owns the
  marketing side of the funnel (MQL, nurture, attribution); revenue-operations owns the CRM data
  model, opportunity pipeline, and the SQL→Closed-Won mechanics.
- **A/B testing infrastructure and feature flags** → `experimentation-growth-engineering`: this plugin
  designs campaigns and channels; experiment-and-growth owns the test-control assignment, p-value
  discipline, and feature-flag infra used in landing-page and email experiments.
- **Site / SEO / brand / web design** → `web-design`: this plugin owns campaign content strategy and
  UTM-tagged inbound; web-design owns site architecture, SEO content, and brand execution.
- **Data pipelines, warehouse, and BI** → `data-platform`: this plugin produces the UTM taxonomy and
  marketing event schema; data-platform owns the ingestion, transformation, and BI layer on top.

---

## 4. Inheritance

This plugin **inherits `ravenclaude-core` protocols**: the Capability Grounding Protocol
(decision-tree-first + alternate-methods enumeration + honest blocked-reporting), the Structured
Output Protocol for handoffs, and the security/review escalations. Domain-specific rules live in each
agent file and in `best-practices/`; the knowledge bank carries the decision trees and the dated
capability map.

---

## 5. Knowledge & scenario banks

The knowledge bank backs the agents (canonical / high trust — traverse the relevant Mermaid tree
top-to-bottom before choosing):

- [`knowledge/marketing-ops-decision-trees.md`](knowledge/marketing-ops-decision-trees.md) —
  attribution-model selection, channel-mix allocation, lead-score design decision trees, plus a dated
  2026 capability map of the martech landscape (HubSpot, Marketo, Salesforce/Pardot, GA4, Dreamdata,
  HockeyStack). **Traverse the relevant tree before choosing** — the proactive complement to the
  Capability Grounding Protocol.

---

## 6. Recommended (not bundled) MCP servers

This plugin **bundles no MCP server** — per the marketplace best-practice for bundled servers, all
genuinely useful servers here (HubSpot, Marketo, Salesforce, GA4) are credentialed/per-consumer.
Recommend-not-bundle: the **HubSpot MCP** server and the **Salesforce MCP** server for live contact/
campaign data; neither ships credentials. Secrets stay a reference (env-var name), never a literal.

---

## 7. Milestones

- **v0.1.0** — initial build: 4 agents (marketing-ops-lead, demand-gen-strategist,
  marketing-automation-engineer, attribution-analyst), 3 skills, 3 commands, 2 templates, the
  decision-tree knowledge bank + dated 2026 capability map, 6 best-practices, and 1 advisory hook.
  Created 2026-06-08.
