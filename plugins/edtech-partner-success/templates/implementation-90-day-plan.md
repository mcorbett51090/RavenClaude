# Implementation 90-day plan — `<partner_name>`

> **What this is.** The 90-day implementation runbook for a newly-contracted partner. Covers the technical-onboarding arc (rostering setup, SSO config, district-admin training, train-the-trainer, first-30-day measurement) that the `edtech-partner-success-manager` agent coordinates with `learning-analytics-analyst` and the partner's IT counterpart.
>
> **When to fill in.** At contract close, alongside the [`success-plan.md`](success-plan.md). The implementation plan is the *technical* counterpart to the success plan's *outcome* framing.
>
> **Pair with:** [`../skills/implementation-90-day-arc/SKILL.md`](../skills/implementation-90-day-arc/SKILL.md) (the playbook), [`../knowledge/sis-sso-rostering-integration-patterns.md`](../knowledge/sis-sso-rostering-integration-patterns.md) (the technical reference), [`../knowledge/district-implementation-failure-modes.md`](../knowledge/district-implementation-failure-modes.md) (what to watch for).

---

## Header

- **Partner:** `<name>`
- **Segment:** `<K-12 / higher-ed / corp L&D>`
- **Contract close:** `<YYYY-MM-DD>`
- **Target go-live:** `<YYYY-MM-DD>` (typically 60-75 days after close for K-12; tighter for higher-ed; variable for corp L&D)
- **PSM owner:** `<name>`
- **Partner-side technical lead:** `<name + role>` (e.g., district IT director, SIS admin, registrar)
- **Partner-side curricular lead:** `<name + role>` (e.g., curriculum director, instructional coach lead)
- **Implementation team contact (vendor-side):** `<name + role>` per `cross-functional-partnership-map.md`

## Week-by-week (the 90-day arc)

### Weeks 1-2 — Discovery and configuration prep

- [ ] Kickoff call with partner-side technical + curricular leads + PSM + implementation team
- [ ] Identify the partner's **SIS** (PowerSchool / Infinite Campus / Skyward / Synergy / other) and integration approach (Clever / ClassLink / OneRoster direct)
- [ ] Identify the partner's **SSO** (SAML / OIDC / district IdP — Active Directory, Google Workspace for Education, Azure AD, district-managed)
- [ ] Map the rostering data: which roles (student, teacher, admin, parent), which scopes (school-level, district-level), which sub-organizations
- [ ] Identify the **named decision-maker** for technical sign-off (often distinct from contract signer)
- [ ] **Calendar check:** confirm go-live target doesn't land in a dead zone (per [`../knowledge/k12-psm-operating-cadence.md`](../knowledge/k12-psm-operating-cadence.md))
- [ ] **Document the partner's data-protection rider requirements** (NY Ed Law §2-d, IL SOPPA, CA SOPIPA — per [`../knowledge/parent-comms-jurisdictional-bear-traps.md`](../knowledge/parent-comms-jurisdictional-bear-traps.md))

### Weeks 3-4 — Integration setup

- [ ] Rostering integration configured + first sync run (test environment)
- [ ] SSO configuration tested end-to-end with at least one user per role
- [ ] Initial roster validated by partner: spot-check 10 users (mix of roles + schools)
- [ ] Sub-processor disclosure list shared with partner if required by state law
- [ ] AI-feature data-flow disclosed if product touches AI (post April 22, 2026 COPPA full enforcement requires separate opt-in for under-13 AI training)

### Weeks 5-6 — Train-the-trainer + admin enablement

- [ ] District admin training: 2-hour session covering admin console, user provisioning, troubleshooting basics
- [ ] Train-the-trainer session: identify 2-3 partner-side internal champions; equip them to run subsequent training waves
- [ ] Implementation runbook handed to partner-side IT (escalation paths, support contacts, vendor SLAs)
- [ ] First-month communication template sent to partner for their own internal distribution (the partner sends to staff, not the vendor)

### Weeks 7-8 — Go-live + first-30-day measurement

- [ ] Production go-live (rollout strategy: all-schools-day-one / cohort / school-by-school)
- [ ] Day-3 check-in: sync still working? auth issues? user complaints?
- [ ] Day-7 check-in: usage starting? feature-X engagement?
- [ ] Day-14 check-in: are the trained-trainers running their own sessions? Is adoption sequencing matching [`../knowledge/k12-adoption-arc-fall-spring-summer.md`](../knowledge/k12-adoption-arc-fall-spring-summer.md)?
- [ ] Day-21 check-in: any rostering drift since week 4? Run a delta check
- [ ] Day-30 measurement: full adoption-baseline established; first health-score snapshot recorded

### Weeks 9-12 — Stabilization + handoff to ongoing PSM motion

- [ ] First implementation retrospective with partner: what worked, what didn't, what to refine for next-school-year expansion
- [ ] Implementation team formally hands off to PSM as primary contact (per [`cross-functional-partnership-map.md`](cross-functional-partnership-map.md) — Implementation function row hand-back criterion)
- [ ] Year-1 success plan reviewed and refined (the implementation is done; the *engagement* begins)
- [ ] Partner profile updated with: technical config (SIS, SSO, rostering vendor), named champions, technical lead, prior incidents from implementation
- [ ] First scheduled QBR for ~Day 60 of school year

## Risk register (fill in as the arc progresses)

| Risk | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|
| `<e.g., partner SIS sync delayed>` | `<low/med/high>` | `<low/med/high>` | `<mitigation>` | `<name>` |

## Failure-mode checks

Before declaring the 90 days complete, audit against [`../knowledge/district-implementation-failure-modes.md`](../knowledge/district-implementation-failure-modes.md):

- [ ] No "trained-trainers never trained anyone" pattern
- [ ] No "rostering looks complete but actually missing entire school" pattern
- [ ] No "SSO works for admins but not for students" pattern (different IdP routes are common)
- [ ] No "go-live in dead zone" pattern (state testing, end-of-year, late August)
- [ ] No "partner technical lead departed mid-implementation" pattern (or, if so, named-decision-maker handoff complete)

## References

- [`success-plan.md`](success-plan.md) — the outcome-side partner; this template is the technical-side
- [`onboarding-checklist.md`](onboarding-checklist.md) — the relationship-side counterpart (this template handles tech; that handles relationship)
- [`../skills/implementation-90-day-arc/SKILL.md`](../skills/implementation-90-day-arc/SKILL.md) — the playbook
- [`../knowledge/sis-sso-rostering-integration-patterns.md`](../knowledge/sis-sso-rostering-integration-patterns.md) — technical reference
- [`../knowledge/district-implementation-failure-modes.md`](../knowledge/district-implementation-failure-modes.md) — what to watch for
- [`cross-functional-partnership-map.md`](cross-functional-partnership-map.md) — Implementation function row hand-back criterion
