# Partition for ordering and parallelism — knowing they conflict

Message ordering is guaranteed only within a partition, so the partition key is your ordering contract: key by the entity that needs ordered events. More partitions buy parallelism and throughput but spread a key's events across consumers; too few throttle throughput. This trade must be decided up front because re-partitioning a live topic is disruptive and changes ordering.
