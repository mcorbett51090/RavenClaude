---
name: salesforce-release-pipeline
description: Stand up a 2GP + DevOps Center release pipeline — packaging, dependency-ordered deploy, test gate, and promotion across environments. Use when designing or running a Salesforce release process.
---

# Salesforce Release Pipeline

Define a repeatable, source-tracked release pipeline so prod is deployed to, never clicked in (house opinion #15).

## When to use

Setting up CI/CD for a Salesforce org, or planning a specific release.

## Steps

1. **Source of truth.** sfdx project layout (`sfdx-project.json`) with package directories; everything in version control. See `templates/sfdx-project-manifest.md` and `knowledge/packaging-and-deployment.md`.
2. **Package it.** Bundle metadata into an **unlocked 2GP** (internal) or **managed 2GP** (ISV) package; version it and declare dependencies.
3. **Order the deploy.** Stage metadata by dependency — objects/fields before code, permission sets after objects, Flows/triggers after referenced types.
4. **Gate on tests.** Run Apex tests with the right test level; enforce ≥75% coverage **plus** bulk assertions (not coverage alone).
5. **Validate before deploy.** Check-only (validation) deploy against the target before the real one.
6. **Promote via DevOps Center / CI.** Work-item-based promotion across scratch/dev → integration → UAT → prod. Never a manual change set to prod.

## Output

The pipeline stages, the package definition, the dependency order, and the test/validation gates — ready to wire into CI.
