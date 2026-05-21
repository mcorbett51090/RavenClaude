# HRIS integration (Workday, BambooHR, ADP, Rippling, others)

> **Last reviewed:** 2026-05-21. Sources: Workday developer docs, BambooHR API docs, ADP / Flexspring / Merge.dev documentation. Refresh when: (a) Workday changes its API contract (rare but possible), (b) Merge.dev / Flexspring change their unified HRIS API, or (c) a major HRIS vendor's market share shifts meaningfully.

## The HRIS landscape

HRIS = Human Resources Information System. The vendors break into tiers:

| Tier | Vendors | Typical client size |
|---|---|---|
| **Enterprise** | Workday HCM, SAP SuccessFactors, Oracle HCM | 1,000+ employees |
| **Mid-market** | UKG (formerly Kronos), Ceridian Dayforce, Paylocity | 200-2,000 employees |
| **SMB** | BambooHR, Gusto, Rippling, Justworks, Zenefits | 50-500 employees |
| **Payroll-focused** | ADP, Paychex | Variable, often layered with above |

**For SMB consulting engagements** ($25-50k profile), the most common HRIS systems are: BambooHR, Rippling, Gusto, ADP. Enterprise (Workday) shows up when consultant is sub-contracted into a larger engagement.

## ELT connector coverage — the unified-API pattern

| Vendor | Direct Fivetran | Direct Airbyte | Merge.dev unified |
|---|---|---|---|
| Workday HCM | ✅ | (via custom) | ✅ |
| Workday Adaptive | ✅ | (no) | (no) |
| Workday Financial Management | ✅ | (no) | (no) |
| BambooHR | (no) | ✅ (source + destination) | ✅ |
| ADP Workforce Now | (no — Flexspring usually) | (no) | ✅ |
| Rippling | (no) | (no) | ✅ |
| Gusto | (no) | (no) | ✅ |
| UKG / Ceridian | (limited) | (no) | ✅ |

**Pattern:** for anything other than Workday, **Merge.dev's unified HRIS API is often the most efficient path** — one connector, one auth flow, normalized schema across providers. Trade-off: less granular access to vendor-specific fields.

## Workday HCM (the enterprise case)

### Auth
- **Workday Integration System User (ISU)** — service account with appropriate domain permissions
- Auth via WS-Security username/password or OAuth (depending on Workday version)
- Long-lived credentials; rotate via Workday Admin

### Common entities
| Entity | Use case |
|---|---|
| `Worker` | Employee dimension |
| `Position` | Position dimension (open + filled positions) |
| `Job_Profile` | Job role dimension |
| `Organization` | Org structure (cost centers, departments) |
| `Compensation` | Comp facts (base salary, bonus, equity) — sensitive |
| `Time_Off` | PTO + leave facts |
| `Performance_Review` | Performance facts |
| `Talent` | Performance + potential ratings |

### Fivetran Workday connectors
Fivetran ships separate connectors for Workday HCM, Workday Adaptive Planning, Workday Financial Management, Workday Strategic Sourcing, Workday RaaS (Report-as-a-Service). Each requires its own ISU + permission set.

### Rate limits
Workday rate limits are tenant-configurable; common defaults are not aggressively low for ELT. Bulk extraction via RaaS Custom Reports is the standard pattern for high-volume tenants.

## BambooHR (the SMB case)

### Auth
- **API key per company subdomain** — Settings → Integrations → API Keys
- Long-lived; rotate periodically

### Common entities
| Entity | Use case |
|---|---|
| `employees` | Employee dimension |
| `time_off_requests` | PTO requests |
| `employment_history` | Position history |
| `compensation_history` | Comp history (sensitive) |
| `job_history` | Job-title history |
| `directory` | Lightweight employee directory |

### Rate limits
- Standard tier: limited; check current docs
- Enterprise: higher

## ADP Workforce Now (the payroll-focused case)

### Auth + access pattern
**ADP doesn't ship a first-class direct ELT connector for most vendors.** The standard paths:

1. **Flexspring** — API-to-API connector specialist; common ADP integration vendor
2. **Merge.dev** — unified HRIS API includes ADP
3. **Custom Airbyte connector** — when neither Flexspring nor Merge.dev fits

### Common entities (via Flexspring or Merge.dev abstraction)
- Workers
- Pay Statements (sensitive)
- Time Records
- Tax records (highly sensitive)
- Benefit elections

## Rippling / Gusto / Justworks (modern SMB platforms)

Each has a documented REST API; most ELT vendors don't ship direct connectors. **Merge.dev unified HRIS API** is the canonical path:

- One connector, normalized schema
- Vendor-specific fields exposed via passthrough
- SOC 2 / HIPAA / GDPR compliance at the Merge.dev layer

## Incremental sync

- **Workday:** typically delta extracts via RaaS — defined as "changes since last run"
- **BambooHR:** `last_updated` field on most objects
- **Merge.dev:** unified API surfaces `modified_at` on every object

## dbt modeling — common marts

| Mart | Purpose |
|---|---|
| `dim_employee` | Employee dimension unified across HRIS |
| `dim_position` | Position dimension |
| `dim_department` / `dim_cost_center` | Org-structure dimension |
| `fact_compensation_history` | Comp facts (slowly-changing dimension Type 2) |
| `fact_time_off` | PTO + leave facts |
| `fact_headcount_snapshot` | Headcount-by-date fact |
| `fact_attrition` | Termination + reason analysis |
| `mart_compensation_equity` | Comp-equity analysis |
| `mart_attrition_cohort` | Attrition-by-cohort analysis |
| `mart_headcount_planning` | Plan-vs-actual headcount |

## Common gotchas

1. **PII / PHI everywhere** — HRIS data is heavily regulated. Route through `ravenclaude-core/security-reviewer` mandatory.
2. **Compensation data is the most sensitive** — many engagements scope it out entirely
3. **Termination reasons are sensitive** — voluntary vs involuntary may have different visibility
4. **Multi-country payroll** — different fields, different currencies, different tax shapes
5. **Slowly-changing dimensions** — employees change titles, departments, comp bands — Type 2 SCD discipline required
6. **Org structure changes** — re-orgs invalidate historical cost-center analysis if not modeled properly
7. **Date precision** — Workday tracks "hire date" and "rehire date" separately; BambooHR has different conventions
8. **Workers vs employees** — contractors, contingent workers, agency workers all show up in Workday/HRIS but may have different analytics treatment

## PII / PHI considerations

- **HRIS data is heavily PII/PHI scoped** — SSN, DOB, home address, salary, performance ratings, medical leave details
- **GDPR Article 88** — EU Member States can set additional rules for employee data; works-council restrictions are real in many countries
- **U.S. state privacy laws** (CCPA, VCDPA, CPA) increasingly apply to employee data
- **OFCCP / EEOC** — federal contractors have additional record-retention requirements
- **Mandatory security-reviewer route** — for any HRIS engagement, the security review is non-negotiable

## Recommended sync configuration

- **Default vendor for non-Workday HRIS:** Merge.dev unified API (one connector, normalized schema)
- **Workday:** Fivetran direct connector
- **Cadence:** daily for analytics; rarely real-time
- **Backfill:** as much history as the HRIS retains (compensation history, employment history)
- **Encryption:** field-level encryption for compensation, SSN, DOB columns in the warehouse

## Refresh triggers

- Workday changes API contract (rare)
- Merge.dev or Flexspring restructure pricing
- New HRIS becomes dominant in client base (none signaled as of 2026-05)
- GDPR Article 88 enforcement in EU changes posture
- Engagement extends into payroll (different sensitivity tier)
- US federal privacy law (long-discussed) lands and changes employee-data treatment
