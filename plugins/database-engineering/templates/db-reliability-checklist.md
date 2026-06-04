# Database reliability checklist

- [ ] Connection pooler in front, limits sized to workload
- [ ] Isolation level chosen per transaction; anomalies handled
- [ ] Transactions short; no long-running locks
- [ ] Read replicas: read-after-write routed correctly
- [ ] Backups automated AND restore tested; PITR if RPO needs it
- [ ] Autovacuum tuned; bloat / long-txn / replica-lag monitored
- [ ] DB metrics fed to observability-sre
