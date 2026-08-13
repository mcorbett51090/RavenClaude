# Best-practices — database-reliability-engineering

Short, enforceable house opinions the agents apply on every engagement. Each file
is one practice: a **Do**, a **Don't**, and a **Flag** (what to surface when you
see the anti-pattern). They operationalize the cross-cutting opinions in
[`../CLAUDE.md`](../CLAUDE.md) §4.

| Practice | One-line |
| --- | --- |
| [a-backup-is-unverified-until-restored](a-backup-is-unverified-until-restored.md) | Schedule restore tests; a green backup job is not a proven recovery. |
| [migrations-are-expand-then-contract](migrations-are-expand-then-contract.md) | Additive, reversible, batched steps — never a destructive one-shot on a hot table. |
| [replication-lag-is-a-first-class-metric](replication-lag-is-a-first-class-metric.md) | Monitor lag as an SLI; pace backfills against it; don't promote a lagging replica blind. |
| [rpo-rto-drive-the-topology](rpo-rto-drive-the-topology.md) | Derive the architecture from stated RPO/RTO; name the cost of each guarantee. |
| [practice-failover-before-you-need-it](practice-failover-before-you-need-it.md) | Drill failover/restore as game-days; measure the real RTO. |
