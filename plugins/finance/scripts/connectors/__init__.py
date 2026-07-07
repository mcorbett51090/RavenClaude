"""finance connectors — reference-implementation OAuth token client, record/replay
transport, per-provider adapters, and drill-through GL lineage.

Offline / reference-impl only: no live credentials, no live sockets. Live wiring (real IdP,
real endpoints, real warehouse) is the consumer's step. Decision-support scaffolding, not a
certified connector and not an accounting/audit/tax opinion (../CLAUDE.md sec.3).
"""
