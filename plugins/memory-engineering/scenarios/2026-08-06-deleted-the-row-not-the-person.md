---
scenario_id: 2026-08-06-deleted-the-row-not-the-person
contributed_at: 2026-08-06
plugin: memory-engineering
product: memory-erasure
product_version: "n/a"
scope: likely-general
tags: [erasure, embeddings, version-history, derived-summary, redaction, retention]
confidence: medium
reviewed: false
---

## Problem

An erasure request arrived for one individual's data. Engineering deleted the matching memories, the endpoint returned success, and the request was reported closed. A later spot-check retrieved the same facts through semantic search and found them again in a weekly rollup summary. The risk: deleting the row is not erasure — embeddings, immutable version history and derived summaries retain the content (§3 #7).

## Context

- Store: durable memories plus a vector index built from them, plus a nightly consolidation that produced summaries under new ids.
- Constraint: the design record had a retention section and no erasure section (§3 #3, #7).
- Nobody had asked what a delete leaves behind, because the API had a delete verb and it returned 200.
- The legal determination — scope, lawful basis, schedule — sat with counsel, not with this team.

## Attempts

- Tried: **enumerating the derived artifacts.** Outcome: four surfaced — the vector rows, the immutable version history, the nightly summary, and an export that had already left the system. There is no automatic cascade between them; each needed its own decision (§3 #7).
- Tried: **redacting the historical versions.** Outcome: the calls on non-head versions applied. The call on the version that was the **current head** returned success-shaped output and changed nothing — the platform will not redact the live value. The sequence had to be *write a new version or delete the memory first, then redact*.
- Tried: **verifying by return code.** Outcome: this is what hid the failure for a week. Verification was switched to **reading the value back**, which is the only check that distinguishes "redacted" from "reported redacted."
- Tried: **rolling back an unrelated change afterwards.** Outcome: with no restore endpoint, rollback is retrieve-then-rewrite — and a rollback run *after* an erasure reintroduces the erased content. Sequencing became an explicit step in the runbook.

## Resolution

The fix was to **treat erasure as a design-time deliverable, not a runtime request**: enumerate every residue before the first write, delete or re-index the vector in the same transaction as the row, redact history in the correct order, and verify by read-back. The output was an erasure section in the [design record](../templates/memory-design-record.md) listing all five residues with an owner and a verification step each, plus a note that backups and exports are answered in the retention policy rather than in code.

**Action for the next engineer hitting this pattern:** **write down what remains after a delete before the store takes its first write.** Vectors, versions, derived summaries, cached prefixes and backups each fail an erasure request in their own way, and a redaction call on the current head fails silently on exactly the data the request was about. Keep the boundary too: whether the store holds personal data, what lawful basis applies and what the schedule must say are determinations for [`data-governance-privacy`](../../data-governance-privacy/) and counsel — this team's job is to make the system able to carry the determination out. See [memory security and privacy](../knowledge/memory-security-and-privacy.md).

Platform behaviour in this narrative is illustrative and unverified — treat as `[unverified — training knowledge]`, and re-check every retention window, cap and redaction behaviour `[verify-at-use]` against [memory surfaces](../knowledge/memory-surfaces-2026.md) before any deliverable (§3 #8).
