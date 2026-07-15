# database-reliability-engineering

> A RavenClaude plugin: the Database Reliability Engineering (DBRE) team — the agents
> that own **the production database as a reliability surface**: available,
> recoverable, and changeable without downtime.

## What it is

A 3-agent team for production database reliability. It designs the HA topology and
backup/PITR strategy from RPO/RTO, executes zero-downtime migrations and
failover/restore drills, and runs DB on-call (incident triage, mitigation, SLOs,
postmortems) — then hands the *schema* to `database-engineering`, the *service SLO*
to `observability-sre`, and the *infra* to `terraform-iac` / the cloud plugins.

It is **advisory and educational**, and treats irreversible operations (failover,
destructive migration steps, retention changes) as requiring confirmation.

## Why it exists (the gap it fills)

`database-engineering` owns the *design* of the database (schema, indexes, query
plans). Nothing owned the *reliability* of the running database:

| Question | Owner |
| --- | --- |
| Schema / indexes / query plans / data model | `database-engineering` |
| App service SLOs, alerting, incident command | `observability-sre` |
| Infra provisioning (instances, networking, storage) | `terraform-iac`, cloud plugins |
| **Availability, recovery, and zero-downtime change of the production DB** | **this plugin** |

## Roster

| Agent | Owns |
| --- | --- |
| **`dbre-architect`** | HA topology, backup/PITR strategy from RPO/RTO, DR, capacity planning, connection-pool architecture, managed-vs-self-hosted. |
| **`database-operations-engineer`** | Zero-downtime / expand-contract migrations, backfills, replication & failover drills, restore verification, upgrades, maintenance. |
| **`database-incident-responder`** | Live incident triage & mitigation, DB SLOs/error budgets, blameless postmortems. |

## What's inside

- **4 skills** — `ha-topology-and-failover`, `zero-downtime-migration`, `backup-and-restore-verification`, `db-incident-triage`.
- **Knowledge bank (2 docs)** — four Mermaid decision trees (HA topology / backup strategy / migration safety / incident triage) and a dated 2026 reference (HA by engine family, managed-service features, backup mechanisms, migration tooling, pooling, SLIs).
- **5 best-practices** — a-backup-is-unverified-until-restored, migrations-are-expand-then-contract, replication-lag-is-a-first-class-metric, rpo-rto-drive-the-topology, practice-failover-before-you-need-it.
- **2 templates** — HA & failover runbook, migration safety checklist.

## Install

```shell
/plugin marketplace update ravenclaude
/plugin install database-reliability-engineering@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0` (inherits the Team Lead, the Capability Grounding
and Structured Output protocols, and the security/review seams).

## Seams

`database-engineering` (schema/query design) · `observability-sre` (service SLOs) ·
`terraform-iac` / `aws-cloud` / `gcp-cloud` / `azure-cloud` (provisioning) ·
`data-orchestration` (pipelines) · `security-engineering` / `auth-identity`
(access/security) · `incident-response-dfir` (DB security incidents).

This plugin owns **the availability, recoverability, and safe changeability of the
production database.** The schema, the service SLO, and the infra belong to someone else.
