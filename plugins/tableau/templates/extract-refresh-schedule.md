> Use this template to document and govern the extract refresh schedule for a Tableau data source — freshness requirements, schedule justification, failure alerting, and the incremental-vs-full decision.

# Extract Refresh Schedule: [Data Source Name]

## Metadata

| Field | Value |
|---|---|
| Data source name | [Name as published on Tableau Server/Cloud] |
| Published location | [Site / Project path] |
| Source system | [e.g., Snowflake / SQL Server / Salesforce] |
| Owner | [Name / Team] |
| Last reviewed | [YYYY-MM-DD] |

---

## Freshness requirement

**What is the maximum acceptable data age for dashboards using this extract?**

[e.g., "Data must be no more than 4 hours old during business hours (8 AM–6 PM local time)."]

**Who defined this requirement and why?**

[e.g., "Finance director: daily P&L review requires same-day actuals by 8 AM."]

---

## Refresh type decision

| Option | Selected? | Reason |
|---|---|---|
| **Full refresh** | [ ] | Source data has updates to historical rows; incremental is not safe |
| **Incremental refresh** | [ ] | Append-only source; incremental key column: `[column name]` |
| **Live connection (no extract)** | [ ] | Freshness requirement < 1 min; accepted query latency: `[X]` s |

If incremental: confirm the incremental key column is monotonically increasing and historical rows are never updated.

---

## Schedule

| Window | Frequency | Time (UTC) | Days |
|---|---|---|---|
| Business hours | [Every N hours / Once] | [HH:MM] | [Mon–Fri] |
| Off-hours maintenance | [Full refresh] | [02:00] | [Sunday] |

**Estimated refresh duration (last measured):** [X minutes]

**Server resource impact:** [Low / Medium / High — note if this runs during peak server hours]

---

## Failure alerting

| Alert type | Recipient | Channel | SLA to acknowledge |
|---|---|---|---|
| Refresh failure | [Name / DL] | [Email / Slack / PagerDuty] | [30 min / 2 hours] |
| Stale data (age > threshold) | [Name / DL] | [Email] | [1 business day] |

**Runbook on failure:**
1. Check Tableau Server Admin → Background Tasks for failed job details.
2. Verify source system connectivity (firewall, credentials).
3. If source unavailable: notify dashboard consumers via [channel] with expected resolution time.
4. If data is stale > [X hours]: disable dashboard or add a "data as of [timestamp]" banner.

---

## Row count and size benchmarks

| Metric | Value | Last measured |
|---|---|---|
| Row count (full extract) | [e.g., 12 M rows] | [YYYY-MM-DD] |
| Extract file size (.hyper) | [e.g., 4.2 GB] | [YYYY-MM-DD] |
| Growth rate | [e.g., ~500 K rows / month] | |
| Estimated 12-month size | [Calculate] | |

**Action if size exceeds [X GB]:** [e.g., apply date-range extract filter, partition by year, migrate to Virtual Connection]

---

## Extract filters applied

| Filter | Value | Reason |
|---|---|---|
| Date range | [Last 3 years] | Reduces extract size; no dashboard uses data older than this |
| Status | [Active records only] | Deleted records not needed |
| [Other] | | |

---

## Change log

| Date | Change | Author |
|---|---|---|
| [YYYY-MM-DD] | [Initial schedule] | [Name] |
| | | |
