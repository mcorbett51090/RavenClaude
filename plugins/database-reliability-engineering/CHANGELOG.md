# Changelog — database-reliability-engineering

All notable changes to this plugin are documented here. Versioning is semver, bumped
on every user-visible change and mirrored in `.claude-plugin/marketplace.json`.

## 0.1.0 — 2026-07-15

Initial release. The Database Reliability Engineering (DBRE) team — owns *the
production database as a reliability surface* (available, recoverable, changeable
without downtime), the layer `database-engineering` (schema/query design) did not.

- **3 agents:** `dbre-architect` (HA topology / backup-PITR / DR / capacity /
  pooling), `database-operations-engineer` (zero-downtime migrations / backfills /
  failover & restore drills / upgrades), `database-incident-responder` (live
  incident triage & mitigation / DB SLOs / postmortems).
- **4 skills:** ha-topology-and-failover, zero-downtime-migration,
  backup-and-restore-verification, db-incident-triage.
- **Knowledge bank (2 docs):** four Mermaid decision trees (HA topology / backup
  strategy / migration safety / incident triage) and a dated 2026 reference.
- **5 best-practices** and **2 templates** (HA & failover runbook, migration safety
  checklist).
- Seams: `database-engineering`, `observability-sre`, `terraform-iac` / cloud
  plugins, `data-orchestration`, `security-engineering` / `auth-identity`,
  `incident-response-dfir`. Requires `ravenclaude-core@>=0.7.0`.
