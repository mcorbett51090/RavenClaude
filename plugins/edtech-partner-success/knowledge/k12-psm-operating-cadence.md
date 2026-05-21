# K-12 PSM operating cadence — time zones, school-calendar dead zones, and signals-by-rhythm

> **Last reviewed:** 2026-05-21. Sources: AASA "School Budgets 101" (fiscal-year + budget-build cadence — already verified for [`renewal-pricing-conversations-edtech.md`](renewal-pricing-conversations-edtech.md)), CoSN K-12 IT calendars, US DOE academic-calendar conventions, US time-zone districts, practitioner synthesis from the existing v0.2.0 + v0.3.0 + v0.4.0 knowledge files. Refresh when: (a) US K-12 fiscal calendar shifts (rare), (b) a major federal academic-calendar change ships (also rare), (c) a regional time-zone change is enacted (e.g., a state opts out of DST), or (d) the existing `partner-health-score-drift.md` thresholds are retuned and the "no response in N hours" judgments need to update.
>
> **Not in scope:** day-rhythm prose ("morning Slack triage → midday calls → afternoon docs"). That's onboarding content for a human PSM. **This file is about which signals fire when, and what an agent should do differently because of that.**

The v0.2.0 + v0.3.0 + v0.4.0 knowledge files cover *what* a K-12 PSM does (rostering, health scores, comms, frameworks, segments, renewals, AI). This file covers ***when*** — and the operational discipline a multi-state K-12 book requires.

---

## 1. Time-zone discipline (the West-Coast book vs. East-Coast book question)

A K-12 PSM book is almost never time-zone-homogeneous. Even a "West Coast" book typically spans PT + MT (and sometimes AKT for Alaska districts). Practical implications:

### Touchpoint scheduling rule

- **Default partner-meeting window:** 10:00 AM – 2:00 PM in the **partner's** local time, not the PSM's. A 9:00 AM PT call is 12:00 PM ET — fine for a Pacific PSM with an Eastern partner; *not* fine if the same call is scheduled for an MT or PT partner who arrives at 9:00 AM their local time and faces a meeting cold.
- **The PSM's calendar** in their own time zone shows what looks like a packed day, but the partner sees that same call land at a sensible time for their school day. The PSM's calendar discipline is "schedule in the partner's TZ, accept the PSM-side calendar pain."
- **For a West-Coast-based PSM with an East-Coast partner**, the PSM's working window for that partner is 6:00 AM – 11:00 AM PT (= 9:00 AM – 2:00 PM ET). The PSM either starts early or accepts that partner is "morning-only" from the PSM's perspective.

### What an agent should do differently

When the `partner-success-manager` agent (or `qbr-composer`, when scheduling) drafts a touchpoint, the touchpoint must include the partner's local time zone and the partner-local time **as the primary surface**, with the PSM's local time as parenthetical. Defaulting to the PSM's TZ first is the most common scheduling-confusion source in cross-TZ books.

### Signal: "no response in 24 hours"

This signal cannot be evaluated without knowing the partner's TZ. A PSM message sent Friday 5 PM PT to an Eastern partner lands at their 8 PM Friday — *the partner doesn't see it until Monday morning their time, which is ~64 hours later in the PSM's clock.* The health-score "no engagement in N hours" decay rule (per [`partner-health-score-drift.md`](partner-health-score-drift.md)) must subtract weekend-and-evening-hours-in-partner-local-TZ before declaring a "stale" signal.

---

## 2. School-calendar dead zones (when NOT to push)

The plugin's [`edtech-segment-fundamentals.md`](edtech-segment-fundamentals.md) names these at high level. This file makes them operational:

### K-12 calendar dead zones (no PSM-driven touchpoints expected to land)

| Dead zone | When | Why | What signal it suppresses |
|---|---|---|---|
| **Late August** | ~Aug 15 – first day of school (state-variable) | District staff in setup mode: rostering, classroom assignments, schedule changes. Curriculum directors are not reading vendor emails. | "No response to PSM check-in" is normal here; don't trigger a yellow on this signal alone in this window. |
| **First two weeks of school** | first 14 calendar days after Day 1 | Implementation issues surface and consume district bandwidth; PSM should be reactive (support escalations) not proactive (QBR scheduling, expansion conversations). | New-feature pitches; expansion calls. Adoption-monitoring is fine and informative. |
| **Thanksgiving week (US)** | Mon–Fri of US Thanksgiving | District offices often partially closed; many states give the full week. | Same as late August — no-response is normal. |
| **Winter break** | ~Dec 22 – Jan 2 (state-variable) | Districts closed. | All proactive signals; reactive support-side only. |
| **Spring break** | March or April, state-variable (~1-2 weeks) | Districts closed. | All proactive signals. |
| **State testing windows** | Spring (state-variable; ~March-May depending on grade and assessment) | District ops + curriculum directors are in "do not disturb" for test administration; admin attention is on the test, not vendor relationships. | Major expansion / new-feature / new-vendor conversations. Quick check-ins are OK; substantive asks are not. |
| **End-of-year wrap-up** | last 2 weeks of school year (state-variable; late May - late June) | Grades closing, last-day events, summer planning. | Renewal-clock conversations should already be 90+ days in by this point (per the [`renewal-pricing-conversations-edtech.md`](renewal-pricing-conversations-edtech.md) 120-180-day K-12 clock); opening renewal in this window means it's too late. |

### Higher-ed calendar dead zones (briefly)

- **Finals weeks** (Dec, May) — no academic-decision-maker bandwidth
- **Summer term gaps** — but corporate/admin layer still works; check segment specifics

### Corporate L&D calendar dead zones

- **Fiscal-year-end + 2-week wrap-up** — varies by vendor (calendar-year vs. April-end vs. October-end fiscal); confirm per partner
- **Last 2 weeks of December** — most US enterprises essentially closed

### What an agent should do differently

The `success-playbook-designer` agent, when designing a play with a "trigger if no response in N hours" condition, must reference this calendar to suppress the trigger during the partner-segment's known dead zones. A red-flag intervention play firing at Day 5 of winter break is noise, not signal.

The `partner-success-manager` agent, when reading a partner-pulse request mid-dead-zone, must surface this in the response: *"Note: partner is in [dead-zone-name] — no-response signal is unreliable here. Recommend re-evaluating at [end of dead zone date]."*

---

## 3. Signals-by-rhythm (when in the week / quarter / year a signal is meaningful)

K-12 partner signals follow a predictable cadence. An agent that knows the cadence weighs signals differently.

### Weekly rhythm

- **Monday morning (partner-local 8-10 AM):** highest-volume signal window. Issues from the prior week that didn't get resolved over the weekend surface here. The PSM's Monday queue is the most-informative single signal of the week.
- **Tuesday-Thursday midday (10 AM-2 PM):** real conversations happen. Curriculum directors and district admins are accessible; partner-meeting touchpoints land best here.
- **Friday afternoon (after 2 PM partner-local):** signal-collapse. Don't draw conclusions from Friday-PM silence; don't send substantive asks (they won't be read until Monday).
- **Weekends:** zero signal. Auto-suppress all decay rules.

### Quarterly rhythm

- **Q1 (school year ~Aug-Oct):** implementation + first-90-day adoption signals. New features, training utilization, rostering completeness are the lead indicators.
- **Q2 (Nov-Jan, minus dead zones):** mid-year value-realization. QBRs land here; first measurable outcomes are visible (assessment data, family-engagement rates for a parent-comms vendor, etc.).
- **Q3 (Feb-Apr):** **renewal-build window** for July-1 fiscal-year districts. The PSM's calendar shifts: success-plan refinement → renewal-conversation prep → board-readable artifact prep. See [`renewal-pricing-conversations-edtech.md`](renewal-pricing-conversations-edtech.md) for the 120-180-day clock detail.
- **Q4 (May-Jul, minus end-of-year-wrap):** renewal closes; summer planning for next-year expansion; relationship-investment touchpoints (not transactional) with non-renewing-yet partners.

### Annual rhythm — the K-12 fiscal calendar overlay

- **July 1 (fiscal year start):** new budget cycle. Spend authorizations land. Expansion conversations that were teed up in Q3-Q4 close here.
- **August (pre-school-start):** implementation-window peak. Most rostering / SSO / launch-prep activity.
- **January-March:** budget-build window for next fiscal year. **The single most important quarter for any vendor whose renewal needs to be in next year's budget.**
- **April-June:** board approval window for next-year contracts. By April, the renewal conversation should already be in board-approval-ready shape; you can't open it here.

---

## 4. The PSM's own cadence (calendar-as-instrument)

A K-12 PSM's calendar should be structured around the partner's cadence, not the PSM's reactive needs.

### Per-partner cadence

| Cadence | What happens | Why this cadence (not more, not less) |
|---|---|---|
| **Weekly** | 15-min async pulse check (Slack/email): "anything new, any blockers?" | Catches issues before they become escalations; respects partner time |
| **Monthly** | 30-min sync touchpoint: review usage, surface 1-2 priorities | Cadence partners actually keep; quarterly is too sparse for active partners |
| **Quarterly** | QBR (45-60 min); see [`../templates/qbr-deck.md`](../templates/qbr-deck.md) | Outcomes + commitments + roadmap signaling |
| **Annual** | Annual partner review (full day or half-day in person/video) | Strategic re-baselining + multi-year direction |

### When to deviate

- **Top-quartile health, low-renewal-risk partner:** monthly may compress to bi-monthly; the PSM's calendar bandwidth recovers
- **Bottom-quartile health, active risk:** weekly upgrades to twice-weekly; this is the recovery-play cadence (see [`success-playbook-designer.md`](../agents/success-playbook-designer.md))
- **In-dead-zone partner:** all cadences suppress; resume at end of dead zone

### What an agent should do differently

When the `partner-success-manager` agent recommends a touchpoint, it must reference the partner's cadence + dead-zone status + TZ. The default-cadence-week-and-time goes in the partner profile (via `partner-profile-curator`), and the agent reads it before scheduling.

---

## 5. Refresh triggers for this document

- Federal academic-calendar change (national standard shift — rare)
- State opts out of (or into) DST in a way that affects multi-state book operations
- US K-12 fiscal-year convention shifts (rare; would also require updating [`renewal-pricing-conversations-edtech.md`](renewal-pricing-conversations-edtech.md))
- Higher-ed or corporate L&D calendar evolves and the per-segment dead-zone table needs new rows
- The advisory hook starts flagging touchpoint-scheduling violations and the rule needs sharpening

## 6. References (existing plugin artifacts)

- [`edtech-segment-fundamentals.md`](edtech-segment-fundamentals.md) — the higher-level segment / calendar / fiscal-year framework (this file is the operational complement)
- [`renewal-pricing-conversations-edtech.md`](renewal-pricing-conversations-edtech.md) — the 120-180-day K-12 renewal clock + budget-build window
- [`partner-health-score-drift.md`](partner-health-score-drift.md) — decay rules that should reference this file's dead-zone suppression
- [`../templates/cross-functional-partnership-map.md`](../templates/cross-functional-partnership-map.md) — the *who-does-what* map that complements this *when* doc
- [`../agents/partner-success-manager.md`](../agents/partner-success-manager.md) — the primary consumer
- [`../agents/success-playbook-designer.md`](../agents/success-playbook-designer.md) — secondary consumer (play-trigger-suppression)
