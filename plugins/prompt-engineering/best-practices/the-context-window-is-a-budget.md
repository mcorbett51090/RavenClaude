# The context window is a budget, not a scratchpad

More context is not free. Cost and latency scale with fill, and past a point
**accuracy drops** — the lost-in-the-middle effect and general dilution mean a
model can do *worse* with more context, not better.

**Do:** budget tokens per section (system / retrieved / history / tools / output
headroom), put decisive material at the start or end, keep the stable prefix first
so it caches, and define what gets evicted or compressed first when the window fills.

**Don't:** dump everything you have into the window because it fits. "It fits" is
not "it helps."

**Flag:** a prompt that grows monotonically with no eviction rule, or a quality
regression that coincides with added context — remove context and re-measure.
