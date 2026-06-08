---
scenario_id: 2026-06-08-backstage-catalog-drift
contributed_at: 2026-06-08
plugin: platform-engineering
product: backstage
product_version: "unknown"
scope: likely-general
tags: [catalog, ownership, auto-discovery, drift, scorecards]
confidence: high
reviewed: false
---

## Problem

A platform team stood up a Backstage catalog by asking every team to hand-write `catalog-info.yaml` for their services. Six months later the catalog was distrusted: ~30% of entries pointed at archived repos, dozens of services that existed in the cluster were missing entirely, and an incident escalated to the wrong team because the listed owner had reorged away. People had quietly gone back to a spreadsheet.

## Constraints context

- ~180 services across ~20 teams; new services created weekly.
- Ownership was modeled as an individual GitHub username in many entries, not a team.
- No enforcement: a service could ship to prod with no catalog entry and nobody noticed.

## Attempts

- Tried: a quarterly "catalog cleanup" sprint where teams fixed their own entries. Failed — it drifted again within weeks because the catalog was decoupled from reality; fixing it was manual toil nobody owned.
- Tried: a linter that rejected PRs with a malformed `catalog-info.yaml`. Helped format quality but did nothing for the missing services or the stale ones (it only ran on files that existed).
- Tried: auto-discovery — a provider that ingests entities from the GitHub org and the Kubernetes cluster, reconciling continuously, plus making the scaffolder template register the service at creation time. Combined with an ownership rule (a *team* group, not a person) enforced at ingestion: an entity with no team owner is quarantined, not published. This worked.

## Resolution

Auto-discovery + registration-at-creation closed the "missing/stale" gap (the catalog now tracks the system of record instead of a parallel hand-maintained copy), and the team-owner requirement closed the "wrong team paged" gap. A production-readiness scorecard surfaced the remaining quarantined/un-owned entities to leadership, so closing them became self-service rather than a cleanup sprint. Trust returned because the catalog stopped being a thing humans maintain by hand.

## Lesson

The catalog is the source of truth or it's nothing — prefer auto-discovery over hand-maintained entities, make the scaffolder register the service at creation, and require a *team* owner as a hard gate. A drifted catalog is worse than no catalog because it actively misleads during an incident.
