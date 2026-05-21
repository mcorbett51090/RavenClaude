# Google Analytics 4 integration

> **Last reviewed:** 2026-05-21. Sources: Google Analytics 4 docs, BigQuery export docs, Fivetran/Airbyte GA4 connector docs. Refresh when: (a) Google changes the GA4 BigQuery export schema (rare but possible), (b) Google deprecates a GA4 API endpoint, or (c) a new GA4-equivalent product replaces it (none signaled as of 2026-05).

## The key recommendation: use the native BigQuery export

**GA4's native BigQuery export is FREE and is the recommended path when the destination is BigQuery.** Daily export + streaming/intraday export both available. ELT vendors charge for sync; Google's native export is $0.

**Configure once in GA4 → Admin → Product Links → BigQuery Links.**

Use an ELT vendor connector only when:
- Destination is NOT BigQuery (Snowflake, Postgres, etc.)
- Blending GA4 data with other sources at extract time
- GA4 BigQuery quota is exceeded (rare)

## Auth

- **Service Account JSON key** — for ELT vendors using the Data API
- **OAuth 2.0 (user-delegated)** — for interactive tools (Looker Studio, Power BI native connector)

## API options

| API | Use case |
|---|---|
| **Google Analytics Data API (v1)** | Real-time + historical reporting; aggregated metrics + dimensions |
| **Google Analytics Admin API** | Property + account management; rarely in ELT scope |
| **BigQuery export** | Raw event-level data; preferred for analytics |

## Rate limits (Data API)

- **Daily quota** — 200,000 tokens per property per day (each query consumes 1-100 tokens depending on complexity)
- **Per-minute quota** — 1,250 tokens per property per minute
- **Concurrent requests** — 10 per property
- **HTTP 429 / 403 on exceed**

> Source: [Google Analytics Data API quotas](https://developers.google.com/analytics/devguides/reporting/data/v1/quotas)

## UA is gone — GA4 only

**Universal Analytics (UA) stopped processing data July 1, 2023.** UA data export windows have closed for most properties. If the client needs pre-GA4 history:
- **Did they preserve their UA BigQuery export?** If yes, that's the path
- **Did they download CSV exports before sunset?** Treat as historical-only data
- **Are they grandfathered in GA360?** Different SLAs

## Connector availability (Data API)

| Vendor | GA4 connector |
|---|---|
| Fivetran | ✅ (source-google-analytics-4-export uses the BigQuery export under the hood) |
| Airbyte | ✅ (source-google-analytics-data-api uses the Data API directly) |
| Hevo | ✅ |

## Common dimensions + metrics (Data API)

### Dimensions
| Dimension | Use case |
|---|---|
| `date` | Date dimension |
| `sessionDefaultChannelGroup` | Attribution channel grouping |
| `sessionSource` / `sessionMedium` | UTM-style source/medium |
| `sessionCampaignName` | Campaign attribution |
| `pagePath` | Page-level engagement |
| `eventName` | Custom event name |
| `deviceCategory` | Desktop / mobile / tablet |
| `country` / `region` / `city` | Geographic |
| `landingPage` | Landing-page analysis |

### Metrics
| Metric | Use case |
|---|---|
| `sessions` | Session count |
| `engagedSessions` | Sessions with engagement |
| `engagementRate` | Engaged sessions / total sessions |
| `newUsers` | New-user acquisition |
| `totalUsers` | Total user count |
| `screenPageViews` | Page views |
| `averageSessionDuration` | Average session length |
| `conversions` | Conversion events |
| `totalRevenue` | E-commerce revenue (if e-com tracking is set up) |

## BigQuery export schema highlights

The native export is event-level, one row per event. Key columns:

- `event_date` / `event_timestamp` — when
- `event_name` — what (page_view, click, purchase, custom)
- `user_pseudo_id` — anonymized user ID
- `event_params` — repeated record with key/value pairs (one row per event-param)
- `user_properties` — repeated record with key/value pairs
- `device.*` — device attributes
- `geo.*` — geographic attributes
- `traffic_source.*` — campaign / source / medium

**Querying the BigQuery export** requires UNNESTing the `event_params` and `user_properties` arrays — non-trivial SQL. dbt models that flatten the export are common.

## dbt modeling — common marts

| Mart | Purpose |
|---|---|
| `stg_ga4__events` | Flattened event-level model (UNNEST event_params) |
| `dim_session` | Session dimension reconstructed from events |
| `fact_session_engagement` | Per-session engagement metrics |
| `fact_pageview` | Page-view fact |
| `fact_conversion` | Conversion event fact |
| `mart_acquisition_attribution` | Attribution analysis (first-touch, last-touch, multi-touch) |
| `mart_funnel_dropoff` | Multi-step funnel analysis |
| `mart_user_cohort` | User-cohort retention analysis |

## Common gotchas

1. **Sampling on the Data API for high-volume properties** — over a certain event volume, GA4 samples results. The BigQuery export is unsampled.
2. **Late-arriving events** — events can arrive hours late; daily reports should refresh on a 2-day-back window to capture this
3. **Custom dimensions / metrics** — must be defined in GA4 before they're queryable; check the property config
4. **`(direct) / (none)` vs `(not set)`** — Google's traffic-source classification has edge cases worth understanding for attribution
5. **Privacy controls (Consent Mode v2)** — when consent is denied, GA4 sends modeled (anonymized) hits instead of raw. Attribution + cohort analysis must account for this.
6. **BigQuery export vs Data API discrepancy** — Data API applies session/conversion logic on top of events; BigQuery export is raw. Numbers won't exactly match.
7. **Looker Studio is free but slow** — the native GA4-Looker-Studio connector is fine for ad-hoc but slow for embedded production dashboards
8. **GA4 has no `transactionId`-style join key** by default — link to e-com analytics via `purchase` event's custom params or via Enhanced Measurement

## PII / PHI considerations

- **`user_pseudo_id` is pseudonymous** — not direct PII, but combined with other data can be re-identifying
- **IP addresses are anonymized by GA4 by default** — verify the property's IP-anonymization setting
- **Consent Mode v2** — required for EEA traffic since March 2024; the warehouse must honor consent state
- **CCPA / GDPR** — user-deletion requests must propagate from GA4 to the warehouse

## Recommended sync configuration

- **Path:** native BigQuery export when destination is BigQuery
- **Cadence (BigQuery export):** daily for analytics; streaming for real-time
- **Cadence (Data API):** daily; 2-day lookback window for late-arriving events
- **Backfill (BigQuery):** export only goes forward; pre-export history requires CSV download
- **Backfill (Data API):** GA4 Data API supports historical queries

## Refresh triggers

- Google changes the GA4 BigQuery export schema
- Google ships GA4 successor (rumored but not announced)
- Consent Mode v3 (or similar) lands
- New custom events / parameters added to the engagement
- Looker Studio is replaced as the default Google-side BI tool
