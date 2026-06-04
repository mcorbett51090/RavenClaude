# Model monitoring plan

| Signal | Metric | Threshold | Alert | Response |
|---|---|---|---|---|
| Input/data drift | PSI / KS | > x | yes | investigate / retrain |
| Prediction drift | output dist shift | > x | yes | investigate concept vs data |
| Performance | accuracy/AUC (when labels) | drop > x | yes | retrain (sig -> applied-statistics) |

**Retraining trigger:** <schedule / drift threshold / perf drop>  **Loop to:** training-pipeline-engineer
