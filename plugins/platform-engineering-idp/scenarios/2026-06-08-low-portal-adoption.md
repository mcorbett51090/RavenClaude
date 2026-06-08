---
scenario_id: 2026-06-08-low-portal-adoption
contributed_at: 2026-06-08
plugin: platform-engineering-idp
product: backstage
product_version: "unknown"
scope: likely-general
tags: [backstage, adoption, portal, catalog-freshness, devex]
confidence: high
reviewed: false
---

## Problem

A platform team spent two quarters building a Backstage portal — software catalog, TechDocs, a
scorecards plugin — and at launch, weekly active usage plateaued at ~10% of engineers. Leadership's
instinct was to **mandate** the portal ("all services must be registered, all docs must live in
TechDocs by Q3"). The platform team asked whether the mandate would fix adoption.

## Context

- ~40 engineers, ~60 services; the catalog had been seeded by a one-time import and was already
  ~30% stale (renamed services, wrong owners, dead links).
- The portal surfaced information but answered no question a developer urgently had — there was no
  golden path / scaffolder behind it, so "create a new service" still meant copying an old repo.
- The one genuinely painful journey (getting a new Postgres) was still a ticket; the portal didn't
  touch it.

## Attempts

- Considered: the mandate. Rejected per the **platform-is-a-product / adoption-is-earned** rule — a
  mandate would force registration of a stale catalog nobody trusted, producing compliance-theater
  data and deeper distrust, while masking the real problem (the portal removed no friction).
- Tried: a developer survey + the adoption funnel (discover → try → adopt → retain). The data showed
  engineers *discovered* the portal but didn't *try* it twice, because it offered nothing they needed
  that they couldn't get faster elsewhere.
- Tried (the move that worked): re-anchored on the **thinnest viable platform**. Built one golden path
  — a scaffolder template that creates a service already wired (CI, ownership, catalog entry,
  TechDocs) — *and* made the painful Postgres request a self-service button. The catalog was moved to
  **as-code** (`catalog-info.yaml` per repo, CI-validated) so it stopped rotting. The portal now
  surfaced things the new path produced.

## Resolution

**Low portal adoption is almost never solved by a mandate; it's solved by making the portal the front
door to something that removes real friction.** A portal with no golden path behind it is a catalog
nobody updates. Within a quarter, voluntary weekly usage rose because creating a service and getting a
database now *started* in the portal — adoption followed value, not decree.

**Action for the next engineer:** before mandating a portal, check whether it sits in front of a real
self-service journey. If not, build the thinnest viable golden path first, move the catalog to as-code
so it's trustworthy, and let adoption be the signal. Cross-reference
[`../best-practices/platform-is-a-product-adoption-is-earned.md`](../best-practices/platform-is-a-product-adoption-is-earned.md)
and [`../best-practices/start-with-the-thinnest-viable-platform.md`](../best-practices/start-with-the-thinnest-viable-platform.md).

**Sources:** Backstage catalog-as-code + discovery behavior per backstage.io docs `[verify-at-use]`.
Figures (10% adoption, 30% stale, 40 engineers) are illustrative; validate against the org's actuals.
