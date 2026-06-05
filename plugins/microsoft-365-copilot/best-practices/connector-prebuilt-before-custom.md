# Use a prebuilt Graph connector before building a custom one

**Status:** Pattern
**Domain:** Copilot connectors
**Applies to:** `microsoft-365-copilot`

---

## Why this exists

Microsoft and third-party vendors publish over 100 prebuilt Graph connectors (ServiceNow, Salesforce, Confluence, GitHub, Jira, Zendesk, and others) available in the Microsoft 365 admin center connector gallery. A custom connector requires authoring the schema, the ACL ingestion logic, the crawl schedule, and the semantic-label mapping — typically 2–4 weeks of engineering. A prebuilt connector for the same source is an admin-center configuration that takes hours. Engineers who jump straight to the custom SDK path for a source that has a prebuilt connector waste the entire effort and lose the vendor-maintained schema and ACL improvements. The prebuilt gallery is the first check, not an afterthought.

## How to apply

1. Search the connector gallery: **M365 admin center → Settings → Search & intelligence → Data sources**.
2. Check the [Microsoft Graph connectors gallery](https://learn.microsoft.com/microsoftsearch/connectors-gallery) for the source system.
3. Verify the prebuilt connector's supported items, semantic labels, and ACL support match the requirement.
4. Only if no prebuilt connector exists or the prebuilt connector cannot express the required schema/ACLs, proceed to the custom SDK.

Evaluation criteria for a prebuilt connector:

| Criterion | Check |
|---|---|
| Source supported | Gallery entry for the system exists |
| Semantic labels | `title`, `url`, `lastModifiedDateTime`, `createdBy` at minimum |
| ACL support | Connector ingests per-item ACLs, not "everyone" |
| Item types needed | Connector covers the item types in scope (pages, tickets, cases, etc.) |
| Refresh cadence | Connector supports the required freshness (full crawl + incremental) |

**Do:**
- If a prebuilt connector exists but has a schema gap (a custom field the org needs), file feedback with the vendor and build a complementary custom connector for the gap, not a replacement.
- Check the GA/preview status of the prebuilt connector before recommending it in a production design `[verify-at-build]`.
- Test the prebuilt connector in a test tenant before advising the customer — some prebuilts have known ACL or semantic-label limitations that are not in the documentation.

**Don't:**
- Recommend a custom connector SDK build for Salesforce, ServiceNow, Confluence, or GitHub without first checking the gallery — these all have prebuilts.
- Mix a prebuilt connector with a custom connector that indexes the same source items — duplicate indexed content degrades ranking.
- Assume a prebuilt connector handles all site/workspace types of its source — many only cover the default tier (e.g., Confluence Cloud but not Confluence Data Center) `[verify-at-build]`.

## Edge cases / when the rule does NOT apply

Proprietary line-of-business systems (internal HRMS, legacy claim-processing systems) with no public API surface will have no prebuilt connector. Custom SDK is the only path; apply the `label-and-acl-trim-every-connector-property` rule.

## See also

- [`../agents/graph-connector-engineer.md`](../agents/graph-connector-engineer.md) — owns connector design and the prebuilt vs custom decision
- [`./connector-choose-synced-vs-federated-and-set-crawl-refresh.md`](./connector-choose-synced-vs-federated-and-set-crawl-refresh.md) — the synced/federated choice that applies once the connector type is selected

## Provenance

Codifies the `graph-connector-engineer` domain knowledge from CLAUDE.md §2 and the `copilot-connectors-2026.md` knowledge file; Microsoft Graph connectors gallery documentation.

---

_Last reviewed: 2026-06-05 by `claude`_
