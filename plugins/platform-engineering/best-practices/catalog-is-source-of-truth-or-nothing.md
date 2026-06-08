# The catalog is the source of truth or it's nothing

A drifted catalog is worse than none — it misleads during an incident and people stop trusting it. Prefer auto-discovery and continuous reconciliation from the system of record (repos, cluster, cloud) over hand-maintained YAML, and register a service in the catalog at creation time via the scaffolder, not as a follow-up ticket.
