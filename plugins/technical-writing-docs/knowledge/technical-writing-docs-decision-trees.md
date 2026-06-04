# Technical Writing & Docs — Decision Trees

_Decision trees + a dated capability map. Capability rows are `[verify-at-build]` — re-check against the vendor before quoting. Last reviewed: 2026-06-04._

Traverse before writing a doc or picking a docs tool.

## Decision Tree: Which kind of doc is this (Diataxis)?

Identify the reader's need; don't blend the four kinds.

```mermaid
graph TD
  A[Something to document] --> B{Is the reader learning the product for the first time?}
  B -- Yes --> C[Tutorial - hand-held, guaranteed-to-work path]
  B -- No --> D{Do they have a specific task/goal right now?}
  D -- Yes --> E[How-to guide - steps to accomplish the task]
  D -- No --> F{Do they need to look up facts e.g. params, endpoints?}
  F -- Yes --> G[Reference - complete, accurate, spec-driven]
  F -- No, they want to understand WHY --> H[Explanation - concepts, trade-offs, background]
```

_A 'tutorial' full of reference tables, or a reference that lectures on concepts, helps no one._

## Decision Tree: Docs tooling choice

Pick by maintenance, versioning, and design-control needs — not by popularity.

```mermaid
graph TD
  A[Need a docs site] --> B{Want hosted + polished out of the box?}
  B -- Yes --> C[Mintlify / hosted platform]
  B -- No, self-host --> D{Heavy customization / React components in docs?}
  D -- Yes --> E[Docusaurus / Starlight]
  D -- No, simple markdown site --> F{Python ecosystem?}
  F -- Yes --> G[MkDocs Material]
  F -- No --> E
  E --> H[Need docs versioning + i18n? confirm support]
  G --> H
```


## Capability map (dated — verify at build)

| Capability | 2026 state `[verify-at-build]` | Notes |
|---|---|---|
| Diataxis framework | established | The 4-kind model |
| Docusaurus / Starlight | GA | React-based, versioning, MDX |
| Mintlify | GA | Hosted, polished, API docs |
| MkDocs Material | GA | Simple, Python, fast |
| OpenAPI -> reference (e.g. Redocly) | GA | Spec-driven, no drift |
| Link-check / doc-test in CI | mature | Gate broken links + examples |
