# Chain of Custody Log — <case / incident ID>

> Template for an evidence chain-of-custody record. An **unbroken** chain — every collection, transfer, and access logged, with matching hashes — is what makes digital evidence trustworthy and admissible. One undocumented handoff can taint the whole chain. Keep one record per evidence item.

**Case / incident ID:** <ID> · **Custodian of record:** <name/role> · **Storage location:** <secure evidence store>

## Evidence item

| Field | Value |
|---|---|
| Evidence ID | <unique ID> |
| Description | <e.g. "RAM image, host WKS-014" / "forensic disk image, SRV-DB01"> |
| Source system | <hostname / asset ID / cloud resource ARN> |
| Type | <memory / disk / network capture / cloud snapshot / logs / mobile> |
| Acquisition method + tool (with version) | <e.g. WinPmem 3.x live dump; write-blocker + FTK Imager> |
| Collected by | <name, role> |
| Date/time collected (UTC) | <YYYY-MM-DD HH:MM UTC> |
| Hash at collection | <algorithm + value, e.g. SHA-256: …> |
| Verified copy hash | <SHA-256 of the working copy — must match> |

## Custody transfers & access

| # | Date/time (UTC) | Released by | Received by | Purpose / action | Storage / integrity note |
|---|---|---|---|---|---|
| 1 | | | | Collected & sealed | Original write-blocked; hash recorded |
| 2 | | | | Transfer to <store/analyst> | Hash re-verified: match ✅ |
| 3 | | | | Analysis on verified copy | Original untouched |
| … | | | | | |

## Integrity attestations
- [ ] Hash computed at collection (SHA-256 or stronger).
- [ ] Original write-blocked / sealed; all analysis performed on a verified copy.
- [ ] Every transfer and access logged above with who/what/when/where/why.
- [ ] Hashes re-verified after each transfer (match confirmed).
- [ ] Tool names + versions documented for reproducibility.

## Legal / retention
- **Legal hold:** <yes/no — if litigation/regulation possible, legal authorized scope before acquisition>.
- **Retention:** <per policy — how long, then disposition>.
