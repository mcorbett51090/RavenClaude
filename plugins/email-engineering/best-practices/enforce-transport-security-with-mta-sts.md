# Deploy TLS-RPT, then ramp MTA-STS to enforce

**Status:** Strong default (Absolute for high-value domains — finance, healthcare,
exec comms).

**Rule.** SMTP `STARTTLS` is opportunistic and strippable, so a domain that wants
confidential inbound transport publishes **MTA-STS** (RFC 8461) to require
authenticated TLS and **TLS-RPT** (RFC 8460) to get reports when a sender
couldn't. Deploy TLS-RPT first (zero risk), run MTA-STS in `mode: testing` until
the reports are clean, then move to `mode: enforce` — and bump the policy `id`
whenever the policy changes.

## Why

DMARC proves the `From:` identity but says nothing about whether the message
travelled encrypted. Without MTA-STS, a man-in-the-middle can strip the
`STARTTLS` advertisement and force cleartext delivery, invisibly. MTA-STS closes
that gap; TLS-RPT is how you find out it's happening.

## How

- `_smtp._tls.<domain>` TXT → `v=TLSRPTv1; rua=mailto:...` (reporting).
- `_mta-sts.<domain>` TXT → `v=STSv1; id=<changes-on-edit>;`.
- `https://mta-sts.<domain>/.well-known/mta-sts.txt` → the policy (`mode`, `mx`,
  `max_age`). Treat that HTTPS cert as production infra — an expired cert silently
  invalidates the policy.

## Edge cases / failure modes

- **Going straight to `enforce`** with a wrong MX or an expired cert can **block
  inbound mail** — always ramp through `testing`.
- **Forgetting to bump `id`** after editing the policy → senders keep the cached
  old policy until `max_age` expires.

## Provenance

RFC 8461 (MTA-STS), RFC 8460 (TLS-RPT). Full mechanics + deployment order:
[`../knowledge/transport-security-mta-sts-tls-rpt.md`](../knowledge/transport-security-mta-sts-tls-rpt.md).
Ported from the retired `email-deliverability-engineering` proposal (PR #435).
