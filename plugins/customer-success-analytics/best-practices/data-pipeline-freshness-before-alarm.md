# Verify data-pipeline freshness before acting on a sudden health-score drop

**Status:** Primary diagnostic
**Domain:** CS analytics — signal reliability
**Applies to:** `customer-success-analytics`

---

## Why this exists

A stale data feed makes a healthy account appear to be in free-fall. If the usage pipeline failed to load yesterday's data, usage activity reads as zero and the tier flips to Red. A CS rep who calls the account to save it from a "crisis" that is actually a pipeline lag damages the CS relationship and wastes a call slot. The freshness check is the diagnostic that separates a real signal drop from a pipeline outage, and it must happen before any CS action is taken on a sudden drop.

## How to apply

When a health-score drop appears sudden (e.g., an account flips from Yellow to Red between one day's snapshot and the next, or a usage signal drops sharply without a corresponding support or NPS signal):

```
Step 1: Check the signal's source-data freshness timestamp
  → Each fact table should carry a data_loaded_at or max_event_timestamp
  → If data_loaded_at is more than 24 hours behind the snapshot date: pipeline lag is the suspect

Step 2: Check the pipeline run log for the source system
  → Was there a failed run in the collection window?
  → Did the API rate-limit or return a partial payload?

Step 3: If lag is confirmed:
  → Flag the impacted accounts' tier status as [data-pending — do not act]
  → Do NOT page the CS rep for a save play on a lag-flagged account
  → Re-evaluate tier after the pipeline catches up

Step 4: If lag is ruled out (feed is fresh):
  → The drop is real — proceed with the renewal call-list tree
```

The renewal call-list decision tree in the knowledge bank (`customer-success-decision-trees.md`) has an explicit "Fix the pipeline first" leaf for this scenario.

**Do:**
- Add a data-freshness column to the CS dashboard so the CS leader can see the feed status without escalating to data engineering.
- Surface a banner on the dashboard when any signal source is more than 24 hours stale.
- Partner with `data-platform` to add pipeline health checks as a first-class observable.

**Don't:**
- Page the CS team on a sudden drop before confirming freshness — false alarms erode trust faster than slow alarms.
- Treat a pipeline lag as a rare edge case — usage pipelines from third-party CS platforms (Planhat, Gainsight, ChurnZero) have regular lag events.

## Edge cases / when the rule does NOT apply

- The drop is confirmed real (freshness is verified, pipeline is healthy) — do not delay the CS action to run additional freshness checks; the delay has a cost when the renewal window is short.

## See also

- [`../agents/churn-signal-analyst.md`](../agents/churn-signal-analyst.md) — the agent that diagnoses tier misfires including pipeline-related ones
- [`../knowledge/customer-success-decision-trees.md`](../knowledge/customer-success-decision-trees.md) — the renewal call-list tree with the "Fix the pipeline first" leaf

## Provenance

Derived from real-world CS analytics failure mode: pipeline lags from third-party CSP exports are a weekly occurrence in most deployments. The `churn-signal-analyst` escalation path to `data-platform` exists because this diagnostic crosses the domain/technical boundary.

---

_Last reviewed: 2026-06-05 by `claude`_
