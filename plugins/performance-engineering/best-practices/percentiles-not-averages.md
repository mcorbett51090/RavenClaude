# Report percentiles, never averages

The mean latency hides the tail that hurts users — a system with a great average can page you on p99. Report p50/p95/p99 (and max); set targets and regression thresholds on the high percentiles, not the mean. A p99 regression is real even when the average is flat, because the average is the number that lies about the worst experiences. "Average response time" on a dashboard is an anti-signal: ask for the percentile distribution.
