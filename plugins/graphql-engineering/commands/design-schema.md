---
description: "Design a GraphQL schema for real client use-cases with deliberate nullability, Relay cursor pagination, a mutation/error model, and a non-breaking evolution plan (library/spec specifics verify-at-use)."
argument-hint: "[domain + clients + existing schema/service if any]"
---

You are running `/graphql-engineering:design-schema`. Use `graphql-schema-architect` + the `graphql-schema-design-and-evolution` skill.

> Engineering judgment, not a spec citation. Every library version, GraphQL-spec detail, and federation/directive claim is `[verify-at-use]`. Model the client's needs, not the database. No PII in examples.

## Steps
1. Capture the domain, the actual clients (web / mobile / partner / internal), and their real read/write use-cases — plus any existing schema or service to evolve from.
2. Traverse the **schema-first-vs-code-first** and **pagination** trees in `knowledge/graphql-decision-trees.md` before choosing an approach.
3. Design the type model with deliberate nullability (a non-null field that can fail nulls its parent), pick Relay cursor connections vs offset per list with a reason, and define the mutation input/payload/error model — flag each library/spec specific `[verify-at-use]`.
4. Write the evolution & deprecation plan: additive-first, `@deprecated` + usage-drain before removal, and treat any nullability move as breaking. Note whether this is a federation subgraph and which entities carry `@key`.
5. Emit using `templates/graphql-schema-design-doc.md` + the Structured Output block, handing resolver performance to `graphql-server-engineer` and authz + query-cost limits to `graphql-security-governance-engineer`.
