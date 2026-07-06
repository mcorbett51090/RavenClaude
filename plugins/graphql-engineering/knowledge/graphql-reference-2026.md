# GraphQL Engineering — 2026 Reference

> Dated reference for the `graphql-engineering` team: the server-library, federation, spec-feature, security, and observability landscape agents reach for. The durable reasoning lives in [graphql-decision-trees.md](graphql-decision-trees.md); this file is the freshness-anchored "what the landscape and tooling are."
>
> **Engineering judgment, not a spec ruling.** The GraphQL library and tooling landscape moves fast. Every library version, spec-feature-support claim, and tooling name below is **volatile** and carries a **source placeholder + retrieval date + `[verify-at-use]`** — re-confirm against the library/spec docs before it drives a build commitment. Estimates are marked `[ESTIMATE]`. No PII.
>
> _Last reviewed: 2026-07-05 by `claude`. Treat every specific as `[verify-at-use]` unless re-confirmed this session._

---

## 1. Server libraries / frameworks

| Library | Ecosystem | Fit | Source / retrieved | Flag |
|---|---|---|---|---|
| Apollo Server | Node/TS | Widely-used, plugin ecosystem, federation-native | _<apollographql.com docs>_ — retrieved 2026-07-05 | `[verify-at-use]` |
| GraphQL Yoga | Node/TS | Lightweight, envelop plugins, spec-forward | _<the-guild.dev docs>_ — retrieved 2026-07-05 | `[verify-at-use]` |
| Mercurius | Node (Fastify) | Fastify-integrated, high-throughput | _<mercurius.dev docs>_ — retrieved 2026-07-05 | `[verify-at-use]` |
| async-graphql | Rust | Code-first, async, strong type system | _<async-graphql docs>_ — retrieved 2026-07-05 | `[verify-at-use]` |
| Juniper | Rust | Code-first, mature | _<graphql-rust docs>_ — retrieved 2026-07-05 | `[verify-at-use]` |
| gqlgen | Go | Schema-first, codegen to typed resolvers | _<gqlgen.com docs>_ — retrieved 2026-07-05 | `[verify-at-use]` |
| gophers/graphql-go | Go | Schema-first, minimal | _<graph-gophers docs>_ — retrieved 2026-07-05 | `[verify-at-use]` |
| Strawberry | Python | Code-first, type-hint/dataclass-driven | _<strawberry.rocks docs>_ — retrieved 2026-07-05 | `[verify-at-use]` |
| Graphene | Python | Code-first, established | _<graphene-python docs>_ — retrieved 2026-07-05 | `[verify-at-use]` |
| graphql-java | JVM | Reference JVM engine, low-level | _<graphql-java docs>_ — retrieved 2026-07-05 | `[verify-at-use]` |
| Netflix DGS | JVM (Spring) | Annotation-driven on graphql-java | _<netflix.github.io/dgs>_ — retrieved 2026-07-05 | `[verify-at-use]` |
| Spring for GraphQL | JVM (Spring) | Spring-native controllers on graphql-java | _<spring.io docs>_ — retrieved 2026-07-05 | `[verify-at-use]` |
| Hot Chocolate | .NET | Code-first/schema-first, federation support | _<chillicream.com docs>_ — retrieved 2026-07-05 | `[verify-at-use]` |

_Library names and versions change; confirm the current release and its schema-first/code-first support before committing._

---

## 2. Federation / gateway

| Tool | What it is | Note | Source / retrieved | Flag |
|---|---|---|---|---|
| Apollo Federation | Subgraph spec + supergraph composition | Subgraphs compose into a supergraph served by a gateway/router | _<apollographql.com federation docs>_ — retrieved 2026-07-05 | `[verify-at-use]` |
| GraphQL Mesh | Gateway over hetero sources (REST/gRPC/etc.) | Wraps non-GraphQL sources into a unified graph | _<the-guild.dev/mesh docs>_ — retrieved 2026-07-05 | `[verify-at-use]` |
| Cosmo | Open federation router + platform | Federation-compatible router, registry, analytics | _<wundergraph.com/cosmo docs>_ — retrieved 2026-07-05 | `[verify-at-use]` |
| Hive gateway / schema registry | Gateway + schema registry/CI | Composition checks, schema versioning | _<the-guild.dev/hive docs>_ — retrieved 2026-07-05 | `[verify-at-use]` |
| Schema stitching | Merge multiple schemas at a gateway | Legacy/interim bridge over schemas you don't own | _<the-guild.dev stitching docs>_ — retrieved 2026-07-05 | `[verify-at-use]` |

_Federation composition rules and router compatibility change release to release; verify the version and directive set your subgraphs emit before composing._

---

## 3. Spec features to check support for

| Feature | What it is | Note | Source / retrieved | Flag |
|---|---|---|---|---|
| @defer / @stream | Incremental delivery of slow/partial results | Support + wire protocol vary by server + client | _<graphql spec / library docs>_ — retrieved 2026-07-05 | `[verify-at-use]` |
| Subscriptions transport | Server-push over WebSocket/SSE | Prefer `graphql-ws`; legacy `subscriptions-transport-ws` deprecated; SSE for HTTP-only | _<graphql-ws / spec docs>_ — retrieved 2026-07-05 | `[verify-at-use]` |
| @oneOf input | Exactly-one-of input object member | Newer directive; confirm server + codegen support | _<graphql spec / library docs>_ — retrieved 2026-07-05 | `[verify-at-use]` |
| Custom scalars | Domain scalars (DateTime, JSON, etc.) | Serialization + validation are per-library | _<library scalar docs>_ — retrieved 2026-07-05 | `[verify-at-use]` |
| Automatic Persisted Queries | Hash-referenced queries to shrink payloads | Requires server + client APQ support | _<apollo APQ docs>_ — retrieved 2026-07-05 | `[verify-at-use]` |

_Spec-feature support is per-library and per-version; confirm the exact server and client both implement the feature before designing around it._

---

## 4. Security / governance tooling

| Tool / control | What it is | Note | Source / retrieved | Flag |
|---|---|---|---|---|
| graphql-depth-limit | Rejects queries past a depth ceiling | First line against deeply-nested abuse | _<graphql-depth-limit docs>_ — retrieved 2026-07-05 | `[verify-at-use]` |
| graphql-cost-analysis | Static complexity/cost scoring per query | Weight fields; reject over budget | _<cost-analysis docs>_ — retrieved 2026-07-05 | `[verify-at-use]` |
| graphql-armor | Bundled protections (depth, cost, aliases, etc.) | Envelop/Yoga/Apollo plugin | _<the-guild.dev/graphql-armor docs>_ — retrieved 2026-07-05 | `[verify-at-use]` |
| Persisted operations / trusted documents | Allow-list of known operation hashes | Blocks arbitrary queries in prod | _<apollo / guild trusted-docs docs>_ — retrieved 2026-07-05 | `[verify-at-use]` |
| Rate limiting | Per-client/operation throttling | Complements cost analysis, not a substitute | _<gateway / middleware docs>_ — retrieved 2026-07-05 | `[verify-at-use]` |

_Library names and their default limits change; confirm the control is wired into the request pipeline and tuned for your schema before relying on it._

---

## 5. Observability

| Tool / signal | What it is | Note | Source / retrieved | Flag |
|---|---|---|---|---|
| Apollo Studio / GraphOS | Managed schema registry + metrics | Field-usage, operation metrics, schema checks | _<apollographql.com/graphos docs>_ — retrieved 2026-07-05 | `[verify-at-use]` |
| OpenTelemetry GraphQL instrumentation | Vendor-neutral traces/metrics | Per-resolver spans; wire into your APM | _<opentelemetry.io docs>_ — retrieved 2026-07-05 | `[verify-at-use]` |
| Field-usage / tracing | Per-field resolve timing + usage | Drives deprecation + N+1/resolver hotspots | _<library tracing docs>_ — retrieved 2026-07-05 | `[verify-at-use]` |

_Observability product names and integration surfaces change; confirm the exporter/registry version and its schema-check semantics before wiring it into CI._

---

## 6. How to use this file

1. Find the library / federation tool / spec feature / control you need.
2. Read its retrieval date — if stale or unconfirmed this session, **re-verify** against the cited source type before quoting.
3. Quote it with its flag (`[ESTIMATE]` / `[verify-at-use]`) intact when it informs an architecture or build commitment.
4. For anything that gates a build decision: confirm against the library/spec docs first.

---

## See also

- [graphql-decision-trees.md](graphql-decision-trees.md) — the durable schema-first/federation/pagination/error-model trees.
