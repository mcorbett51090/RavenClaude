# GraphQL Schema & Perf Review — <service / date>

> Audit output template for an existing GraphQL schema + server: breaking-change scan, N+1 / resolver fan-out, query-cost exposure, field-level authz, and pagination correctness. One per review pass. Every library/spec/version specific carries a source + date or `[verify-at-use]`; no PII in examples.

## Header
- **Schema / service under review:** _____
- **Deployed schema baseline (SDL / introspection source):** _____
- **Prepared:** 2026-__-__  · **Owner:** _____

## 1. Breaking-change scan
_New schema vs the deployed schema: removed, re-typed, or nullability-narrowed fields that break live clients._
| Field / type | Change | Breaking? | Deployed-client impact |
|---|---|---|---|
| | removed / re-typed / non-null-narrowed / arg-required | yes / no | |
| | | | |

## 2. N+1 / resolver fan-out findings
| Resolver | Downstream calls per parent | Batched? (DataLoader / join) | Fix |
|---|---|---|---|
| | | yes / no | |
| | | | |

## 3. Query-cost exposure
| Control | Present? | Notes | Flag |
|---|---|---|---|
| Depth limit | | max depth | _[verify-at-use]_ |
| Cost / complexity budget | | per-field weights? | _[verify-at-use]_ |
| Persisted / allow-listed queries | | arbitrary queries accepted? | |
| Introspection in prod | | disabled? | |

## 4. Authorization
| Surface | Field-level authz present? | Gap |
|---|---|---|
| Sensitive fields / types | | _authz at the resolver, not just the route_ |
| Mutations | | |
| Entity references (federation) | | |

## 5. Pagination correctness
| List field | Bounded? | Scheme | Issue |
|---|---|---|---|
| | max page size enforced? | Relay / offset / none | _unbounded list -> cost + N+1 blast radius_ |
| | | | |

## Prioritized findings
| Pri | Finding | Impact | Remediation |
|---|---|---|---|
| P0 | _breaks clients / unauthenticated data exposure / DoS surface_ | | |
| P1 | _N+1 under load / missing cost limits_ | | |
| P2 | _hardening / correctness nits_ | | |

- **Recommended remediation order:** _P0 breaking/authz -> P1 fan-out + cost -> P2 hardening; ship guards before schema fixes so the surface is closed while the shape is corrected_
- **Two things that would change the priority:** _____

---
_Plus the ravenclaude-core Structured Output block. All library/spec/version cells: verify-at-use before commitment. Seams: graphql-server-engineer (resolver/N+1 fixes), graphql-security-governance-engineer (authz + cost limits + persisted queries)._
