# itsm-service-management

A Claude Code plugin: the team that **runs IT as a service on the ITIL 4 operating model**. For the IT manager, service-desk lead, or MSP running incidents, changes, requests, SLAs, and a CMDB — this plugin brings ITIL 4 discipline without the bureaucracy.

Part of the [RavenClaude](../../README.md) marketplace. Inherits the `ravenclaude-core` protocols.

## What it gives you

**4 specialist agents:**

- **service-management-lead** — the ITIL 4 service value system, which practices to actually adopt (and how lightly), governance, and continual improvement.
- **incident-and-problem-manager** — restore service (incidents, major-incident command, swarming) and remove causes (problems, RCA, known errors) — two different jobs, kept distinct.
- **change-and-release-manager** — change enablement (standard / normal / emergency), change models, risk assessment, the CAB (and when to skip it), and release management.
- **service-desk-and-request-manager** — the service desk, request fulfillment, the service catalog, SLAs/OLAs/UCs, knowledge & self-service, and the CMDB / configuration management.

Plus **5 skills**, a **knowledge bank** (Mermaid decision trees + an ITIL 4 practice reference + a dated 2026 ITSM tooling map), **8 best-practices**, **4 templates**, **4 commands**, and **1 advisory hook**.

## House opinions

1. **An incident restores service; a problem removes the cause** — two jobs, two metrics.
2. **Change enablement balances speed and risk — it is not a bureaucracy.**
3. **Standard changes are pre-authorized, not CAB-bottlenecked.**
4. **Every service has an SLA, backed by OLAs and underpinning contracts.**
5. **A major incident needs a commander and communications, not just engineers.**
6. **The CMDB is only as good as its maintenance discipline.**
7. **Shift left: knowledge and self-service deflect tickets.**

## Commands

- `/triage-incident` — classify incident vs problem vs major incident and route it.
- `/plan-change` — pick the change type (standard/normal/emergency) and build the RFC.
- `/design-sla` — define an SLA backed by OLAs and underpinning contracts.
- `/run-major-incident` — stand up major-incident command, roles, and comms.

## Where it stops (seams)

Engineering incident response / SRE / observability / chaos engineering → `observability-sre` (this plugin owns the **ITIL operating model**, that one owns the **engineering reliability practice** — a prod outage is usually both). CI/CD deployment automation → `devops-cicd`. Security incidents / GRC → `cybersecurity-grc`. Asset cost → `finops-cloud-cost`.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install itsm-service-management@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.
