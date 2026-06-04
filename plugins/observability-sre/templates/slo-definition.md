# SLO definition

**Service:** <name>

| SLI | Definition (good/valid) | SLO target | Window | Budget |
|---|---|---|---|---|
| Availability | non-5xx / total | 99.9% | 28d | ~40 min |
| Latency | p99 < 300ms | 99% | 28d | — |

**Error-budget policy:** budget > 25% remaining → ship; < 0 → feature freeze + reliability work.
**Burn-rate alerts:** fast (2% in 1h AND 5m) page; slow (10% in 6h) ticket.
**Owner:** <name>
