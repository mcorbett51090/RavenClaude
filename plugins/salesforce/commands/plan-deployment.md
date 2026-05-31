---
description: Plan a safe Salesforce deployment — pick the test level deliberately, deploy in dependency order, route deletions through destructiveChanges (not the org UI), use validation-only deploys in CI, and stage through scratch/sandbox with source tracking.
argument-hint: "[what's being deployed and to which org, e.g. 'trigger + LWC to UAT']"
---

# Plan a deployment

You are running `/salesforce:plan-deployment`. Produce a safe, ordered deployment plan for the change the user described (`$ARGUMENTS`), following this plugin's ALM best-practices and the `salesforce-release-pipeline` skill. This is the `salesforce-platform-architect`'s release discipline.

## When to use this

Before pushing metadata to a shared org (UAT/staging/prod) — especially when the change spans multiple metadata types or includes deletions.

## Steps

1. **Deploy in dependency order** (`package-and-deploy-in-dependency-order`): fields before the layouts/flows that use them; objects before their triggers; permission sets last. List the order explicitly.
2. **Pick the test level deliberately** (`alm-pick-the-deploy-test-level-deliberately`): `RunLocalTests` for prod, `RunSpecifiedTests` for a scoped sandbox deploy, `NoTestRun` only in scratch. Never default blindly.
3. **Validation-only first in CI** (`alm-ci-cd-with-validation-only-deploys`): a `--dry-run` / check-only deploy validates against the target before the real one — catches failures without a partial deploy.
4. **Deletions go through destructiveChanges** (`alm-deletions-go-through-destructive-changes-not-the-org-ui`), never the org UI — so the removal is in source control and reproducible.
5. **Config is metadata, not data** (`platform-config-as-metadata-not-data`): app config travels as metadata; only true data goes via Data Loader.
6. **Stage through environments** (`alm-scratch-orgs-and-source-tracking`, `platform-org-strategy-and-environments`): scratch → sandbox → prod, with source tracking; for modular delivery use 2GP unlocked packages (`alm-2gp-unlocked-package-modularization`).
7. Emit the ordered `sf project deploy` / `sf project deploy validate` commands and the rollback note.

## Guardrails

- Never delete metadata through the org UI on a tracked org.
- Never run a prod deploy without a prior validation-only pass.
- Tee up the actual deploy commands but leave the prod execution to the human (high-blast) with the exact command ready.
