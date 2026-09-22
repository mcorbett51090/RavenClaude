# Cube cross-tenant denial test harness

**New (FORGE dashboard-top1pct P1-9, 2026-09-03).** An executable, docker-compose-backed
integration test replacing the "documented procedure, not a passing CI check" status both app
starters previously carried in their `test/cross-tenant-denial.md` files.

## Why this exists, and why it wasn't built sooner

data-platform's own house rule (§3 #3): *"Every stack ships a cross-boundary denial test
appropriate to its enforcement layer… No test, no merge."* Both starters' `test/cross-tenant-
denial.md` deliberately shipped as a **procedure**, not a script — "a script that always
'passes' because it never actually reaches a live Cube instance would be worse than no test."
That reasoning was correct; the closeable gap was never the script, it was the missing
environment. This harness provides that environment as a CI-only fixture.

**Scope note.** This is a `docker-compose` stack brought up for the duration of a CI job and
torn down afterward — a **test fixture**, not persistent infrastructure. No ongoing cost, no
persistent address. If a stricter reading of "no live infrastructure" applies to your fork of
this plugin, treat this directory as optional and keep using the documented procedure instead.

## What's in here

```
docker-compose.yml         → Postgres 16 + Cube v1.7.33 (pinned — see the file's own comment
                              on why: P0-1's finding that access_policy needs Cube Core >=1.2.0)
seed/two-tenant-fixture.sql → tenant-A (2 orders, $425.50) + tenant-B (1 order, $425.00) —
                              deliberately distinct amounts so a leaked cross-tenant read is
                              unambiguous, not a coincidental match
tests/cross-tenant-denial.test.ts → vitest: positive control (tenant A sees its own revenue) +
                              denial (tenant A cannot see tenant B's, at both the Cube
                              access_policy layer and the Postgres RLS layer) + (P2-14, added
                              2026-09-03) an export-path denial block covering the ROW-LEVEL
                              dimensional query shape the starters' /api/export routes issue —
                              a materially different shape than the dashboard's aggregate-
                              measures query above, including a service-identity-token test
                              (no tenant_id claim) mirroring the exact failure mode named in
                              best-practices/export-runs-under-the-viewer-scope-never-a-
                              service-identity.md + (P2-17, added 2026-09-03) a request-tagging
                              block asserting Cube's REST API accepts a client-set X-Request-Id
                              header and the tagged query stays tenant-scoped — it does NOT
                              assert the tag reaches Cube's Query History export, which needs
                              Cube Cloud or a self-hosted monitoring integration this compose
                              fixture doesn't stand up (named limit, not a silent skip; see
                              knowledge/dashboard-query-cost-instrumentation.md)
```

## Running it

```bash
docker compose up -d --wait   # brings up Postgres + Cube, waits for both health checks
npm install
npm test                       # or: DP_INTEGRATION=1 ./run-from-audit-gates.sh (see below)
docker compose down -v         # tear down — this is a fixture, not infrastructure
```

⛔ **Honest status:** this harness has been authored and reasoned through carefully (the Cube
REST API shape, the `access_policy` override semantics, the Postgres `SET LOCAL` RLS contract)
but has **not been executed against a live Cube+Postgres pair in the session that built it** —
no docker runtime was available in that sandbox. What **was** verified without docker:
`docker-compose.yml` parses as valid YAML; the Cube image tag (`cubejs/cube:v1.7.33`) was
confirmed to exist via the Docker Hub registry API directly, not just a documentation search;
the schema mount path matches Cube's own documented convention (verified via Context7 against
Cube's official docs, not assumed); the test file typechecks clean and — run against no live
server — correctly fails with `ECONNREFUSED` rather than a syntax or import error, proving its
structure is sound (6 tests collected — the original 4 plus the P2-14 export-path pair — 6
skipped, 0 syntax/import failures). **Running this for real, once, with docker present, is the
first thing to do before trusting it in CI.**

⛔ **A specific, unresolved question this run would settle (flagged by security review, P2-14,
2026-09-03):** `../cube-schema-starter.yml` gates every `access_policy` block on `role: viewer`
(confirmed by inspection — lines 42, 134, 202), but **no token minted anywhere in this plugin
carries a `role`/`roles` claim**, and no `contextToRoles` config is mounted into the Cube
container (confirmed — `grep`'d both mint-token modules and this whole directory). Whether that
means the policy silently never binds (in which case *something else* — likely the
`securityContext.tenant_id` filter itself, independent of the role gate — is doing the real
work) or whether Cube's own default-deny-on-unmatched-policy behavior makes this a moot point is
genuinely **not known** — it's inference from Cube's current docs, not an observation from this
harness. Direction of failure matters: Cube's docs currently say an unmatched policy group
**denies**, not leaks, which is why this is flagged as an open question rather than a blocker —
but the docs' current terminology (`group:`) doesn't match this schema's (`role:`), which may
itself be a syntax rename relative to the pinned `v1.7.33`. This is exactly the kind of thing
running the harness once, for real, converts from inference to observation — and P2-14's
row-level export makes the answer matter more than it did when only aggregate queries were at
stake.

## The superuser-bypasses-RLS trap this harness deliberately avoids

The compose Postgres user (`cube_test`, from `POSTGRES_USER`) is the database's initial
superuser — and **a Postgres superuser always bypasses Row Level Security, regardless of
policy.** An RLS-layer test connected as that user would pass unconditionally and prove
nothing. `seed/two-tenant-fixture.sql` grants `LOGIN` to `database-schema-starter.sql`'s own
`viewer_role` specifically so the test can connect as the actual RLS-enforced role — the test
file's `PG_CONNECTION_STRING` default connects as `viewer_role`, never `cube_test`. If you
modify this harness, preserve that distinction; it is the single easiest way for a "passing"
RLS test to be silently meaningless.

## Wiring into CI (`audit-gates.sh` Tier 4, opt-in)

`scripts/audit-gates.sh` gates this behind `DP_INTEGRATION=1` (never in the default run — it
needs docker) and is required only on a PR that touches a starter, a Cube schema, or an RLS
template. See that script's own Tier-4 section for the exact invocation and the "docker
absent → loud-skip, not a silent pass" contract.

## Mutation tests (the teeth, per plan.md's own acceptance criteria — NOT yet run)

1. Delete the `access_policy` block from `../cube-schema-starter.yml` → the Cube-layer denial
   test must **fail** (tenant B's real revenue, 425.00, leaks through). Restore → passes again.
2. Drop `FORCE ROW LEVEL SECURITY` from `../database-schema-starter.sql` → the RLS-layer test
   must fail. Restore → passes again.

Neither mutation has been run in this session (same docker-absent limitation as above) — they
are the acceptance test this harness is built to satisfy, recorded here so the next session
with docker available can run them directly rather than re-deriving what to check.

## Refresh triggers

- Cube major version bump past the pinned `v1.7.33` (re-verify the image tag still exists and
  still satisfies the `>=1.2.0` `access_policy` floor)
- `database-schema-starter.sql` or `cube-schema-starter.yml` structural changes (table/cube
  renames need mirroring in `seed/two-tenant-fixture.sql` and the test file's assertions)
- The first real run with docker present — update this file's "not yet executed" status once
  it has actually passed, don't just delete the caveat
