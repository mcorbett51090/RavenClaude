# Isolate state by blast radius

A single state file for the entire estate means one `apply` can damage everything, every plan is slow, and a lock blocks all work. Split state by lifecycle and blast radius (foundational network, data, app) so a risky, frequent app change can never touch the rarely-changed, high-blast network layer.
