# Stack decision record — {{Engagement / Client Name}}

> Engagement-start decision record. Fill this in BEFORE database / ELT / dashboard / embed-pattern choices are locked.
> Produced by the `stack-selection` skill invoked by `ravenclaude-core/architect`.
>
> **Last updated:** {{YYYY-MM-DD}}
> **Engagement Case:** A | B | C | D | mixed

---

## 1. Engagement context

- **Client / engagement name:** {{...}}
- **Target user(s) of the dashboard:** {{the consultant's own marketing site / one client's internal users / multiple client tenants in a productized SaaS / client's BI tool — data pipes only}}
- **Estimated viewer count:** {{1-5 / 5-50 / 50-500 / 500+}}
- **Engagement length:** {{one-off / multi-month / ongoing retainer}}
- **Post-engagement ownership:** {{client takes over the infra / consultant hosts indefinitely / hybrid}}

## 2. Case match

**Case A — Portfolio dashboard on consultant's own marketing site**
- [ ] Yes (default Evidence.dev OSS → static deploy)

**Case B — Per-client deliverable inside the client's app**
- [ ] Yes (default Apache Superset OR Metabase OSS self-hosted + JWT embed; Power BI Embedded F2 alt for Microsoft-stack)

**Case C — Long-bet productized SaaS**
- [ ] Yes (default Cube OSS + Next.js + Tremor + Recharts + Postgres RLS)

**Case D — Client has BI tool; scope is data pipes only**
- [ ] Yes (default Airbyte + Supabase or client-cloud Postgres + dbt; no dashboard work)

**Rationale for the Case match:** {{1-2 sentences}}

## 3. Client tech-stack context

- **Cloud preference:** {{AWS / Azure / GCP / on-prem / Supabase-style managed / agnostic}}
- **Microsoft-stack indicators:** {{Dynamics 365 / Power BI / Power Platform / Teams / M365 — yes/no}}
- **Existing data warehouse:** {{Snowflake / Databricks / BigQuery / Postgres / none}}
- **Existing BI tool:** {{Power BI / Tableau / Looker Studio / Looker / Metabase / Superset / Sigma / none}}

## 4. Compliance constraints

- [ ] HIPAA (requires BAA-signing vendor; Supabase Team / Neon Scale)
- [ ] SOC 2 Type 2 (most managed vendors offer)
- [ ] GDPR (EU data residency)
- [ ] State student-privacy law (NY Ed Law 2-d / IL SOPPA / CA SOPIPA / etc. — applies if EdTech vertical)
- [ ] PCI-DSS (rare for SMB consulting; vendor must be in scope)
- [ ] None of the above

## 5. Source systems in scope

- [ ] QuickBooks Online (rate-limit-aware connector required)
- [ ] QuickBooks Desktop (deferred to v0.2.0 of data-platform plugin; flag as out-of-scope OR plan workaround)
- [ ] Stripe (batch ELT + webhook hybrid)
- [ ] Salesforce (Bulk API 2.0 standard)
- [ ] HubSpot (rate-limit-aware — 110/10s OAuth)
- [ ] Google Analytics 4 (native BigQuery export FREE — recommended path if destination is BQ)
- [ ] Shopify (GraphQL Admin API required for new apps as of April 2025)
- [ ] HRIS (Workday / BambooHR / ADP — see ipaas-connector-landscape-2026.md)
- [ ] EdTech LMS (Canvas / Moodle / Schoology — custom Airbyte connector required; see edtech-lms-connector-gap.md)
- [ ] Other: {{...}}

## 6. Stack picks

### Database
- **Selected:** {{Supabase Pro / Neon Scale / Fabric F2 reserved / RDS / Snowflake / etc.}}
- **Rationale:** {{1-2 sentences. If not Supabase Pro / Fabric F2 default, document why.}}
- **Pricing:** {{$X/mo as of YYYY-MM-DD per vendor.com/pricing}}

### ELT / connectors
- **Selected:** {{Airbyte Cloud Standard / Airbyte self-hosted / Fivetran free / n8n / data sharing / custom Airbyte}}
- **Rationale:** {{1-2 sentences}}
- **Cost predictability flag:** {{e.g., "Fivetran proposed on Salesforce — 2026 deletes-count change risk surfaced to client"}}

### Modeling layer
- **dbt Core:** {{yes / no — should be yes for any non-trivial engagement}}
- **Marts planned:** {{list 3-5 high-value marts}}

### Dashboard framework
- **Selected:** {{Evidence OSS / Apache Superset / Metabase OSS / Cube + custom React / Power BI Embedded F2 / Looker Studio}}
- **Rationale:** {{1-2 sentences. If per-viewer-priced tool selected, explain the math and why it works for this engagement.}}

### Embed + auth pattern (Case B / C only)
- **JWT issuance:** {{HS256 shared-secret / RS256 JWKS}}
- **Tenant scoping:** {{Postgres RLS / Cube securityContext / DAX role / single-tenant — no scoping}}
- **CSP `frame-ancestors`:** {{explicit allowlist for host app's domain}}
- **Cross-boundary denial test:** {{pass / not-yet-written / n/a (single-tenant)}}

## 7. Per-viewer-pricing-trap check

If any of the following were selected, document the math:

- [ ] Looker — viewer cost ~$400/yr × {{viewer count}} = $...
- [ ] Tableau Embedded — viewer cost ~$420/yr × {{viewer count}} = $...
- [ ] Sigma — median $61k deployment (Vendr)
- [ ] Metabase Pro — $144/viewer/yr + $575/mo base = ...

If none → confirm: {{"per-viewer-priced tools resisted by default per house opinion #2"}}

## 8. Cross-plugin handoffs identified

- [ ] `ravenclaude-core/architect` — owns this skill's invocation
- [ ] `ravenclaude-core/security-reviewer` — invoked for JWT / RLS / embed CSP review
- [ ] `power-platform/power-bi-engineer` — Power BI semantic-model / DAX / PBIP work
- [ ] `web-design/frontend-coder` — integration into host marketing site
- [ ] `edtech-partner-success` — partner-success motion above the data layer (if EdTech vertical)

## 9. Risks and open questions

- {{Risk 1: ...}}
- {{Open question 1: ...}}
- {{Pricing-claim verification not-yet-done: ...}}

## 10. Acceptance criteria for the build phase

- [ ] Database schema applied; cross-boundary denial test passing in CI
- [ ] ELT pipeline running; data-handoff plan documented
- [ ] Dashboard scaffold deployed in dev; JWT-issuance flow validated by `ravenclaude-core/security-reviewer`
- [ ] Pricing claims in client-facing materials verified within last 30 days
- [ ] Cross-plugin handoff routes documented (if more than one plugin's agents are needed)

---

**Refresh triggers for this decision record:**
- Engagement scope materially changes
- Client pivots cloud / BI tool
- Compliance scope changes
- Source system added or removed
- Quarterly review of pricing claims

---

*This template was generated by `data-platform/skills/stack-selection/SKILL.md`. Re-run the skill if any of the above changes.*
