# Stream only when latency demands it

Real-time streaming infrastructure carries significant operational weight — brokers, schema governance, stateful processors, exactly-once tuning. If the business need is hourly or daily, batch ELT (data-platform) is simpler, cheaper, and more reliable. Reserve streaming for genuine sub-minute latency requirements; adopting it for novelty buys operational cost with no latency benefit.
