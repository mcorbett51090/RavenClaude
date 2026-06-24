# G4b — Per-conflict tiebreaks (Team-Lead rulings, evidence-cited from critic + G1)

> Rulings made by the Team Lead on the gap-delta forks. The critic gave decisive, evidence-based
> direction on most, so these are reasoned rulings (not coin-flips). Genuine product-direction items
> are flagged DEFER-to-Matt rather than auto-resolved.

| # | Conflict | Ruling | Rationale |
|---|----------|--------|-----------|
| D1 | Connector SDK depth/timing | **B (thin base-class v1; defer manifest compiler)** | Critic CE-6/R7/R8: A's full compiler is iPaaS-sized substrate built on faith. Build 2 plain connectors, let one break, MEASURE fix time, then decide registry/manifest depth. |
| D2 | Semantic layer (Cube vs dbt) | **B (dbt Core + Evidence v1; Cube deferred)** | Critic R8 + G1 5a/5b: dbt solves 80% with zero new runtime service per instance; Cube's value (programmatic metric API, caching) arrives at 5+ customers. Keep the "no raw-table refs in dashboards" lint either way. |
| D3 | Sync engine (Temporal vs BullMQ) | **B (BullMQ + Redis v1)** | Critic R8: Temporal is one more service per single-tenant instance (ops weight, CE-5). BullMQ gives retry/backoff/DLQ now; revisit Temporal only if durability pain is measured. |
| D4 | Vendor SDK clients | **B (use vendor npm clients for types/transport; write sync/transform/cursor yourself)** | Critic explicitly endorses; saves 30–40%/connector; does NOT violate "connections live in the app" (you own the sync logic, the data, the vault). Directly attacks B.4 cost. |
| D5 | Reverse-ETL timing | **SYNTHESIS: B timing (demand-gated) + A safety coupling** | Build outbound only when a customer asks (B) — BUT inherit A's hard rule: durable/idempotent path + mandatory dry-run GATE every outbound write (critic R10). Demand-gating must not drop the retry-safety coupling. |
| D6 | Common Data Model | **SYNTHESIS: minimal-stable-target, not full CDM up front** | Don't build all categories up front (B). DO define a minimal stable schema for the FIRST category in P1 so dashboards target a stable shape, not raw vendor JSON. Expand per category as customers arrive. |
| D7 | Multi-instance mgmt | **SYNTHESIS: B shell scripts v1, A's content promoted at instance #2** | `deploy/upgrade-customer.sh` v1 (B). The moment a 2nd instance exists, promote A's pin-record + advisory + **cross-tenant isolation test** (critic R3/R9) and make the FULL ops surface — not just connectors — the fleet concern (critic R5: `upgrade-all`, patching, restore-tests). |
| D8 | Framework / layman dashboard surface | **SYNTHESIS: B's lean backend (Hono) + an interactive BI surface for the layman** | Lean app server (B). But static Evidence alone fails the non-technical viewer (critic CE-3/R4): Evidence = Claude-authored canonical reports; add Metabase/Lightdash on the same marts for layman self-serve filter/drill — pending the 1-hr spike. Its DB role is scoped per CE-1. |

## Additive corrections (not forks — both plans missed these; fold into synthesis)
- **C1 (CE-1/R2):** analytics/dashboard DB role gets ZERO grant on the vault schema; vault in a
  separate DB or instance. Add a negative test: dashboard role cannot read `credentials`.
- **C2 (CE-2/R3):** provisioning gate includes a **cross-tenant** negative test (instance B → AccessDenied
  on instance A's KMS key) + one reviewed IAM policy template.
- **C3 (CE-4/R6):** dashboard **template library is the source artifact** (config-driven, renders without
  an LLM in the loop); Claude generates config + net-new only. Add per-customer rebuild-cost to DoD.
- **C4 (CE-5/R5):** explicit ops ceiling + first-class fleet automation before scaling past ~3 instances.
- **C5 (CE-6/R7):** tie any registry/manifest-compiler investment to a MEASURED break-fix-time threshold
  (B's DoD #7), shared across both — A's content, B's evidence-gated timing.

## DEFER to Matt (genuine product-direction — not auto-resolved)
- **T1 (CE-7/R1 — the headline call):** adopt **"consultant registers one OAuth app per provider; layman
  only does end-user consent"**, with **Salesforce & QuickBooks explicitly consultant-onboarded (not
  fully self-serve)**. This changes the "layman wires the connections" promise. Recommended (it's the
  only way the one-click promise is true), but it reshapes the persona model, so **Matt confirms**.
  Carries a consequence: a per-provider `client_secret` is a GLOBAL secret, not per-customer-isolated —
  the threat model must hold it as such.
- **T2:** the premise check (build connectors from scratch vs vendor). **Already pinned by Matt** —
  ruling stands (from scratch, made sustainable). Recorded, not re-opened.
