# email-engineering

> A RavenClaude plugin for the systems that put mail in the **inbox, not the spam folder** — domain authentication, deliverability, ESP integration, responsive templates, and the bounce/complaint feedback loop.

## What you get

Two specialist agents:

- **email-deliverability-architect** — SPF/DKIM/DMARC setup + alignment + a safe `p=none → quarantine → reject` rollout, BIMI, domain/IP warm-up, transactional/marketing stream separation, spam-landing triage, and Gmail/Yahoo bulk-sender compliance.
- **email-sending-engineer** — ESP integration (SES/SendGrid/Postmark/Resend/Mailgun), idempotent sends, signature-verified idempotent webhook handling, suppression enforcement, and responsive MJML templates that survive Outlook, Gmail clipping, and dark mode.

Plus **5 skills**, a **3-doc knowledge bank** (3 Mermaid decision trees — auth setup, spam diagnosis, ESP choice — and a dated 2026 ESP capability map), **8 best-practices**, **3 templates**, **4 commands**, a **scenarios bank**, a stdlib **SPF/DMARC record linter** (`scripts/email_auth_lint.py`), and **1 advisory hook**.

## Install

```shell
/plugin marketplace add ./        # from a separate Claude Code project
/plugin install email-engineering@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.

## Commands

- `/email-engineering:set-up-email-authentication` — produce the SPF/DKIM/DMARC records + staged rollout.
- `/email-engineering:audit-email-deliverability` — find the failing layer when mail goes to spam.
- `/email-engineering:diagnose-bounce-or-spam-spike` — stop a bounce/complaint spike, protect reputation.
- `/email-engineering:design-transactional-email` — idempotent send + verified webhook + responsive template.

## What this plugin is NOT

- **Not** campaign strategy/copy/segmentation — that's `marketing-operations`. This is the **delivery plumbing**.
- **Not** the sending queue/worker — that's `backend-engineering`; the webhook contract is `api-engineering`.
- **Not** DNS hosting / SES provisioning — that's the cloud plugins (`aws-cloud` / `azure-cloud` / `gcp-cloud`).

## House line

Authenticate, then **align** (alignment, not pass/fail, is the deliverable). Never publish `p=reject` blind. Separate transactional from marketing. Build for exactly-once on top of idempotency. One-click unsubscribe is a deliverability feature. Volatile provider rules carry a retrieval date.

## The auth linter

```shell
python3 plugins/email-engineering/scripts/email_auth_lint.py dmarc "v=DMARC1; p=reject; rua=mailto:dmarc@example.com"
python3 plugins/email-engineering/scripts/email_auth_lint.py spf   "v=spf1 include:sendgrid.net ~all"
```

Stdlib only, no DNS lookups, no third-party deps.
