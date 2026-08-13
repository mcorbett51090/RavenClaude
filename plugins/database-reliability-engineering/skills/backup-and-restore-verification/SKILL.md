---
name: backup-and-restore-verification
description: "Design a backup + point-in-time-recovery strategy from RPO/RTO and — critically — the restore-verification that proves it works: cadence, retention, failure-domain isolation, and a scheduled test restore measuring actual restore time. Reach for this when backups are unproven, when setting RPO/RTO, after a near-miss, or before relying on recovery. Pairs with ha-topology-and-failover."
---

# Skill: Backup & restore verification

A backup exists to be **restored**. This skill designs the backup *and* the proof
it works — because an untested backup is a guess.

## Step 0 — One opinion up front
**A backup is unverified until a restore is tested.** The most common backup failure
is discovering, mid-disaster, that the backups were never restorable. Verification
is not optional — it's the point.

## Step 1 — Derive from RPO/RTO
Trace [`../../knowledge/dbre-decision-trees.md`](../../knowledge/dbre-decision-trees.md) §2:
- **RPO** sets the cadence: near-zero → continuous archiving (base + WAL/binlog) for
  PITR; minutes/hours → periodic full + incremental.
- **RTO** sets the restore approach: tight → warm standby / fast-restore path;
  relaxed → restore-from-storage (still measured).

## Step 2 — Isolate and protect
- Store backups in a **different failure domain** from the primary (a backup on the
  same disk/AZ dies with it).
- **Encrypt** at rest; set **retention**; make them **immutable** (protection against
  accidental delete and ransomware).

## Step 3 — Schedule restore verification
This is the step teams skip. On a schedule:
1. Restore the backup to an **isolated** instance.
2. **Validate**: row counts / checksums / a smoke query against known values.
3. **Measure** actual restore time; compare to RTO.
4. **Alert** if verification is stale or fails.

## Step 4 — Rehearse the full DR path
Periodically restore-and-promote as a game-day, not just a file restore — the real
RTO includes app reconnection and validation, not just bytes on disk.

## Step 5 — Hand off
- The **HA topology** that complements backups → `ha-topology-and-failover`.
- **Storage/infra** provisioning → `terraform-iac` / cloud plugins.
- **Security incident** (ransomware, exfiltration) → `incident-response-dfir`.

## Output
A backup/PITR strategy (cadence, retention, isolation, encryption, immutability)
plus a restore-verification procedure with a schedule, validation checks, a measured
restore time vs RTO, and staleness alerting.
