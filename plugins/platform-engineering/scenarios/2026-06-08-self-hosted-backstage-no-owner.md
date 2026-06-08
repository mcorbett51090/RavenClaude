---
scenario_id: 2026-06-08-self-hosted-backstage-no-owner
contributed_at: 2026-06-08
plugin: platform-engineering
product: backstage
product_version: "unknown"
scope: likely-general
tags: [build-vs-buy, backstage, tco, ownership, portal]
confidence: high
reviewed: false
---

## Problem

A 40-engineer org decided to "just self-host Backstage" because it's CNCF and free. A motivated staff engineer stood up a slick instance in two weeks during a hack week, then moved back to their stream-aligned team. Nine months later the portal was on an unpatched Backstage version three majors behind, the catalog auth had broken after an SSO change nobody owned, and a security advisory against a transitive dependency sat unactioned because there was no named owner to triage it. Developers had stopped opening the portal; the "platform" was a liability with a login page.

## Constraints context

- ~40 engineers, no dedicated platform team — the portal was a side project, not a staffed product.
- Backstage is a framework, not a product: every upgrade is a code-merge-and-test exercise, not a managed bump.
- Leadership read "open source" as "free" and never budgeted the team-to-own-it as a real cost.

## Attempts

- Tried: rotating a volunteer maintainer each quarter. Failed — no continuity; each volunteer relearned the codebase, and nobody owned the upgrade backlog across rotations.
- Tried: a "we'll upgrade it next quarter" backlog item. Failed — it never beat product work for priority, so the version gap compounded into a high-risk big-bang upgrade nobody wanted to start.
- Tried: re-running build-vs-buy honestly with the real TCO on the table. At 40 engineers with no platform team, a managed/SaaS portal (Port / Roadie / Cortex) carried a fraction of the total cost of ownership of a self-hosted framework that needs a standing team. They migrated the catalog model (which was portable) to a managed portal and retired the self-hosted instance. This worked.

## Resolution

The catalog *model* — entities, team ownership, lifecycle/tier — was portable, so the migration moved the opinions, not a pile of bespoke code. The managed portal absorbed the upgrade, security-patch, and uptime burden the org could never staff. The lesson that actually landed with leadership was naming the TCO: "self-host" means "we are now a portal-maintenance team," and they had no intention of being one.

## Lesson

Buy the undifferentiated, build only the differentiating — the portal/catalog/scaffolder are mostly undifferentiated, and "we'll just self-host Backstage" is a product you now own with a team you must staff. Name the real TCO (a standing owner + the upgrade/security treadmill) before recommending self-hosting; without a named owner, a self-hosted portal decays into a security liability.
