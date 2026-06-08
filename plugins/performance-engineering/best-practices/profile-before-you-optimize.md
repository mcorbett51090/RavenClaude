# Profile before you optimize

Measure the bottleneck before changing anything. A CPU/memory/IO profile, a flame graph, or a USE/RED breakdown names the actual constraint; optimizing an un-profiled guess is how teams speed up the thing that wasn't slow and ship no improvement. Apply USE (utilization/saturation/errors per resource) and RED (rate/errors/duration per request stream) to triangulate, then read the flame graph — including the **off-CPU** profile, because the worst latency is often a thread blocked on a lock, IO, or a slow downstream that a CPU profile alone never shows.
