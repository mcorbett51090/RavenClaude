# HA & failover runbook — `<database / service>`

> Output of `dbre-architect` + `database-operations-engineer`. The living document
> for how this database stays available and how it fails over. Keep in version
> control; review after every drill and every incident.

## 1. Reliability targets
- **RTO:** `<how long can we be down>`
- **RPO:** `<how much data can we lose>`
- **Failure domains we must survive:** `<node | AZ | region>`

## 2. Topology
- **Engine + version:** `<…>` — *verify HA features against this version, dated*
- **Primary:** `<location / failure domain>`
- **Replicas:** `<count, sync/async/quorum, domains>`
- **Topology tree path taken (§1) + runner-up:** `<…>`
- **Connection pooling:** `<where it lives, mode, sizing vs DB ceiling>`

## 3. Failover mechanism
- **Promotion:** `<orchestrator / managed control plane>`
- **Split-brain guard:** `<fencing / quorum / STONITH>`
- **Trigger + health signal:** `<who/what, on what signal>`
- **App reconnection:** `<DNS / proxy / service discovery>`
- **Expected failover time (measured):** `<…>` vs RTO `<…>`

## 4. Failover procedure (step-by-step)
1. `<preconditions / confirm replica health + lag>`
2. `<promote>`
3. `<confirm split-brain guard fired>`
4. `<verify app reconnected + writes succeeding>`
5. `<measure data loss vs RPO>`
6. `<rollback / re-establish replication>`

## 5. Backups & PITR (cross-ref)
- **Strategy:** `<see backup-and-restore-verification>`
- **Last verified restore + measured time:** `<date, duration>`

## 6. Drill log
| Date | Type (failover/restore) | Real RTO measured | Findings | Actions |
| --- | --- | --- | --- | --- |
| `<…>` | `<…>` | `<…>` | `<…>` | `<…>` |

## Hand-offs
- [ ] Provisioning (IaC) → `terraform-iac` / cloud plugins
- [ ] Schema design → `database-engineering`
- [ ] Live incident → `database-incident-responder`
