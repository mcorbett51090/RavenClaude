# Salesforce — best-practice docs

Named, consumer-facing rules for building on the Salesforce platform with this plugin's agents. Each file is **one rule** — read, applied, and cited as a whole. They are the consumer-facing distillation of the plugin's [15 house opinions](../CLAUDE.md) and the [`knowledge/`](../knowledge/) bank that backs them.

For the full reference material (limits tables, decision trees, sources) see [`../knowledge/`](../knowledge/); for the agents that enforce these rules see [`../agents/`](../agents/).

---

## Index

| Doc | Status | Use when |
|---|---|---|
| [`bulkify-every-soql-and-dml.md`](./bulkify-every-soql-and-dml.md) | Absolute rule | Writing or reviewing any Apex (or Flow loop) that touches records — no SOQL/DML inside a loop, ever |
| [`flow-vs-apex-one-entry-point.md`](./flow-vs-apex-one-entry-point.md) | Pattern | Adding automation to an object — deciding declarative vs code and avoiding stacked, unordered entry points |
| [`agentforce-earns-its-non-determinism.md`](./agentforce-earns-its-non-determinism.md) | Absolute rule | Designing an Agentforce agent — deciding agent-vs-deterministic-automation and gating with the Trust Layer |
| [`enforce-sharing-and-crud-fls.md`](./enforce-sharing-and-crud-fls.md) | Absolute rule | Designing record access or writing user-context Apex — `with sharing` by default and CRUD/FLS enforced in code |
| [`package-and-deploy-in-dependency-order.md`](./package-and-deploy-in-dependency-order.md) | Pattern | Shipping metadata — 2GP packaging, dependency-ordered deploys, the 75% gate, never click-deploying to prod |

---

## How these relate

`bulkify-every-soql-and-dml` is the foundation — its limit budget is shared by Flow and by Agentforce invocable actions, so the other docs reference it. `flow-vs-apex-one-entry-point` and `agentforce-earns-its-non-determinism` are both *placement* rules: keep deterministic, fixed-path work on the cheapest reliable tool (a before-save Flow before Apex; a Flow/Apex before an agent). `enforce-sharing-and-crud-fls` and `package-and-deploy-in-dependency-order` are the *guardrails* around that work — who can see the data, and how it ships to production.
