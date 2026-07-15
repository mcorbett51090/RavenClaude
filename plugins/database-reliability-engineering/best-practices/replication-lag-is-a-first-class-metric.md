# Replication lag is a first-class metric

A read replica that is silently minutes behind is worse than no replica: it serves
stale data as if it were fresh, and it can't be promoted cleanly in a failover
without data loss beyond your RPO. Replication lag is not a background curiosity —
it's a reliability SLI that gates reads, failovers, and migrations.

**Do:** monitor lag in seconds-behind as a named SLI with alert thresholds; gate
read-routing on freshness where correctness needs it; and **pace every backfill and
bulk write against lag** — if lag climbs, slow down.

**Don't:** assume a replica is caught up because it exists, or route
read-your-own-writes traffic to an async replica without a freshness guarantee.

**Flag:** a replica with no lag monitoring, a backfill/bulk job that ignores lag, or
a failover plan that promotes a lagging replica without measuring the data-loss
window against RPO.
