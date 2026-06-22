# Email authentication & deliverability decision trees

> Source of truth for the auth-setup and diagnosis branches. Agents carry compact inline priors; this file is re-read on demand.
>
> _Last reviewed: 2026-06-13 by `claude`. Confidence: Tier 1 (SPF/DKIM/DMARC mechanics are stable RFCs — RFC 7208 SPF, RFC 6376 DKIM, RFC 7489 DMARC, RFC 8058 one-click unsubscribe). Volatile specifics (Gmail/Yahoo thresholds, BIMI/VMC requirements) are flagged inline and carry a re-verify rider._

---

## Tree 1 — Authenticate → Align → Enforce (setup)

```mermaid
flowchart TD
  A[Domain needs to send] --> B{SPF published?}
  B -- no --> B1[Publish TXT v=spf1 include:ESP ~all<br/>≤10 DNS lookups] --> C
  B -- yes --> C{DKIM signing?}
  C -- no --> C1[Publish ESP DKIM key<br/>selector._domainkey, 2048-bit] --> D
  C -- yes --> D{Does an authenticated<br/>identifier ALIGN with From:?}
  D -- no --> D1[Fix return-path / d= to a<br/>subdomain of the From: domain] --> E
  D -- yes --> E[Publish DMARC p=none; rua=...]
  E --> F{RUA reports show all<br/>legitimate streams aligned?}
  F -- no --> F1[Find + fix the unaligned source<br/>stay at p=none] --> F
  F -- yes --> G[p=quarantine; pct=25 → ramp to 100]
  G --> H[p=reject]
  H --> I{Want brand logo in inbox?}
  I -- yes --> I1[BIMI record + VMC/CMC cert<br/>VERIFY current requirement]
  I -- no --> Z[Done — enforced + aligned]
```

**The rule the tree encodes:** you cannot meaningfully enforce (`reject`) before you align, and you should not align-and-enforce blind — `p=none` + RUA reports are the evidence gate. SPF authenticates the envelope/return-path; DKIM signs the `d=` domain; DMARC requires one of them to **align** with the visible `From:`.

| Mechanism | Authenticates | Alignment check | Breaks on |
| --- | --- | --- | --- |
| SPF (RFC 7208) | envelope return-path | return-path domain == From: domain | **forwarding** (return-path changes) |
| DKIM (RFC 6376) | the `d=` signing domain | `d=` domain == From: domain | message body modified in transit |
| DMARC (RFC 7489) | the From: domain (via SPF **or** DKIM align) | n/a — it's the policy | neither SPF nor DKIM aligns |

> Because SPF breaks on forwarding, **DKIM alignment is the durable one** — design so DKIM aligns, and SPF is the bonus.

---

## Tree 2 — "Why are we landing in spam?" (diagnosis)

```mermaid
flowchart TD
  S[Mail landing in spam] --> A{SPF & DKIM pass?<br/>check Authentication-Results}
  A -- no --> A1[Fix authentication first<br/>→ email-authentication-setup] --> done
  A -- yes --> B{DMARC passes — i.e. an<br/>identifier ALIGNS with From:?}
  B -- no --> B1[Align return-path / d= to From:<br/>the 'but we have SPF!' trap] --> done
  B -- yes --> C{Domain/IP warmed?<br/>Postmaster reputation OK?}
  C -- no --> C1[Warm-up ramp / cut volume /<br/>isolate the bad stream] --> done
  C -- yes --> D{Complaint & bounce<br/>rates under threshold?}
  D -- no --> D1[Suppress bounces+complaints,<br/>stop bad lists, confirm opt-in] --> done
  D -- yes --> E{Content OK? text part,<br/>HTML<102KB, links aligned?}
  E -- no --> E1[Fix message: add text part,<br/>shrink, fix link domains] --> done
  E -- yes --> F[Likely a provider-specific<br/>reputation/filter issue →<br/>Postmaster Tools + ESP support]
  done[Confirm via Postmaster Tools / RUA]
```

**Order matters:** never debug content (E) before authentication/alignment (A-B). A lower layer is meaningless if a higher one fails.

---

## Tree 3 — Which ESP / sending architecture?

```mermaid
flowchart TD
  N[Need to send email] --> T{Transactional, marketing,<br/>or both?}
  T -- transactional --> X[Postmark / Resend / SES<br/>fast, deliverability-focused]
  T -- marketing --> Y[SendGrid Mktg / Mailchimp /<br/>Customer.io — list + campaign tooling]
  T -- both --> Z[Separate SUBDOMAINS per stream<br/>e.g. notifications. vs news.<br/>isolate reputation]
  X --> V{High volume / cost-sensitive<br/>+ already on AWS?}
  V -- yes --> V1[Amazon SES — cheapest,<br/>you own more of the stack]
  V -- no --> V2[Postmark/Resend — DX + speed,<br/>more managed]
```

See [`esp-capability-map-2026.md`](esp-capability-map-2026.md) for the dated feature comparison. The **stream-separation rule is non-negotiable**: transactional and marketing never share a sending subdomain, so a marketing reputation dip can't drop password-reset mail.

---

## Gmail / Yahoo bulk-sender requirements (volatile — verify)

For senders of **5,000+ messages/day** to Gmail/Yahoo (announced Oct 2023, enforced from **Feb 2024**):

1. **Authenticate** with SPF **and** DKIM, and publish a **DMARC** policy (at least `p=none`).
2. **One-click unsubscribe** — `List-Unsubscribe` + `List-Unsubscribe-Post: List-Unsubscribe=One-Click` (RFC 8058), honored within a short window (provider guidance: ~2 days).
3. **Spam-complaint rate** kept low — guidance targets staying **well under ~0.3%** (and never spiking to it), measured in Google Postmaster Tools.

> ⚠️ The exact thresholds, dates, and message-volume bars are **volatile** — re-verify against the current Gmail/Yahoo postmaster documentation before quoting to a client. Marked `[verify-at-use]`; map last reviewed 2026-06-13.
