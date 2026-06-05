---
scenario_id: 2026-06-05-pii-discovery-in-the-warehouse
contributed_at: 2026-06-05
plugin: data-governance-privacy
product: data-catalog
product_version: "n/a"
scope: likely-general
tags: [pii-discovery, classification, warehouse, column-tagging, derived-pii]
confidence: high
reviewed: false
---

## Problem

A data team migrated to a cloud warehouse (Snowflake-style) and granted the analytics group broad `SELECT` on the raw and modeled schemas to "unblock" them. Security later asked a simple question — *which columns contain personal data, and who can see them?* — and nobody could answer. There was no inventory. The team's mental model was "PII lives in the `customers` table," but PII had **propagated**: an `email` column had been copied into a `marketing_events` fact table, a free-text `support_notes` column held names and phone numbers, and a `user_id_hash` in an analytics mart was a reversible hash that re-linked to the person. Broad access had been granted over data nobody had classified — the inverse of CLAUDE.md §2 #1 (you can't govern what you can't find) and §2 #2 (classify before you grant).

## Constraints context

- A live warehouse with hundreds of tables and thousands of columns; manual column-by-column review was not going to happen and would be stale the day after it finished.
- "Anonymized for analytics" was assumed but never verified — the `user_id_hash` was a deterministic hash with no salt rotation, so it was **pseudonymized, not anonymized** (still personal data — §2 #5). The team had been treating it as out of scope.
- Free-text columns (`support_notes`, `feedback`) are the hard case: regex/name heuristics catch structured PII (email, phone, SSN-shaped) but miss names buried in prose.

## Attempts

- Tried: a one-time manual classification spreadsheet. Failed the staleness test — a new dbt model copying `email` into a new mart the next week wasn't in the spreadsheet, so the inventory was wrong almost immediately. Discovery has to be **automated and recurring**, not a one-off (best-practice: automate-discovery-and-keep-it-current).
- Tried: column-name heuristics only (`%email%`, `%phone%`, `%ssn%`). Caught the obvious structured columns but **missed the derived/copied PII** (the hash, the free-text notes) — the exact columns that cause a breach because no one thinks of them.
- Tried (the move that worked): stand up a **data catalog with automated, scheduled sensitive-data discovery** — column-name heuristics *plus* sampled value-pattern scanning *plus* a pass over free-text columns — that **tags** each column with a classification (public / internal / confidential / restricted + a PII flag) and **propagates the tag along lineage**, so when `email` is copied into a new table the copy inherits the PII tag automatically. Classification then **drives the controls**: restricted/PII columns get column-masking and role-gated access at the warehouse layer; broad `SELECT` was revoked and re-granted least-privilege.

## Resolution

The fix was **discovery → classification → tag-propagation-by-lineage → controls**, in that order, and **automated** so it stays current. The load-bearing insight: the dangerous columns are the **derived and copied** ones (the hash, the email in the fact table, the names in free text), not the obvious `customers.email`. Tag propagation along lineage is what keeps the classification honest as data moves; a reversible hash is pseudonymization, so it stays in PII scope.

**Action for the next engineer:** don't trust "PII only lives in the customer table" and don't trust "it's hashed so it's anonymous." Run automated discovery that samples values and scans free-text, not just column names; verify any claimed anonymization against the re-identification bar (a keyless, non-re-linkable transform) before treating it as out of scope; and propagate tags along lineage so copies inherit the classification. The warehouse RLS/masking *implementation* routes to `data-platform`; this team sets the classification + policy they enforce (§3).

Cross-reference: complements the **Classify this data** and **Is this anonymized or pseudonymized?** trees in [`../knowledge/data-governance-privacy-decision-trees.md`](../knowledge/data-governance-privacy-decision-trees.md), the [`data-inventory`](../templates/data-inventory.md) and [`classification-scheme`](../templates/classification-scheme.md) templates, and [`../best-practices/lineage-must-track-derived-and-copied-pii.md`](../best-practices/lineage-must-track-derived-and-copied-pii.md). The [`../scripts/pii_risk_score.py`](../scripts/pii_risk_score.py) `classify` mode turns the discovered signals into a defensible classification tier.

**Sources (retrieved 2026-06-05):**
- OpenMetadata — auto-classification / PII tagging via metadata workflows: https://github.com/open-metadata/OpenMetadata
- Apache Atlas — classification + tag propagation along lineage (Apache Ranger integration): https://atlas.apache.org/

Tool capabilities are version-volatile — `[verify-at-use]` against the current release before quoting a feature.
