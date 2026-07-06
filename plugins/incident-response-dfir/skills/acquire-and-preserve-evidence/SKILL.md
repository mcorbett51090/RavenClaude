---
name: acquire-and-preserve-evidence
description: Acquire and preserve digital evidence so it survives scrutiny — collect in RFC 3227 order of volatility (most-volatile first), hash at collection, maintain an unbroken chain of custody, and use the right acquisition method per source (memory, disk, network, cloud). Returns the acquisition plan, the chain-of-custody log, and the hash/verification record. Used by `detection-and-forensics-engineer` (primary); enforced as a gate by `dfir-response-lead` before remediation.
---

# Skill: acquire-and-preserve-evidence

> **Invoked by:** `detection-and-forensics-engineer` (primary); enforced as a pre-remediation gate by `dfir-response-lead`.
>
> **When to invoke:** "image this host"; "capture memory before we contain"; "we need forensics-grade evidence"; before any containment/eradication that could destroy volatile state.
>
> **Output:** the acquisition plan in order of volatility, a chain-of-custody log, and the hashes proving integrity.

## When to invoke

Before you remediate — the moment an incident is confirmed on a live system. Remediation (power-off, reimage, isolate) frequently destroys volatile evidence, so acquisition comes *first*.

## Output

An ordered acquisition plan, a populated [`chain-of-custody-log`](../../templates/chain-of-custody-log.md), and a hash record (e.g. SHA-256) taken at collection and re-verified on the working copy.

## Procedure — RFC 3227 order of volatility

1. **Capture the most volatile first.** Per RFC 3227, collect in decreasing order of volatility so nothing is lost while you deliberate:
   1. CPU registers, cache
   2. Routing table, ARP cache, process table, kernel statistics, **RAM (memory image)**
   3. Temporary filesystem / swap
   4. Disk (raw image)
   5. Remote logging & monitoring data relevant to the system
   6. Physical configuration, network topology
   7. Archival media
2. **Do not power off a live system before memory capture.** RAM holds process state, network connections, injected/unpacked malware, and encryption keys that a power-off destroys forever. Capture memory *then* decide on containment.
3. **Hash at collection.** Compute a cryptographic hash (SHA-256) of every acquired artifact at the moment of collection. This is the integrity anchor — it proves the evidence didn't change afterward.
4. **Work on a copy; write-block the original.** Acquire a forensic image, verify its hash matches the source, then do all analysis on the copy. The original is write-blocked and sealed.
5. **Maintain chain of custody.** Log every transfer and access: who collected/handled it, what it is, when (timestamped), where it was stored, and why it moved. An unbroken chain is what makes evidence trustworthy and admissible. Use [`../../templates/chain-of-custody-log.md`](../../templates/chain-of-custody-log.md).
6. **Acquire per source correctly** (see the table). Cloud and network evidence have their own volatility and legal-access nuances — snapshot before an instance is terminated, and pull provider audit logs early (they age out).

## Quick reference — acquisition per source

| Source | Method | Volatility note |
|---|---|---|
| **Memory (RAM)** | Live memory dump (e.g. before isolation) | Highest priority after CPU state — gone on power-off |
| **Disk** | Write-blocked forensic image (bit-for-bit), hash-verified | Persistent, but capture running-system artifacts first |
| **Network** | Full-packet capture / flow logs / firewall + proxy logs | Ephemeral — capture live or from retained logs |
| **Cloud** | Snapshot volumes before termination; export provider audit/API logs (CloudTrail-style) | Instances are ephemeral; audit logs have retention windows — pull early |
| **Endpoint/EDR** | EDR-retained telemetry + triage collection (KAPE-style) | Retention-bounded; collect before rotation |

## Guardrails
- **Order of volatility is not optional** — capture RAM/live state before disk before archives; a power-off first is evidence destruction. See [`../../best-practices/preserve-evidence-before-you-remediate.md`](../../best-practices/preserve-evidence-before-you-remediate.md).
- **Hash at collection, re-verify on the copy** — no hash means no integrity proof means worthless evidence.
- **Chain of custody must be unbroken** — one undocumented handoff can taint the whole chain. Log every touch.
- **Know the legal posture** — for anything that may become litigation/regulatory, flag legal *before* acquisition (authorization, scope, privilege). See [`../../best-practices/notification-timelines-are-legal-deadlines-not-guidelines.md`](../../best-practices/notification-timelines-are-legal-deadlines-not-guidelines.md).
