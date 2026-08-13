# DBRE decision trees

Four Mermaid decision trees the agents traverse. Each ends at a leaf you can act
on; **record the path and the runner-up** when you use one. These encode *durable*
reliability craft — the tradeoffs move slowly. Volatile facts (engine HA feature
matrices, managed-service SLAs, tool flags) live in
[`dbre-2026-reference.md`](dbre-2026-reference.md), retrieval-dated.

Two definitions used throughout:
- **RPO (Recovery Point Objective):** how much data you can afford to lose (drives
  *backup/replication cadence*).
- **RTO (Recovery Time Objective):** how long you can be down (drives *topology and
  restore approach*).

---

## §1 — HA topology selection

Start from the availability target, not from a favorite architecture.

```mermaid
flowchart TD
    A[State RTO + RPO + budget] --> B{RTO measured in<br/>seconds/minutes, or hours?}
    B -- Hours OK --> C{RPO tolerate minutes<br/>of data loss?}
    C -- Yes --> D[Single primary + async replica<br/>+ tested restore. Manual failover.]
    C -- No / near-zero --> E[Primary + SYNC replica<br/>so no acknowledged write is lost]
    B -- Seconds/minutes --> F{Can you tolerate an<br/>AZ outage taking you down?}
    F -- Yes --> G[Multi-replica, single-AZ,<br/>automatic failover + split-brain guard]
    F -- No --> H{Need to survive a<br/>REGION outage too?}
    H -- No --> I[Multi-AZ: sync/quorum replicas across AZs,<br/>automatic failover, fencing]
    H -- Yes --> J[Multi-region: async cross-region replica<br/>or quorum; accept higher write latency<br/>or bounded cross-region RPO]
    G --> K[Specify: promotion mechanism,<br/>split-brain guard, who/what triggers]
    I --> K
    J --> K
    E --> K
```

Rules: a replica in the **same failure domain** as the primary is not HA. Design
the **failover mechanism** (promotion + split-brain guard: fencing / quorum /
STONITH), not just the replica. Synchronous replication protects RPO but costs
write latency — choose it deliberately.

---

## §2 — Backup & recovery strategy

A backup exists to be *restored*. Design backward from RTO/RPO.

```mermaid
flowchart TD
    A[RPO + RTO + data size] --> B{RPO?}
    B -- Near-zero --> C[Continuous archiving:<br/>base backup + WAL/binlog streaming<br/>-> PITR to any moment]
    B -- Minutes/hours --> D[Periodic full + incremental,<br/>WAL/binlog for point-in-time]
    C --> E{RTO?}
    D --> E
    E -- Tight --> F[Keep a warm standby / fast-restore path;<br/>test restore time vs RTO]
    E -- Relaxed --> G[Restore-from-storage acceptable;<br/>still measure actual restore time]
    F --> H[Store backups in a DIFFERENT<br/>failure domain + encrypted]
    G --> H
    H --> I[Set retention + immutability<br/>ransomware/delete protection]
    I --> J[SCHEDULE restore-verification:<br/>a backup is unverified until restored]
```

Rule: **a backup is unverified until a restore is tested.** Untested backups fail
exactly when you need them. Bake a restore-verification cadence in, measure real
restore time against RTO, and keep backups in a separate, immutable, encrypted
location.

---

## §3 — Schema-migration safety (zero-downtime)

Default to **expand-contract**. Never a destructive change in one step.

```mermaid
flowchart TD
    A[Schema change needed] --> B{Is it purely additive?<br/>new nullable column / new table / new index}
    B -- Yes --> C{Index on a hot table?}
    C -- Yes --> D[Build the index CONCURRENTLY / online<br/>to avoid a long lock]
    C -- No --> E[Apply directly - low risk, still off-peak]
    B -- No --> F[EXPAND-CONTRACT:]
    F --> G[1. EXPAND: add the new shape, additive + reversible]
    G --> H[2. Dual-write app to old + new]
    H --> I[3. BACKFILL: batched, throttled, idempotent,<br/>paced against replication lag]
    I --> J[4. CUTOVER reads to the new shape]
    J --> K[5. CONTRACT: drop the old shape<br/>once nothing reads it]
    D --> L{Lock duration acceptable<br/>under production load?}
    E --> L
    K --> L
    L -- No --> M[Re-plan: smaller steps / online tool /<br/>maintenance window as last resort]
    L -- Yes --> N[Ship, with rollback for each step]
```

Rules: watch **lock duration** — a brief ACCESS EXCLUSIVE lock on a hot table is an
outage. Backfills are **batched, throttled, idempotent, resumable**, never one big
`UPDATE`. Each step is individually reversible.

---

## §4 — Incident triage

Classify first, then reach for the failure-mode diagnostic. Stabilize before full
root-cause.

```mermaid
flowchart TD
    A[DB incident] --> B{Latency, errors,<br/>or saturation?}
    B -- Errors --> C{Connection errors?}
    C -- Yes --> D[CONNECTION STORM: check active/idle<br/>connections vs max; find source; throttle/pool-limit]
    C -- No --> E[Disk-full / read-only?<br/>check free space, WAL/binlog growth]
    B -- Latency --> F{Queries blocked?}
    F -- Yes --> G[LOCK CONTENTION: inspect blocking/blocked;<br/>kill the blocker least-blast-radius first]
    F -- No --> H{One bad query, or broad?}
    H -- One --> I[RUNAWAY QUERY: bad plan / missing index<br/>under load; kill + fix plan]
    H -- Broad --> J[Saturation: CPU/IOPS/memory;<br/>shed load, throttle, scale]
    B -- Saturation --> J
    A --> K{Reads stale / replica down?}
    K -- Yes --> L[REPLICATION LAG/BREAK: check status,<br/>lag seconds, apply/network; reroute reads]
    D --> Z[Stabilize -> mitigate reversibly -><br/>then postmortem]
    E --> Z
    G --> Z
    I --> Z
    J --> Z
    L --> Z
```

Rule: **least blast radius first** — kill one query before restarting the instance;
throttle one source before failing over. Every failure mode has a diagnostic
view/query — look before you act. After the bleeding stops, blameless postmortem
with contributing factors, not a single root cause.
