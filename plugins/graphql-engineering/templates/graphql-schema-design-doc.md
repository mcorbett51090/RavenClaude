# GraphQL Schema Design — <service / date>

> Output template for a GraphQL schema design: the type model, nullability, pagination, mutation/error strategy, and a non-breaking evolution plan. One per service/domain (revisit on a major schema change). Every library/spec/federation specific carries a source + date or `[verify-at-use]`; no PII in examples.

## Header
- **Service / domain:** _____
- **Clients (web / mobile / partner / internal):** _____
- **Prepared:** 2026-__-__  · **Owner:** _____
- **Federation:** _is this a subgraph? which entities carry `@key`, and on what field(s)?_ _[verify-at-use]_

## 1. Domain & client use-cases
_What the clients actually need to read and write — the queries/mutations that justify the schema, not a mirror of the database._
| Client | Needs (query / mutation) | Shape driven by | Notes |
|---|---|---|---|
| | | screen / workflow | |
| | | | |

## 2. Type model
| Type | Key fields | Nullability rationale |
|---|---|---|
| | | _why nullable vs non-null — a non-null field that can fail propagates null to its parent_ |
| | | |

## 3. Pagination & connections
_Which lists are Relay cursor connections vs offset/limit vs unpaginated, and why._
| List field | Scheme (Relay connection / offset / none) | Why | Flag |
|---|---|---|---|
| | | unbounded? stable ordering? deep pages? | _[verify-at-use]_ |
| | | | |

## 4. Mutations
| Mutation | Input type | Payload type | Error model |
|---|---|---|---|
| | `___Input` | `___Payload` | _errors-as-data union / userErrors[] / top-level_ |
| | | | |

## 5. Error strategy
| Failure class | Surfaced as | Rationale |
|---|---|---|
| Unexpected / infra | top-level `errors[]` | _client can't act on it_ |
| Expected / domain (validation, not-found, forbidden) | errors-as-data (union / `userErrors`) | _typed, client-handleable, doesn't null the field_ |

## 6. Evolution & deprecation plan
_How fields get added and retired without breaking deployed clients._
- **Additive-first:** _new optional fields/args; never re-type or narrow-nullability in place_
- **Deprecation path:** _`@deprecated(reason:)` -> measure field usage -> remove only after clients drain_
- **Nullability moves:** _widening (non-null -> nullable) breaks clients that omitted null handling; narrowing (nullable -> non-null) breaks servers — treat both as breaking_
- **Versioning stance:** _continuous evolution vs versioned endpoint, and why_ _[verify-at-use]_

## Headline + risks
- **Headline decision:** _the schema shape + pagination/error bet, in one line_
- **Top risks:** _the reversal-expensive assumptions (nullability, connection choice, entity keys) + how they're verified_
- **Two things that would change the answer:** _____

---
_Plus the ravenclaude-core Structured Output block. All library/spec/federation cells: verify-at-use before commitment. Seams: graphql-server-engineer (resolver perf), graphql-security-governance-engineer (field-level authz + query-cost limits)._
