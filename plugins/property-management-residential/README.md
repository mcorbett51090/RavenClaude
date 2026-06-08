# Property Management — Residential

The **property-management-residential** plugin — the craft of running residential rental housing (apartments and single-family rentals) as an operation: filling units, keeping them livable, and reporting the numbers to owners. Fair-housing-aware throughout — it **flags** fair-housing and habitability risk and routes it to counsel; it does **not** give legal advice. Distinct from commercial real estate, from the trust/GL books, and from the physical trade work.

## Agents

- **`leasing-and-tenant-ops`** — The leasing funnel and the lease lifecycle: lead-to-lease funnel and time-to-lease, a consistent documented applicant-screening standard, lease execution, renewals and rent increases, move-in/move-out and security-deposit handling, and fair-housing basics. Flags protected-class and legal risk and routes to counsel; never opines on the law.
- **`maintenance-coordinator`** — Work orders and the physical asset: work-order intake and triage (emergency vs. routine, safety/habitability first), preventive-maintenance scheduling, vendor dispatch, unit turns, and emergency/habitability response. Triages and dispatches; the licensed trade work routes to `skilled-trades-contracting`.
- **`owner-and-portfolio-reporting-analyst`** — The owner-facing numbers: rent roll, delinquency and a consistent collections ladder, owner statements, NOI (operating-only — never debt service / capex / depreciation), and occupancy/vacancy and portfolio reporting. Produces the operational reporting; the books of record route to `finance`.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install property-management-residential@ravenclaude
```

## Seams

- **Commercial leases (NNN, CAM reconciliation, tenant-improvement allowances, cap-rate underwriting)** → `commercial-real-estate`; this plugin is residential-only.
- **The trust-account reconciliation, GL posting, audited financials, and tax treatment** → `finance`; we produce the operational rent roll and owner statement, they own the books of record.
- **The licensed trade work, the scope-of-work, and the contractor bid** → `skilled-trades-contracting`; we triage, classify, and dispatch a work order, they do the repair.
- **Fair-housing law, eviction/non-renewal legality, lease-clause enforceability, warranty-of-habitability as a legal question** → qualified legal counsel; agents **flag and route**, they do not opine.
- **Tenant PII (SSNs, screening/background reports, bank data)** → handled under `ravenclaude-core/security-reviewer` data-handling guidance.

Inherits `ravenclaude-core` protocols (Capability Grounding + Structured Output). Requires `ravenclaude-core@>=0.7.0`. Designed to be installed alongside `finance` and `skilled-trades-contracting`.
