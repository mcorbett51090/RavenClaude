---
name: ha-topology-and-failover
description: "Design a production database's high-availability topology from its RPO/RTO targets — replica type (sync/async/quorum), failure-domain spread (multi-AZ/region), and the failover mechanism with a split-brain guard. Reach for this when a DB needs to survive an AZ/region outage, when failover has never been designed, or when 'we have a replica' is mistaken for HA. Pairs with backup-and-restore-verification."
---

# Skill: HA topology & failover

Design availability from the **targets down**, and design the *failover*, not just
the replica.

## Step 0 — One opinion up front
**A replica is not HA; a tested failover is.** A standby you can't promote safely
under load is decoration. The deliverable is the promotion path + split-brain guard,
not the replica count.

## Step 1 — State the targets
Write down **RTO** (how long can we be down?), **RPO** (how much data can we lose?),
and the **failure domains** you must survive (node → AZ → region). No targets, no
design.

## Step 2 — Trace the topology tree
Traverse [`../../knowledge/dbre-decision-trees.md`](../../knowledge/dbre-decision-trees.md) §1
to a leaf. Record the path and the runner-up. Key forks: async vs sync (RPO vs write
latency), single-AZ vs multi-AZ vs multi-region (which outage you survive),
automatic vs manual failover (RTO vs complexity).

## Step 3 — Design the failover mechanism
Specify explicitly:
- **Promotion:** what promotes a replica (orchestrator / managed control plane).
- **Split-brain guard:** fencing / quorum / STONITH so two primaries can't both accept writes.
- **Trigger:** who or what initiates, and the health signal it uses.
- **App reconnection:** how clients discover the new primary (DNS, proxy, service discovery).

## Step 4 — Place across failure domains
Confirm primary, replicas, and backups live in *different* domains. A replica in the
primary's AZ doesn't survive an AZ outage.

## Step 5 — Prove it (game-day)
A topology is a hypothesis until failover is rehearsed. Hand the drill to
`database-operations-engineer` (the `ha-topology-and-failover` design pairs with an
operational failover drill).

## Step 6 — Hand off
- The **backup/PITR** that complements HA → `backup-and-restore-verification`.
- **Provisioning** the instances/replicas → `terraform-iac` / cloud plugins.
- The **schema** the topology carries → `database-engineering`.

## Output
An HA topology with the tree path + runner-up, RPO/RTO it meets, the failover
mechanism (promotion + split-brain guard + trigger + app reconnection), the
failure-domain placement, and a game-day plan to prove it.
