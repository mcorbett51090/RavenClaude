---
name: graphql-security-and-governance
description: "Defend a GraphQL endpoint whose single URL accepts arbitrary nested queries: depth limiting, cost/complexity budgets, field-level authorization (authorize at the field, not the endpoint), introspection hardening in prod, persisted/allow-listed operations, rate and batching limits, and error-message hygiene so internals never leak. Library/spec specifics verify-at-use."
---

# GraphQL Security & Governance

A GraphQL endpoint is one URL that accepts arbitrarily shaped, arbitrarily deep queries — the attack surface of REST's every-endpoint compressed into a single expressive interface. Governance is what stops a client from asking a question expensive or privileged enough to hurt you.

> **Engineering judgment.** GraphQL spec/library specifics change across versions — every version/library/spec-feature claim is `[verify-at-use]`. No PII.

## Workflow

1. **Limit query depth.** Cyclic types (`user → posts → author → posts …`) let a client nest arbitrarily deep and detonate the resolver tree. Enforce a maximum depth; reject over-deep queries before execution.
2. **Budget query cost / complexity.** Depth alone doesn't catch a wide shallow query pulling millions of rows. Assign each field a cost (constant, plus a multiplier for paginated lists by their `first`/`last`), sum it for the incoming query, and **reject over-budget queries before executing**. Different clients can get different budgets.
3. **Authorize at the field, not the endpoint.** A single endpoint means endpoint-level auth is far too coarse. Check authorization in (or via a directive/middleware on) each protected **field/type**, against the request's identity — `Query.adminReport`, `User.email`, `Order.internalNotes` each gate independently. A public field and a privileged field can sit on the same object.
4. **Harden introspection in production.** Introspection is a developer convenience and an attacker's map. Disable it (or restrict it to authenticated internal callers) in prod; ship the schema to your own tooling out of band. `[verify-at-use]` — disabling introspection is defense-in-depth, not a substitute for field auth.
5. **Move to persisted / allow-listed operations.** In production, accept only a **known set** of operations (client ships a hash/id; the server holds the registered query text). This caps the query space to what your own clients actually send — the strongest single control against hostile arbitrary queries and a bonus on request size.
6. **Rate-limit and cap batching.** Rate-limit by identity, ideally weighted by query *cost* not request count. Bound array-batched requests (many operations in one HTTP call) and aliased-field duplication so one request can't multiply work past the cost budget.
7. **Keep error messages clean.** Never return stack traces, SQL text, internal hostnames, or downstream error bodies to clients. Return a stable error `code` + safe message; log the detail server-side keyed by a correlation id. Errors-as-data business failures (from the schema skill) are fine to surface; *internals* are not.

## Metrics / decision table

| Control | Enforce | Bypasses if you skip it | Flag |
|---|---|---|---|
| Depth limit | Max nesting depth, pre-execution | Cyclic-type depth bomb | spec-stable |
| Cost/complexity budget | Per-query cost cap, pre-execution | Wide shallow row-explosion | `[verify-at-use]` per library |
| Field-level authz | Per field/type against identity | Privileged field on a public endpoint | design-critical |
| Introspection | Off / gated in prod | Full schema map handed to attacker | `[verify-at-use]` |
| Persisted operations | Allow-list registered queries only | Arbitrary hostile queries | `[verify-at-use]` |
| Rate limiting | By identity, cost-weighted | Volumetric / expensive-query abuse | design choice |
| Batching cap | Bound batched + aliased ops | Cost budget multiplied per request | `[verify-at-use]` |
| Error hygiene | Code + safe message; log detail server-side | Stack trace / SQL / host leak | always |

## Cost analysis — sketch

Assign field costs and multiply list fields by their requested page size, then reject over-budget before executing:

```graphql
type Query {
  # cost = 1 + first * (cost of Post)
  posts(first: Int!): [Post!]!   @cost(weight: 1, multipliers: ["first"])
}
type Post {
  id: ID!                        @cost(weight: 0)
  comments(first: Int!): [Comment!]!  @cost(weight: 2, multipliers: ["first"])
}
```

A query for `posts(first: 100){ comments(first: 100){ … } }` scores ~100 × 100 × 2 — reject it against a per-client budget *before* a single resolver runs. Directive names/syntax are `[verify-at-use]`; the principle (static cost estimate, pre-execution gate) is stable.

## Field-level authorization — sketch

Authorize where the sensitive data lives, not at the door:

```js
const resolvers = {
  User: {
    email: (user, _args, ctx) => {
      // same object, per-field gate: self or admin only
      if (ctx.viewer.id !== user.id && !ctx.viewer.isAdmin) {
        throw new ForbiddenError('Not authorized'); // safe message, no internals
      }
      return user.email;
    },
    name: (user) => user.name, // public field, same type — no gate
  },
};
```

`name` and `email` share a type yet gate differently — that's exactly why endpoint-level auth can't express GraphQL's real authorization surface.

## Anti-patterns

- Authorizing only at the endpoint/gateway, so any authenticated caller can reach a privileged field simply by selecting it.
- Leaving introspection on in prod and treating "it's off" as *the* control instead of one layer over field auth.
- Depth limiting but not cost limiting — a shallow query pulling a paginated list of paginated lists sails under the depth cap.
- Accepting arbitrary queries in production when the client set is finite and could be an allow-list.
- Rate limiting by request count while one request can cost 1000× another — count is the wrong unit; cost is the right one.
- Returning downstream/DB error text (stack traces, SQL, hostnames) straight to the client.
- No cap on array-batched or aliased operations, letting one HTTP request fan out past every per-query budget.

## See also

- Traverse the **abuse-surface triage** and **authorization-placement** trees in [`../../knowledge/graphql-decision-trees.md`](../../knowledge/graphql-decision-trees.md).
- Dated depth/cost/persisted-query/introspection library specifics: [`../../knowledge/graphql-reference-2026.md`](../../knowledge/graphql-reference-2026.md).
- Sibling skills: [`../graphql-schema-design-and-evolution/SKILL.md`](../graphql-schema-design-and-evolution/SKILL.md) (errors-as-data vs internal leakage), [`../resolver-performance-and-n-plus-one/SKILL.md`](../resolver-performance-and-n-plus-one/SKILL.md) (cost budgets pair with batching), [`../graphql-federation-and-composition/SKILL.md`](../graphql-federation-and-composition/SKILL.md) (auth across the supergraph).
- Sibling agents: `graphql-security-governance-engineer` (owns this skill), `graphql-schema-architect` (auth-aware schema shape), `graphql-server-engineer` (enforcing limits in the server).
- Escalate security/privacy verdicts to `ravenclaude-core/security-reviewer`.
