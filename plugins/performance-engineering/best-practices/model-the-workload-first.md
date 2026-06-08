# Model the workload before you load it

The traffic mix, the arrival pattern, the data distribution, and cache warmth drive the result — so model them before writing a test. A run against uniform synthetic data on a warm cache proves nothing about production, where data is skewed and the cache misses. Specify the request mix (read/write, endpoint weights), the arrival pattern (open vs. closed, steady vs. peak), the data shape (cardinality, skew, size), and the cache-warmth assumption first; the test is only as truthful as the model behind it.
