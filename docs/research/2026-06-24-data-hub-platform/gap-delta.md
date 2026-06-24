# Gap-delta — Plan A (opus, arch-first) vs Plan B (sonnet, pragmatic/skeptic)

## Where they AGREE (the spine — both panels independently converged here)
These are the load-bearing decisions both models reached. High confidence, but **flagged for the
critic to probe for correlated error**:
- **Stack:** TypeScript / Node 22, **Postgres single-tenant** as the control + analytics store.
- **Vault:** app-level **AES-256-GCM + per-customer DEK + KEK in a KMS off the app DB** (G1 1a). Both
  make the credential store the single chokepoint; both refuse plaintext-env fallback in prod.
- **Dashboards = Evidence.dev** (BI-as-code, Claude-authored, Git-versioned).
- **OAuth 2.1 + PKCE**, per-connector PKCE flag for older providers; refresh + reconnect on
  `invalid_grant`.
- **Incremental per-stream cursors** (not full-refresh); **idempotent outbound = upsert key** (G1 3a).
- **A connector abstraction that bounds maintenance** + **a versioned connector registry** are the
  answer to B.4 (they differ on *when/how deep*, not *whether*).
- **A metrics/semantic layer must exist before freehand SQL** (G1 5a); enforce "no raw-table refs in
  dashboards."
- **Phase 1 = a thin end-to-end vertical** (one connector → store → one Claude dashboard).

## Where they DIVERGE (the real conflicts → G4b tiebreak inputs)
| # | Decision | Plan A (arch-first) | Plan B (pragmatic) | Type | Impact |
|---|---|---|---|---|---|
| D1 | **Connector SDK depth/timing** | Declarative YAML manifest + CDK-style compiler from **P2** | Thin TS **base-class v1**; YAML manifest deferred to P4, **scale-gated** (3+ connectors copy-pasting) | substantive fork | HIGH — sets build cost + first-value date |
| D2 | **Semantic layer** | **Cube headless** + Evidence from the start | **dbt Core** + Evidence; Cube deferred to P3+ | substantive fork | HIGH — infra weight per instance |
| D3 | **Sync engine** | **Temporal** durable workflows (BullMQ fallback at P3 gate) | **BullMQ + Redis** | substantive fork | MED-HIGH — ops weight vs free durability |
| D4 | **Vendor SDK clients** | Lean full-control (build HTTP from scratch) | **Use vendor npm clients** (`stripe`, `@hubspot/api-client`) for types/request-building; write sync/transform yourself (saves 30–40%/connector) | substantive fork | HIGH — directly attacks B.4 cost |
| D5 | **Reverse-ETL timing** | Planned **P4** | **Demand-gated** — only if a customer asks | fork | MED |
| D6 | **Common Data Model** | Defined **up front** per category | **Deferred** to dbt until 2+ customers with different CRMs | fork | MED |
| D7 | **Multi-instance mgmt** | First-class **fleet dashboard + registry control plane** (P2/P5) | **Shell scripts** (`deploy-customer.sh`/`upgrade-customer.sh`), loop over customers | fork | MED — toil now vs platform later |
| D8 | **Web framework / monolith shape** | NestJS modular monolith (React layman UI) | Hono + HTMX admin (no React in v1) | minor | LOW |
| D9 | **Timeline framing** | Phase-gated, no week estimates | Concrete weeks (≈6–8 wk to first customer value) | minor | LOW (B's estimates are useful) |
| D10 | **Field-mapping UI** | In the plan (idea #10, with CDM) | Cut from v1 (vibecoder does it in dbt) | minor | LOW |

## A's silences B fills
- **Per-instance ops toil addressed early** (B's `deploy-customer.sh` in P2; A defers full fleet ops to
  P5). B is more honest about solo-consultant toil biting fast.
- **An explicit week-level timeline** and a **"what I'd cut/defer" list** (B), absent in A.
- **Honest connector-cost arithmetic** (B: 8 sources × 3 breaks/yr × 2hr ≈ 48 hr/yr ≈ 6 consulting
  days) — A asserts the registry bounds it but doesn't put the number on the table.

## B's silences A fills
- **Drift/DLQ/observability as a hardened phase** (A's P3); B folds these in lighter and later.
- **A registry with fleet view + canary + audit** as a first-class object (A); B's `connector_registry.json`
  is lighter and may under-serve the audit/rollback need at >2 instances.
- **Mandatory dry-run before outbound** and the durable-engine-gates-outbound ordering (A's P3-before-P4
  safety rule) — B's demand-gated P3 outbound is less explicit about the retry-safety coupling.

## Note on A's sequencing
A does **not** over-serialize badly — it explicitly parallelizes CDM/Cube authoring with SDK work and
connectors within P2. But B's core critique stands: A front-loads SDK + Cube + registry **before** a
real customer validates the shape, which is exactly the pre-commitment B sequences against.
