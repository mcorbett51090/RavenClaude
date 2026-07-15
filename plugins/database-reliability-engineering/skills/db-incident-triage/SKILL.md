---
name: db-incident-triage
description: "Triage and mitigate a live production database incident — classify latency vs errors vs saturation, rank the suspects (lock contention, replication lag, connection storm, runaway query, disk-full, failover), run the per-mode diagnostic, and apply the least-blast-radius reversible mitigation first. Reach for this when a DB is slow/erroring in prod now. Pairs with zero-downtime-migration when a change caused it."
---

# Skill: DB incident triage

Diagnose and stop a live database incident under time pressure — safely.
**Stabilize before you fully diagnose.**

## Step 0 — One opinion up front
**Least blast radius first.** Kill one query before restarting the instance;
throttle one source before failing over. Escalate drasticness only as needed, and
name what each step risks.

## Step 1 — Classify
Latency, errors, or saturation? Trace
[`../../knowledge/dbre-decision-trees.md`](../../knowledge/dbre-decision-trees.md) §4
from the symptom.

## Step 2 — Rank the suspects and run the diagnostic
For the likely mode, look *before* you act (every mode has a view/query):
- **Lock contention** → inspect blocking/blocked sessions; kill the blocker.
- **Replication lag/break** → check replica status + lag seconds; reroute reads,
  investigate apply/network.
- **Connection storm** → active/idle vs max connections; find the source; throttle /
  pool-limit.
- **Runaway query** → find the expensive plan; kill it; fix the plan/index.
- **Disk-full / read-only** → free space, WAL/binlog growth; reclaim, expand.
- **Failover event** → confirm which node is primary; verify no split-brain.

## Step 3 — Mitigate reversibly
Apply the safest action that stops customer harm. Confirm it helped (watch the SLI),
and confirm it didn't shift the problem elsewhere.

## Step 4 — Stabilize, then hunt
Once the bleeding stops, do the full diagnosis. Resist the urge to keep changing
things once the incident is contained.

## Step 5 — Postmortem
Blameless, timeline-first, **contributing factors** (not one root cause),
detection/mitigation gaps, and action items owned + dated. Separate the systemic fix
from the band-aid.

## Step 6 — Hand off
- An **architecture gap** the incident exposed → `dbre-architect`.
- The **durable fix as planned change** → `database-operations-engineer` /
  `zero-downtime-migration`.
- **App-layer cause** (bad deploy, N+1, retry storm) → `backend-engineering`.
- **Security incident** → `incident-response-dfir` / `security-engineering`.

## Output
A triage path (classification → ranked suspects → per-mode diagnostic), the
least-blast-radius mitigation applied with its risk named, confirmation via the SLI,
and a blameless postmortem with owned action items.
