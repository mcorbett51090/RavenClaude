# Performance-engineering best-practices

Atomic, enforceable rules the performance-engineering agents apply. Each file is one rule with a short rationale; the agents cite them by filename. Canonical decision logic lives in [`../knowledge/performance-engineering-decision-trees.md`](../knowledge/performance-engineering-decision-trees.md); these rules are the always-on priors.

| Rule | Gist |
|---|---|
| target-needs-a-workload | A target is a percentile + threshold + the load it holds at |
| percentiles-not-averages | Report p95/p99/max; the mean hides the tail that pages you |
| model-the-workload-first | Mix, arrival pattern, data shape, cache warmth — set before testing |
| open-vs-closed-is-a-choice | Pick the workload model by question; open for user-facing traffic |
| avoid-coordinated-omission | A stalled generator hides the worst latencies; correct for it |
| profile-before-you-optimize | A flame graph / USE/RED names the constraint before any change |
| headroom-is-computed-not-vibed | Little's law + saturation point + explicit failover/growth headroom |
| regression-needs-a-baseline | Gate on a committed baseline + a p95/p99 threshold, not a gut check |
