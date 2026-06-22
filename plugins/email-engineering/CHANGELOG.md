# Changelog — email-engineering

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.1.0] — 2026-06-13

Initial release. A specialist team for getting legitimate mail to the inbox and proving the domain is authentic.

- **2 agents** — `email-deliverability-architect` (SPF/DKIM/DMARC + alignment + staged rollout, BIMI, warm-up, stream separation, spam triage, Gmail/Yahoo compliance) and `email-sending-engineer` (ESP integration, idempotent sends + webhooks, suppression, MJML templates). Full scenario-authoring frontmatter.
- **5 skills** — `email-authentication-setup`, `deliverability-audit`, `transactional-email-integration`, `email-template-engineering`, `bounce-complaint-suppression`.
- **Knowledge bank (3 docs)** — `email-authentication-decision-tree.md` (3 Mermaid trees: auth setup / spam diagnosis / ESP choice, + the alignment table and Gmail/Yahoo gates), `deliverability-fundamentals.md` (the stable model), `esp-capability-map-2026.md` (dated, `[verify-at-use]` vendor comparison).
- **8 best-practices** — authenticate; align-not-just-pass; staged DMARC rollout; stream separation; warm-up; idempotent sends+webhooks; one-click unsubscribe + suppression; volatile-claims-carry-dates.
- **3 templates** — DMARC rollout plan, transactional email spec, deliverability incident runbook.
- **4 commands** — set-up-email-authentication, audit-email-deliverability, diagnose-bounce-or-spam-spike, design-transactional-email.
- **Scenarios bank** — README + 2 dated scenarios (`p=reject` broke forwarding; Gmail/Yahoo bulk-sender compliance).
- **Runnable linter** `scripts/email_auth_lint.py` — SPF/DMARC record linter (lookup-count, `+all`, `p=reject` with no `rua`, `pct` range). Stdlib only, ruff-clean, **no DNS lookups / no deps**.
- **1 advisory hook** `flag-email-smells.sh` — flags DMARC-enforce-with-no-rua, SPF `+all`, a committed ESP secret, and bulk mail with no `List-Unsubscribe`. Set `EMAIL_ENG_STRICT=1` to make it blocking.

Seams: campaign strategy → `marketing-operations`; sending infra → `backend-engineering`; webhook contract → `api-engineering`; DNS/SES → the cloud plugins; auth-secret/webhook verdicts → `security-engineering`. Requires `ravenclaude-core@>=0.7.0`.

### Accuracy note

Email-auth mechanics are RFC-grounded (Tier 1). Gmail/Yahoo bulk-sender thresholds and BIMI/VMC requirements are **volatile** and carry `[verify-at-use]` riders + retrieval dates throughout the knowledge bank — re-verify against current provider guidance before a client commitment.
