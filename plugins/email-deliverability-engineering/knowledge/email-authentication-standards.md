# Email authentication standards (durable reference)

> The RFC-grounded mechanics behind every record this plugin recommends. These
> facts are **durable** (the standards change rarely); provider *policy* specifics
> live in the companion `sender-requirements-and-reputation.md` with retrieval
> dates. Each standard is named so a recommendation can cite it.

## The three core mechanisms

| Mechanism | RFC | What it authenticates | Survives forwarding? |
|---|---|---|---|
| **SPF** | RFC 7208 | The envelope-from (`Return-Path`) domain is authorized to send from this IP | **No** — forwarding changes the connecting IP |
| **DKIM** | RFC 6376 | A cryptographic signature ties the message to the signing (`d=`) domain | **Yes** — the signature travels with the message |
| **DMARC** | RFC 7489 | Ties SPF/DKIM results to the visible `From:` domain via *alignment* + tells receivers what to do on failure | Relies on DKIM for forwarded mail |

### Alignment — the concept most setups miss

DMARC passes when **SPF or DKIM passes AND is *aligned*** with the `From:` header
domain:

- **SPF alignment** — the `Return-Path` domain matches the `From:` domain
  (`aspf=r` relaxed allows a subdomain; `aspf=s` strict requires exact).
- **DKIM alignment** — the signature's `d=` domain matches the `From:` domain
  (`adkim=r`/`adkim=s` likewise).

A "passing" SPF on an unrelated bounce domain contributes **nothing** to DMARC.
This is why DKIM (with an aligned `d=`) is treated as the load-bearing mechanism.

## SPF details (RFC 7208)

- **One record per domain.** Two SPF TXT records → `permerror`.
- **The 10-DNS-lookup limit.** SPF evaluation may not exceed 10 DNS lookups
  (counting `include`, `a`, `mx`, `ptr`, `exists`, `redirect`, recursively).
  Exceeding it → `permerror` → DMARC fail. The most common silent break; audit
  the `include:` chain depth.
- **Qualifiers:** `-all` (fail), `~all` (softfail), `?all` (neutral — does
  nothing), `+all` (pass everyone — never use).

## DKIM details (RFC 6376)

- Published at `<selector>._domainkey.<domain>` as a TXT record holding the public
  key; the sender signs with the private key.
- **2048-bit** keys are the current norm; 1024-bit is weak.
- **Rotate keys** periodically (publish a new selector, sign with it, retire the
  old). Static keys are a standing risk.
- Sign with a `d=` that **aligns** with the `From:` domain.

## DMARC record tags (RFC 7489)

Published at `_dmarc.<domain>`:

| Tag | Meaning |
|---|---|
| `p=` | Policy: `none` (monitor only) / `quarantine` / `reject` |
| `sp=` | Policy for subdomains (defaults to `p`) |
| `rua=` | Where to send **aggregate** reports (the data that drives the ramp) |
| `ruf=` | Where to send **forensic/failure** reports (privacy-sensitive; often omitted) |
| `pct=` | Percent of mail the policy applies to (ramp lever) |
| `adkim=` / `aspf=` | DKIM/SPF alignment mode: `r` relaxed (default) / `s` strict |

### The enforcement ramp (never start at reject)

```
p=none  (monitor — read RUA, confirm every legitimate stream passes aligned auth)
   ↓
p=quarantine  (optionally with pct< 100 to ramp)
   ↓
p=reject  (full enforcement)
```

Reaching `reject` before RUA confirms all legitimate streams pass aligned auth
**blackholes legitimate mail** — third-party senders, forwarders, mailing lists.

## Transport security

- **MTA-STS (RFC 8461)** — declares that senders must use TLS to reach you.
  Requires a policy file at
  `https://mta-sts.<domain>/.well-known/mta-sts.txt` plus a `_mta-sts.<domain>`
  TXT record (with an `id` that changes when the policy changes).
- **TLS-RPT (RFC 8460)** — a `_smtp._tls.<domain>` TXT record telling reporters
  where to send TLS-negotiation failure reports.

## Brand + list-management headers

- **BIMI** — a `default._bimi.<domain>` record pointing at an SVG logo; inbox
  *display* of the logo generally requires a **VMC** (Verified Mark Certificate)
  or CMC, and DMARC must already be at enforcement (`quarantine`/`reject`).
- **One-click unsubscribe (RFC 8058)** — bulk mail needs both the
  `List-Unsubscribe` header (RFC 2369) **and** `List-Unsubscribe-Post:
  List-Unsubscribe=One-Click`, and the unsubscribe must take effect promptly.
- **ARF (RFC 5965)** — the Abuse Reporting Format used by feedback loops (FBLs)
  to report complaints back to senders.

## How they compose (the inbox-eligibility floor)

```
SPF (envelope auth) ─┐
                     ├─► DMARC (alignment + policy on the From: domain) ─► receiver decision
DKIM (signature) ────┘                                                      (+ reputation + engagement)
```

Authentication makes you *eligible* for the inbox. Reputation and recipient
engagement (covered in the companion doc) decide whether you actually land there.
