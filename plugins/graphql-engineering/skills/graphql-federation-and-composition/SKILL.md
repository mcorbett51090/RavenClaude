---
name: graphql-federation-and-composition
description: "Decide whether to federate, keep a monolithic graph, or stitch — and if federating, design clean subgraph ownership boundaries with entity @key, reference resolvers, and @external/@requires/@provides, then weigh the real operational cost of running a gateway/router. Federation spec and directive specifics verify-at-use."
---

# GraphQL Federation & Composition

Federation lets many teams each own a subgraph and compose them into one supergraph the client sees as a single API. It is an org-boundary tool first and a technical one second — reach for it when *team ownership* is the problem, not when a single service simply got large.

> **Engineering judgment.** GraphQL spec/library specifics change across versions — every version/library/spec-feature claim is `[verify-at-use]`. No PII.

## Workflow

1. **Test whether you actually need federation.** One team, one deployable, one datastore → a **monolithic graph** is simpler and faster; don't pay the gateway tax for it. Multiple teams needing independent deploy cadence and clear ownership of parts of the graph → **federation**. An existing set of separate GraphQL services you can't modify → **schema stitching** as the pragmatic (older, more manual) fallback.
2. **Draw ownership boundaries along the domain, not the data.** Each subgraph owns a coherent slice — `accounts`, `products`, `reviews` — and the types that belong to it. If two teams keep fighting over one type, the boundary is wrong. Ownership is the unit; the wire protocol serves it.
3. **Define entities with `@key`.** An entity is a type that more than one subgraph contributes fields to, identified by a `@key`. The owning subgraph defines the canonical type; other subgraphs extend it, keyed on the same field(s).
4. **Implement reference resolvers.** A subgraph that extends an entity must resolve it from just the `@key` fields the router passes it (`__resolveReference` / equivalent). Keep it a cheap, batchable lookup — the router will fan these out.
5. **Use `@external`/`@requires`/`@provides` sparingly and deliberately.** `@external` marks a field defined elsewhere that this subgraph references; `@requires` pulls a field from another subgraph to compute a local one (adds a router hop — cost); `@provides` lets a subgraph return a field it can supply inline to *save* a hop. Each is a performance/coupling lever, not decoration.
6. **Compose and validate the supergraph in CI.** Composition catches conflicts (a type owned by two subgraphs, a `@key` that doesn't resolve, an `@external` with no source) *before* deploy. A subgraph that composes locally but breaks the supergraph is a broken deploy — gate it. `[verify-at-use]` for the current composition tool/version.
7. **Budget the operational cost honestly.** A federated gateway/router is a new tier: extra network hops per entity resolution, a single point of failure, distributed tracing across subgraphs, and schema-composition as a release gate. That cost is worth it for org scaling and worthless for a single team.

## Decision table — federate vs monolith vs stitch

| Situation | Choose | Why |
|---|---|---|
| One team, one deployable | **Monolithic graph** | No gateway tax; simplest ops |
| Many teams, independent deploy cadence, clear domain slices | **Federation** | Ownership boundaries + independent deploys |
| Pre-existing GraphQL services you can't restructure | **Schema stitching** | Compose without re-architecting the subgraphs |
| One large service that's just messy internally | **Refactor the monolith** | Federation won't fix an internal-modularity problem |

## Federation directive cheat-sheet

| Directive | Means | Cost / caution |
|---|---|---|
| `@key(fields: "id")` | This type is an entity, resolvable by these fields | Fields must be stably resolvable |
| `@external` | Field is owned by another subgraph, referenced here | Only meaningful with `@requires`/`@provides` |
| `@requires(fields: "…")` | Compute a local field using fields from elsewhere | Adds a router round-trip — real latency |
| `@provides(fields: "…")` | This subgraph can return these inline | Saves a hop *only if* the data is truly local |
| `@shareable` / value types | A field/type resolvable by more than one subgraph | Values must agree or composition fails |

`[verify-at-use]` — directive names, syntax, and availability differ by federation version and library; confirm against the current spec before committing.

## Subgraph & entity example

Owning subgraph (`products`) defines the canonical entity:

```graphql
# products subgraph
type Product @key(fields: "id") {
  id: ID!
  name: String!
  price: Money!
}
```

Extending subgraph (`reviews`) contributes fields to the same entity, keyed identically:

```graphql
# reviews subgraph
type Product @key(fields: "id") {
  id: ID!
  reviews: [Review!]!          # this subgraph's contribution
  averageRating: Float
}

type Review {
  id: ID!
  body: String!
  rating: Int!
}
```

The `reviews` subgraph's reference resolver receives only `{ id }` from the router and hydrates its slice:

```js
const resolvers = {
  Product: {
    __resolveReference(ref) {
      // ref = { id } — resolve reviews for this product id only
      return reviewsByProductId.load(ref.id); // batched — see resolver-performance skill
    },
  },
};
```

Note the reference resolver is a prime N+1 site: the router calls it once per entity in the result set. Batch it with a per-request loader — that's `resolver-performance-and-n-plus-one`'s domain.

## Anti-patterns

- Federating a single-team service — buying the gateway tier and composition gate to solve a problem you don't have.
- Boundaries drawn along the database instead of the domain, so two teams co-own one type and every change is a negotiation.
- `@requires` chains that add hidden router hops nobody budgeted — federation latency death by a thousand cross-subgraph fetches.
- Reference resolvers that aren't batchable, turning each entity in a list into its own downstream call.
- Skipping supergraph composition in CI, so a locally-valid subgraph breaks the whole graph on deploy.
- Treating stitching and federation as interchangeable — stitching is the fallback for services you can't restructure, not the default.

## See also

- Traverse the **federate-vs-monolith-vs-stitch** and **subgraph-boundary** trees in [`../../knowledge/graphql-decision-trees.md`](../../knowledge/graphql-decision-trees.md).
- Dated federation-spec/router/directive specifics: [`../../knowledge/graphql-reference-2026.md`](../../knowledge/graphql-reference-2026.md).
- Sibling skills: [`../graphql-schema-design-and-evolution/SKILL.md`](../graphql-schema-design-and-evolution/SKILL.md), [`../resolver-performance-and-n-plus-one/SKILL.md`](../resolver-performance-and-n-plus-one/SKILL.md), [`../graphql-security-and-governance/SKILL.md`](../graphql-security-and-governance/SKILL.md).
- Sibling agents: `graphql-schema-architect` (owns subgraph boundaries), `graphql-server-engineer` (reference-resolver implementation + gateway ops), `graphql-security-governance-engineer` (auth across the supergraph).
