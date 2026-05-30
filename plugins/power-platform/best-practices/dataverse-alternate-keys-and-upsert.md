# Define alternate keys on natural keys and use Upsert to import GUID-free across environments

**Status:** Pattern — the default for cross-environment data movement and natural-key lookups.

**Domain:** Dataverse / Data modeling

**Applies to:** `power-platform`

---

## Why this exists

Every Dataverse row's primary key is a system GUID, and **GUIDs differ across environments** — the `account` you imported into dev has a different `accountid` in test and prod. Code, flows, and import scripts that key on GUIDs therefore need a translation table per environment, which is the migration tax this rule eliminates. An **alternate key** declares one or more columns as a *natural* unique key (e.g. `cnt_code`, or `email` + `region`); once defined, you can address a row by its business value via `(key=value)` in the Web API and, crucially, **Upsert** by that key — create-if-absent / update-if-present — without ever knowing the GUID. The trap: creating an alternate key on a column that **already has duplicates** produces a key definition that **silently does not enforce uniqueness**, with no warning in the designer. So the rule is two-part: define keys on natural keys, but only after verifying the data is actually unique.

## How to apply

Verify uniqueness, define the key, then Upsert by the key — no GUID anywhere.

```http
# 1) BEFORE creating the key on a populated table: check for existing duplicates.
GET /api/data/v9.2/cnt_projects?$select=cnt_code&$filter=cnt_code ne null
#    (group/count cnt_code in the results; if any value repeats, clean up FIRST —
#     a key created over duplicates is defined but NOT enforced, with no UI warning.)

# 2) Create the alternate key (async metadata job — poll until Active).
POST /api/data/v9.2/EntityDefinitions(LogicalName='cnt_project')/Keys
{ "@odata.type": "Microsoft.Dynamics.CRM.EntityKeyMetadata",
  "SchemaName": "cnt_project_code_key",
  "KeyAttributes": ["cnt_code"] }

# 3) UPSERT by the natural key — create-if-absent, update-if-present, GUID-free.
PATCH /api/data/v9.2/cnt_projects(cnt_code='PRJ-0042')
{ "cnt_name": "Atlas migration", "cnt_status": 100000001 }
#    Composite key: cnt_projects(cnt_code='PRJ-0042',cnt_region='EMEA')
```

Two controls worth knowing on the Upsert PATCH:
- Add header `If-Match: *` to force **update-only** (fail if the row is absent).
- Add header `If-None-Match: *` to force **insert-only** (fail if the row already exists).

**Do:**
- Define an alternate key on **any column you'll look up across environments**, especially during data migration — it removes the GUID-translation table entirely.
- **Query for duplicates first** on populated tables. A key over existing duplicates is created but inactive/unenforced, silently.
- Use **Upsert (`PATCH` to `table(key=value)`)** for idempotent, re-runnable imports — a failed batch can be safely re-run.
- Use a **composite** alternate key (multiple `KeyAttributes`) when no single column is unique (e.g. `email` + `region`).
- Wait for the key's async metadata job to reach **Active** before relying on it.

**Don't:**
- Hard-code GUIDs in flows, formulas, or import scripts — look up by name or alternate key (house rule §3 #11).
- Put **column-level security on a column used in an alternate key** — Dataverse lets you try, then throws runtime errors. Plan keys and FLS together at design time.
- Assume the key is enforcing uniqueness just because the designer accepted it — verify it's Active and that the source data had no duplicates.
- Treat an alternate key as a substitute for the primary key — it's an *additional* addressable unique index, not a replacement GUID.

## Edge cases / when the rule does NOT apply

- **Auto-number columns** give you a human-readable per-row ID but are **not** unique-keys by themselves and have **gaps** across imports/deletes — pair an auto-number with an alternate key if you need both readability and addressability.
- **High-write tables**: every alternate key is an enforced unique index, so it adds write-time cost and lock contention — don't add keys you won't query by.
- A **GUID is fine to use within a single environment** at runtime (it's stable there); the cross-environment translation problem is specifically a migration/ALM concern.
- Upsert semantics depend on the key matching exactly — a **case/format mismatch** on the natural key value creates a *new* row instead of updating, which looks like a duplicate-import bug.

## See also

- [`../skills/dataverse-web-api/resources/dataverse-design-rules.md`](../skills/dataverse-web-api/resources/dataverse-design-rules.md) — "Alternate Keys on Existing Duplicates" silent-failure gotcha; "Creating alternate keys before data cleanup" trap
- [`../skills/dataverse-web-api/resources/security-model.md`](../skills/dataverse-web-api/resources/security-model.md) — "Cannot apply column-level security to columns used in alternate keys"
- [`./dataverse-bulk-operations-and-throttling.md`](./dataverse-bulk-operations-and-throttling.md) — batching Upserts under service-protection limits
- [`../knowledge/dataverse-decision-trees.md`](../knowledge/dataverse-decision-trees.md) — `## Decision Tree: Data modeling — addressing rows across environments`
- [`../agents/dataverse-architect.md`](../agents/dataverse-architect.md) — owner; "Alternate keys for any column you'll look up across environments"

## Provenance

Grounded in `skills/dataverse-web-api/resources/dataverse-design-rules.md` (the silent unenforced-key-over-duplicates gotcha and the check-first query), `resources/security-model.md` (the alternate-key + column-security incompatibility), and the `dataverse-architect` opinion "Alternate keys for any column you'll look up across environments … Lets you avoid GUID translation tables." Upsert `PATCH table(key=value)` and the `If-Match`/`If-None-Match` controls are the documented Dataverse Web API behavior — verify the exact header semantics against current Microsoft Learn before relying on insert-only/update-only enforcement.

---

_Last reviewed: 2026-05-30 by `claude`_
