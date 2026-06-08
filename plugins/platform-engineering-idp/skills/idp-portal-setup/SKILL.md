---
name: idp-portal-setup
description: "Stand up an internal developer portal and model the software catalog: choose Backstage vs a managed portal (Port/Cortex/OpsLevel/Spotify Portal), model components/systems/APIs/resources with an owner for every entity, keep catalog-info.yaml as code validated in CI, author scaffolder/software templates, and wire TechDocs."
---

# IDP / Portal Setup

**Purpose:** build the front door of the platform — a portal + a software catalog that answers the
questions developers actually ask, kept as code so it doesn't rot.

## Choose the portal

Traverse the buy-vs-build tree in
[`../../knowledge/platform-engineering-decision-trees.md`](../../knowledge/platform-engineering-decision-trees.md).
Short version: managed (Port/Cortex/OpsLevel/Spotify Portal) when customization is standard and the
maintenance budget is thin; Backstage when deep customization is a real requirement *and* a team will
own the upgrades.

## Model the catalog

- Model from developer questions: "who owns this?", "what depends on this API?", "how do I make a new
  service?" — not from the org chart.
- Entity kinds: `Component`, `System`, `Domain`, `API`, `Resource`, `Group`/`User`; relationships
  `ownedBy`, `dependsOn`, `providesApis`, `partOf`.
- **Every entity has an owner.** Unowned == unmaintained.
- **Catalog as code:** one `catalog-info.yaml` per repo (see
  [`../../templates/backstage-catalog-info.yaml`](../../templates/backstage-catalog-info.yaml)),
  discovered via the VCS processor, validated in CI. Never maintain the catalog by hand in the UI.

## Scaffolder / software templates

A parameterized template that creates a repo wired to the golden path: CI, ownership, the catalog
entry, TechDocs. This is the create step of `golden-path-design`.

## TechDocs

Docs-as-code rendered in the portal; content quality is `technical-writing-docs`' job.

## Anti-patterns

- Hand-maintained catalog in the UI (rots).
- Entities with no owner.
- A template that doesn't wire the paved road.
- Backstage chosen with no budget to maintain it.

## Output

A catalog model + as-code convention, a scaffolder template, or a portal build-vs-buy recommendation.
