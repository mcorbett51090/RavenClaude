# Changelog — incident-response-dfir

All notable changes to this plugin are documented here. Format follows [Keep a Changelog](https://keepachangelog.com); this plugin versions per [SemVer](https://semver.org).

## [0.1.0] — 2026-07-01

### Added

- Initial release. The incident-response-dfir team — blue-team Digital Forensics & Incident Response (DFIR) / SOC: running a security incident end to end and building the detections and forensics that make it possible.
- **2 agents:** `dfir-response-lead` (NIST 800-61 incident lifecycle, triage & severity, containment strategy, eradication/recovery, breach coordination, comms, regulatory notification, tabletops) and `detection-and-forensics-engineer` (detection engineering with SIEM/Sigma/MITRE ATT&CK + alert tuning, threat hunting, evidence acquisition & forensics, malware triage).
- **5 skills:** `triage-and-classify-an-incident`, `run-the-incident-lifecycle`, `engineer-a-detection`, `hunt-for-a-threat`, `acquire-and-preserve-evidence` (shared at the analysis/evidence seam).
- **Knowledge bank (4 docs):** two Mermaid decision trees (`incident-lifecycle-decision-tree` and `detection-and-hunting-reference`), `forensics-and-evidence-handling.md` (RFC 3227 order of volatility + chain of custody), and a dated `dfir-tooling-2026.md` category map.
- **5 best-practices** (contain-before-you-eradicate, preserve-evidence-before-you-remediate, severity-drives-the-response-not-the-noise, every-detection-maps-to-attack-and-has-a-tuning-plan, notification-timelines-are-legal-deadlines-not-guidelines), **3 templates** (IR plan, blameless post-mortem, chain-of-custody log), and **1 advisory hook** (`flag-dfir-hygiene-smells.sh`, POSIX-ERE only).
- Seams to `security-engineering` (the appsec/secure-coding fix), `cybersecurity-grc` (governance/risk/audit/compliance), `observability-sre` (reliability incidents + telemetry pipeline), and `trust-and-safety` (platform abuse).
