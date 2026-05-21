# Salesforce integration

> **Last reviewed:** 2026-05-21. Sources: Salesforce developer docs ([developer.salesforce.com/docs/atlas.en-us.api_asynch.meta/api_asynch/bulk_common_limits.htm](https://developer.salesforce.com/docs/atlas.en-us.api_asynch.meta/api_asynch/bulk_common_limits.htm)), Fivetran/Airbyte Salesforce docs. Refresh when: (a) Salesforce raises or restructures Bulk API 2.0 ceilings, (b) the SOQL deprecation list changes materially, or (c) a Salesforce edition / org-type the engagement uses has different limits.

## Auth

- **Connected App + OAuth 2.0** is the modern standard for ELT
- **JWT-bearer flow** (server-side) — preferred for unattended ELT
- **Web Server flow** — interactive; for initial setup only
- **Username-password flow** — deprecated; don't use for new builds

## API choices

| API | Use case |
|---|---|
| **Bulk API 2.0** | The ELT backbone — high-volume, async, CSV-shaped |
| **REST API** | Real-time reads; metadata; small/medium queries |
| **SOQL via REST** | Custom queries with relationship traversal |
| **Streaming API (PushTopic / Change Data Capture)** | Real-time updates; complement to ELT for fast-moving entities |
| **Metadata API** | Schema introspection; rarely in ELT scope |

**Bulk API 2.0 is the standard for ELT.** All major vendors use it.

## Rate limits (Bulk API 2.0)

| Limit | Value | Notes |
|---|---|---|
| Records / 24 hours | **150,000,000** | The headline ceiling |
| Batch submissions / 24 hours | **15,000** | Per org |
| Records per batch | **10,000** | Hard ceiling |
| Batch payload size | **10 MB** | Includes column overhead |

**Rolling 24-hour window** — not a calendar day. Org-wide limits apply across all integrations.

> Source: [Bulk API 2.0 Limits](https://developer.salesforce.com/docs/atlas.en-us.api_asynch.meta/api_asynch/bulk_common_limits.htm)

## Connector availability

All major ELT vendors ship a Salesforce connector. Bulk API 2.0 is the universal backbone.

## Common entities

### Standard objects
| Object | Use case |
|---|---|
| `Account` | Account dimension (customer entity in B2B) |
| `Contact` | Contact dimension |
| `Opportunity` | Pipeline fact |
| `OpportunityLineItem` | Opportunity-line-item fact |
| `Case` | Service / support fact |
| `Lead` | Pre-conversion lead dimension |
| `Campaign` | Marketing-attribution dimension |
| `User` | Internal user dimension (account owners, case owners) |
| `Task` / `Event` | Activity facts (calls, meetings, emails) |
| `Product2` / `Pricebook2` / `PricebookEntry` | Product + pricing dimensions |

### Common custom objects
Salesforce customers heavily customize — most engagements have N custom objects. The pattern:

1. Inventory the custom objects (`/services/data/v59.0/sobjects/` lists them)
2. Pick the ones with analytics value
3. Add to the Airbyte / Fivetran connector configuration
4. Document the custom-object-to-mart mapping in the engagement

## SOQL relationship-query nuances

Salesforce's SOQL allows parent-to-child and child-to-parent traversals:

```sql
-- Parent → child (nested query): all opportunities for an account
SELECT Id, Name, (SELECT Id, Amount, StageName FROM Opportunities)
FROM Account
WHERE Industry = 'Technology'

-- Child → parent (dot-notation): opportunity with account fields inline
SELECT Id, Amount, Account.Name, Account.Industry
FROM Opportunity
WHERE CloseDate = THIS_QUARTER
```

ELT connectors typically pull each object as a separate stream and join downstream in dbt — not via SOQL relationships during extract.

## Field selection — avoid the 10MB payload trap

A single Account record with all standard + custom fields can be huge. **Default ELT configurations often pull every field;** for high-volume orgs, this hits the 10MB payload limit and breaks Bulk API 2.0.

**Mitigation:**
- Explicitly enumerate fields in the connector config (don't `SELECT *`)
- Split very-wide objects into multiple streams (e.g., Account_core + Account_extended)

## Incremental sync

- **`LastModifiedDate`** is the canonical cursor field for every standard object
- **Custom objects** typically have `LastModifiedDate` automatically; verify per object
- **Soft-deletes** — Salesforce uses `IsDeleted` flag; some connectors handle this, some don't. Verify deleted-record behavior before relying on counts.

## dbt modeling — common marts

| Mart | Purpose |
|---|---|
| `dim_account` | Account dimension |
| `dim_contact` | Contact dimension |
| `dim_user` | Salesforce internal user dimension (for owner attribution) |
| `fact_opportunity` | Pipeline + closed-won/lost facts |
| `fact_opportunity_history` | OpportunityFieldHistory — stage transitions |
| `fact_case` | Service/support volume + resolution times |
| `fact_activity` | Tasks + Events for activity reporting |
| `mart_pipeline_waterfall` | Pipeline movement (created, advanced, slipped, won, lost) |
| `mart_arr_movement` | New ARR / expansion ARR / churn from Salesforce + Stripe joined |
| `mart_activity_heatmap` | Sales-rep activity by week/day |

## Common gotchas

1. **OpportunityFieldHistory is huge** — every field change creates a row. Filter to the fields that matter (StageName, Amount, CloseDate) before ELT.
2. **Multi-currency orgs** — Amount is in the opportunity's currency, not necessarily USD. Need `CurrencyIsoCode` + currency conversion table.
3. **Record-type-driven schemas** — different record types may have different required fields; dim_record_type is often needed.
4. **Soft-deletes vs hard-deletes** — `IsDeleted = true` records are recoverable; check connector behavior. The Apex Recycle Bin holds them for 15 days before hard-delete.
5. **Person Accounts (B2C orgs)** — single record with both Account and Contact fields; some connectors handle, some don't.
6. **Custom objects ending in `__c`** — schema mapping needs to handle this naming convention.
7. **Profile / Permission Set filtering** — the connector's user/profile may not see all records. Use a dedicated "Integration User" with View All Data permission for ELT.
8. **API consumption accounting** — every Bulk API call counts against the rolling 24h ceiling, even failed batches. Failed-batch storms can lock out the integration.

## PII / PHI considerations

- **Standard objects contain PII** — Name, Email, Phone, Address on Account/Contact/Lead
- **Healthcare orgs (Health Cloud)** may have PHI — route through `ravenclaude-core/security-reviewer`
- **GDPR / CCPA** — Salesforce honors right-to-erasure; warehouse needs parallel delete process
- **Encrypt sensitive custom fields** with Salesforce Shield Platform Encryption (separate license) — note this affects extractability

## Recommended sync configuration

- **Cadence:** daily for analytics; hourly only if dashboards must reflect intraday pipeline movement
- **Backfill:** 24+ months for pipeline analytics; full history for OpportunityFieldHistory if doing stage-transition analysis
- **Incremental cursor:** `LastModifiedDate` (rare exception: Tasks/Events sometimes need `SystemModstamp`)
- **Field-selection:** explicit enumeration, not `*` — avoids 10MB payload trap

## Refresh triggers

- Salesforce raises or restructures Bulk API 2.0 ceilings (rare but possible)
- SOQL deprecation list changes (legacy syntax retirement)
- Engagement uses a Salesforce-Industries cloud (Health Cloud, Financial Services Cloud) with different object set
- Custom objects added that require ELT inclusion
- Salesforce Connect / External Objects become relevant (different extraction pattern)
