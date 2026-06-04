# Bound state and handle backpressure

Stateful stream operators (aggregations, windows, joins) must checkpoint for recovery and bound their state with TTL, or state grows until the processor runs out of memory. A fast producer feeding a slow consumer creates ever-growing lag or memory pressure; rely on the framework's backpressure, scale the bottleneck operator, and monitor consumer lag as a first-class signal. Both are design concerns, not things to discover in an incident.
