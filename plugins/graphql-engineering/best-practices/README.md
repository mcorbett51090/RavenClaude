# graphql-engineering — best-practice docs

Named, citable rules for the `graphql-engineering` team's specialists. Each file is **one rule**. Engineering judgment, not a spec tutorial; GraphQL library/spec/version specifics are `[verify-at-use]`; no PII.

---

## Index

_5 rules across client-first schema design, N+1 elimination, additive evolution, query-cost bounding, and field-level authorization._

| Doc | Status | Use when |
|---|---|---|
| [`design-the-schema-for-clients-not-your-database.md`](./design-the-schema-for-clients-not-your-database.md) | Absolute rule | Modeling any type or field — shape the graph around client use-cases and the domain, not table structure. |
| [`kill-the-n-plus-one-with-batching.md`](./kill-the-n-plus-one-with-batching.md) | Absolute rule | Any resolver that fetches per-parent — batch with DataLoader and per-request caching before it fans out to N+1 calls. |
| [`make-schema-changes-additive-and-non-breaking.md`](./make-schema-changes-additive-and-non-breaking.md) | Absolute rule | Evolving a live schema — add and `@deprecate`, never remove or retype a field clients still use. |
| [`bound-query-cost-before-you-accept-it.md`](./bound-query-cost-before-you-accept-it.md) | Absolute rule | Any public or partner-facing endpoint — enforce depth, cost, and persisted-query limits before execution, not after. |
| [`authorize-at-the-field-not-just-the-endpoint.md`](./authorize-at-the-field-not-just-the-endpoint.md) | Absolute rule | Any authenticated graph — enforce authorization at the field/type resolver with the request's principal, not only at the endpoint. |

---

Each rule cites its provenance and carries a `Last reviewed` date. Volatile GraphQL library/spec/version specifics live (dated, verify-at-use) in [`../knowledge/graphql-reference-2026.md`](../knowledge/graphql-reference-2026.md).
