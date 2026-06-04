# Choose delivery semantics deliberately

Pick the weakest semantic that meets the requirement: at-least-once with idempotent consumers is the pragmatic default, while exactly-once costs throughput and complexity and is only truly end-to-end when the sink participates in the transaction. Name the guarantee you need at each hop; assuming exactly-once you didn't configure, or paying for it where at-least-once would do, are both common and costly mistakes.
