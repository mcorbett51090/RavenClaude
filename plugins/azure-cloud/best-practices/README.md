# azure-cloud — best-practice docs

Named, citable rules for standing up and running Azure under the Microsoft stack. Each file is **one rule**, grounded in this plugin's CAF/WAF-sourced knowledge bank ([`../knowledge/`](../knowledge/)) and enforced (where grep-able) by the `check-azure-anti-patterns.sh` hook. Read a doc whole and cite it; don't paraphrase a fragment.

These docs codify the cross-cutting **house opinions** in [`../CLAUDE.md`](../CLAUDE.md) §3 into copy-paste-grade guidance. For the underlying reference material and decision trees, go to the knowledge bank.

---

## Index

| Doc | Status | Use when |
|---|---|---|
| [`passwordless-by-default.md`](./passwordless-by-default.md) | Absolute rule | Authoring IaC or CI/CD — managed identity / workload identity federation for auth; never a secret, connection string, or key literal in code |
| [`private-by-default-paas-data-planes.md`](./private-by-default-paas-data-planes.md) | Absolute rule | Provisioning Key Vault / Storage / SQL / Cosmos / ACR — Private Endpoint + Private DNS, `publicNetworkAccess` Disabled |
| [`pick-compute-from-the-decision-tree.md`](./pick-compute-from-the-decision-tree.md) | Pattern | Deciding "where does this run?" — traverse the compute tree (scale-to-zero + ops burden) instead of defaulting to AKS |

---

## How to add a new entry

1. Confirm it's a **rule** (a named, reusable prior), not a one-off story.
2. Copy the shape of an existing doc: `# <imperative rule name>`, then `**Status:**` / `**Domain:**` / `**Applies to:** azure-cloud`, then `## Why this exists` · `## How to apply` (real Bicep/CLI/Policy block + Do/Don't) · `## Edge cases` · `## See also` (link this plugin's own knowledge/agents) · `## Provenance` · the `_Last reviewed:_` line.
3. Append a row to the index table above.
4. Cross-link from the relevant knowledge file and agent.

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — the team constitution + the house opinions these docs codify
- [`../knowledge/`](../knowledge/) — the dated, citation-grounded reference bank + decision trees
- [`../../../docs/best-practices/_TEMPLATE.md`](../../../docs/best-practices/_TEMPLATE.md) — the marketplace-wide doc template
