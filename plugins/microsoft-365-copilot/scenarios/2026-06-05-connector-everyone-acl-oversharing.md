---
scenario_id: 2026-06-05-connector-everyone-acl-oversharing
contributed_at: 2026-06-05
plugin: microsoft-365-copilot
product: copilot-connector
product_version: "unknown"
scope: likely-general
tags: [graph-connector, acl, oversharing, semantic-label, recrawl, security-reviewer]
confidence: high
reviewed: false
---

## Problem

A team built a synced Copilot (Graph) connector over a line-of-business knowledge base so Copilot could ground on it. After the first crawl, **every user could see every item** in Copilot results — including HR-restricted and finance-restricted documents that those users could not open in the source system. The connector had been registered to get data flowing first; ACLs were "to be added later." Separately, the ranking was poor — relevant items buried under noise.

## Context

- Synced connector (index-into-Graph), not federated. Large LoB store, scale + ranked retrieval was the goal — the connector mode was correct per the connector-mode tree.
- The items were ingested with an effective "everyone" / `grantEveryone` ACL because per-item ACLs weren't mapped during ingestion.
- Schema properties were ingested without semantic labels — no `title`/`url` mapping and no `createdBy`/`lastModifiedBy`, so semantic ranking and citations degraded.
- This is a security finding, not just a quality one: a connector indexed with "everyone" ACLs is an **oversharing incident** (CLAUDE.md §3 #7), and the ACL design is a mandatory `ravenclaude-core/security-reviewer` gate.

## Attempts

- Tried: turning on Restricted SharePoint Search / Restricted Content Discovery to "contain" it. Wrong tool — RSS/RCD reduce Copilot's *reach*; they are **not a security boundary** (CLAUDE.md §3 #9) and don't stop a user seeing connector items they shouldn't. They buy time for cleanup, they don't end the gate.
- Tried: re-ingesting with per-item ACLs mapped from the source system's permissions so Copilot trims results per-user — traversing the oversharing-gate tree in [`../knowledge/copilot-extensibility-decision-trees.md`](../knowledge/copilot-extensibility-decision-trees.md) (the "connector 'everyone' ACL → fix ingestion first" leaf). A schema/ACL change triggers a **full recrawl**, and the admin re-approves the connector — that's expected, not a regression.
- Tried (the quality half): added the mandatory semantic labels on every schema property — `title`/`url`/`iconUrl` plus `createdBy`/`lastModifiedBy`/`authors` — which carry the ranking and citation. Ranking improved markedly once the labels were present (CLAUDE.md §3 #6).

## Resolution

Two non-negotiables for a synced connector, both before grounding is allowed: **per-item ACLs ingested for per-user trimming** (the security control) and **semantic labels on every property** (ranking + citation). The fix was a re-ingest mapping source permissions to per-item ACLs + a full schema with semantic labels, then a security-reviewer pass on the ACL design before enabling, then the full recrawl. RSS/RCD were left as reach-reduction during cleanup, never sold as the boundary.

**Action for the next engineer hitting this pattern:** if connector items surface to users who shouldn't see them, the cause is almost always **"everyone"/missing per-item ACLs at ingestion** — fix the ingestion ACL mapping and accept the full recrawl; do not reach for RSS/RCD as the fix (not a boundary, §9). Route the ACL design through `ravenclaude-core/security-reviewer` (mandatory). Add semantic labels in the same pass — they're cheap and they carry ranking + citations. State the `Licensing impact:` line for org-data grounding (§3 #8).

**Sources (retrieved 2026-06-05):**
- Copilot connectors — ACLs and per-user trimming, semantic labels — Microsoft Learn: https://learn.microsoft.com/en-us/microsoftsearch/connectors-overview and the Copilot connectors / Graph connectors schema docs. `[verify-at-build]`.
- Restricted Content Discovery / Restricted SharePoint Search are reach-reduction, not access control — Microsoft Learn restricted-content-discovery docs. `[verify-at-build]`.
