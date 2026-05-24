---
name: implementation-90-day-arc
description: Run the 90-day technical-onboarding arc for a newly-contracted EdTech partner — discovery (weeks 1-2) → integration setup (3-4) → train-the-trainer (5-6) → go-live + Day-30 measurement (7-8) → stabilization + PSM handoff (9-12). Calendar-dead-zone go-live check is the highest-leverage pre-flight. Used by `partner-success-manager` + `learning-analytics-analyst`.
---

# Skill: implementation-90-day-arc

> **Invoked by:** `partner-success-manager` (the primary owner; coordinates the arc), `learning-analytics-analyst` (first-30-day measurement + signal-baseline establishment).
>
> **When to invoke:** at contract close, alongside [`success-plan-authoring.md`](../success-plan-authoring/SKILL.md). Use throughout the 90-day arc as the playbook for what should be happening when.
>
> **Output:** a filled [`../templates/implementation-90-day-plan.md`](../../templates/implementation-90-day-plan.md) + a coordinated handoff at Day 90 from implementation-team-as-primary-contact to PSM-as-primary-contact.

## What this skill is and isn't

**It is:** the playbook for the 90-day technical-onboarding arc — rostering setup, SSO config, district-admin training, train-the-trainer, first-30-day measurement.

**It isn't:** the success-plan (outcome-side, that's [`success-plan-authoring.md`](../success-plan-authoring/SKILL.md)). It isn't the onboarding-checklist (relationship-side, that's [`../templates/onboarding-checklist.md`](../../templates/onboarding-checklist.md)). Implementation is the *technical* arc; the success plan is the *outcome* arc; the onboarding checklist is the *relationship* arc. All three run in parallel and the PSM coordinates.

> **Why this skill exists, not a new agent (per house-rule 2026-05-21):** the implementation arc has genuine technical content but the indistinguishability test was: could `partner-success-manager` + this skill + the SIS/SSO knowledge file produce equivalent output? The answer is yes when the knowledge file is rich enough. Revisit for agent-promotion in v0.6.0 if live engagement signal proves structural distinctness.

## The arc shape

```
W1-2  Discovery & config prep        → kickoff, SIS/SSO mapping, calendar check, data-protection rider
W3-4  Integration setup              → rostering sync test, SSO config, sub-processor disclosure
W5-6  Train-the-trainer + admin      → train-the-trainer session, admin enablement, runbook handoff
W7-8  Go-live + day-30 measurement   → production go-live, Day 3 / 7 / 14 / 21 / 30 check-ins
W9-12 Stabilization + PSM handoff    → retrospective, partner-profile update, first scheduled QBR
```

Reference: [`../../templates/implementation-90-day-plan.md`](../../templates/implementation-90-day-plan.md) for the per-week checklist.

## The flow

1. **At contract close:** PSM + implementation-team-contact (per [`../../templates/cross-functional-partnership-map.md`](../../templates/cross-functional-partnership-map.md) Implementation row) jointly fill in the 90-day-plan template header (partner, segment, contract date, target go-live, partner-side technical lead, partner-side curricular lead).
2. **Calendar check (critical):** target go-live must NOT land in a known K-12 dead zone (late August setup, Thanksgiving week, winter break, state testing, end-of-year wrap). Per [`../../knowledge/k12-psm-operating-cadence.md`](../../knowledge/k12-psm-operating-cadence.md). Push the go-live forward or back if the default lands in a dead zone — this is the single most common reason 90-day arcs fail.
3. **Technical configuration:** consult [`../../knowledge/sis-sso-rostering-integration-patterns.md`](../../knowledge/sis-sso-rostering-integration-patterns.md) for SIS-specific quirks (OneRoster, Clever, ClassLink, PowerSchool, Infinite Campus, Skyward, Synergy) and SSO patterns (SAML/OIDC against AD, Google Workspace for Education, Azure AD).
4. **Failure-mode pre-flight:** consult [`../../knowledge/district-implementation-failure-modes.md`](../../knowledge/district-implementation-failure-modes.md) and pre-emptively check each pattern against the current partner. Most failures are predictable.
5. **Train-the-trainer:** use [`../../templates/train-the-trainer-curriculum.md`](../../templates/train-the-trainer-curriculum.md). Direct vendor-to-teacher training doesn't scale in K-12; train-the-trainer is the only model that does.
6. **First-30-day measurement:** at Day 30 post-go-live, `learning-analytics-analyst` runs the adoption-baseline snapshot. This becomes the comparison point for every subsequent adoption signal.
7. **Day-90 handoff:** the implementation team formally transfers primary-contact status to the PSM (per the [`../../templates/cross-functional-partnership-map.md`](../../templates/cross-functional-partnership-map.md) Implementation function hand-back criterion: "implementation milestones met + first 30/60/90 outcomes documented"). PSM is now the front door for all partner communication.

## The non-negotiable failure-mode checks (at Day 90, before declaring success)

Per [`../../knowledge/district-implementation-failure-modes.md`](../../knowledge/district-implementation-failure-modes.md):

- [ ] **Trained-trainers actually trained someone** (not just attended sessions). Cascade is real, not theoretical.
- [ ] **Rostering completeness validated against partner's own data** (not just "the sync ran successfully"). Spot-check 10 users across roles + schools.
- [ ] **SSO works for ALL roles**, not just admins. Students and teachers often route through different IdPs.
- [ ] **First-30-day measurement is real**, not aspirational. Baseline numbers in the partner-profile.
- [ ] **Named partner-side technical lead is still in role** (or, if they left, named-decision-maker handoff is complete).
- [ ] **Go-live was not in a dead zone** (most common failure: go-live lands in late August setup or state testing). If it was, retrospective explicitly flags this for the next implementation.

## Anti-patterns this skill flags

- **Skipping the calendar check.** Default-scheduled go-lives land in dead zones constantly. The 90-day arc starts before the calendar check, so the PSM has to insert it deliberately.
- **Train-the-trainer that doesn't include "facilitation craft."** Equipping champions on PRODUCT depth but not on HOW TO RUN A TRAINING SESSION is the most common reason trained-trainers never train anyone. The curriculum template covers both.
- **Implementation handoff to PSM without documentation.** The PSM inherits the relationship cold if the implementation team didn't update the partner-profile with technical config + named champions + technical lead + prior incidents.
- **Rostering validated by "sync ran successfully" instead of partner-side spot-check.** A sync that completes successfully can still be missing entire schools or roles. Cross-reference [`../../knowledge/rostering-data-quality-typology.md`](../../knowledge/rostering-data-quality-typology.md).
- **Champion redundancy of 1.** Implementing with only one trained-trainer means the cascade dies if that champion gets reassigned. Train 2-3 from the start.
- **First-30-day measurement that's never reviewed.** Capture the numbers + the PSM-AE-CSM team reviews them + the partner sees them. Otherwise the baseline doesn't exist operationally.

## When NOT to invoke

- The partner is post-implementation. Use [`success-plan-authoring.md`](../success-plan-authoring/SKILL.md) for ongoing engagement.
- The partner is a renewal expansion (additional schools to an existing deployment). The 90-day arc is for net-new implementations; expansion uses a lighter sub-implementation pattern (typically 30-45 days).
- The partner is corporate L&D or higher-ed — the K-12-specific dead zones + train-the-trainer assumptions don't transfer directly. Use the broader [`../knowledge/edtech-segment-fundamentals.md`](../../knowledge/edtech-segment-fundamentals.md) overlay.

## Refresh triggers

- Major SIS or SSO surface change (new OneRoster version, new district IdP pattern)
- New product line that adds significant technical-onboarding surface
- The `/wrap` slash command surfaces an implementation scenario the failure-modes knowledge file didn't anticipate
- House-rule revisit: if 3+ live implementation engagements show this skill genuinely needs an agent (not just richer knowledge), promote in v0.6.0

## References

- [`../../templates/implementation-90-day-plan.md`](../../templates/implementation-90-day-plan.md) — the per-week checklist artifact
- [`../../knowledge/sis-sso-rostering-integration-patterns.md`](../../knowledge/sis-sso-rostering-integration-patterns.md) — SIS / SSO technical reference
- [`../../knowledge/district-implementation-failure-modes.md`](../../knowledge/district-implementation-failure-modes.md) — patterns to pre-check
- [`../../knowledge/k12-psm-operating-cadence.md`](../../knowledge/k12-psm-operating-cadence.md) — dead-zone calendar
- [`../../knowledge/rostering-data-quality-typology.md`](../../knowledge/rostering-data-quality-typology.md) — rostering-completeness validation
- [`../../knowledge/parent-comms-jurisdictional-bear-traps.md`](../../knowledge/parent-comms-jurisdictional-bear-traps.md) — data-protection rider state variance
- [`../../templates/train-the-trainer-curriculum.md`](../../templates/train-the-trainer-curriculum.md) — train-the-trainer artifact
- [`../../templates/cross-functional-partnership-map.md`](../../templates/cross-functional-partnership-map.md) — Implementation function row routing
- [`success-plan-authoring.md`](../success-plan-authoring/SKILL.md) — the outcome-side counterpart skill
- [`partner-health-scoring.md`](../partner-health-scoring/SKILL.md) — health-score baseline established at Day 30
