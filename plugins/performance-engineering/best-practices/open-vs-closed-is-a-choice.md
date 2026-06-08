# Open vs. closed workload model is a deliberate choice

A closed model (fixed virtual users + think time) and an open model (fixed arrival rate) answer different questions and diverge sharply under saturation. State which one and why. Prefer an **open** arrival-rate model for user-facing traffic, where requests arrive independent of how fast the system responds — a closed model self-throttles when the system slows, hiding the saturation that prod will hit. Reserve the closed model for genuinely closed systems (batch workers, fixed connection pools). Never let the tool's default pick for you.
