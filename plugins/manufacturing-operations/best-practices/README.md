# Manufacturing-operations best-practices

Atomic, enforceable rules the manufacturing-operations agents apply. Each file is one rule with a short rationale; the agents cite them by filename. Canonical decision logic lives in [`../knowledge/manufacturing-operations-decision-trees.md`](../knowledge/manufacturing-operations-decision-trees.md); these rules are the always-on priors.

| Rule | Gist |
|---|---|
| plan-to-the-constraint-not-infinite-capacity | A schedule must respect the bottleneck's finite rate + material |
| the-bottleneck-sets-the-rate | Optimize the constraint; a non-bottleneck gain is a mirage |
| oee-denominators-must-be-defined | No OEE number without a stated ideal cycle time + downtime split |
| produce-to-takt-not-to-machine-speed | Build to demand rate; ahead of takt is over-production |
| containment-is-not-a-capa | An NCR needs root-cause + preventive action, not just scrap |
| special-cause-before-you-react | Don't tamper with common-cause noise; limits from the process |
| prevention-beats-detection-beats-scrap | Push quality upstream; final inspection is the weakest control |
| state-the-assumptions-behind-every-number | Forecast horizon, cycle-time basis, sample size, AQL — surfaced |
| lot-size-trades-setup-against-holding | A lot size is a stated trade; a setup at the constraint is lost throughput |
| safety-stock-is-a-decision-not-a-default | Size buffers to variability + a service level, not to feel |
| the-bom-must-match-as-built | A drifted BOM poisons MRP — check integrity before netting |
| no-silent-regulated-sign-off | Draft the regulated disposition; the accountable human signs it |
