---
name: graphql-schema-design-and-evolution
description: "Design a GraphQL schema for the clients that consume it — not the database underneath: nullability discipline, Relay cursor-connection pagination, input/payload mutation shape, errors-as-data vs top-level errors — and evolve it without breaking clients via additive change, @deprecated, and staged field rollout. Spec/library specifics verify-at-use."
---

# GraphQL Schema Design & Evolution

The schema is the contract. It outlives any resolver, any datastore, and most of the clients that will ever call it — so model it for the consumer, keep it strict where strictness is cheap, and only ever grow it in ways that don't break the app already in production.

> **Engineering judgment.** GraphQL spec/library specifics change across versions — every version/library/spec-feature claim is `[verify-at-use]`. No PII.

## Workflow

1. **Model the client's view, not the table.** Start from the queries the UI needs and design types that answer them. A `User.fullAddress` field can compose three columns; a `Cart.total` can be computed. Don't leak `user_id` foreign keys or join tables into the graph — expose the relationship (`order.customer`) instead.
2. **Decide schema-first vs code-first, then commit.** Schema-first (author SDL, generate types) keeps the contract reviewable as a single artifact and is easy for cross-team review; code-first (types emitted from resolver code — e.g. Nexus/Pothos/`graphql-ruby`) keeps schema and implementation from drifting. Pick one per service and don't half-do both. `[verify-at-use]` for the library's current codegen story.
3. **Apply nullability discipline.** Non-null (`!`) is a promise you can never weaken without a breaking change — a nullable field can *become* non-null safely, but never the reverse. Make a field non-null only when it is genuinely always present. Prefer nullable for anything that can fail independently, so one downstream error doesn't null the whole parent object (a non-null field that errors propagates the null *up* to the nearest nullable ancestor).
4. **Choose pagination shape deliberately.** Use Relay-style cursor connections for anything unbounded or infinite-scroll; reserve offset/limit for small, stable, page-numbered lists. Cursors survive insertions/deletions mid-scroll; offsets don't.
5. **Shape mutations with input + payload types.** One `input` type per mutation, one `payload` type back. Name mutations `verbNoun` (`createOrder`, `archiveProject`). Return the mutated entity *and* room for future fields in the payload.
6. **Decide errors-as-data vs top-level errors per failure class.** Unexpected/system failures → top-level `errors[]`. Expected, recoverable, business-rule failures the client must render (validation, "email taken", "insufficient funds") → model them into the schema as a result union or an errors field on the payload.
7. **Evolve additively, deprecate before you remove.** New optional fields/args and new types are safe. Everything else is a breaking change — mark the old field `@deprecated(reason:)`, ship the replacement alongside, watch field-usage telemetry drop to zero, *then* remove.

## Metrics / decision table

| Decision | Choose this | Over this | Flag |
|---|---|---|---|
| API surface strategy | Schema-first when the contract is reviewed cross-team | Code-first when drift is the bigger risk | `[verify-at-use]` per library |
| Field nullability | Nullable by default; `!` only when always-present | Non-null everywhere (brittle) | spec-stable |
| List pagination | Cursor connection for unbounded/infinite feeds | Offset/limit for small page-numbered lists | Relay spec `[verify-at-use]` |
| Expected business failure | Errors-as-data (result union / payload errors) | Top-level `errors[]` | design choice |
| Unexpected/system failure | Top-level `errors[]` | Swallowing into data | spec-stable |
| Removing a field | `@deprecated` → watch usage → remove | Delete outright | breaking |

## Nullability, non-breaking direction

Only these transitions are non-breaking; everything else breaks a client:

| Change | Safe? |
|---|---|
| Add a nullable field | ✅ |
| Add an optional (nullable / defaulted) argument | ✅ |
| Make an output field nullable → non-null | ✅ (clients already handle the value) |
| Make an output field non-null → nullable | ❌ breaking |
| Make an input field / arg nullable → non-null | ❌ breaking |
| Add a value to an enum | ⚠️ can break exhaustive client switches — treat as risky |
| Remove or rename a field, type, or enum value | ❌ breaking |

## Pagination — cursor connection shape

Model unbounded lists as a Relay connection so cursors are opaque and insertion-stable:

```graphql
type Query {
  products(first: Int, after: String, last: Int, before: String): ProductConnection!
}

type ProductConnection {
  edges: [ProductEdge!]!
  pageInfo: PageInfo!
  totalCount: Int
}

type ProductEdge {
  cursor: String!
  node: Product!
}

type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}
```

The cursor is opaque to the client (often a base64 of a stable sort key + id) — never a raw offset, so a row inserted mid-scroll doesn't shift the window. Pagination cost and downstream fetch limits are `resolver-performance-and-n-plus-one`'s concern; hand it the connection shape as the constraint.

## Mutation shape — input + payload + errors-as-data

```graphql
type Mutation {
  createOrder(input: CreateOrderInput!): CreateOrderPayload!
}

input CreateOrderInput {
  clientMutationId: String
  customerId: ID!
  lineItems: [LineItemInput!]!
}

type CreateOrderPayload {
  order: Order
  userErrors: [UserError!]!   # expected, renderable failures — errors-as-data
}

type UserError {
  field: [String!]
  message: String!
  code: OrderErrorCode!
}
```

`userErrors` carries the validation/business failures the UI must render field-by-field; the top-level `errors[]` array stays reserved for genuinely unexpected faults. A single input type (never scalar arg lists) keeps the mutation evolvable — new optional input fields are additive.

## Anti-patterns

- Mirroring database tables into the graph (foreign keys, join tables, snake_case columns) instead of modeling the client's domain.
- Marking everything non-null because it "feels safer" — one downstream failure then nulls the whole response up to the nearest nullable ancestor.
- Offset pagination on an infinite feed: duplicated/skipped rows the moment anything is inserted.
- Scalar argument lists on mutations instead of an `input` type — every new field is then a breaking signature change.
- Removing or renaming a field without a `@deprecated` window and usage telemetry.
- Overloading top-level `errors[]` for expected validation failures the client is supposed to render.

## See also

- Traverse the **schema-design** and **schema-evolution / breaking-change** trees in [`../../knowledge/graphql-decision-trees.md`](../../knowledge/graphql-decision-trees.md).
- Dated spec/library specifics (Relay spec, `@deprecated`, library codegen): [`../../knowledge/graphql-reference-2026.md`](../../knowledge/graphql-reference-2026.md).
- Sibling skills: [`../graphql-federation-and-composition/SKILL.md`](../graphql-federation-and-composition/SKILL.md), [`../resolver-performance-and-n-plus-one/SKILL.md`](../resolver-performance-and-n-plus-one/SKILL.md), [`../graphql-security-and-governance/SKILL.md`](../graphql-security-and-governance/SKILL.md).
- Sibling agents: `graphql-schema-architect` (owns this skill), `graphql-server-engineer` (resolver implementation), `graphql-security-governance-engineer` (auth/governance on the shape).
