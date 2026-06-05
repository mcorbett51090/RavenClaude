# Treat the consent store as a system of record — versioned, auditable, and queryable

**Status:** Absolute rule
**Domain:** Privacy / consent engineering
**Applies to:** `data-governance-privacy`

---

## Why this exists

Consent is not a boolean flag in a user record. It is a time-stamped, versioned event: consent version 2.1, granted on 2025-03-15, for purpose `marketing_email`, via consent form URL `/signup/v3`. If the consent version is later updated (a new privacy policy), all pre-existing consents need to be re-solicited. If a user revokes, the revocation must propagate to every downstream system that used their data under that consent basis within a reasonable window. A `consented: true` column in the users table records none of this — it cannot answer "which version did they consent to?" or "when did they revoke?"

## How to apply

```sql
-- Consent events table (append-only log)
CREATE TABLE consent_events (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    subject_id      uuid NOT NULL,                   -- FK to users or accounts
    consent_version varchar(20) NOT NULL,             -- '2.1', '3.0'
    purpose         text NOT NULL,                   -- 'marketing_email', 'analytics'
    action          text NOT NULL,                   -- 'granted', 'revoked', 'expired'
    channel         text,                            -- 'web_signup', 'email_link', 'api'
    ip_address      inet,
    user_agent      text,
    lawful_basis    text NOT NULL,                   -- 'consent', 'contract', 'legitimate_interest'
    recorded_at     timestamptz DEFAULT now(),
    source_url      text                             -- URL of the form/page where consent was given
);

-- Materialized current-consent view (query this, don't JOIN to the event table directly)
CREATE VIEW current_consent AS
SELECT DISTINCT ON (subject_id, purpose)
    subject_id, consent_version, purpose, action, recorded_at
FROM consent_events
ORDER BY subject_id, purpose, recorded_at DESC;
```

**Do:**
- Append a new consent event on every grant, revocation, or version change — never update in-place.
- Propagate revocations to downstream marketing, CRM, and analytics systems within the SLA (24-48 hours for most regulatory frameworks).
- Store the consent form version/URL so you can prove exactly what the subject agreed to.
- Audit the consent store for gaps: any personal-data use requires a current, valid consent record for the relevant purpose.

**Don't:**
- Use `consented: true/false` as a mutable field — it loses history.
- Treat a single all-purposes consent record as sufficient — purposes are granular.
- Delete consent records even after revocation — the history is the proof.

## Edge cases / when the rule does NOT apply

- When lawful basis is `contract` or `legal_obligation`, consent is not required and consent events are not the mechanism. Record the lawful basis in a separate `lawful_basis_log` table instead.

## See also

- [`../agents/privacy-compliance-engineer.md`](../agents/privacy-compliance-engineer.md) — implements the consent store and revocation pipeline
- [`./know-your-lawful-basis-honor-consent.md`](./know-your-lawful-basis-honor-consent.md) — the lawful-basis rule this consent store enforces

## Provenance

GDPR Article 7 requires the controller to be able to demonstrate that consent was given (burden of proof). The append-only event log pattern is the engineering implementation that satisfies this. Codifies data-governance-privacy CLAUDE.md §2 house opinion #3 ("consent is granular, recorded, and revocable").

---

_Last reviewed: 2026-06-05 by `claude`_
