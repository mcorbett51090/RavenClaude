# Use Tableau Pulse for a tracked metric; reserve a hand-built dashboard for rich exploration

**Status:** Pattern — match the next-gen surface to the deliverable; deviate with a reason. **Volatile** — the Pulse / Tableau-Next / CRM-Analytics surface moves every quarter; `[verify-at-build]` every positioning claim.

**Domain:** Next-gen surface / metrics

**Applies to:** `tableau`

---

## Why this exists

"Build me a dashboard to track revenue" is often the wrong ask answered the wrong way. If the real deliverable is *one number, watched over time, with an alert when it moves*, a hand-built dashboard is over-engineering: someone maintains layout, filters, and subscriptions for what is fundamentally a **metric definition**. **Tableau Pulse** is built for exactly that — define the metric once and it produces trend, automatic anomaly/insight detection, and per-user subscriptions, with no dashboard to lay out `[verify-at-build]`. Conversely, when the user genuinely needs to *explore* — slice many fields, pivot, drill, ask follow-up questions — Pulse's metric-centric surface is too narrow and a classic dashboard (or Tableau Next, if the data is Data-Cloud-native and you want agentic/semantic analytics) is right. Choosing the surface deliberately saves a maintained dashboard that should have been a metric, or a cramped Pulse metric that should have been a dashboard. Because this surface is renamed and repositioned almost every quarter, date every claim.

## How to apply

Traverse the next-gen-surface decision tree; pick by the deliverable, not by habit.

```
Ask: "What does the stakeholder actually need to DO with this?"

  Watch ONE metric, get trend + auto-insight + an alert on change
      → Tableau Pulse  (a metric definition: name, measure, time grain, dimensions to break down by)
        [verify-at-build]

  Explore MANY fields interactively, drill, pivot, ask follow-ups
      → Classic Tableau dashboard on a published/certified data source

  Data lives in Salesforce Data Cloud + want agentic/semantic on-platform analytics
      → Tableau Next  [unverified — positioning changes fast; verify-at-build]

  Data + audience live on the Salesforce platform (not Data Cloud)
      → CRM Analytics  → seam with the `salesforce` plugin  [verify-at-build]
```

**Do:**
- Reach for **Pulse** when the deliverable is a single tracked metric with insight + subscription.
- Reach for a **classic dashboard** when the user needs rich, multi-field interactive exploration.
- Name the platform/edition and **`[verify-at-build]`** any Pulse / Tableau-Next / CRM-Analytics claim before quoting to a client.
- Seam to the `salesforce` plugin when the data and audience are Salesforce-platform-native (CRM Analytics).

**Don't:**
- Hand-build a dashboard whose only job is to show one number and email it weekly — that's a Pulse metric.
- Quote Pulse / Tableau-Next / CRM-Analytics feature availability from memory — it changes every quarter.
- Assume Pulse replaces dashboards — it complements them; rich exploration still lives in dashboards.

## Edge cases / when the rule does NOT apply

- **A metric plus exploration** — sometimes you want both: a Pulse metric for the watch-and-alert, and a linked dashboard for the deep-dive. Build both; don't force one surface to do the other's job.
- **Edition/platform gating** — Pulse and Tableau Next availability differ by Cloud vs Server and by edition `[verify-at-build]`; confirm the target supports the surface before recommending it.
- **CRM Analytics on-platform** — when the analytics genuinely belong on the Salesforce platform, this is a `salesforce`-plugin seam, not a Tableau-Server decision.

## See also

- [`../knowledge/governance-embedding-decision-trees.md`](../knowledge/governance-embedding-decision-trees.md) — `## Decision Tree: Next-gen surface — Tableau Pulse vs Tableau Next vs classic dashboard`
- [`./gov-certified-data-sources-and-governance.md`](./gov-certified-data-sources-and-governance.md) — the governed source a Pulse metric or a dashboard sits on
- [`../agents/tableau-admin.md`](../agents/tableau-admin.md) — owns this rule; dates every next-gen claim
- Tableau Help, "Tableau Pulse" + Tableau Next / Data Cloud positioning `[unverified — training knowledge; verify-at-build]`

## Provenance

Codifies the `tableau-admin` discipline #6 ("Pick the next-gen surface deliberately") and constitution house opinion #9 ("Volatile claims carry a retrieval date"). Pulse/Tableau-Next/CRM-Analytics positioning is `[unverified — training knowledge]` and moves quarterly — re-verify against current Tableau/Salesforce docs before quoting to any client.

---

_Last reviewed: 2026-05-30 by `claude`_
