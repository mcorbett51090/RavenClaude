---
name: resolver-performance-and-n-plus-one
description: "Kill the N+1 problem GraphQL's per-field resolution invites: batch and per-request-cache with DataLoader, be selection-set aware so you fetch only requested fields, bound pagination cost, avoid over-fetching downstream, and layer response caching / APQ. Includes a worked N+1 example and its DataLoader fix. Library specifics verify-at-use."
---

# Resolver Performance & the N+1 Problem

GraphQL resolves field-by-field, so a naive `posts { author { name } }` fetches every author in its own query — the N+1 problem, GraphQL's signature performance failure. The discipline is to make the graph's shape stop mapping one-to-one onto downstream calls.

> **Engineering judgment.** GraphQL spec/library specifics change across versions — every version/library/spec-feature claim is `[verify-at-use]`. No PII.

## Workflow

1. **Find the N+1 sites.** Any resolver that runs once *per parent* in a list and does its own I/O is an N+1: `Post.author`, `Order.customer`, a federation `__resolveReference`. Log per-request downstream call counts; a query returning N items that fires N+k backend calls is the smell.
2. **Batch with DataLoader.** Wrap every by-key downstream fetch in a loader that collects the keys requested within a single tick and issues **one** batched call (`SELECT … WHERE id IN (…)` / one bulk API request). This is the primary fix and it is not optional at scale.
3. **Scope the loader per request, cache within it.** Create loaders fresh **per request** (never module-global — that leaks data across users and staleness across requests). Within the request, the loader's cache dedupes repeat keys for free.
4. **Be selection-set aware.** Inspect the requested fields (the resolve info) and project them down — fetch only the columns/fields the client asked for, join only the relations actually selected. Don't `SELECT *` and don't eager-load relations nobody requested.
5. **Bound pagination cost.** A connection resolver must cap `first`/`last`, refuse unbounded lists, and push `LIMIT`/paging into the downstream query rather than fetching all and slicing in memory. Pagination cost compounds with nesting — a paginated list of paginated lists multiplies.
6. **Avoid over-fetching downstream.** One coarse "get everything about this entity" call per field re-fetches the same payload repeatedly. Prefer narrow, batchable, cacheable calls the loader can dedupe.
7. **Layer caching outermost.** Resolver-level caching (memoize expensive computed fields), response caching (cache whole responses keyed on query + variables + auth scope, honoring per-field TTL/scope hints), and **Automatic Persisted Queries (APQ)** to cut request *size* (client sends a hash; server keeps the query text) — APQ reduces bytes on the wire, it is not itself a result cache. `[verify-at-use]` for the cache/APQ library specifics.

## The N+1 problem — worked example

Schema:

```graphql
type Query { posts(first: Int!): [Post!]! }
type Post { id: ID!  title: String!  author: User! }
type User { id: ID!  name: String! }
```

Naive resolver — **1 query for posts, then N queries for authors** (the N+1):

```js
const resolvers = {
  Query: {
    posts: (_, { first }) => db.query('SELECT * FROM posts LIMIT ?', [first]),
  },
  Post: {
    // fires ONCE PER POST — 20 posts ⇒ 20 author queries
    author: (post) => db.query('SELECT * FROM users WHERE id = ?', [post.author_id]),
  },
};
```

For 20 posts that's **21 queries**. At three levels of nesting it explodes.

## The DataLoader fix

Create the loader **per request** and batch the by-id lookups into one query:

```js
import DataLoader from 'dataloader';

// per-request context factory — NOT module-global
function createContext() {
  return {
    userLoader: new DataLoader(async (ids) => {
      const rows = await db.query(
        'SELECT * FROM users WHERE id IN (?)', [ids]     // ONE query for all ids
      );
      const byId = new Map(rows.map((r) => [r.id, r]));
      return ids.map((id) => byId.get(id) ?? null);       // MUST return in key order, 1:1
    }),
  };
}

const resolvers = {
  Query: {
    posts: (_, { first }) => db.query('SELECT * FROM posts LIMIT ?', [first]),
  },
  Post: {
    author: (post, _args, ctx) => ctx.userLoader.load(post.author_id),
  },
};
```

Now 20 posts ⇒ **2 queries** (posts, then one batched user query), and repeat author ids are deduped by the loader's per-request cache. Two contracts the batch function must honor: it returns results **in the same order as the keys**, and **exactly one entry per key** (null for misses) — violating either silently corrupts results.

## Metrics / decision table

| Metric | Target / read | Flag |
|---|---|---|
| Downstream calls per query | O(depth), not O(result-set size) | measure per request |
| DataLoader scope | Per-request, never module-global | correctness-critical |
| Selection-set projection | Fetch only requested fields/relations | `[verify-at-use]` per library |
| Pagination bound | `first`/`last` capped; `LIMIT` pushed downstream | design-stable |
| Response cache key | query + variables + auth scope | staleness/leak risk |
| APQ | Cuts request bytes (hash for text) — not a result cache | `[verify-at-use]` |

## Anti-patterns

- Solving N+1 by "just caching" instead of batching — a cache hides the count, it doesn't remove the round-trips on a cold path.
- A **module-global** DataLoader: cross-user data leaks and cross-request staleness. Loaders are per-request, always.
- `SELECT *` / fetch-everything resolvers ignoring the selection set, then discarding most of it.
- Unbounded list resolvers with no `first`/`last` cap — one query can pull the whole table.
- Fetch-all-then-slice pagination in application memory instead of pushing `LIMIT`/`OFFSET`/cursor into the datastore.
- Confusing APQ (request-size reduction) with response caching (result reuse) — they solve different problems.
- A batch function that returns results out of key order or not 1:1 with keys — silent data corruption.

## See also

- Traverse the **N+1 triage** and **caching-layer** trees in [`../../knowledge/graphql-decision-trees.md`](../../knowledge/graphql-decision-trees.md).
- Dated DataLoader/APQ/response-cache library specifics: [`../../knowledge/graphql-reference-2026.md`](../../knowledge/graphql-reference-2026.md).
- Sibling skills: [`../graphql-schema-design-and-evolution/SKILL.md`](../graphql-schema-design-and-evolution/SKILL.md) (pagination shape), [`../graphql-federation-and-composition/SKILL.md`](../graphql-federation-and-composition/SKILL.md) (reference resolvers are N+1 sites), [`../graphql-security-and-governance/SKILL.md`](../graphql-security-and-governance/SKILL.md) (cost limits complement query budgets).
- Sibling agents: `graphql-server-engineer` (owns this skill), `graphql-schema-architect` (pagination/shape upstream), `graphql-security-governance-engineer` (cost budgets as an abuse control).
