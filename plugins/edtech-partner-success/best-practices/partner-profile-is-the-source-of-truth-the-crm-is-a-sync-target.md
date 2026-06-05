# Partner profile is the source of truth — the CRM is a sync target

**Status:** Absolute rule
**Domain:** EdTech partner profile management
**Applies to:** `edtech-partner-success`

---

## Why this exists

Most CS teams build their institutional memory inside the CRM: contact records, activity logs, renewal dates. The CRM is the right place for pipeline data and activity-log dates. It is the wrong place for the durable record of what the partner has been promised, what they care about, and what the relationship arc looks like across multiple PSM owners. CRM data structures are optimized for deal and contact management, not for preserving the context that survives a PSM handoff. When the PSM changes, the CRM record tells the new owner who they spoke to last and when; the partner profile tells them what was promised, what the district values, and what will matter in the next conversation. The CRM is a sync target for task data; the profile is the canon.

## How to apply

Maintain the partner profile as a distinct document (using the plugin's `partner-profile.md` template) and keep the CRM synced to its key dates and contacts — not the other way around.

```
Partner profile vs. CRM — what lives where:

  Partner profile (canonical):
    — Institutional history: key events, product adoptions, expansions, incidents
    — Named programs and initiatives the district cares about
    — Decision-makers with role, tenure, known priorities, and "what they care about"
    — Prior promises and commitments (what was said in the last QBR, last renewal)
    — Renewal-risk posture and history (prior near-churn, prior expansions)
    — What the PSM should NOT say or push (anti-patterns for this specific partner)

  CRM (sync target):
    — Activity dates and types (call on [date], email on [date])
    — Renewal date, contract value, product line
    — Contact names and titles (mirror from profile; CRM is the scheduling surface)
    — Opportunity stage and dollar value

  Rule: the partner profile is updated by the PSM after every meaningful touch.
  If the profile and the CRM disagree on what was promised, the profile is correct.
```

**Do:**
- Update the partner profile within 24 hours of any meaningful touch that produces a new commitment or reveals new context.
- Treat a PSM handoff as a profile-completeness review, not just a CRM activity-log transfer.
- Store the partner profile in a location accessible to the incoming PSM (shared drive, wiki, CS platform notes).

**Don't:**
- Use the CRM activity log as the only source of context for a partner — it records when, not what matters.
- Let the partner profile go stale for more than 60 days while the PSM is actively working the account.
- Treat the profile as optional documentation — it is the continuity asset.

## Edge cases / when the rule does NOT apply

For very small books (fewer than 10 partners), the PSM may maintain a single well-structured notes document rather than a formal profile per the template; the canon vs. sync-target principle still applies. For partners where the CRM itself has a rich structured note field and the team has a discipline around updating it with context (not just activity), the CRM can serve as the profile location — but the discipline must be deliberate and documented.

## See also

- [`../agents/partner-profile-curator.md`](../agents/partner-profile-curator.md) — owns the durable partner record and the update discipline.
- [`./risk-confirm-the-decision-maker-is-alive-in-the-role-every-quarter.md`](./risk-confirm-the-decision-maker-is-alive-in-the-role-every-quarter.md) — the companion rule on keeping the decision-maker record current, which the profile owns.

## Provenance

Codifies the plugin's §3 house opinion #1 ("The partner profile is the source of truth, not the CRM"). The CRM-as-canon error leads directly to lost institutional memory on PSM handoffs; the profile-first discipline is the structural fix.

---

_Last reviewed: 2026-06-05 by `claude`_
