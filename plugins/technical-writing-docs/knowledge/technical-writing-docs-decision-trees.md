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

## Decision Tree: Where does this content belong?

Diataxis says which kind; this says which page already owns the fact. Default to linking, not restating.

```mermaid
graph TD
  A[A fact to document] --> B{Does a canonical home already exist?}
  B -- Yes --> C[Link to it; do NOT restate - duplication drifts]
  B -- No --> D{Is the reader looking it up e.g. params/codes?}
  D -- Yes --> E[Reference - one authoritative page, spec-driven if possible]
  D -- No --> F{Are they doing a task?}
  F -- Yes --> G[How-to guide - steps; link the reference + concept]
  F -- No --> H{Do they need to understand WHY?}
  H -- Yes --> I[Explanation - concepts/trade-offs; link the how-to]
  H -- No --> J[Learning from zero -> Tutorial]
```

_The same fact in two places is one place that will go wrong. One owner, everything else links._

## Decision Tree: Is this doc worth writing (and keeping)?

A confidently-wrong or never-read doc is a liability; write to a real reader need, prune the rest.

```mermaid
graph TD
  A[A doc someone wants written] --> B{Is there a real reader with a real task for it?}
  B -- No --> C[Don't write it - it'll rot unread]
  B -- Yes --> D{Does the truth live in code/spec we can generate from?}
  D -- Yes --> E[Generate it; don't hand-maintain a copy]
  D -- No --> F{Can we commit to keeping it current with the product?}
  F -- No --> G[Either don't write it or date it + mark volatile]
  F -- Yes --> H{Already covered elsewhere?}
  H -- Yes --> I[Improve/link the existing page, don't fork]
  H -- No --> J[Write it - pick the Diataxis kind, tie to the release]
```

_Maintaining less but accurate beats hoarding more that quietly rotted._

## Decision Tree: How do I keep examples from going stale?

Examples must run; choose the mechanism by how the example is produced and tested.

```mermaid
graph TD
  A[A code example in the docs] --> B{Can it be extracted FROM tested code?}
  B -- Yes --> C[Embed from the tested source - single source of truth]
  B -- No --> D{Can the snippet be executed in CI as written?}
  D -- Yes --> E[Doc-test it - run the snippet, assert output, gate the build]
  D -- No --> F{Is it generated from a spec e.g. OpenAPI?}
  F -- Yes --> G[Regenerate on spec change; no hand-editing]
  F -- No --> H[Last resort: hand-written + a periodic manual verify + a date]
  C --> I[Broken example fails the build like any regression]
  E --> I
```

_A copy-paste snippet that errors destroys trust faster than a missing one._

## Capability map (dated — verify at build)

| Capability | 2026 state `[verify-at-build]` | Notes |
|---|---|---|
| Diataxis framework | established | The 4-kind model |
| Docusaurus / Starlight | GA | React-based, versioning, MDX |
| Mintlify | GA | Hosted, polished, API docs |
| MkDocs Material | GA | Simple, Python, fast |
| OpenAPI -> reference (e.g. Redocly) | GA | Spec-driven, no drift |
| Link-check / doc-test in CI | mature | Gate broken links + examples |
