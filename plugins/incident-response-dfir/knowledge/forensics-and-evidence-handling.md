# Knowledge — Forensics & evidence handling

> **Last reviewed:** 2026-07-01 · **Confidence:** High (RFC 3227 order of volatility and chain-of-custody principles are settled forensic doctrine). **Not legal advice** — admissibility and authorization are legal calls; flag them before acquiring anything that may become litigation.
> The `detection-and-forensics-engineer` follows this order **every time**; the `dfir-response-lead` enforces it as a gate before any destructive remediation.

The discipline: **capture most-volatile first → hash at collection → work on a copy → unbroken chain of custody.** A hard power-off before memory capture is evidence destruction.

---

## Order of volatility (RFC 3227 — collect top to bottom)

| Priority | Evidence | Why it's this volatile | Destroyed by |
|---|---|---|---|
| 1 | CPU registers, cache | Nanosecond lifetime | Any instruction / power-off |
| 2 | Routing table, ARP cache, process table, kernel stats, **RAM** | Live system state, memory-resident malware, keys, connections | **Power-off** |
| 3 | Temporary filesystem / swap | Overwritten by normal use | Reboot / heavy use |
| 4 | Disk (raw image) | Persistent but deletions/overwrites accrue | Reimage / continued use |
| 5 | Remote logging & monitoring data | Retention-bounded, rotates | Log rotation / TTL |
| 6 | Physical configuration, network topology | Slow to change | Reconfiguration |
| 7 | Archival media / backups | Most stable | Retention policy |

> **The load-bearing rule:** capture RAM (and live network/process state) **before** you power off, isolate destructively, or reimage. Memory holds unpacked malware, injected code, live C2 connections, and encryption keys that vanish on power-off.

## Chain of custody — the fields that must never break

| Field | Records |
|---|---|
| What | Description + unique evidence ID |
| Who | Person collecting/handling (name, role) |
| When | Timestamp of every collection/transfer/access |
| Where | Physical/logical storage location |
| Why | Reason for each transfer or access |
| Integrity | Hash (e.g. SHA-256) at collection, re-verified on the working copy |

An **unbroken** chain — every touch logged, hashes matching — is what makes evidence trustworthy and admissible. One undocumented handoff can taint the whole chain. Analyze a **verified working copy**; write-block and seal the original. Use [`../templates/chain-of-custody-log.md`](../templates/chain-of-custody-log.md).

## Acquisition per source

| Source | Method | Gotcha |
|---|---|---|
| **Memory** | Live RAM dump before isolation/power-off | Must precede power-off; anti-forensics can hide in memory too |
| **Disk** | Bit-for-bit image via a write-blocker, hash-verified | Capture live-system artifacts first; verify source hash == image hash |
| **Network** | Full packet capture, NetFlow, firewall/proxy/DNS logs | Ephemeral — retained logs age out; capture live where possible |
| **Cloud** | Snapshot volumes **before** instance termination; export provider audit logs (CloudTrail/Activity Log style) | Instances are ephemeral; audit logs have retention windows — pull early; know the provider's evidence-access process |
| **Endpoint / EDR** | EDR-retained telemetry + triage collection (KAPE-style targeted artifacts) | Retention-bounded; collect before rotation |
| **Mobile** | Vendor-supported extraction; document method + tool version | Encryption/lock state limits what's recoverable |

## Analysis hygiene

- **Hash first, analyze second** — SHA-256 at collection is the integrity anchor.
- **Copy, don't touch** — original write-blocked; all work on a verified copy.
- **Document tools + versions** — reproducibility is part of admissibility.
- **Legal in the loop early** — authorization, scope, and privilege before acquisition when litigation/regulation is possible.

## Provenance
- RFC 3227 *Guidelines for Evidence Collection and Archiving* (order of volatility). NIST SP 800-86 *Guide to Integrating Forensic Techniques into Incident Response* (acquisition/analysis discipline). Chain-of-custody principles per standard forensic practice. Last reviewed 2026-07-01.
- See also [`../best-practices/preserve-evidence-before-you-remediate.md`](../best-practices/preserve-evidence-before-you-remediate.md) and [`incident-lifecycle-decision-tree.md`](incident-lifecycle-decision-tree.md).
