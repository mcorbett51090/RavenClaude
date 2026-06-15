# email-deliverability-engineering plugin

> The **engineering of email deliverability** for the RavenClaude marketplace:
> the authentication, sending infrastructure, and reputation work that decides
> whether your transactional and marketing email lands in the **inbox** or the
> spam folder. It answers **"why is our mail going to spam, and what records and
> practices fix it?"** — not what the email *says* (that's `marketing-operations`).

**Designed for:** an engineer, platform/ops owner, or technical marketer
responsible for an organization's outbound email — transactional (receipts,
password resets) and/or bulk (newsletters, lifecycle) — who needs to set up or
repair SPF/DKIM/DMARC, meet the Google/Yahoo 2024 bulk-sender requirements, and
keep domain reputation healthy.

## What this plugin gives you

- A correct, aligned **authentication stack** — SPF (RFC 7208), DKIM (RFC 6376),
  and **DMARC** (RFC 7489) with *alignment* understood (not just "records exist"),
  plus BIMI, MTA-STS, and TLS-RPT where they earn their keep.
- A concrete path to the **Google/Yahoo 2024 bulk-sender requirements**: DMARC at
  the org domain, one-click `List-Unsubscribe` (RFC 8058), and keeping the
  Postmaster-Tools complaint rate under 0.3%.
- A **reputation model** you can act on — domain vs IP reputation, subdomain
  separation (marketing vs transactional), warmup, and a recovery path when
  reputation has already tanked.
- **Feedback-loop + list-hygiene** mechanics — bounce classification (hard vs
  soft), complaint (FBL/ARF) handling, suppression lists, and sunset policies.
- An **incident triage** runbook for "deliverability dropped" — is it auth,
  reputation, content, list, or the receiver?

## The two agents

| Agent | Owns |
|---|---|
| `deliverability-architect` | The end-to-end sending posture: domain/subdomain strategy, the auth stack design, reputation model, warmup plan, ESP/MTA selection at a posture level, and the 2024-bulk-sender compliance plan. |
| `email-auth-engineer` | The concrete records and headers: writing/auditing SPF, DKIM key rotation, the DMARC record + reporting + the `p=none → quarantine → reject` enforcement ramp, MTA-STS/TLS-RPT policy files, BIMI, and reading DMARC aggregate (RUA) reports. |

## The two skills

| Skill | What's inside |
|---|---|
| `email-auth-audit` | A step-by-step audit of a domain's SPF/DKIM/DMARC/MTA-STS/TLS-RPT/BIMI posture, with the exact checks, the common failure modes (alignment, the SPF 10-lookup limit, `+all`, missing DKIM alignment), and a prioritized fix list. |
| `deliverability-incident-triage` | A runbook for a sudden inbox-placement drop: a decision tree that isolates auth vs reputation vs content vs list vs receiver, the evidence to gather (DMARC RUA, Postmaster Tools, bounce/complaint rates), and the recovery sequence. |

## When to use it

- You're standing up sending for a new domain and need the auth stack + warmup
  plan done right *before* the first send.
- Your mail started going to spam, or a mailbox provider began rejecting it after
  the 2024 sender rules took effect, and you need to find and fix the cause.
- You need to ramp DMARC from `p=none` to `p=reject` without blackholing
  legitimate mail (third-party senders, forwarding).

## When *not* to use it

- You need campaign strategy, segmentation, subject lines, or content — that's
  `marketing-operations`.
- You need the DNS zone *provisioned* in a cloud/registrar — that's
  `devops-cicd` / the cloud plugins. This plugin tells you **what records must
  exist and why**; they apply them.
- You need a security *verdict* on a broader system — escalate to
  `security-engineering` / `ravenclaude-core/security-reviewer`.

## Seams to neighbouring plugins

- **`marketing-operations`** — campaign strategy/content/segmentation (above this layer).
- **`devops-cicd` / cloud plugins** — DNS record provisioning + sending-host infra.
- **`api-engineering` / `fintech-payments-engineering`** — generic webhook plumbing;
  this owns the *ESP bounce/complaint/FBL webhook semantics*.
- **`data-governance-privacy`** — consent + retention for the subscriber list.
- **`ravenclaude-core`** — the domain-neutral constitution + security-reviewer.

## Requires

- `ravenclaude-core@>=0.7.0`.

See [`CLAUDE.md`](CLAUDE.md) for the team constitution and house opinions.
