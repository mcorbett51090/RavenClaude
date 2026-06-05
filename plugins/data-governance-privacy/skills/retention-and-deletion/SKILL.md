---
name: retention-and-deletion
description: "Design and operate a data retention and deletion programme: classify data by retention period, build automated purge pipelines, verify deletion propagates to all copies including derived and replicated data, and produce evidence for audit — so data does not persist beyond its legal or business justification."
---

# Skill: retention-and-deletion

**Purpose:** Build the engineering capability that ensures data is deleted when its retention period expires — across primary storage, replicas, backups, derived copies, and downstream systems. Used by `privacy-compliance-engineer` (primary) and `data-governance-architect` (policy definition) and `data-catalog-lineage-engineer` (lineage to find all copies).

## When to use

- A retention schedule exists as a policy but is not yet automated.
- A GDPR/CCPA deletion obligation exists and the team needs to verify it propagates to all copies.
- A new data store is being onboarded and its retention period must be set before first data is written.
- An audit or privacy assessment requires evidence that expired data has been deleted.

---

## Step 1: Retention schedule — classify every data asset

Before building any purge pipeline, every governed data asset must have a defined retention period. Retention is driven by three sources in priority order:

1. **Legal / regulatory mandate** — a jurisdiction's law sets a minimum retention (e.g. tax records 7 years, employment records 6 years EU, medical records jurisdiction-specific). You cannot delete below the legal floor.
2. **Contract obligation** — a customer contract may require shorter or longer retention than the law mandates.
3. **Business purpose** — data may be retained for analytics or product purposes beyond the legal minimum only while the original collection purpose is still valid (GDPR principle of purpose limitation).

**Retention schedule table:**

| Data asset | Classification | Retention period | Basis | Delete by | Storage location(s) | Copies / derived |
|---|---|---|---|---|---|---|
| Customer PII (name, email, address) | Restricted / PII | Account life + 3 years post-closure | Contract + GDPR purpose | Account close + 3yr | primary DB, CRM, DWH | Marketing lists, analytics events |
| Transaction records | Confidential | 7 years from transaction date | Tax / accounting law | 7yr from transaction | primary DB, data warehouse | Reporting aggregates |
| Application logs (no PII) | Internal | 90 days | Business operations | 90 days | Log aggregation platform | — |
| Marketing consent records | Restricted / PII | Life of consent + 5 years after withdrawal | GDPR accountability | Consent withdrawn + 5yr | Consent store | Campaign history |
| Support chat transcripts | Confidential | Account life + 1 year | Business operations | Account close + 1yr | Support platform | — |

---

## Step 2: Build the purge pipeline

For each data asset at retention end, the purge pipeline must:

1. **Identify** rows/objects past their retention date.
2. **Delete** from the primary store.
3. **Propagate** to every downstream copy and replica listed in the lineage graph.
4. **Verify** deletion with a confirmation query.
5. **Log** the deletion event with a timestamp, row count, and operator identity for audit.

**Pattern — database purge job:**

```python
# Example pattern — not production code; adapt to your stack
import datetime, logging

RETENTION_DAYS = 1095  # 3 years

def purge_expired_customer_pii(db_conn, audit_log):
    cutoff_date = datetime.date.today() - datetime.timedelta(days=RETENTION_DAYS)

    # 1. Identify
    count_query = """
        SELECT COUNT(*) as expired_count
        FROM customers
        WHERE account_closed_at < %(cutoff)s
          AND pii_deleted_at IS NULL
    """
    count = db_conn.execute(count_query, {"cutoff": cutoff_date}).fetchone()["expired_count"]

    if count == 0:
        logging.info("No records to purge.")
        return

    # 2. Delete (or pseudonymize — see design choice below)
    delete_query = """
        UPDATE customers
        SET email = NULL,
            full_name = NULL,
            address_line_1 = NULL,
            phone = NULL,
            pii_deleted_at = CURRENT_TIMESTAMP,
            deletion_basis = 'retention_expiry'
        WHERE account_closed_at < %(cutoff)s
          AND pii_deleted_at IS NULL
    """
    db_conn.execute(delete_query, {"cutoff": cutoff_date})

    # 3. Log for audit
    audit_log.write({
        "event": "retention_purge",
        "table": "customers",
        "rows_affected": count,
        "cutoff_date": cutoff_date.isoformat(),
        "executed_at": datetime.datetime.utcnow().isoformat(),
        "operator": "automated_retention_job"
    })
    logging.info(f"Purged PII for {count} expired customer records.")
```

**Design choice — hard delete vs pseudonymization:**
- **Hard delete**: removes the row entirely; safest from a privacy standpoint; may break referential integrity (orphaned FKs in transaction tables).
- **Pseudonymization / field nulling**: replaces PII fields with NULL or a non-reversible hash while keeping the row for analytical/statistical purposes. Use when the row has non-PII value (e.g., order revenue for financial reporting).
- **Aggregation before delete**: aggregate to a non-personal level (e.g., "X customers in region Y, average order $Z") and delete the individual rows. Use when only the aggregate has analytics value.

---

## Step 3: Propagate deletion to all copies

A deletion from the primary database is incomplete if it does not propagate to:

| Copy type | Example | How to propagate |
|---|---|---|
| Read replicas | Database read replicas | Replication propagates automatically — verify after replication lag |
| Data warehouse / lake | Bigquery, Snowflake, Databricks | Run equivalent purge job in the warehouse; standard replication does NOT auto-delete |
| Backups | Daily / weekly snapshots | Document backup retention period separately; ensure backup TTL ≤ data retention period |
| Analytics copies | dbt-built marts, aggregated tables | Trigger a dbt full-refresh or incremental run AFTER the purge so marts no longer reflect the deleted PII |
| Downstream SaaS | CRM, marketing automation, support tools | API-based deletion call to each system; document the API endpoint and confirmation response |
| Archive / cold storage | S3 Glacier, Azure Archive | Programmatic lifecycle rule tied to retention policy; confirm objects are purged not just transitioned |

**Lineage is the map for this step.** The `data-catalog-lineage-engineer` maintains the lineage graph that shows every downstream copy. A deletion without consulting the lineage graph will miss copies. See: `../../skills/catalog-and-lineage/SKILL.md`.

---

## Step 4: Produce audit evidence

Every purge run must produce an audit log entry that is itself retained for the required evidence period (typically the same period as the data that was deleted, or longer if required by the applicable regulation).

**Minimum audit log record:**

```json
{
  "event_type": "data_retention_purge",
  "data_asset": "customers.pii_fields",
  "retention_policy_id": "POLICY-003",
  "retention_period_days": 1095,
  "cutoff_date": "2023-06-05",
  "rows_affected": 4821,
  "storage_locations_purged": ["primary_db", "analytics_warehouse", "crm_api"],
  "locations_pending": ["backup_snapshots_pending_ttl"],
  "executed_at": "2026-06-05T02:00:00Z",
  "executed_by": "automated_retention_job_v2",
  "verification_query_result": "0 rows with pii_deleted_at IS NULL and account_closed_at < 2023-06-05"
}
```

---

## Pitfalls

- **Deleting from the primary store but not the warehouse** — the most common failure; the warehouse is a copy of the data, not an automatic extension of the primary deletion.
- **Backup TTL longer than the retention period** — data lives in cold backups for 5 years even though the retention policy says 3 years; set backup lifecycle rules to match or be shorter than the retention period.
- **No audit trail of deletions** — when a regulator or a DSR erasure audit asks "was this data deleted?" the answer must be evidenced, not asserted.
- **Purge job runs but the dbt mart is not refreshed** — the primary DB has no PII but the `fct_customers` mart still has it; always trigger mart refreshes after purge.
- **Retention period set as a comment in a Confluence page** — it must be enforced programmatically; a policy document is not a retention control.
