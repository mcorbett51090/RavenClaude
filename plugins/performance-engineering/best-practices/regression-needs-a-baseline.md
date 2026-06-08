# A regression claim needs a committed baseline and a threshold

"It feels slower" is not a finding. Regression detection requires a committed baseline (the percentiles at a known workload) and a threshold (the allowed p95/p99 delta); gate the release on the measured delta, not a gut check. The baseline and the new run must use the same pinned workload, data, environment, and tool version, or the comparison is noise. When a regression is confirmed, a flame-graph diff against the baseline localizes what changed — turning "slower" into a named, routable cause.
