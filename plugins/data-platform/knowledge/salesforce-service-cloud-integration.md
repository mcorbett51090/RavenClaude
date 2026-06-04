---
name: salesforce-service-cloud-integration
description: "Salesforce Service Cloud (Case + Entitlements + Milestones) ingestion — extends the general Salesforce knowledge file with the service-specific surface. Bulk API 2.0 is the backbone but **PK Chunking is DISABLED in Bulk 2.0** (only Bulk 1.0). Use **`LastModifiedDate`** for incremental watermark (NOT `SystemModstamp` — that fires on triggered automations and produces phantom rows). First-class `IsEscalated` boolean. SLA-breach detection lives in `Entitlement` / `Milestone` (`IsViolated`, `MilestoneStatus`)."
last_reviewed: 2026-06-04
confidence: high
---

# Salesforce Service Cloud integration

> **Last reviewed:** 2026-06-04. **Specializes** [`salesforce-integration.md`](./salesforce-integration.md) for the Service-Cloud-specific shape (Case + CaseHistory + EmailMessage + Entitlement + Milestone + BusinessHours). Sources: Salesforce Object Reference (Case), Salesforce Bulk API 2.0 docs (PK Chunking), Salesforce Help (Case Fields), Planhat ↔ Salesforce integration. Refresh when: (a) Bulk API 2.0 acquires PK Chunking (currently absent), (b) `LastModifiedDate` semantics change, (c) Entitlement/Milestone shape shifts on a new edition, or (d) Planhat ↔ Salesforce SFDC integration changes its `sourceId` convention.

## Connector strategy — BUY (Bulk 2.0 under the hood)

- **Fivetran** — first-party Salesforce connector covering Sales + Service Cloud objects. Bulk API 2.0 under the hood for large initial loads. `[verify-at-use — 2026-06-04]`
- **Airbyte** — Salesforce source covering arbitrary SObjects (Case included).
- **Hightouch** — Salesforce as a **destination** (write back to Cases / Account-level CS-health fields).
- **Planhat ↔ Salesforce** — explicitly documented bidirectional config; maps the SFDC `Account.Id` onto Planhat `Company.sourceId`.

For warehouse ingestion of Service Cloud objects, **Bulk API 2.0 is the right shape**. Composite/REST is only correct for low-volume real-time use (<100 records/min).

## API extraction pattern — Service Cloud specifics

### The PK Chunking gotcha (Bulk 2.0)

- **Bulk 2.0 does NOT support PK Chunking.** It's an artifact of Bulk 1.0 only. `[verify-at-use — 2026-06-04]`
- **Implication:** for orgs with >50M Cases, connector parallelism must be **date-range parallelism**, not PK chunks. Split `LastModifiedDate` into bounded ranges per worker.

### Watermark — `LastModifiedDate`, not `SystemModstamp`

- **Use `LastModifiedDate`** for incremental ingestion.
- **Do NOT use `SystemModstamp`** — it updates when triggered automations run even if no user data changed. That produces **phantom rows in the warehouse**: Cases that appear "modified" with no actual field delta. `[verify-at-use — 2026-06-04]`
- **Pattern:**
  ```sql
  SELECT … FROM Case WHERE LastModifiedDate > :hwm ORDER BY LastModifiedDate ASC
  ```
  Submit via Bulk 2.0; persist `max(LastModifiedDate)` from the batch as the new HWM.
- **Edge case:** `Task` / `Event` records sometimes need `SystemModstamp` because their `LastModifiedDate` doesn't always update on ownership/sharing recalculation. Verify per object before picking the watermark.

### Soft deletes — `queryAll`

- `IsDeleted=TRUE` rows are returned only by `queryAll`, not `query`. Bulk 2.0 accepts `operation=queryAll` explicitly — **set it or you'll miss deleted records.** The Recycle Bin holds them for 15 days before hard-delete. `[verify-at-use — 2026-06-04]`

### API limits (Service Cloud is governed by org-level Bulk 2.0 limits)

| Limit | Value | Notes |
|---|---|---|
| Records / 24h | **150,000,000** | org-wide |
| Batch submissions / 24h | **15,000** | org-wide |
| Records per batch | **10,000** | hard ceiling |
| Batch payload size | **10 MB** | includes column overhead — wide Case rows can hit this |

`[verify-at-use — 2026-06-04]` — see [`salesforce-integration.md`](./salesforce-integration.md) for full Bulk 2.0 detail and the field-selection trap.

## Schema shape — Service Cloud entities

### `Case` standard fields

`Id`, `CaseNumber`, `AccountId`, `ContactId`, `AssetId`, `OwnerId`, `Status`, `Priority`, **`IsEscalated`** (boolean — first-class), `Origin`, `Type`, `Reason`, `Subject`, `Description`, `SuppliedName`, `SuppliedEmail`, `SuppliedPhone`, `SuppliedCompany`, `ClosedDate`, `IsClosed`, `CreatedDate`, `LastModifiedDate`, `SystemModstamp`, `ParentId` (parent case for hierarchy), `RecordTypeId`, `MilestoneStatus`, `EntitlementId`, `SlaStartDate`, `SlaExitDate`, `BusinessHoursId`.

`[verify-at-use — 2026-06-04]`

### Related objects (the SLA + audit surface)

| Object | Use |
|---|---|
| `CaseComment` | Public / private comments — conversation_event grain |
| `CaseHistory` | Every field change — the canonical input for status-transition / aging analysis |
| `EmailMessage` | Email channel — conversation_event grain for email-driven cases |
| `Entitlement` | SLA contract — `StartDate`, `EndDate`, `BusinessHoursId`, `SlaProcessId` |
| `Milestone` | Per-entitlement SLA target — `TargetDate`, `CompletionDate`, `IsCompleted`, **`IsViolated`** |
| `BusinessHours` | The schedule used for business-hour SLA math |

## Ticket-aging derivation

- `CreatedDate` → first outbound `EmailMessage` = first-response (when email-driven). For omnichannel, derive from `CaseHistory` `OwnerId` first non-null transition.
- `CreatedDate` → `ClosedDate` = total resolution.
- **Business-hours aging:** join `Case.BusinessHoursId` (or `Entitlement.BusinessHoursId`) → `BusinessHours` schedule. Snowflake / BigQuery have no native business-hours diff function — use a calendar table or `dbt-utils` business-hours macros.

## SLA-breach detection — Entitlements + Milestones

Service Cloud's first-class SLA concept is **Entitlements + Milestones**:

- `Milestone.IsViolated = TRUE` — the canonical breach flag.
- `Milestone.CompletionDate IS NULL AND Milestone.TargetDate < NOW()` — derived live-clock breach detection.
- `Case.MilestoneStatus` rolls up to `"On Track"` / `"Open Violation"` / `"Closed Violation"` / `"Complete"` — useful for the dashboard's headline status.

`[verify-at-use — 2026-06-04]` — Salesforce convention; field is in Case Object Reference.

## Themes / tags & escalation

- **No first-class tags** on Case. Categorization uses `Type`, `Reason`, `RecordTypeId`, and custom topic fields (e.g., `Case.CS_Theme__c` populated by a topic-modeling pipeline).
- **`IsEscalated` is a first-class boolean.** Escalation rules in SFDC flip it based on time/owner/priority criteria.

## Linking to SFDC Account / Planhat Company

**Trivial — `Case.AccountId` IS the bridge** in the SFDC universe.

For multi-system stitching:
- Planhat ↔ Salesforce maps SFDC `Account.Id` → Planhat `Company.sourceId` → clean three-way join.
- See [`./planhat-integration.md`](./planhat-integration.md) for the Planhat side of the bridge.

## Common gotchas

1. **`LastModifiedDate` vs. `SystemModstamp`.** Pick `LastModifiedDate` for the warehouse incremental cursor. `SystemModstamp` fires on triggered automation and produces phantom rows. `[verify-at-use — 2026-06-04]`
2. **Bulk 2.0 lacks PK Chunking.** For orgs with >50M Cases, parallelism must be date-range-based, not PK-based. `[verify-at-use — 2026-06-04]`
3. **Custom statuses + custom Record Types.** Status picklist varies by RecordType — persist `Case.Status` + `RecordType.Name` together to disambiguate.
4. **Merged Cases.** SFDC supports case merge; `MasterRecordId` on the loser points to the survivor. Filter `WHERE IsDeleted = FALSE AND MasterRecordId IS NULL` for the canonical list; include both for audit.
5. **Soft deletes are `queryAll`-only.** Bulk 2.0 requires explicit `operation=queryAll` to surface `IsDeleted=TRUE` rows.
6. **CaseHistory is huge.** Every field change writes a row. Filter to the fields you care about (Status, Priority, OwnerId, IsEscalated) before ELT.
7. **Wide Cases hit the 10 MB Bulk payload cap.** Explicit field enumeration is mandatory for tenants with many custom fields. See [`salesforce-integration.md`](./salesforce-integration.md) for the field-selection mitigation.

## Recommended sync configuration

- **Cadence:** every 1–2 hours for Case + CaseHistory + EmailMessage; daily for Entitlement / Milestone / BusinessHours.
- **Backfill:** 24+ months for resolution-time distributions; full CaseHistory for stage-transition analysis.
- **Incremental cursor:** `LastModifiedDate` on Case + Milestone; `SystemModstamp` only where verified necessary.
- **Field selection:** explicit enumeration — never `SELECT *` on Case.
- **Soft-delete coverage:** `queryAll` operation for Cases.

## Refresh triggers

- Bulk 2.0 acquires PK Chunking (would simplify >50M-Case loads materially).
- `LastModifiedDate` semantics change.
- Entitlement / Milestone shape shifts on a new edition or release.
- Planhat ↔ Salesforce changes the `sourceId` convention.
- A canonical Service-Cloud-specific dbt package emerges.

## References

All URLs accessed 2026-06-04.

- https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_case.htm — Case Object Reference
- https://help.salesforce.com/s/articleView?id=service.cases_fields.htm — Case Fields
- https://developer.salesforce.com/docs/atlas.en-us.sfFieldRef.meta/sfFieldRef/salesforce_field_reference_Case.htm — Case Field Reference
- https://help.salesforce.com/s/articleView?id=release-notes.rn_api_bulk_2.htm — Bulk API 2.0 Release Notes
- https://developer.salesforce.com/docs/atlas.en-us.api_asynch.meta/api_asynch/async_api_headers_enable_pk_chunking.htm — PK Chunking (Bulk 1.0 only)
- https://developer.salesforce.com/docs/atlas.en-us.api_asynch.meta/api_asynch/asynch_api_code_curl_walkthrough_pk_chunking.htm — PK Chunking walkthrough
- https://help.planhat.com/en/articles/9587130-setting-up-the-salesforce-integration — Planhat ↔ Salesforce setup
- https://help.planhat.com/en/articles/9587260-salesforce-troubleshooting-guide — Planhat ↔ Salesforce troubleshooting
