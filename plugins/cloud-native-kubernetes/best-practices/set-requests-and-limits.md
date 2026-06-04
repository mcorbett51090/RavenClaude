# Set requests and limits, and know the difference

Requests drive scheduling; limits cap usage. A pod with no requests makes the scheduler guess and becomes the eviction candidate or the noisy neighbor. Set both, understand the resulting QoS class (Guaranteed/Burstable/BestEffort), and enforce sane defaults with a namespace LimitRange.
