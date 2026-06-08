# Capacity needs headroom, and headroom is computed

Don't plan capacity to 100% utilization and don't size it by gut feel. Use Little's law (`L = λ·W`: concurrency = arrival rate × mean service time) and the *measured* per-instance saturation point to derive the instance count, then add explicit headroom for failover (survive a node loss) and growth (the peak multiplier, not the average). Saturation — a queue building — hurts latency long before utilization reaches 100%, so size below the knee, not at it. A capacity plan with no stated headroom is a plan that fails on the first bad day.
