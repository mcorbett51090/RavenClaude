# Preserve evidence before you remediate

**Status:** Absolute rule
**Domain:** Digital forensics / evidence handling (RFC 3227)
**Applies to:** `incident-response-dfir`

---

## Why this exists

Remediation is destructive to evidence. The instinctive first move on a compromised machine — power it off, pull the network cable, reimage — permanently destroys the most valuable evidence there is: the contents of memory. RAM holds running processes, live network connections, injected and *unpacked* malware (the on-disk copy may be encrypted/packed), and encryption keys. RFC 3227's *order of volatility* exists precisely because the most valuable evidence is the most fragile: once you power off, it is gone and unrecoverable. You cannot re-run the incident to get it back.

## How to apply

Before any destructive remediation on a live system, capture evidence in order of volatility — most volatile first: CPU/cache → routing/ARP/process tables and **RAM** → temp/swap → disk → remote logs → physical config. Hash each artifact at collection, log the chain of custody, and analyze a verified copy. *Then* contain and remediate.

**Do:**
- Capture a **memory image before power-off / isolation** on any host with forensic value.
- Hash (SHA-256) at collection; work on a write-blocked copy; keep an unbroken chain of custody.
- Snapshot cloud volumes and export provider audit logs *before* an instance is terminated (they're ephemeral and retention-bounded).

**Don't:**
- Hard power-off, reimage, or destructively isolate a live system before memory capture.
- Analyze the original evidence (analyze a verified copy); leave the original unhashed.
- Let a containment reflex ("just pull it offline") override the evidence gate when the evidence matters.

## Edge cases / when the rule does NOT apply

- **Active destruction in progress** (ransomware encrypting, active exfil) can justify immediate isolation even at the cost of some volatile evidence — stopping the harm wins. Prefer *network isolation* (which preserves memory) over *power-off* (which doesn't) where possible.
- **A trivial, no-forensic-value endpoint** (a disposable kiosk with nothing to learn) may not warrant full acquisition — but that's a deliberate call, not a default.
- **Legal hold / litigation** raises the bar, not lowers it: flag legal *before* acquiring (authorization, scope, privilege).

## See also
- [`../skills/acquire-and-preserve-evidence/SKILL.md`](../skills/acquire-and-preserve-evidence/SKILL.md)
- [`../knowledge/forensics-and-evidence-handling.md`](../knowledge/forensics-and-evidence-handling.md)
- [`contain-before-you-eradicate.md`](contain-before-you-eradicate.md)

## Provenance
Codifies RFC 3227 (order of volatility) and NIST SP 800-86 (forensic acquisition discipline); the "capture memory before power-off" imperative is settled forensic practice. Last reviewed 2026-07-01.

---

_Last reviewed: 2026-07-01 by `claude`_
