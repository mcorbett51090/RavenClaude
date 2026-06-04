# Model serving rollout

**Model:** <registry version>  **Pattern:** online | batch

| Stage | Traffic | Compare | Promote if | Rollback |
|---|---|---|---|---|
| shadow | 0% (mirror) | new vs current on live | metrics match/beat | drop shadow |
| canary | 5% -> 25% | live metric | metric >= baseline (sig: applied-statistics) | route to current |
| full | 100% | — | — | redeploy prior version |

**Latency budget:** <p99>  **Serving infra:** <k8s/serverless/managed>
