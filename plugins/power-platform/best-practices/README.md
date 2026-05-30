# Power Platform best-practice docs

Named, citable rules for Power Platform engagements — each file is one rule, grounded in this plugin's own [`knowledge/`](../knowledge/) bank and enforced by its [`agents/`](../agents/). Read and apply a doc as a whole.

For the cross-tool rule format and the marketplace-wide index, see [`docs/best-practices/_TEMPLATE.md`](../../../docs/best-practices/_TEMPLATE.md) and [`docs/best-practices/README.md`](../../../docs/best-practices/README.md). For the plugin's house opinions and anti-patterns these rules sit inside, see [`../CLAUDE.md`](../CLAUDE.md) §3-§4.

---

## Index

| Doc | Status | Use when |
|---|---|---|
| [`managed-vs-unmanaged-solution-discipline.md`](./managed-vs-unmanaged-solution-discipline.md) | Absolute rule | Exporting/importing any solution along a dev → test → prod path — managed downstream, unmanaged only in dev |
| [`create-cloud-flows-via-dataverse-web-api.md`](./create-cloud-flows-via-dataverse-web-api.md) | Primary diagnostic | An SPN hits HTTP 401 on `api.flow.microsoft.com`, or you're about to script bulk cloud-flow create/update/delete |
| [`dataverse-access-error-is-not-a-schema-error.md`](./dataverse-access-error-is-not-a-schema-error.md) | Primary diagnostic | A Dataverse Web API read returns 401/403/404 — before concluding a column or table is missing |

---

## See also

- [`../knowledge/`](../knowledge/) — the production-lessons bank these rules are extracted from
- [`../CLAUDE.md`](../CLAUDE.md) — the Power Platform team constitution (house opinions §3, anti-patterns §4, Capability Grounding Protocol §5)
- [`../../../docs/best-practices/README.md`](../../../docs/best-practices/README.md) — the marketplace-wide best-practice index and format
