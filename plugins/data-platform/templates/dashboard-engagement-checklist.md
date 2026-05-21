# Dashboard engagement checklist — {{Engagement / Client Name}}

> New-engagement checklist for a data-platform deliverable. Use alongside [`stack-decision-record.md`](stack-decision-record.md).
>
> **Last updated:** {{YYYY-MM-DD}}

---

## Phase 1 — Discovery (Week 1)

- [ ] Stack-selection skill run; `stack-decision-record.md` populated and signed off by client
- [ ] Client tech-stack confirmed (cloud, existing BI tool, data warehouse, compliance scope)
- [ ] Source-system inventory: every data source the dashboard depends on, with auth credentials path defined
- [ ] Viewer count + access model defined (single-tenant? multi-tenant? embed vs standalone?)
- [ ] Compliance constraints documented (HIPAA / SOC 2 / GDPR / state-privacy / none)
- [ ] Post-engagement ownership plan: who hosts, who maintains, when does the handoff happen
- [ ] Pricing claims in the SOW verified against vendor pages within last 30 days

## Phase 2 — Infrastructure setup (Week 2)

### Database
- [ ] Database provisioned (Supabase / Neon / Fabric / RDS / etc.)
- [ ] Connection-string scaffold committed (env-var convention, dev/staging/prod separation)
- [ ] Multi-tenant schema starter applied (if Case B multi-tenant or Case C)
- [ ] RLS policies applied with `FORCE ROW LEVEL SECURITY`
- [ ] `tenant_id` index added to all fact tables
- [ ] `rls-cross-tenant-test.sql` passing in CI

### ELT / connectors
- [ ] ELT tool selected and provisioned (Airbyte / Fivetran / n8n / data sharing)
- [ ] Each source connector configured with rate-limit-aware retry
- [ ] OAuth tokens rotating proactively (no API-401 reactive refresh)
- [ ] Initial historical backfill complete
- [ ] Ongoing sync cadence defined and scheduled
- [ ] Data-handoff plan documented (what changes at engagement end)

### Modeling
- [ ] dbt project initialized
- [ ] Base / staging / intermediate / marts layers structured
- [ ] Initial mart set deployed (3-5 high-value marts per the decision record)

## Phase 3 — Dashboard build (Weeks 3-5)

### Front-end framework
- [ ] Dashboard framework deployed (Evidence / Superset / Metabase / Cube + Next.js / Power BI)
- [ ] Auth integration tested
- [ ] Visual design aligned with host site (route to `web-design/visual-designer` if installed)
- [ ] Responsive layouts verified (desktop, tablet, mobile)
- [ ] Accessibility audit (WCAG 2.1 AA basics — keyboard nav, contrast, alt text)

### Embed + auth (Case B / C only)
- [ ] JWT issuer scaffolded with `tenant_id` claim from session
- [ ] Expiration set to 5-15 min
- [ ] `JWT_SIGNING_KEY` in env vars (NEVER inline — the hook catches inline)
- [ ] Smoke test: JWT round-trip works
- [ ] CSP `frame-ancestors` configured for host app's domain
- [ ] iframe `sandbox` attributes set (start with `allow-scripts allow-same-origin`)
- [ ] `postMessage` origin checks in place (both directions)
- [ ] `ravenclaude-core/security-reviewer` invoked; review pass

### Content
- [ ] KPI cards / charts authored per partner-stated goals
- [ ] Every chart has source query + date range + comparison baseline accessible
- [ ] No raw SQL endpoints customer-facing (pre-aggregate in semantic layer)
- [ ] Provenance discipline: every metric carries its source

## Phase 4 — Validation + UAT (Week 6)

- [ ] Cross-boundary denial test passing in CI (mandatory, no exceptions)
- [ ] Performance acceptable (page load < 3s; chart interactions < 200ms warm cache)
- [ ] All pricing claims in client-facing materials re-verified
- [ ] Client UAT signoff on at least 3 representative dashboard pages
- [ ] Edge cases tested (empty data, missing tenant, expired JWT, multi-tenant boundary)
- [ ] `ravenclaude-core/security-reviewer` final review pass

## Phase 5 — Handoff (Week 7)

- [ ] Runbook documented: ops procedures, refresh schedule, escalation contacts
- [ ] Connection-string + secrets rotation plan handed to client (if client takes over)
- [ ] dbt project committed to client's git or maintained-fork strategy documented
- [ ] Pricing-refresh calendar set (quarterly minimum)
- [ ] Cross-plugin handoff (if applicable): `edtech-partner-success` for renewal/QBR motion, `power-platform/power-bi-engineer` for ongoing Power BI work
- [ ] Final client invoice issued
- [ ] Engagement archived in partner-profile if relevant (route to `edtech-partner-success/partner-profile-curator` if EdTech)

## Phase 6 — Post-launch (Weeks 8+)

- [ ] First-month usage check: are viewers actually using the dashboard?
- [ ] Performance check: any unexpected query patterns?
- [ ] Cost check: are connector / capacity / dashboard costs matching the engagement's estimates?
- [ ] Renewal-quote prep (60-90 days before contract end if recurring relationship)

---

## Cross-plugin coordination notes

- If engagement uses Power BI Embedded → coordinate with `power-platform/power-bi-engineer` on DAX/PBIP/semantic-model decisions
- If engagement is EdTech vertical → coordinate with `edtech-partner-success` on data → partner-success-motion handoff
- If embedding into ravenpower.net or client marketing site → coordinate with `web-design` on visual integration

---

*Refresh triggers for this checklist:* engagement methodology evolves, new ELT/dashboard tools enter the stack, compliance posture changes, or a post-mortem identifies a missing checkpoint.
