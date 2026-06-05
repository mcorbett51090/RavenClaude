# Run PII discovery before connecting any new data source to the warehouse

**Status:** Absolute rule
**Domain:** Data catalog / PII discovery
**Applies to:** `data-governance-privacy`

---

## Why this exists

A new data pipeline that lands CRM, support, or HR data in a warehouse without a prior PII scan is a classification debt that accrues interest immediately. Once the data is in the warehouse and joined into marts, re-identifying which columns contain PII, who has accessed them, and where copies have propagated is an expensive retroactive exercise. A pre-ingestion PII scan takes minutes; a post-ingestion remediation takes weeks. The catalog and lineage system can only track what has been classified — land first without scanning and you lose the classification window.

## How to apply

Before a new Airbyte, Fivetran, or custom connector is activated in production:

1. **Run a PII discovery scan** on the source's schema (column names + sample values) using the catalog's discovery tool (OpenMetadata's PII detection, DataHub's ML classifier, or a column-name heuristic).
2. **Tag identified columns** in the catalog with the appropriate classification (Confidential+PII, Restricted+PII, or Internal).
3. **Apply the corresponding controls** (column masking, access policy, retention period) before the pipeline first runs.
4. **Document the lawful basis** for landing each PII column in the warehouse.

**Column-name heuristic (start here before scanning sample values):**

```python
PII_SIGNALS = [
    "email", "phone", "name", "first_name", "last_name", "address",
    "ssn", "tax_id", "dob", "date_of_birth", "ip_address", "device_id",
    "user_id", "customer_id", "account_number", "credit_card",
    "salary", "compensation", "health", "diagnosis"
]

def flag_for_pii_review(column_name: str) -> bool:
    return any(sig in column_name.lower() for sig in PII_SIGNALS)
```

**Do:**
- Add PII discovery to the pipeline acceptance criteria — a new connector does not go to production without a completed scan and classification.
- Involve the `data-governance-architect` in the classification step for any Restricted or PII column.
- Store classification tags in the catalog (not only in a spreadsheet) so lineage tracking can use them.

**Don't:**
- Land data first and "do the PII scan later" — later never comes until an audit or a breach.
- Trust column names alone — run a sample-value scan for columns like `notes`, `description`, `comments` that may contain free-text PII.

## Edge cases / when the rule does NOT apply

- A source that contains no human-generated or behavioral data (e.g., a weather API, a stock price feed) may be exempt — but document the determination.
- Internal system logs that contain only system-generated IDs (no human identifiers) may be expedited through the scan, but the absence-of-PII finding must be recorded.

## See also

- [`../agents/data-catalog-lineage-engineer.md`](../agents/data-catalog-lineage-engineer.md) — runs the PII discovery and manages catalog tagging
- [`./classification-drives-controls.md`](./classification-drives-controls.md) — the classification-to-controls rule that follows discovery

## Provenance

Codifies data-governance-privacy CLAUDE.md §2 house opinion #1 ("You can't govern what you can't find. Classification precedes control") applied at the pipeline-entry gate — a specific enforcement point for the discovery-first principle.

---

_Last reviewed: 2026-06-05 by `claude`_
