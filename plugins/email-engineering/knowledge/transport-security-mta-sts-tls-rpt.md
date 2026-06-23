# Transport security — MTA-STS & TLS-RPT (and the ARF feedback loop)

> _Last reviewed 2026-06-22._ The SPF/DKIM/DMARC layer proves a message is
> **authentic**; this layer makes the **SMTP transport** to your domain
> confidential and tamper-resistant, and gives you reporting when it fails. These
> are durable, RFC-grounded mechanics — ported in from the `email-deliverability-
> engineering` proposal (PR #435) because the auth knowledge bank covered
> SPF/DKIM/DMARC/BIMI but not the transport layer.

## Why this layer exists

SMTP's `STARTTLS` is **opportunistic** by default — a man-in-the-middle can strip
the `STARTTLS` advertisement and force mail to be delivered in cleartext, and the
sender has no way to know. MTA-STS lets a receiving domain **declare that senders
MUST use authenticated TLS**, and TLS-RPT gives the receiving domain **reports
when a sender couldn't**. Together they close the downgrade gap that DMARC does
not address (DMARC is about the `From:` identity, not the transport).

## MTA-STS (RFC 8461) — enforce TLS to your domain

Two pieces, both required:

1. **A DNS TXT record** at `_mta-sts.<domain>` — signals that a policy exists and
   carries an `id` that **changes whenever the policy changes** (so senders know
   to re-fetch):
   ```
   _mta-sts.example.com.  IN TXT  "v=STSv1; id=20260622T000000;"
   ```
2. **A policy file** served over HTTPS at a well-known URL on a `mta-sts.`
   subdomain (the HTTPS certificate is what authenticates the policy):
   ```
   https://mta-sts.example.com/.well-known/mta-sts.txt
   ```
   ```
   version: STSv1
   mode: enforce          # testing → enforce (ramp like DMARC)
   mx: mail.example.com
   mx: *.example.net
   max_age: 604800        # seconds senders may cache the policy (e.g. 1 week)
   ```

**Ramp `mode` like DMARC:** start `mode: testing` (failures are reported via
TLS-RPT but mail still flows), confirm the reports are clean, then move to
`mode: enforce`. Going straight to `enforce` with a misconfigured MX or an
expired cert can **block inbound mail**.

## TLS-RPT (RFC 8460) — get reports when TLS fails

A single DNS TXT record at `_smtp._tls.<domain>` naming where aggregate TLS
reports should be sent:
```
_smtp._tls.example.com.  IN TXT  "v=TLSRPTv1; rua=mailto:tls-reports@example.com"
```
Deploy TLS-RPT **first** (or together with MTA-STS `mode: testing`) so you have
visibility before you enforce. Reports surface STARTTLS downgrade attempts,
certificate problems, and MX mismatches.

## How it composes with the auth layer

```
Authentication (who sent it):   SPF + DKIM → DMARC alignment + policy   (RFC 7208/6376/7489)
Transport (how it travelled):   MTA-STS enforce + TLS-RPT reporting     (RFC 8461/8460)
Brand (what the inbox shows):   BIMI (needs DMARC at enforcement)
```

DMARC enforcement is the prerequisite for BIMI; MTA-STS/TLS-RPT are independent of
DMARC but follow the same **deploy-in-reporting-mode-then-enforce** discipline.

## The feedback-loop format — ARF (RFC 5965)

Complaint feedback loops (FBLs) — the mechanism by which a mailbox provider tells
you a recipient hit "report spam" — deliver those complaints in the **Abuse
Reporting Format (ARF, RFC 5965)**: a `multipart/report` message with a
`message/feedback-report` part. The suppression path
([`../skills/bounce-complaint-suppression/SKILL.md`](../skills/bounce-complaint-suppression/SKILL.md))
consumes these; this is the wire format behind it. Suppress every ARF complainer
**immediately and permanently** — repeat sends to a complainer are the fastest way
to lose reputation and breach the bulk-sender complaint ceiling.

## Deployment order (durable checklist)

1. **TLS-RPT** record — start collecting reports (zero risk).
2. **MTA-STS** `mode: testing` + policy file + `_mta-sts` record — failures
   reported, mail still flows.
3. Read TLS-RPT for a cycle; fix any cert/MX issues.
4. **MTA-STS** `mode: enforce` — bump the policy `id` so senders re-fetch.
5. Treat the HTTPS cert on `mta-sts.<domain>` as production infrastructure — an
   expired cert silently invalidates the policy.

## When to reach for this

- A security/compliance requirement to prevent cleartext-mail downgrade.
- Hardening a high-value domain (finance, healthcare, exec comms) beyond DMARC.
- TLS-RPT reports (or a pentest) flag STARTTLS stripping or cert problems.

Not every sender needs `enforce` MTA-STS, but **TLS-RPT is low-risk and worth
deploying broadly** for the visibility alone. DNS provisioning of these records is
a cloud/DNS task (see §9 seams); this plugin specifies *what records must exist
and why*.
