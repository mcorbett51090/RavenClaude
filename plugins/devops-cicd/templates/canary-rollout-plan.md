# Canary rollout plan

**Service:** <name>  **Artifact digest:** <sha256:...>

| Step | Traffic | Hold | Promote if | Abort if |
|---|---|---|---|---|
| 1 | 1% | 10 min | error-rate < baseline+0.5%, p99 < SLO | burn-rate > 2x |
| 2 | 10% | 15 min | same | same |
| 3 | 50% | 15 min | same | same |
| 4 | 100% | — | — | — |

**Health signal (from observability-sre):** <SLO / burn-rate query>
**Rollback action:** shift 100% to previous digest (rehearsed <date>)
**Owner:** <name>
