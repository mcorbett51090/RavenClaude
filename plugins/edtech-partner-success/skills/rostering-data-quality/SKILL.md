---
name: rostering-data-quality
description: Diagnose rostering / SIS / LMS data-sync issues in EdTech contexts — K-12 (Clever, ClassLink, OneRoster), higher-ed (SIS/LMS), corporate L&D (HRIS/LMS). When to escalate to product vs coach the partner's admin. Reach for this skill when a partner says "the data isn't right" or when partner-engagement metrics drop without an obvious user-side cause.
---

# Skill: Rostering Data Quality

Rostering issues masquerade as engagement issues. A partner who looks "red" on the health score may simply have a broken sync. **Check the rostering first; declare the partner red second.**

## Step 1 — Identify the rostering surface

Before diagnosing, pin down:

| Segment | Common surfaces |
|---|---|
| K-12 (district / school) | Clever, ClassLink, OneRoster (via Clever/ClassLink or direct), legacy CSV upload from SIS |
| Higher-ed | SIS (Banner, Workday Student, Colleague, Jenzabar), LMS-side rostering (Canvas, Blackboard, D365), LTI integration |
| Corporate L&D | HRIS (Workday, BambooHR, ADP), LMS (Cornerstone, Docebo, Saba, Litmos), SCIM provisioning, identity provider sync (Okta, Azure AD) |

Document which surface is in play for the partner. The diagnostic playbook diverges from here.

## Step 2 — Identify the failure pattern

Common patterns:

- **Stale data** — sync hasn't run in N days. Look at last-sync timestamp first.
- **Partial sync** — some entities synced, others didn't. Usually a permission / scope issue or a vendor-side outage during an incremental window.
- **Schema mismatch** — fields renamed, dropped, or repurposed on one side. Usually a partner-side admin change that wasn't communicated.
- **Identifier drift** — same user has different IDs across systems. Typically caused by email-as-identity changing (marriage, name change, departmental moves) without a stable backing ID.
- **Role / grade misclassification** — users sync but with wrong role / grade / cohort. Typically a partner-side admin mapping error.
- **Orphan accounts** — users in our system who no longer exist in the source of truth. Usually a sync that handles adds but not removes (intentional or otherwise).
- **Duplicate accounts** — users in our system multiple times. Usually a sync re-keying without dedup.

## Step 3 — Decide who owns the fix

This is the most common error. Categorize:

| Failure pattern | Likely owner |
|---|---|
| Stale data, no recent sync | Partner-side admin OR vendor outage. Check vendor status page first; if green, it's the partner. |
| Partial sync | Usually vendor; sometimes a permission / scope change on the partner side |
| Schema mismatch | Partner-side admin change OR our integration regression. Diff our integration's expected schema against current source. |
| Identifier drift | Our integration design (we may be using a non-stable identifier as primary key) |
| Role / grade misclassification | Partner-side admin mapping; coach the partner, don't escalate to engineering |
| Orphan accounts | Our integration design (didn't subscribe to delete events) OR partner-side decision (they want to retain accounts) |
| Duplicate accounts | Our integration design (insufficient dedup logic) |

**Anti-pattern:** assuming the partner is to blame when it's our integration. **Anti-pattern:** assuming engineering needs to fix it when it's a partner-side admin config.

## Step 4 — Verify before escalating

Before opening an engineering ticket OR before pushing the partner to investigate, verify:

- **Vendor status page** — for Clever, ClassLink, Workday, etc. — is there a current outage?
- **Sync logs** — when did the last successful sync run? What did it return?
- **Source-of-truth spot check** — pull 3–5 specific entities from the partner's SIS / HRIS / LMS and compare against our copy. Are they the same?
- **Schema diff** — diff the current source schema against the version our integration expects. Any fields renamed, added, dropped?
- **Partner-side admin** — did the partner make any recent admin changes (school year rollover, new academic term, M&A, reorg)?

A 15-minute verification before escalating saves a 5-day round-trip.

## Step 5 — Communicate the diagnosis to the partner

A partner who heard "your data is broken" without a specific cause will distrust the PSM. The right framing:

- Name the failure pattern in plain language (not "stale data" — "the sync from your Clever account hasn't run since 2026-05-18")
- Name the likely owner clearly (yours / theirs / vendor)
- Propose the specific next step (you check X / they check Y / we open a ticket with vendor Z)
- Set a check-in date (not "I'll follow up" — "I'll check back Friday at 2 ET")

## Step 6 — Document the resolution

The partner profile gets an entry under "prior incidents." Include:
- What broke
- When detected vs when started (the delay is itself a finding — if it took 3 weeks to detect, instrumentation is the gap)
- Who owned the fix
- What the fix was
- What to monitor going forward

A rostering incident that resolves without documentation is a future repeat-incident.

## Step 7 — Escalation paths

- **Partner-side admin coaching** — PSM (`edtech-partner-success-manager`) handles directly; pull `ferpa-comms-translator` if the partner-admin needs a parent / institution-leadership-facing version
- **Vendor outage / vendor-side bug** — open a ticket with the vendor; track in `ravenclaude-core/project-manager`; PSM keeps partner informed
- **Our integration regression** — escalate to `ravenclaude-core/architect` or `data-engineer`; usually requires a code change
- **Persistent identifier-drift issue** — architecture review; `ravenclaude-core/architect`
- **Privacy implication** (e.g., orphan accounts retaining FERPA-covered records past required retention) — mandatory `ravenclaude-core/security-reviewer` and likely `regulatory-compliance` if installed

## What this skill does NOT cover

- Designing the integration architecture (route to `ravenclaude-core/architect`)
- Choosing a rostering vendor (route to `ravenclaude-core/architect`)
- Vendor contract negotiation (out of scope for any agent; that's a business / legal motion)
- Generic data-quality patterns unrelated to EdTech rostering (route to `ravenclaude-core/data-engineer`)
