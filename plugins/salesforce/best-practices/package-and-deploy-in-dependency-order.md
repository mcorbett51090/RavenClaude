# Package metadata in 2GP and deploy in dependency order — never click-deploy to prod

**Status:** Pattern — strong default; deviate only with a written reason and a migration note.

**Domain:** ALM / packaging & release

**Applies to:** `salesforce`

---

## Why this exists

A change set hand-clicked into production has no source of truth, no repeatable order, and no rollback. The two failure modes are (1) deploying a class before the field it references exists — the deploy fails halfway, leaving the org in a partial state — and (2) "it worked in the sandbox" coverage that turns out to be below the 75% production gate. Second-generation packages (2GP) plus a source-tracked pipeline make the unit of release versioned, ordered, and auditable. This is house opinion #15 and the `salesforce-platform-architect`'s release discipline.

## How to apply

Pick the package type by audience, declare dependencies so installs order themselves, and promote through a pipeline (DevOps Center / CI), validating check-only before the real deploy.

```bash
# Internal modular dev → unlocked 2GP package, versioned, dependency-declared
sf package version create --package "Billing" --installation-key-bypass --wait 30

# Validate (check-only) against prod BEFORE the real deploy — runs tests, no commit
sf project deploy validate --target-org prod --test-level RunLocalTests

# Only after validation passes: the real deploy, same ordered manifest
sf project deploy start --target-org prod --test-level RunLocalTests
```

**Do:**
- Use **unlocked 2GP** for internal modular development; **managed 2GP** for ISV/AppExchange distribution (namespace + IP protection).
- Deploy in dependency order: objects/fields before the code that references them; permission sets after the objects; Flows/triggers after their referenced types.
- Gate on **≥75% org-wide Apex coverage** with real bulk assertions — and run a check-only validation before every prod deploy.
- Source-control the project and promote through **DevOps Center** (or equivalent CI).

**Don't:**
- Click-deploy a change set straight into production.
- Treat 75% coverage as a quality measure — it is a deploy gate; pair it with the 200-record bulk assertions.

## Edge cases / when the rule does NOT apply

A genuine one-off, low-risk config tweak (a new picklist value, a report) does not need a package — but it still belongs in the pipeline's source so the org's state stays reproducible. Hotfixes under incident pressure may deploy a minimal source set directly, but the change is back-ported to the package and pipeline immediately after, never left as a divergent manual edit. The 75% gate is a Salesforce platform floor, not a house preference — it cannot be waived.

## See also

- [`../knowledge/packaging-and-deployment.md`](../knowledge/packaging-and-deployment.md) — the package-type decision tree, deploy ordering, and the coverage gate
- [`./bulkify-every-soql-and-dml.md`](./bulkify-every-soql-and-dml.md) — the bulk assertions that make coverage meaningful
- [`../templates/sfdx-project-manifest.md`](../templates/sfdx-project-manifest.md) — the project manifest skeleton
- [`../agents/salesforce-platform-architect.md`](../agents/salesforce-platform-architect.md) — the agent that owns packaging and release

## Provenance

Codifies house opinion #15 from [`../CLAUDE.md`](../CLAUDE.md) and the `salesforce-platform-architect`'s release discipline. Grounded in [`../knowledge/packaging-and-deployment.md`](../knowledge/packaging-and-deployment.md), sourced from Salesforce's 2GP, Metadata-API-deployment, and code-coverage documentation.

---

_Last reviewed: 2026-05-30 by `claude`_
