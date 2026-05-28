# Claude app cost model — <APP / DATE>

> Owned by `claude-app-ops-engineer`. See `knowledge/claude-app-finops-reliability-and-security.md`. Metric: cost-per-resolved-task, not raw tokens.

## Per-request shape
| Component | Tokens | $/MTok (dated) | Notes |
|---|---|---|---|
| Cache read (input) | | 0.1× input | the win — maximize hit rate |
| Cache write | | 1.25× (5m) / 2× (1h) | one-time per prefix |
| Uncached input | | 1× | minimize via caching |
| Output | | (per model) | size max_tokens to actual |

- **Cache hit rate (target):** <cache_read / (cache_read + input) ≥ ?>
- **Model:** <which; routing ladder>

## Levers (priority order)
1. [ ] Prompt-cache hit rate — <current → target>
2. [ ] Routing ladder — <Haiku triage → escalate>; metric = cost-per-resolved-task
3. [ ] Batch the async work (50%, +300k-output beta) — <which jobs>
4. [ ] `max_tokens` right-sized — <value>
5. [ ] Deployment-target economics — <Claude API vs Bedrock/Vertex/Foundry>

## Projection
- **Volume:** <requests/day> · **Cost/resolved-task:** <$> · **Monthly:** <$>
- **Sensitivity:** <what changes the number most>
