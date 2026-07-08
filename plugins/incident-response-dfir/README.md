# incident-response-dfir

> A RavenClaude plugin for **blue-team Digital Forensics & Incident Response (DFIR) / SOC work** — running a security incident from the first triage decision to the blameless post-mortem, and building the detections and forensics that make it possible. Two specialist agents cover the two halves of DFIR: incident command (lifecycle, severity, containment, breach coordination) and the technical surface (detection engineering, threat hunting, forensics, malware triage).

Part of the [RavenClaude](https://github.com/mcorbett51090/RavenClaude) marketplace. Requires `ravenclaude-core@>=0.7.0`.

## What it's for

When an alert fires and you have to decide *fast* — is this an incident, how bad is it, do we contain now or capture memory first, who do we have to notify and by when — this plugin is the team that runs it with you, on the four-phase incident-handling lifecycle (NIST SP 800-61r3, CSF 2.0-aligned; supersedes r2). And between incidents, it builds the detections (Sigma rules mapped to MITRE ATT&CK), hunts for what the alerts missed, and acquires evidence that survives scrutiny (order of volatility, chain of custody). It is the **SOC / blue-team lane** — the *response*, not the appsec fix or the compliance program.

## Agents

| Agent | Owns | When to spawn |
|---|---|---|
| [`dfir-response-lead`](agents/dfir-response-lead.md) | Incident lifecycle (NIST 800-61), triage & severity, containment strategy, eradication/recovery, breach coordination, comms, regulatory notification (GDPR 72h), tabletops | "is this an incident?"; "run our active breach"; "what are our notification obligations?"; "run a tabletop" |
| [`detection-and-forensics-engineer`](agents/detection-and-forensics-engineer.md) | Detection engineering (SIEM/Sigma/ATT&CK), alert tuning, threat hunting, evidence acquisition & forensics, malware triage | "write a Sigma rule"; "hunt for X"; "image this host"; "triage this binary" |

## Skills

- [`triage-and-classify-an-incident`](skills/triage-and-classify-an-incident/SKILL.md) — the is-it-an-incident gate + impact × scope severity matrix.
- [`run-the-incident-lifecycle`](skills/run-the-incident-lifecycle/SKILL.md) — the NIST 800-61 phase runbook + containment/eradication/recovery + blameless review.
- [`engineer-a-detection`](skills/engineer-a-detection/SKILL.md) — Sigma rule + ATT&CK mapping + false-positive tuning plan.
- [`hunt-for-a-threat`](skills/hunt-for-a-threat/SKILL.md) — hypothesis-driven, ATT&CK-guided hunt up the pyramid of pain.
- [`acquire-and-preserve-evidence`](skills/acquire-and-preserve-evidence/SKILL.md) — order of volatility + chain of custody + per-source acquisition.

## Knowledge bank

- [`incident-lifecycle-decision-tree.md`](knowledge/incident-lifecycle-decision-tree.md) — Mermaid is-it-an-incident → severity → containment tree + the NIST phases.
- [`detection-and-hunting-reference.md`](knowledge/detection-and-hunting-reference.md) — Mermaid alert → triage → escalate/tune/hunt tree + ATT&CK tactics + pyramid of pain.
- [`forensics-and-evidence-handling.md`](knowledge/forensics-and-evidence-handling.md) — order-of-volatility table, chain of custody, acquisition per source.
- [`dfir-tooling-2026.md`](knowledge/dfir-tooling-2026.md) — dated category map (SIEM, EDR, forensics suites, sandboxes — re-verify at use).

Plus 5 [`best-practices/`](best-practices/README.md) rules, 3 [`templates/`](templates/) (IR plan, blameless post-mortem, chain-of-custody log), and 1 advisory [`hook`](hooks/flag-dfir-hygiene-smells.sh).

## Reach for it vs. adjacent plugins

| Need | Goes to |
|---|---|
| Running a security incident, forensics, detections, hunts | **incident-response-dfir** (this plugin) |
| The application-security / secure-coding fix for the vuln | `security-engineering` |
| Governance, risk, audit, the compliance program behind a notification | `cybersecurity-grc` |
| A reliability (non-security) outage; the log/telemetry pipeline | `observability-sre` |
| Platform abuse / content harm | `trust-and-safety` |

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install incident-response-dfir@ravenclaude
```
