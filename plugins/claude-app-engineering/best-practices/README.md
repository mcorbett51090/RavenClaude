# claude-app-engineering — best-practice docs

Named, citable rules for building production applications on the Claude API, the Claude Agent SDK, and MCP. Each file is **one rule**, grounded in this plugin's dated, first-party-sourced knowledge bank ([`../knowledge/`](../knowledge/)) and (where grep-able) enforced by the `check-claude-app-anti-patterns.sh` hook. Read a doc whole and cite it; don't paraphrase a fragment.

These docs codify the cross-cutting **house opinions** in [`../CLAUDE.md`](../CLAUDE.md) §3 into copy-paste-grade guidance. Numeric / GA claims (model lineup, cache multipliers, minimums) are **dated** and live in [`../knowledge/model-selection-and-2026-capability-map.md`](../knowledge/model-selection-and-2026-capability-map.md) — the platform ships monthly, so verify before quoting a client.

---

## Index

| Doc | Status | Use when |
|---|---|---|
| [`cache-the-static-prefix.md`](./cache-the-static-prefix.md) | Absolute rule | Laying out or debugging a prompt — stable above the breakpoint, volatile below; never mutate tool defs per request ("Claude is too expensive" usually means a misplaced breakpoint) |
| [`right-size-with-a-routing-ladder.md`](./right-size-with-a-routing-ladder.md) | Pattern | Choosing the model — triage cheap (Haiku), escalate on uncertainty, reserve Opus for the hard tail; measure cost-per-resolved-task |
| [`evals-before-vibes.md`](./evals-before-vibes.md) | Absolute rule | Shipping any prompt / model / tool-definition change — gate it on a golden-set delta, not "it looks better" |

---

## How to add a new entry

1. Confirm it's a **rule** (a named, reusable prior), not a one-off story.
2. Copy the shape of an existing doc: `# <imperative rule name>`, then `**Status:**` / `**Domain:**` / `**Applies to:** claude-app-engineering`, then `## Why this exists` · `## How to apply` (real Python/TS/config block + Do/Don't) · `## Edge cases` · `## See also` (link this plugin's own knowledge/agents) · `## Provenance` · the `_Last reviewed:_` line.
3. Append a row to the index table above.
4. Cross-link from the relevant knowledge file and agent.

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — the team constitution + the house opinions these docs codify
- [`../knowledge/`](../knowledge/) — the dated, citation-grounded reference bank + the build-surface decision tree
- [`../../../docs/best-practices/_TEMPLATE.md`](../../../docs/best-practices/_TEMPLATE.md) — the marketplace-wide doc template
