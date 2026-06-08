---
description: "Model a software catalog with team ownership and build a scaffolder template that generates and registers a paved-road service in one action."
argument-hint: "[services + ownership reality + portal (Backstage/Port/Cortex/...) if chosen]"
---

You are running `/platform-engineering:scaffold-service-catalog`. Use `developer-portal-engineer` + the `software-catalog-and-portal` skill.

## Steps
1. Model the catalog: components/systems/APIs/resources + owner (a team, not a person) + lifecycle + tier; prefer auto-discovery over hand-maintained entities.
2. Enforce ownership — no un-owned components; show the convention and where catalog-info lives.
3. Build a scaffolder/software template that generates a paved-road repo AND registers it (catalog entry + CI + docs + security defaults); document the opinions it bakes in.
4. Wire TechDocs (docs-as-code) and design scorecards (production-readiness/ownership/security) mapped to catalog metadata, each failing check linking to remediation.
5. Keep it portal-neutral; if no portal owner exists, recommend managed and say why.
6. Emit the catalog model + template + the Structured Output block (with `Cognitive load removed:` and `Handoff to build teams:`).
