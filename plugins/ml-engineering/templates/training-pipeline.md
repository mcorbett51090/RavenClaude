# Training pipeline

```
prep (versioned data) -> train (tracked: params/metrics/code/data/env)
  -> evaluate (leakage-free, time-aware split, test used once)
  -> register (versioned + metrics + lineage + model card)
```

- Features via feature store / shared transform (train==serve)
- Experiment tracking on every run
- Significance of comparisons -> applied-statistics
