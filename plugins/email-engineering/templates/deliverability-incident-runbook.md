# Deliverability incident runbook — <date>

> Use when mail starts landing in spam or a bounce/complaint spike hits. Top-down: fix the highest failing layer first.

## 1. Detect & scope

- **Symptom:** `<spam placement / bounce spike / complaint spike / reputation drop>`
- **First observed:** `<timestamp>`
- **Scope:** which stream/subdomain/campaign? `<...>`
- **Evidence source:** Google Postmaster Tools ☐ · DMARC RUA ☐ · ESP dashboard ☐ (not "it reached my Gmail")

## 2. Triage (traverse top-down — stop at the first failing layer)

| Layer | Check | Result |
| --- | --- | --- |
| 1. Authentication | SPF & DKIM pass? (`Authentication-Results`) | ☐ pass / ☐ fail |
| 2. Alignment | DMARC pass — identifier aligns with `From:`? | ☐ pass / ☐ fail |
| 3. Reputation | Postmaster domain/IP reputation; recent volume spike? | ☐ ok / ☐ degraded |
| 4. List hygiene | Bounce rate / complaint rate (< ~0.3%)? | ☐ ok / ☐ high |
| 5. Content | Text part, <102KB, aligned links, no spammy patterns? | ☐ ok / ☐ issue |
| 6. Bulk compliance | One-click unsubscribe + spam rate (Gmail/Yahoo)? | ☐ ok / ☐ gap |

## 3. Contain

- [ ] Pause the offending stream (don't push harder)
- [ ] Suppress the hard bounces + complainers (hard pre-send gate)
- [ ] If a bad list import: quarantine/remove it; confirm opt-in source

## 4. Remediate (the failing layer)

- `<the specific fix for the layer identified in §2>`

## 5. Recover & confirm

- [ ] Resume sending at controlled volume to **engaged** recipients (mini warm-up)
- [ ] Confirm recovery in Postmaster Tools / RUA over `<window>`
- [ ] Postmortem: root cause + the prevention (e.g. double opt-in, form protection, stream separation)
