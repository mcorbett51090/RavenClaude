# Email-engineering best-practices

> The codified house rules the `email-deliverability-architect` and `email-sending-engineer` enforce. Each file is a single rule with why/how/edge-cases/provenance. The advisory hook ([`../hooks/flag-email-smells.sh`](../hooks/flag-email-smells.sh)) mechanically flags a subset.

| Rule | Status | What it guards |
| --- | --- | --- |
| [`authenticate-with-spf-dkim-dmarc.md`](authenticate-with-spf-dkim-dmarc.md) | Absolute | Every sending domain publishes SPF + DKIM + DMARC |
| [`align-dmarc-not-just-pass.md`](align-dmarc-not-just-pass.md) | Absolute | Alignment, not pass/fail, is the deliverable |
| [`roll-out-dmarc-from-none-to-reject.md`](roll-out-dmarc-from-none-to-reject.md) | Absolute | Never publish `p=reject` blind |
| [`separate-transactional-and-marketing-streams.md`](separate-transactional-and-marketing-streams.md) | Strong default | Reputation isolation by subdomain |
| [`warm-up-new-sending-domains.md`](warm-up-new-sending-domains.md) | Strong default | A cold blast looks like spam |
| [`make-sends-and-webhooks-idempotent.md`](make-sends-and-webhooks-idempotent.md) | Absolute | Exactly-once under at-least-once delivery |
| [`honor-one-click-unsubscribe-and-suppress.md`](honor-one-click-unsubscribe-and-suppress.md) | Absolute | Complaints are cheaper to prevent than recover |
| [`volatile-deliverability-claims-carry-retrieval-dates.md`](volatile-deliverability-claims-carry-retrieval-dates.md) | Absolute | Gmail/Yahoo/BIMI specifics drift |
| [`enforce-transport-security-with-mta-sts.md`](enforce-transport-security-with-mta-sts.md) | Strong default | Close the opportunistic-STARTTLS downgrade gap (MTA-STS + TLS-RPT) |

## Promotion path

When ≥2 independent scenarios corroborate a new lesson, an agent may propose promoting it into a new best-practice file here or a knowledge-bank decision tree.
