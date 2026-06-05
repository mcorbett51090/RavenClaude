# Choose the database before the dashboard framework, not after

**Status:** Absolute rule
**Domain:** Engagement architecture / sequencing
**Applies to:** `data-platform`

---

## Why this exists

The most common sequencing error in a dashboard engagement is picking the visualization framework first and then discovering its data connection requirements constrain the database choice. Metabase requires a live Postgres/MySQL connection and its multi-tenant security depends on Postgres-level RLS — if you commit to Metabase before asking "does this need RLS at the DB layer?", you've inherited an architecture decision by accident. Picking the database first, by workload shape and tenant model, lets the dashboard framework selection flow naturally from the data layer's capabilities.

## How to apply

Follow the Case A/B/C/D sequencing from the `stack-selection` skill:

1. **Start with the engagement classification** (Case A: portfolio/Evidence; B: client deliverable/Superset/Metabase; C: productized SaaS/Cube+React; D: M365/Power BI).
2. **Select the database** for the chosen Case using the workload-match decision tree.
3. **Derive the ELT tooling** from the source systems and the DB choice.
4. **Then select the dashboard framework** — by Case and by what the DB layer already enforces (RLS capabilities, connection model, materialization support).

**Explicit sequencing gate in `dashboard-engagement-checklist.md`:**

```markdown
## Sequencing gate (must complete in order)
- [ ] Engagement Case classified (A/B/C/D)
- [ ] Database selected (workload + tenant model drives this)
- [ ] ELT tooling selected (sources + DB drives this)
- [ ] Dashboard framework selected (Case + DB capabilities drives this)
```

**Do:**
- Use the `stack-decision-record.md` template to record the decision in sequence.
- Name the tenant model (single/multi) before any dashboard framework is mentioned.
- If a client pre-selects a dashboard tool, work backward to confirm the DB layer supports its security model.

**Don't:**
- Recommend a dashboard framework before the database is chosen.
- Let a client's preference for a specific BI tool drive you to a database that can't enforce their tenant model.
- Accept "we'll figure out the DB later" as a valid engagement posture.

## Edge cases / when the rule does NOT apply

- If the client is already on a fixed database (e.g., they run Supabase in production), the DB is a constraint, not a choice. In this case, select the dashboard framework from the DB's capabilities and document the constraint.

## See also

- [`../agents/database-setup-guide.md`](../agents/database-setup-guide.md) — the sequencing entry point for the DB selection step
- [`./warehouse-select-by-workload-not-brand.md`](./warehouse-select-by-workload-not-brand.md) — the workload-first DB selection rule

## Provenance

Codifies data-platform CLAUDE.md §4 anti-patterns: "A new client engagement where the database choice happens *after* the dashboard framework is picked (gets the layering wrong)."

---

_Last reviewed: 2026-06-05 by `claude`_
