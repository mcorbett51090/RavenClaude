# ITSM — 2026 Capability Map

_A dated read of the ITSM tooling landscape. Every row is `[verify-at-use]` — platform names, capabilities, and licensing are volatile; re-confirm against the vendor before quoting or adopting. Last reviewed: 2026-06-19 (training-knowledge baseline — verify live before relying on any specific row)._

> This map orients; it does not endorse. License, fit, and total cost must be vetted at adoption; route security-sensitive integrations through `ravenclaude-core/security-reviewer`.

## ITSM platforms
| Tier / fit | Representative platforms `[verify-at-use]` | Note |
|---|---|---|
| Enterprise suite | ServiceNow, BMC Helix, Ivanti | Full ITIL practice coverage + CMDB + discovery; heavier + costlier. |
| Mid-market / dev-aligned | Jira Service Management, Freshservice, ManageEngine ServiceDesk Plus | Strong fit when the org already lives in the adjacent ecosystem. |
| SMB / lightweight | Zendesk (IT use), Freshservice (lower tiers), HaloITSM | Right-size: don't buy enterprise process for SMB pain. |

## Deflection & AIOps (the 2026 shift)
| Capability | Representative tooling `[verify-at-use]` | Note |
|---|---|---|
| Virtual agent / self-service deflection | platform-native virtual agents, LLM-backed assistants | Measure deflection rate; the cheapest ticket is the prevented one (§2 #7). |
| AIOps event correlation / noise reduction | platform AIOps modules, dedicated AIOps tools | Overlaps `observability-sre` telemetry — coordinate, don't duplicate. |
| Major-incident automation | platform major-incident workflows | Automate the command/comms scaffolding, not the judgment. |

## Discovery & CMDB
| Need | Representative tooling `[verify-at-use]` | Note |
|---|---|---|
| Automated discovery | platform discovery (e.g. ServiceNow Discovery), agent/agentless scanners | A CMDB fed by discovery survives; manual entry rots (§2 #6). |
| Cloud asset / cost reconciliation | cloud-native inventory + `finops-cloud-cost` | Asset *cost* lens is finops'; the CI/relationship model is here. |

## What this map deliberately does NOT do
- It does not pick your platform — the practice selection and the org's pain do.
- It does not freeze versions — every row is verify-at-use by design.
- It does not equate buying a tool with having a practice — a platform without the discipline (§2 #6) is shelfware.
