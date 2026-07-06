# GraphQL Engineering — Decision Trees

> Reference decision trees for the `graphql-engineering` team. Agents **traverse the relevant tree top-to-bottom before deciding** (the proactive complement to the Capability Grounding Protocol). Each `## Decision Tree` section is a Mermaid graph plus the rule it encodes.
>
> **Engineering judgment, not a spec ruling.** Anything touching a GraphQL library, the spec, or a version — feature support, transport, directive availability — is `[verify-at-use]`: confirm against the library/spec docs before it drives a build commitment. No PII.
>
> _Last reviewed: 2026-07-05 by `claude`. Principles are durable; dated specifics live in [graphql-reference-2026.md](graphql-reference-2026.md)._

---

## Decision Tree: schema-first vs code-first

```mermaid
flowchart TD
    A[New GraphQL API] --> B{Who owns the contract<br/>+ type-safety need?}
    B -- "contract is the artifact,<br/>front/back negotiate SDL,<br/>polyglot consumers" --> C[Schema-first<br/>SDL is source of truth<br/>+ codegen types/resolvers]
    B -- "one team owns both,<br/>types flow from code,<br/>refactor-driven" --> D[Code-first<br/>resolvers/types generate schema]
    C --> E{Codegen wired into CI<br/>so SDL + resolvers<br/>can't drift?}
    E -- no --> F[Add codegen + drift check<br/>before shipping]
    E -- yes --> G[Commit; SDL review<br/>gates schema changes]
    D --> H{Schema exported + snapshotted<br/>so breaking changes<br/>are visible in review?}
    H -- no --> I[Emit SDL artifact<br/>+ schema-diff check]
    H -- yes --> J[Commit; type system<br/>anchors the contract]
```

**Rule:** decide on **who owns the contract and the team's type-safety path**, not framework fashion. Schema-first when the SDL is the negotiated artifact across teams/languages; code-first when one team owns both sides and types should flow from code. Either way, make the schema a reviewed, drift-checked artifact — library/codegen specifics `[verify-at-use]`.

---

## Decision Tree: monolithic graph vs federation vs schema stitching

```mermaid
flowchart TD
    A[Need a graph] --> B{How many teams/services<br/>own slices of it?}
    B -- "one team,<br/>one service" --> C[Monolithic graph<br/>single schema, no gateway]
    B -- "multiple teams/services,<br/>independent deploys" --> D{Appetite to run<br/>a gateway + registry?}
    D -- yes --> E[Federation<br/>subgraphs + composed supergraph]
    D -- "no — can't operate<br/>a gateway yet" --> F[Start monolithic;<br/>modularize toward federation]
    B -- "must unify existing schemas<br/>you don't control/can't refactor" --> G[Schema stitching<br/>legacy/interim bridge]
    G --> H{Can migrate to<br/>owned subgraphs later?}
    H -- yes --> I[Stitch now,<br/>plan federation migration]
    H -- no --> J[Keep stitched;<br/>accept gateway coupling]
```

**Rule:** let **org and ownership boundaries** pick the topology, not schema size alone. One team → monolithic graph. Multiple teams owning slices, with the operational appetite for a gateway + schema registry → federation. Reach for stitching only as a legacy/interim bridge over schemas you can't refactor, with a migration plan. Composition/gateway specifics `[verify-at-use]`.

---

## Decision Tree: pagination style — offset vs Relay cursor connections

```mermaid
flowchart TD
    A[List field returns many rows] --> B{Set size + growth?}
    B -- "small, bounded,<br/>admin/stable list" --> C[Offset/limit<br/>simple page + total count]
    B -- "large / unbounded /<br/>infinite scroll" --> D{Rows mutate under<br/>the reader?}
    D -- "yes — inserts/deletes<br/>shift pages" --> E[Relay cursor connections<br/>stable under mutation]
    D -- "no — snapshot-stable" --> F{Realtime or<br/>client-cache normalization?}
    F -- yes --> E
    F -- no --> C
    E --> G[edges/node + pageInfo,<br/>opaque cursors]
    C --> H[Guard skip cost;<br/>cap page size]
```

**Rule:** default to **Relay cursor connections** for large, realtime, infinite-scroll, or mutation-heavy lists — cursors stay stable when rows shift and match client-cache conventions. Reserve **offset/limit** for small, stable admin lists where a page number and total are what's actually wanted. Watch deep-offset cost either way. Connection-spec details `[verify-at-use]`.

---

## Decision Tree: error model — top-level errors vs errors-as-data

```mermaid
flowchart TD
    A[An operation can fail] --> B{Is the failure expected<br/>domain behavior?}
    B -- "no — bug, outage,<br/>auth/system fault" --> C[Top-level errors array<br/>unexpected/system failures]
    B -- "yes — validation,<br/>not-found, conflict,<br/>business rule" --> D{Should the client<br/>handle it typed?}
    D -- yes --> E[Errors-as-data<br/>union/result payload types]
    D -- "no — treat as fatal" --> C
    E --> F[Mutation returns<br/>Success | DomainError union;<br/>client matches on __typename]
    C --> G[Map to error extensions/code;<br/>don't leak internals]
```

**Rule:** split by **expectedness**. Unexpected/system failures (bugs, outages, auth) belong in the **top-level `errors`** array with safe codes and no leaked internals. Model **expected domain failures as data** — union/result payload types the client discriminates on `__typename` — so predictable outcomes are part of the typed schema, not exception handling. Framework/union-type ergonomics `[verify-at-use]`.

---

## See also

- [graphql-reference-2026.md](graphql-reference-2026.md) — dated server-library, federation, spec-feature, security, and observability landscape (verify-at-use).
