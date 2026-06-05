# Segment solutions by functional domain, not by component type

**Status:** Pattern
**Domain:** Power Platform ALM
**Applies to:** `power-platform`

---

## Why this exists

A common naive segmentation puts all tables in one solution, all flows in another, and all apps in a third. This creates circular dependencies at import time (the apps solution imports before the tables solution is fully settled) and makes it impossible to release a domain feature independently. The correct segmentation follows functional ownership: a "Customer Onboarding" solution owns the tables, flows, apps, and views that implement that domain — so a patch to customer onboarding does not require re-importing the entire org's table schema. Domain-based segmentation aligns with the platform's own dependency tracking and produces a dependency graph that `pac solution check` can validate.

## How to apply

Segmentation principles:

| Principle | Rationale |
|---|---|
| **Shared foundation** — a base solution holds org-wide shared entities (Contact, Account extensions, global option sets, publisher prefix) | Other solutions depend on it; it changes infrequently |
| **Feature domain** — each business domain (e.g., Complaints, Onboarding, Billing) owns the components it authors | Deploy independently; patch independently |
| **App solution** — canvas or model-driven apps that *consume* shared + domain components but do not own the schema | Can be re-deployed without re-running the domain migration |
| **Governance solution** — DLP notes, environment variable definitions, connection references for the domain | Travels with the domain, rebindable on import |

**Do:**
- Define the dependency order in the ALM pipeline: base → domain → app, with the base solution promoted first.
- Use `pac solution add-reference` to wire inter-solution dependencies so `pac solution build` respects the order.
- Confirm the dependency graph is acyclic: `pac solution check` in the pipeline stage catches circular deps before import.

**Don't:**
- Put a table in Solution A and the flow that writes to it in Solution B if B deploys before A — the flow import fails or runs without the table.
- Create a "miscellaneous" catch-all solution for components that don't fit — miscellaneous grows into the monolith you were avoiding.
- Mix managed and unmanaged components from different domains in a single solution — the managed/unmanaged discipline from `managed-vs-unmanaged-solution-discipline.md` must hold per solution.

## Edge cases / when the rule does NOT apply

For small projects (one domain, one team, fewer than 30 components), a single solution with clear naming is acceptable. Document the decision; revisit when the project exceeds the threshold.

## See also

- [`../agents/solution-alm-engineer.md`](../agents/solution-alm-engineer.md) — owns solution structure and pipeline design
- [`./alm-pipeline-stages-dev-test-prod.md`](./alm-pipeline-stages-dev-test-prod.md) — the promotion pipeline this segmentation feeds into

## Provenance

Codifies `solution-alm-engineer`'s opinion from CLAUDE.md §3 and the `alm-pipeline-design` skill; standard Power Platform solution layering practice documented in Microsoft Learn.

---

_Last reviewed: 2026-06-05 by `claude`_
