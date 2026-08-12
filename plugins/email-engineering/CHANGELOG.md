# Changelog — email-engineering

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.3.3] — 2026-08-10

Inbox categorization — a new knowledge file + best-practice covering how Gmail tabs (Primary/Promotions/Updates/Social/Forums), Outlook Focused Inbox, and Apple Mail categories work, what header and content signals drive placement, and how to send the right signals per email class.

- **New knowledge doc** `knowledge/inbox-categorization.md` — Gmail tab breakdown, categorization signals (headers: `List-Unsubscribe`/`Precedence:bulk`/ESP headers; content; sender pattern; per-user moves), Gmail Promotions annotations (JSON-LD/schema.org), Outlook Focused Inbox (per-user model, SNDS reputation link), Apple Mail on-device categorization, a Mermaid decision tree for "which tab should my mail land in?", and a volatility note since provider models update without announcement.
- **New best-practice** `best-practices/know-which-tab-your-mail-lands-in.md` — the two-rule model (transactional mail → Primary signals; marketing mail → Promotions is correct), what to check in an audit, and a cross-reference to the knowledge doc.

No agents or skills changed.

## [0.3.0] — 2026-06-22

Reputation-monitoring completeness — folded the one genuinely-additive idea from a retired `marketing-operations` email-deliverability draft (everything else it carried was already covered here, often more deeply).

- **Microsoft SNDS + JMRP as a first-class reputation surface.** The knowledge bank and audit skill leaned entirely on Google Postmaster Tools + DMARC RUA; a Postmaster-only check is blind to Outlook/Hotmail, whose reputation moves independently of Gmail's. Added a "Where you read reputation (the monitoring surfaces)" section to `knowledge/deliverability-fundamentals.md` (Postmaster / SNDS+JMRP / RUA), and threaded SNDS into the `deliverability-audit` skill's reputation step and the `warm-up-new-sending-domains` best-practice.

No agents, skills, templates, or commands added; no frontmatter changed. Knowledge/skill/best-practice text edits only.

## [0.2.0] — 2026-06-22

Transport-security layer — ported from a retired `email-deliverability-engineering` proposal (PR #435).

- **New knowledge doc** `knowledge/transport-security-mta-sts-tls-rpt.md` — MTA-STS (RFC 8461) enforce-ramp + policy file, TLS-RPT (RFC 8460) reporting, and the ARF (RFC 5965) feedback-loop format behind suppression.
- **New best-practice** `best-practices/enforce-transport-security-with-mta-sts.md` — rule for hardening SMTP transport beyond DMARC.

No agents or skills changed.

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
