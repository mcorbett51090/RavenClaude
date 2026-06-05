# Document the single-tenant assumption explicitly so a multi-tenant pivot doesn't inherit a silent gap

**Status:** Absolute rule
**Domain:** Multi-tenancy / architecture
**Applies to:** `data-platform`

---

## Why this exists

A single-tenant deliverable has no tenant axis — so it needs no RLS policy, no JWT `tenant_id` claim, and no cross-boundary denial test. That is correct and intentional. The problem arises when the client later adds a second tenant and inherits the schema and embed code without realizing that no tenant controls were ever built. The missing control is invisible — the schema still works, the dashboard still loads, and no error surfaces. The fix is to record the assumption as an explicit architectural decision so a future developer sees exactly what is absent and why.

## How to apply

In the `stack-decision-record.md` for every single-tenant engagement, add a tenancy section:

```markdown
## Tenancy model

**Classification:** Single-tenant (as of YYYY-MM-DD)

**What this means:**
- No `tenant_id` column on fact/dimension tables.
- No Postgres RLS policy on any table.
- No `tenant_id` claim in JWTs.
- No cross-boundary denial test (N/A — single tenant).

**Multi-tenant pivot checklist (if the client ever adds a second tenant):**
- Add `tenant_id uuid NOT NULL` to every fact + dimension table (backfill required).
- Author RLS policies via `skills/rls-policy-authoring`.
- Add `tenant_id` claim to JWT issuance via `skills/jwt-embed-issuance`.
- Write and run the cross-boundary denial test (`templates/rls-cross-tenant-test.sql`).
- Re-route through `ravenclaude-core/security-reviewer` before merge.
```

**Do:**
- Add the tenancy section to `stack-decision-record.md` at engagement start, not after.
- Keep the checklist as a living artifact in the repo (e.g., `docs/architecture/tenancy.md`).
- Revisit when any engagement scope change mentions "a second client" or "white-labeling."

**Don't:**
- Omit the assumption because "it's obvious this is single-tenant."
- Mark the cross-boundary denial test as N/A without writing why.
- Assume a single-tenant schema can become multi-tenant with a minor migration — the `tenant_id` column propagation + backfill is non-trivial.

## Edge cases / when the rule does NOT apply

This rule applies to every single-tenant engagement. There are no exceptions — documenting an assumption costs one paragraph; discovering its absence during a live pivot costs a re-architecture.

## See also

- [`../agents/database-setup-guide.md`](../agents/database-setup-guide.md) — owns schema design and tenancy documentation
- [`./enforce-tenant-isolation-closest-to-data.md`](./enforce-tenant-isolation-closest-to-data.md) — the isolation rule that kicks in when multi-tenancy is introduced

## Provenance

Codifies data-platform CLAUDE.md §3 house opinion #3, sub-point: "Single-tenant deliverables: no tenant axis = no tenant policy — but document the assumption so a future multi-tenant pivot doesn't inherit a silently-missing control."

---

_Last reviewed: 2026-06-05 by `claude`_
