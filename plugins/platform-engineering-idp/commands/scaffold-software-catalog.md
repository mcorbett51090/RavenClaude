---
description: "Model the software catalog and produce catalog-info.yaml as code: components/systems/APIs/resources with an owner for every entity, the relationships, and the CI-validation + discovery convention."
argument-hint: "[what to model, e.g. 'our 3 services + the payments API + the Postgres they share']"
---

You are running `/platform-engineering-idp:scaffold-software-catalog`. Use the `idp-portal-engineer`
discipline and the `idp-portal-setup` skill.

## Steps

1. Model from the questions developers ask (ownership, dependencies, how-to-create), not the org chart.
2. Assign entity kinds (Component/System/Domain/API/Resource/Group) and relationships (ownedBy,
   dependsOn, providesApis, partOf).
3. Ensure **every entity has an owner** — flag any that don't.
4. Emit `catalog-info.yaml` from `templates/backstage-catalog-info.yaml`, one per repo, as code.
5. Define the CI-validation + VCS-discovery convention so the catalog stays authoritative (never
   hand-maintained in the UI).
6. Emit the Structured Output block with handoffs (golden-path-engineer for the create step's wiring;
   technical-writing-docs for TechDocs content).
