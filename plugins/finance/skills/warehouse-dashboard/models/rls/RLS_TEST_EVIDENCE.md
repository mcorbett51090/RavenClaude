# RLS denial test — EXECUTED evidence (DB layer)

The warehouse-dashboard entity-level isolation is no longer "specified only" for the
**Postgres layer**. `run_rls_denial_test.sh` stands up a disposable `postgres:16`
container, applies the **shipped** `close_rls_policies.sql` (roles, `ENABLE`+`FORCE`
RLS, the array-claim policy) + `bootstrap_test_schema.sql`, and runs the **shipped**
`rls_cross_entity_denial_test.sql`. No live credentials, no warehouse — just Docker.

## Result (postgres:16-alpine, 2026-07-06)

```
RESULT granted=1 (expect 1)        # portfolio {A} sees exactly entity A
RESULT leaked=0 (expect 0)         # explicit WHERE entity_id=B returns nothing — RLS overrides the filter
RESULT unset=0 (expect 0)          # no grant → deny all (fail-closed)
RESULT empty=0 (expect 0)          # empty '{}' grant → deny all (not "see everything")
RESULT portfolio_AC=2 (expect 2)   # array claim {A,C} returns the 2-entity portfolio (the finance delta)
== ✅ FORCE-RLS cross-entity denial PROVEN against postgres:16-alpine ==   (exit 0)
```

## What this proves (and what it still does not)

**Proven (DB layer):** the load-bearing control works — a viewer granted entity A
cannot read entity B **even with an explicit filter**, the FORCE clause defeats a
table-owner exemption, an unset/empty grant fail-closes, and the **array-claim `IN`**
correctly returns a multi-entity portfolio (the finance delta over a scalar
`tenant_id`). This directly answers the security review's open question *"is the
Postgres FORCE-RLS actually reached?"* — **yes**.

**Two fixes surfaced by executing it (folded into the shipped files):**
1. `rls_cross_entity_denial_test.sql` — the per-request `SET LOCAL` is a silent no-op
   outside an explicit transaction, so each grant+query block is now wrapped in
   `BEGIN/COMMIT` (a naive autocommit run previously false-failed).
2. `close_rls_policies.sql` — the predicate now coerces an empty-string GUC via
   `NULLIF(current_setting('app.entity_ids', true), '')::uuid[]`, so a lingering
   `SET LOCAL` (which leaves the placeholder as `''`) fail-closes to zero rows instead
   of aborting the query with a cast error.

**Still NOT proven here (needs infra a container can't cheaply supply):** the **Cube**
semantic-layer `access_policy` (array = `IN`) — that needs a running Cube instance;
and the **live JWT issuer / IdP** that mints the `allowed_entities[]` claim. Those
remain the consumer's first-light steps. The isolation claim is gated on the Cube
denial test too — do not treat this DB-layer pass as end-to-end tenant isolation.
