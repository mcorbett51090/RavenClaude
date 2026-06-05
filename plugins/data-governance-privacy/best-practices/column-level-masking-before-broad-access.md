# Apply column-level masking on PII columns before granting broad read access

**Status:** Absolute rule
**Domain:** Access governance / data masking
**Applies to:** `data-governance-privacy`

---

## Why this exists

A warehouse role that can SELECT from any table in `marts` exposes every PII column to every holder of that role — analysts, BI tools, ML pipelines — regardless of whether their use case requires it. Granting read access and then trusting individuals not to query sensitive columns is not access control; it is hope. Column-level masking (dynamic data masking on Snowflake, column-level security on BigQuery, RLS-equivalent column policies on Postgres) ensures that PII columns return masked values unless the querying role is explicitly in the unmasked group.

## How to apply

**Postgres (column-level security via view + RLS):**

```sql
-- Masked view for analysts without PII access
CREATE VIEW marts.fct_customers_masked AS
SELECT
    customer_id,
    tenant_id,
    created_at,
    customer_tier,
    -- Mask PII for non-privileged roles
    CASE WHEN current_setting('app.role', true) = 'pii_reader' 
         THEN email 
         ELSE md5(email) || '@masked.invalid'
    END AS email,
    CASE WHEN current_setting('app.role', true) = 'pii_reader'
         THEN phone
         ELSE regexp_replace(phone, '\d', 'X', 'g')
    END AS phone
FROM marts.fct_customers;

GRANT SELECT ON marts.fct_customers_masked TO analytics_role;
-- Only pii_reader role gets SELECT on the unmasked table
GRANT SELECT ON marts.fct_customers TO pii_reader_role;
```

**Snowflake (dynamic data masking):**

```sql
CREATE MASKING POLICY email_mask AS (val string) RETURNS string ->
  CASE
    WHEN CURRENT_ROLE() IN ('PII_READER', 'ANALYST_PRIVILEGED') THEN val
    ELSE SHA2(val)
  END;

ALTER TABLE fct_customers MODIFY COLUMN email
  SET MASKING POLICY email_mask;
```

**Do:**
- Apply masking policies to every PII-classified column before the table is accessible to any shared role.
- Maintain a named `pii_reader` role (or equivalent) and limit its membership to approved users.
- Audit `pii_reader` role membership quarterly.

**Don't:**
- Grant unmasked access to PII columns to a "general analyst" role.
- Implement masking only in the BI tool layer — masking must live at the warehouse, not the dashboard.
- Mask aggregate columns (a masked `SUM(revenue)` is meaningless) — masking applies to individual-level PII, not aggregated metrics.

## Edge cases / when the rule does NOT apply

- Internal development environments where all data is synthetic and no real PII is present are exempt. Document this and add a CI guard that prevents real data from being loaded into dev.

## See also

- [`../agents/data-catalog-lineage-engineer.md`](../agents/data-catalog-lineage-engineer.md) — tags PII columns; masking follows classification
- [`./least-privilege-data-access.md`](./least-privilege-data-access.md) — the least-privilege access rule that masking enforces

## Provenance

Codifies data-governance-privacy CLAUDE.md §3 seams ("Warehouse row-/column-level security and masking implementation → data-platform; we set the classification + policy they enforce") — this rule is the governance side of that seam: defining which columns need masking and which roles bypass it.

---

_Last reviewed: 2026-06-05 by `claude`_
