---
name: warehouse-dashboard
description: "Turn per-entity close packages into a recurring, warehouse-backed, MULTI-TENANT controller dashboard where one controller sees only their PORTFOLIO of entities. Flattens close packages into fact/dim rows (scripts/close_package_to_rows.py, KPI parity with entity_dashboard.derive_kpis), resolves an allowed_entities[] array claim deny-all-by-default (scripts/entity_rls.py), and ships reference dbt marts + a Cube access_policy + Postgres FORCE-RLS. REUSES data-platform for the security surface. Used by `controller` + `board-pack-composer`."
---

# Skill: warehouse-dashboard

**Purpose:** The `per-entity-dashboard` skill renders ONE entity, one period, file-in/file-out. This skill is the **recurring, warehouse-backed, multi-tenant** tier above it: many entities, row-level isolation, an embedded live dashboard, where a controller who runs an outsourced-close portfolio sees **only the entities they were granted** — not the whole group.

It builds **only the finance-specific deltas** and **reuses `data-platform`** for the security surface. It does not re-implement auth, JWT issuance, RLS mechanics, or dbt scaffolding.

Engines (stdlib only, Python 3.8+):
- [`../../scripts/close_package_to_rows.py`](../../scripts/close_package_to_rows.py) — close package → `dim_entity`, `dim_period`, `fct_close_statement_line`, `fct_recon_exception`, `fct_flux_movement`, `fct_close_kpi`, `fct_close_state`. `fct_close_kpi` is produced by **importing and calling** `entity_dashboard.derive_kpis` — so warehouse KPIs are **byte-identical** to the single-entity dashboard's (KPI parity), and an absent input is `value=null / is_na=true`, never plugged.
- [`../../scripts/entity_rls.py`](../../scripts/entity_rls.py) — the `allowed_entities[]` **array-claim resolver**. `resolve(requested, allowed)` returns the intersection; the token envelope (`resolve_from_claim`) **fails closed** on expired / missing-claim / >30-min-TTL. This is the tested proof-of-invariant core.

## What to REUSE from `data-platform` (do NOT hand-roll these)

The security surface is `data-platform`'s owned lane. This skill names the four skills you invoke and supplies only the finance deltas on top:

| data-platform skill | What it owns | The finance delta this skill adds |
|---|---|---|
| [`rls-policy-authoring`](../../../data-platform/skills/rls-policy-authoring/SKILL.md) | Postgres FORCE-RLS, the closeness-to-data invariant, the denial-test contract | ARRAY predicate `entity_id = ANY(current_setting('app.entity_ids',true)::uuid[])` for a **portfolio**, not a scalar `tenant_id` |
| [`jwt-embed-issuance`](../../../data-platform/skills/jwt-embed-issuance/SKILL.md) | Short-lived signed embed JWT, required claims, 5–15 min TTL, rotation | The token carries an **`allowed_entities[]` array claim**; `entity_rls.py` resolves it deny-all-by-default |
| [`cube-schema-scaffolding`](../../../data-platform/skills/cube-schema-scaffolding/SKILL.md) | Cube `access_policy` / `securityContext`, measures/dimensions, denial test | `securityContext.allowed_entities` with **`operator: in`** (explicit array-membership; on the cubes AND the view — see the caveat below) |
| [`dbt-project-scaffolding`](../../../data-platform/skills/dbt-project-scaffolding/SKILL.md) | sources→staging→marts, tests, doc-blocks, `build_role`/`query_role` split | The finance close **semantic schema** (marts under `models/`), query role is `finance_close_query_role` (NO BYPASSRLS) |

Any change to these files routes to **`ravenclaude-core/security-reviewer`** (finance CLAUDE.md §2, §10).

## The reference semantic schema — `models/` (specified, not executed)

There is **no warehouse in this repo**, so `models/` is reference SQL/YAML, not a running deployment:

```
models/
  staging/   stg_close__*.sql + _finance_close__sources.yml   (raw → typed, one per table)
  marts/     dim_entity, dim_period, fct_close_statement_line, fct_recon_exception,
             fct_flux_movement, fct_close_kpi, fct_close_state + _close_marts__models.yml
  cube/      close_kpi.yml        — access_policy scoping entity_id to securityContext.allowed_entities
                                    (operator: in, explicit array-IN); the partner-facing portfolio_close
                                    VIEW carries its OWN identical access_policy too (belt-and-suspenders)
  rls/       close_rls_policies.sql            — ENABLE + FORCE RLS, ANY(uuid[]) predicate, query role NO BYPASSRLS
             rls_cross_entity_denial_test.sql  — the go-live gate (MUST return zero rows for an ungranted entity)
```

## The 3 go-live denial tests (all must pass before a real deployment)

Enforcement here is **specified, not executed** — so before go-live a consumer proves each of these against real infrastructure:

1. **Claim resolution `[done]` (runs in THIS repo).** `entity_rls.resolve` / `resolve_from_claim` prove the deny-all invariant: Bob (entity C) requesting A+B → `[]`; partial overlap keeps only the granted; expired / missing-claim / >30-min-TTL → `[]`. Covered by `scripts/test_warehouse_rls.py` — the one denial test that is green in this repo today.
2. **Postgres FORCE-RLS denial (consumer runs).** Deploy `rls/close_rls_policies.sql`, then run `rls/rls_cross_entity_denial_test.sql` against a fresh test DB in CI: grant entity A only, prove entities B and C return **zero rows**, and prove an **unset** `app.entity_ids` denies everything (fail-closed). No test passing = no merge.
3. **Cube `access_policy` denial (consumer runs).** Issue an embed JWT whose `allowed_entities` is `[A]`, request entity B through Cube, and prove **zero rows** — the `securityContext.allowed_entities` filter overrides the explicit request (the cross-boundary denial test from `cube-schema-scaffolding`).

## Consumer runbook

```shell
# 1. Produce a close package per entity (existing controller-autopilot cycle).
python3 scripts/controller_cycle.py --entity entity-A.json --coa coa.csv \
    --tb tb-2026-06.csv --prior-tb tb-2026-05.csv --subledger sub.csv \
    --run-dir ./run-A --out-json close-A.json

# 2. Flatten each package into fact/dim CSVs (grain entity_id × period).
python3 scripts/close_package_to_rows.py --package close-A.json --out-dir ./rows-A
#    (pass --entity-id <uuid> to use your warehouse's real entity id;
#     default derives a stable UUID-shaped id from the entity name.)

# 3. Land the CSVs into the raw schema (consumer ELT), then run dbt (reference):
#    dbt build   # staging → marts, with the tests in _close_marts__models.yml

# 4. Deploy the enforcement layer + PROVE it (consumer infra):
#    psql -f models/rls/close_rls_policies.sql
#    psql -f models/rls/rls_cross_entity_denial_test.sql   # must return zero leaked rows
#    (Cube-fronted stack: deploy models/cube/close_kpi.yml + run the Cube denial test.)

# 5. Per request, the host app resolves the token's array claim and sets the context:
python3 scripts/entity_rls.py --claim embed-claim.json --now 1800000000 \
    --requested "aaaa...,bbbb..."     # -> {"granted": [...], "denied": false, ...}
#    then: SET LOCAL app.entity_ids = '{<granted uuids>}';   (never SET — pool leak)
```

## Honest limitations — READ THIS

- **Decision-support / reference implementation, NOT an audited close or a live-verified system.** The engines run and are tested; the security schema is **specified, not executed** (there is no warehouse, Cube, or Postgres here).
- **SPLIT-BRAIN (read with `idp-segregation`).** The RLS `allowed_entities[]` array claim (entity *entitlement*) and the close's *SoD identity* MUST come from **one verified token / issuer**. Two separate tokens let a viewer hold entitlement as one principal while the close is approved under another. Bind them with `entity_rls.bind_entitlement_to_identity(entity_claims, identity)`, which fails closed unless the entitlement token's `iss` + `sub@iss` match the verified `VerifiedIdentity`.
- **"Tenant isolation" is a GATED claim — the claims-layer test ALONE does not establish it.** `entity_rls`/`resolve_from_claim` (green in this repo) prove only the *policy decision* (the array-claim intersection + envelope fail-closed). Isolation is only established once **BOTH** enforcement denial tests pass **against a containerized instance**: (1) the **Postgres FORCE-RLS** denial test (`rls/rls_cross_entity_denial_test.sql` — ungranted entities and an unset `app.entity_ids` return zero rows) **AND** (2) a **Cube `access_policy`** denial test (an embed JWT scoped to `[A]` requesting entity B returns zero rows). Until both pass on real infra, do not claim tenant isolation — claim only "the policy decision is tested."
- **`entity_rls.py` is the policy *decision*, not the enforcement.** It does the array-claim intersection and the token-envelope checks; it does **not** verify a JWT signature, bind the claim to an authenticated identity, or cut a single row at the database. Signature verification is the host app's job (`jwt-embed-issuance`); the row cut is the warehouse's job (FORCE-RLS / Cube `access_policy`). It is a **second, testable** place the deny-all invariant is written down — never the only place.
- **Cube array-membership filter spelling is UNVERIFIED.** `operator: in` is pinned as the explicit array-IN form for the `securityContext.allowed_entities` row-level `access_policy` filter (per the security review, rather than relying on `equals`-against-an-array compiling to SQL `IN`). The exact spelling is asserted from the array-filter convention, not verified against a running Cube here. Confirm against cube.dev/docs for your version and prove it with the denial test before go-live.
- **Enforcement is specified, not executed.** It **needs `ravenclaude-core/security-reviewer` sign-off and a real warehouse/IdP** before it protects anything. Live wiring, the IdP, the warehouse, and real credentials are the consumer's step.
- **security_review_targets:** `scripts/entity_rls.py`, `models/rls/close_rls_policies.sql`, `models/rls/rls_cross_entity_denial_test.sql`, `models/cube/close_kpi.yml`.

## Scope boundary

This skill owns the **finance deltas** only: the close→rows flattener, the array-claim resolver, and the finance close semantic schema. The **security mechanics** (RLS enforcement patterns, JWT issuance/verification, Cube `access_policy` correctness, dbt scaffolding discipline) are `data-platform`'s owned surface — reuse them, and route auth/RLS/embed changes to `ravenclaude-core/security-reviewer`. Cross-plugin reference is soft/optional per the marketplace graceful-degradation convention; if `data-platform` is not installed, treat its four named skills as the design pointer for the security tier.
