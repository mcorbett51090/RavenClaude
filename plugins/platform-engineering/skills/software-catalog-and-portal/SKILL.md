---
name: software-catalog-and-portal
description: "Model a software catalog (components/systems/APIs/resources + team ownership + lifecycle + tier), prefer auto-discovery over hand-maintained entities, build scaffolder templates that generate paved-road repos and register them, wire TechDocs, and design scorecards that surface gaps. Portal-neutral (Backstage/Port/Cortex/OpsLevel/Roadie)."
---

# Software Catalog & Developer Portal

## The catalog is the source of truth — or nothing
A drifted catalog is worse than none; people stop trusting it. Prefer **auto-discovery/ingestion** (from repos, the cluster, the cloud) over hand-maintained YAML. Reconcile continuously.

## Ownership is the first metadata
Every component has an **owner (a team, not a person)**, a **lifecycle** (experimental / production / deprecated), and a **tier/criticality**. An un-owned service is a page nobody answers — reject or quarantine catalog entries with no owner.

## Model the relationships
Components, systems (groups of components), APIs (what a component provides), and resources (DBs, queues). Capture depends-on / part-of / provides-API so impact and ownership are traceable.

## The scaffolder template is onboarding
A software template generates a paved-road repo — code skeleton + CI + **catalog-info registration** + docs + security defaults — and automates post-create steps. If creating a service doesn't also register, wire, and document it, the template isn't done. Document the opinions the template bakes in.

## TechDocs: docs live with the code
Docs-as-code in the repo, reviewed with the change, rendered in the portal. A separate wiki rots.

## Scorecards measure, they don't shame
Production-readiness / ownership / security-maturity checks mapped to catalog + external data. Every failing check links to its remediation (often a scaffolder action or golden-path doc). It's a self-service health check, not a blame leaderboard.

## Portal-neutral
The catalog/template/scorecard concepts map across Backstage, Port, Cortex, OpsLevel, and Roadie. Model the concepts; bind to whichever product the org adopts. Self-hosting Backstage is a product you own — recommend managed if there's no portal owner.
