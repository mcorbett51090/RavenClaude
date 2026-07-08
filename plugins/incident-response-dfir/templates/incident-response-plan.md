# Incident Response Plan — <organization>

> Template for a security incident-response plan, structured on the four-phase incident-handling lifecycle (from NIST SP 800-61r2, superseded by r3 (2025, CSF 2.0-aligned) — cite r3 as current). Copy and tailor. Review at least annually and after every significant incident and tabletop. This is a living document — the bus factor is not one person's memory.

**Owner:** <name/role> · **Version:** <x.y> · **Last reviewed:** <YYYY-MM-DD> · **Next review:** <YYYY-MM-DD>

## 1. Purpose & scope
- What this plan covers (systems, data, environments) and what it does not.
- Definitions: *event* vs *incident*; the severity levels (S1–S4).

## 2. Roles & contacts (Preparation)
| Role | Name | Contact | Backup |
|---|---|---|---|
| Incident Commander (DFIR Response Lead) | | | |
| Detection & Forensics Engineer | | | |
| Comms / PR lead | | | |
| Legal / DPO | | | |
| Executive sponsor | | | |
| External IR retainer / cyber-insurer | | | |

- **Out-of-band comms channel:** <how the team communicates if the primary systems are compromised>.

## 3. Severity & triage (Detection & Analysis)
- The is-it-an-incident gate and the impact × scope severity matrix (S1–S4) — see the triage skill.
- Response tier per severity: who is engaged, comms cadence, escalation path.

## 4. Response procedures — the four phases
### 4.1 Preparation
- Tooling, logging, and access inventory; ensure the team can reach the logs/EDR/SIEM.
### 4.2 Detection & Analysis
- Validate, scope (vector, blast radius, affected data), build the timeline, map to MITRE ATT&CK.
- **Evidence gate:** capture volatile evidence (order of volatility) before any destructive step.
### 4.3 Containment, Eradication & Recovery
- Containment options (short-term isolate/disable/block; long-term rebuild clean).
- Eradication (root cause: malware, vuln, creds, persistence).
- Recovery (restore known-good, validate, monitor for recurrence).
### 4.4 Post-Incident Activity
- Blameless post-mortem (use the incident-report/postmortem template) within ~2 weeks; track follow-ups.

## 5. Evidence handling
- Order of volatility, hashing at collection, chain of custody (use the chain-of-custody log).
- Retention policy and storage for evidence.

## 6. Notification & regulatory obligations
- The clock starts at **awareness**. Map obligations: GDPR 72h authority notice, data-subject notice, contractual, cyber-insurer, sector rules.
- **Legal owns the reportability determination — flag counsel early.**

## 7. Communications plan
- Internal cadence (even "no change, next update in 30 min"), external/customer comms, holding statements, spokesperson.

## 8. Preparation & testing
- Tabletop schedule and scenarios; detection-coverage reviews; plan review cadence.
- After-action: fold every lesson back into this plan.

## 9. References
- NIST SP 800-61r3 (2025, CSF 2.0-aligned; supersedes r2); RFC 3227; MITRE ATT&CK; the plugin's knowledge bank and best-practices.
