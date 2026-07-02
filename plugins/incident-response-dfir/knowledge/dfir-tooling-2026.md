# Knowledge — DFIR tooling (2026)

> **Last reviewed:** 2026-07-01 · **Confidence:** Medium-High for the categories (stable); **volatile** for specific product feature sets, current versions, and vendor names — **re-verify at use** before quoting a consumer. This is a *category map*, not a settled fact sheet; retrieval date 2026-07-01.

The discipline: recommend the **category and the fit**, name a tool second, and carry a retrieval date on any volatile specific (a product's current feature set, a framework's current version). Tooling churns; the categories don't.

---

## SIEM / detection & log analytics

| Category | Representative tools (2026, re-verify at use) | Pick it when |
|---|---|---|
| SIEM (search + correlate + alert) | Splunk, Microsoft Sentinel, Elastic Security, Google SecOps (Chronicle) | Central alerting/correlation across log sources |
| Detection content standard | **Sigma** (SigmaHQ) — vendor-neutral rules, converted per-SIEM | Detection-as-code, portable rules in version control |
| Detection framework | **MITRE ATT&CK** + ATT&CK Navigator (coverage heatmaps) | Mapping/gap-analysis of detection coverage |

> ATT&CK version and technique IDs change between releases — **re-verify the technique ID at use** against attack.mitre.org.

## EDR / XDR (endpoint telemetry & response)

| Category | Representative tools (re-verify at use) | Note |
|---|---|---|
| EDR/XDR | CrowdStrike Falcon, Microsoft Defender for Endpoint, SentinelOne, Elastic Defend | Process/telemetry visibility + isolate/kill/collect actions |
| Open telemetry | Sysmon (+ config baselines), osquery, Velociraptor | Endpoint visibility & live hunting/collection at scale |

## Forensics suites & acquisition

| Need | Tools (re-verify at use) | Note |
|---|---|---|
| Disk imaging / analysis | Autopsy / The Sleuth Kit, EnCase, X-Ways, FTK | Write-blocked imaging + filesystem forensics |
| Memory acquisition | WinPmem / AVML / LiME (capture); **Volatility 3** (analysis) | Capture RAM *before* power-off; analyze the image |
| Triage collection | **KAPE**, Velociraptor, CyLR | Targeted artifact collection from live/mounted systems |
| Timeline | Plaso / log2timeline, Timesketch | Super-timeline correlation across artifacts |
| Cloud | Provider-native (AWS/Azure/GCP snapshots + audit-log export); cloud-forensics tooling | Snapshot before termination; export audit logs early |

## Malware triage & sandboxing

| Need | Tools (re-verify at use) | Note |
|---|---|---|
| Static triage | PE tools, `strings`, YARA, CyberChef, capa | Hashes/strings/structure/capabilities before detonation |
| Multiscan / intel | VirusTotal, Hybrid Analysis | **Do not upload confidential samples without authorization** — public submission can tip off the adversary |
| Dynamic sandbox | Cuckoo-lineage sandboxes, CAPE, ANY.RUN, Joe Sandbox | Detonate in an isolated network; assume anti-sandbox evasion |

## Threat intel & IOC management

| Need | Tools (re-verify at use) | Note |
|---|---|---|
| Intel platform / sharing | MISP, OpenCTI; STIX/TAXII for exchange | Structured IOC + TTP sharing |
| Case management / SOAR | TheHive + Cortex; SOAR platforms for playbook automation | Track cases, automate repeatable response steps |

## Provenance
- Vendor/project homepages + docs (Sigma/SigmaHQ, MITRE ATT&CK, Volatility, KAPE, Velociraptor, MISP, TheHive, the SIEM/EDR vendors above). **Specific product feature availability, current versions, and vendor names are volatile — re-verify at use (retrieved 2026-07-01).** Last reviewed 2026-07-01.
- See also [`detection-and-hunting-reference.md`](detection-and-hunting-reference.md) and [`forensics-and-evidence-handling.md`](forensics-and-evidence-handling.md).
