---
name: executive-sponsor-mapping
description: Map the partner's buying committee — economic buyer, champion, technical buyer / IT, user-champion, blocker, executive sponsor — across segments (K-12 / higher-ed / corp L&D). Includes the multi-thread coverage gap visualization, the "ghost sponsor" detection pattern, sponsor-change protocols, and integration with the durable partner profile. Reach for this skill on a new-partner kick-off, before a renewal, when a critical contact leaves, or when QBRs are well-attended but decisions aren't happening. Used by `partner-profile-curator` (primary) + `partner-success-manager`.
---

# Skill: executive-sponsor-mapping

> **Invoked by:** `partner-profile-curator` (primary — when building or refreshing the stakeholder section of the durable partner profile), `partner-success-manager` (when running a touchpoint cadence that needs sponsor-coverage diagnosis), `success-playbook-designer` (when a renewal, expansion, or recovery play needs the sponsor map as input).
>
> **When to invoke:** new-partner kick-off; pre-renewal (T-180 in the renewal play); when a critical contact leaves the partner organization; when QBRs are well-attended but decisions aren't happening; when a "ghost sponsor" pattern is suspected; quarterly sponsor-map refresh as standard hygiene.
>
> **Output:** an updated stakeholder section of the partner profile with the 6-role coverage grid, ghost-sponsor flags, and any sponsor-change protocols triggered.

## The core opinion this skill encodes

**Single-thread to one champion is a single point of failure.** When that champion leaves — and in EdTech they leave at high rates (K-12 superintendent turnover ~23%, school-leader turnover higher, L&D-leader churn even more) — the partner relationship is on the new person's desk with no internal advocate. That's the most common driver of "safe" renewals that suddenly slip.

The fix is not "find more contacts." The fix is **mapping the actual influence map** (not the org chart) across six functional roles, keeping the map current, and detecting ghost-sponsor patterns before they become churn.

The partner profile is the source of truth (team constitution §3 #1), and the sponsor map is the most-load-bearing section of that profile.

## The 6-role taxonomy

Every buying committee has these six roles, even when they're collapsed onto fewer people. Map them by **function**, not by title.

| Role | What they do | What we need from them |
|---|---|---|
| **Economic buyer** | Controls the budget line; signs the renewal | Direct relationship (not via champion); awareness of the value-evidence pack; confidence in the partner's internal recommendation |
| **Champion** | Internal advocate; carries the narrative day-to-day; often a power-user-leader | Active engagement; willingness to advocate internally; armament pack for internal conversations |
| **Technical buyer / IT** | Owns rostering, SSO, integrations, security review, DPA | Confidence the implementation is healthy; visibility into the technical roadmap; no surprises on data-privacy at renewal |
| **User-champion** | The day-to-day power user (teacher, faculty member, L&D specialist) who actually loves the product | Sustained use; willingness to give testimony (in QBRs, in advocacy) |
| **Blocker** | The skeptic; the person who'll say "we should evaluate alternatives" at the renewal meeting | Surface their concerns *now*; address them in the value-evidence pack; never pretend they don't exist |
| **Executive sponsor** | The senior exec whose approval ultimately matters (often above the economic buyer in larger orgs) | Awareness; confidence in the value story; willingness to defend the decision in an approval body |

**Collapsing rules:** in smaller orgs, the same person may hold 2-3 roles (the champion is often also the economic buyer in a small private school or a 50-person L&D team). The map still needs all six rows; the same name just appears multiple times.

## Segment-specific role mapping

The titles vary by segment. Map by *function*, then translate to local titles.

### K-12 (district / school)

| Role | Title examples |
|---|---|
| Economic buyer | Business manager / CFO / district finance director; in smaller districts, the superintendent or the asst. superintendent for curriculum |
| Champion | Curriculum director, instructional coach, director of teaching & learning; sometimes a strong principal |
| Technical buyer / IT | CTO, director of IT, director of technology, sometimes the data-systems administrator |
| User-champion | Teacher, instructional coach, department chair |
| Blocker | Skeptical principal, a board member with a specific concern, a teachers' union rep in unionized states |
| Executive sponsor | Superintendent (district level); principal (school level); board chair (board level for material decisions) |

**Plus a K-12-specific consideration:** parents and families are *not* on the buying committee but their dissatisfaction can reach the board / superintendent through other channels. The advocacy / FERPA-comms workstream is the relevant connection (see [`../../skills/advocacy-program-design/SKILL.md`](../advocacy-program-design/SKILL.md) and `ferpa-comms-translator`).

### Higher-ed

| Role | Title examples |
|---|---|
| Economic buyer | VP Student Affairs, VP Academic Affairs, Dean (depending on what the product touches); procurement office for material spend |
| Champion | Dean, department chair, director of teaching & learning, director of student success |
| Technical buyer / IT | CIO, director of academic technology, LMS administrator |
| User-champion | Faculty member, advisor, student-success staff |
| Blocker | Faculty senate, procurement office (RFP-issuing role), a faculty member with academic-freedom or AI concerns |
| Executive sponsor | Provost, VPSA, sometimes the President for institution-wide spend |

**Plus a higher-ed-specific consideration:** faculty governance can delay or override decisions that look made. The map needs to include faculty-governance touchpoints, not just admin ones.

### Corporate L&D

| Role | Title examples |
|---|---|
| Economic buyer | CHRO, CLO, VP L&D, sometimes the business-line leader funding from their own budget |
| Champion | L&D director, learning experience lead, business-line training partner |
| Technical buyer / IT | IT-L&D liaison, LMS administrator, sometimes the CISO for security review |
| User-champion | Business-line manager, team lead, individual learner with influence |
| Blocker | Finance (L&D budgets are first-cut), a business-line leader who's never bought in, sometimes CISO on data-flow concerns |
| Executive sponsor | CHRO, sometimes the CEO for enterprise-wide L&D platforms |

**Plus a corp L&D-specific consideration:** business-line leaders are often the actual budget holders, not the central L&D org. The map should reflect "who pays for this specific deployment," which may be multiple business lines for an enterprise platform.

## The multi-thread coverage gap visualization

The map is rendered as a grid that makes coverage *visible*:

| Role | Current contact | Last touched | Influence rating (1-5) | Engagement signal |
|---|---|---|---|---|
| Economic buyer | (name + title) | (date) | (1-5) | (active / passive / unknown / ghost) |
| Champion | | | | |
| Technical buyer / IT | | | | |
| User-champion | | | | |
| Blocker | | | | |
| Executive sponsor | | | | |

**Blank cells are the action items.** A row with no name = a coverage gap, which is a touchpoint to schedule. A row with a name but a stale "last touched" date = a relationship to refresh. A row with low influence rating = the named contact isn't the right person for that role; the real one needs to be identified.

**Engagement signal definitions:**

- **Active** — engaged in the last 60 days; participated in a QBR or meaningful working session
- **Passive** — exists in the relationship but hasn't engaged recently
- **Unknown** — we don't know how engaged they are; intelligence gap
- **Ghost** — named in the role but doesn't respond, doesn't attend, doesn't advocate (see below)

## The "ghost sponsor" detection pattern

A ghost sponsor is a leading indicator of an organizational change you missed.

**Pattern:** the named sponsor on the profile *never attends meetings*, *never replies to email*, *never advocates internally*, *never refers other contacts*, and yet is the *only listed sponsor for that role*. The PSM hasn't actually had a relationship with this person in months. The profile still lists them because nobody updated it.

**What this almost always means:**

- The named sponsor has been quietly demoted, sidelined, or de-prioritized
- A real decision-maker has emerged elsewhere and we don't know who
- An org-chart change happened that the PSM didn't catch
- The original sponsor is still in title but no longer in influence

**Detection cues:**

- Two consecutive QBRs missed
- 60+ days with no direct response (any channel)
- Communications go through an intermediary every time
- The intermediary makes decisions that "the sponsor approved" but the sponsor never confirmed in writing
- LinkedIn shows a recent role change

**Remedy:** convert the ghost-sponsor flag into an immediate sponsor-change protocol (below). Don't wait for a renewal to discover the real map.

## Sponsor-change protocols

Three patterns trigger protocols. Run them quickly — the longer the gap, the more brittle the relationship.

### New sponsor arrives → re-onboarding sequence

A new economic buyer, executive sponsor, or critical champion arrived. The previous relationship doesn't transfer automatically.

1. **Confirm the change** (LinkedIn, partner directory, ask the champion)
2. **Update the profile** within 7 days — the partner profile is the source of truth
3. **Schedule a re-onboarding meeting** with the new person — vendor exec sponsor + PSM, 30-minute working session, not a courtesy intro
4. **Share the value-evidence pack** so the new sponsor inherits the case-for-renewal, not a blank slate
5. **Refresh the multi-thread coverage** — the new sponsor may have a different style and need different supporting contacts
6. **Document their stated priorities** (different from the predecessor's) and incorporate into the success plan

### Sponsor leaves → emergency multi-thread

The named sponsor left and there's no immediate replacement. Single-thread failure has happened or is imminent.

1. **Cross-reference the multi-thread coverage grid** — which other contacts can step up
2. **Touch each remaining contact in the row** within 14 days — confirm the change, hear their take, ask who they think the new decision-maker will be
3. **Escalate to vendor exec sponsor** if no clear successor emerges (often signals a wider org-disruption)
4. **Flag the renewal play** (see [`renewal-play-design.md`](../renewal-play-design/SKILL.md)) — sponsorship gap is a known leading indicator of renewal risk
5. **Trigger recovery play if applicable** (see [`recovery-play-design.md`](../recovery-play-design/SKILL.md)) — if combined with another red flag

### Sponsor demoted / sidelined → escalate concern

The sponsor is still listed but org changes signal reduced influence (reporting line changed, function reorganized, role narrowed).

1. **Validate** through a careful third-party check — don't ask the sponsor directly; that's a relationship-damaging conversation
2. **Identify who picked up the influence** — usually visible in who's now setting the agenda
3. **Begin parallel-thread** to the rising contact without abandoning the existing sponsor (treat them with respect; org changes reverse sometimes)
4. **Adjust touchpoint cadence** — the rising contact needs onboarding; the sidelined contact may still be relevant for some decisions

## QBR attendance as a sponsor-health signal

A free, almost-passive sponsor-health signal: who shows up to the QBR.

| Pattern | Signal |
|---|---|
| Sponsor attends, asks substantive questions, names commitments | **Healthy.** Map is accurate. |
| Sponsor attends but quietly; lets champion drive | **Likely passive.** Acceptable in mature relationships; suspicious in early ones. |
| Sponsor doesn't attend, sends a delegate | **Mid-yellow.** Investigate one level: is the delegate empowered? Is this a one-time scheduling thing or a pattern? |
| Sponsor doesn't attend, no delegate | **Yellow.** First miss = ambient. Second miss in a row = ghost-sponsor flag fires. |
| Sponsor doesn't attend, never has | **Ghost-sponsor flag should already be on.** If it isn't, the profile is stale. |

This is a leading indicator that costs zero to capture. Just record attendance on every QBR.

## Integration with the durable partner profile

The sponsor map lives in the stakeholder section of [`../templates/partner-profile.md`](../../templates/partner-profile.md). It is *the* canonical source of who's who.

- The CRM is a sync target; the profile is the canon
- The PSM updates the profile within 7 days of any sponsor change — not at the next quarterly review, not at renewal
- The profile's stakeholder section includes the 6-role coverage grid, not just a list of names
- The profile carries the ghost-sponsor flag explicitly when one fires
- On PSM handoff, the next PSM reads the stakeholder section first, before anything else

The reason the profile lives outside the CRM: CRMs encourage one-row-per-contact thinking. The sponsor map is six rows that may collapse to two people or expand to ten. The profile renders it the right way; the CRM doesn't.

## Anti-patterns this skill flags

- **Single-thread** — one champion, no other contacts. A single point of failure that will fail.
- **No map at all** — the partner profile's stakeholder section is a list of names with no role coding.
- **Mapping the org chart instead of the influence map.** The org chart says the superintendent decides; the influence map says the curriculum director shapes the recommendation and the business manager controls the budget line.
- **Ghost sponsors un-flagged.** The named sponsor hasn't responded in 90 days but the profile still says "active." Flag it.
- **Stale "last touched" dates** that haven't been updated even though the PSM has had touchpoints — the discipline is to update the profile *during* the touchpoint, not in arrears.
- **QBR attendance not tracked.** A free signal is being thrown away.
- **Sponsor change captured in CRM but not in profile.** The CRM update isn't enough — the profile is the canon.
- **Re-onboarding skipped when a new sponsor arrives.** The relationship clock resets; treating it like a continuous-relationship is how renewals slip.
- **Mapping only the champion's network.** The champion isn't the economic buyer in most cases; talking only to the champion's contacts maps half the committee.

## Hygiene checklist

For every partner profile, the stakeholder section meets:

- [ ] All 6 roles are represented (even if collapsed onto fewer people)
- [ ] Each row has: contact, last-touched date, influence rating, engagement signal
- [ ] No row is missing a name without an explicit "coverage gap" flag
- [ ] No ghost sponsor flags are stale (either resolved or escalated within 30 days)
- [ ] Segment-specific titles applied (K-12 / higher-ed / corp L&D)
- [ ] QBR attendance log present
- [ ] Last refresh date within 90 days
- [ ] Sponsor-change protocol triggered within 7 days of any change

## When NOT to invoke

- The partner is in active churn-prep (recovery-play exit branch) — sponsor-mapping shifts focus to the *exit-conversation* sponsor, not the renewal sponsor.
- The partner is brand-new (week 1 of implementation) — the map is incomplete by definition; build it over the first 30 days, not before kick-off.
- The work is purely day-to-day touchpoint coordination with one named contact — the full map is overkill; check it at the next refresh cadence.

## Refresh triggers

- New PSM owner takes the partner over (handoff)
- A renewal play is starting (T-180)
- A red-flag trigger fires that involves sponsorship
- Quarterly profile-refresh cadence
- LinkedIn / org-chart signal of partner-side change
- Two consecutive QBR no-shows by the listed sponsor
- A new product module changes who the relevant technical buyer is

## References

- [`../templates/partner-profile.md`](../../templates/partner-profile.md) — the stakeholder section that this skill populates
- [`renewal-play-design.md`](../renewal-play-design/SKILL.md) — T-180 sponsor confirmation arc uses this map
- [`recovery-play-design.md`](../recovery-play-design/SKILL.md) — sponsorship-hypothesis diagnostic uses this map
- [`expansion-play-design.md`](../expansion-play-design/SKILL.md) — Gate 3 (organizational readiness) uses this map
- [`partner-health-scoring.md`](../partner-health-scoring/SKILL.md) — champion-strength signal feeds from this map
- [`qbr-composition.md`](../qbr-composition/SKILL.md) — QBR attendance is a sponsor-health signal
- [`../knowledge/edtech-segment-fundamentals.md`](../../knowledge/edtech-segment-fundamentals.md) — segment-specific buyer patterns
- [`../knowledge/renewal-pricing-conversations-edtech.md`](../../knowledge/renewal-pricing-conversations-edtech.md) — superintendent turnover and segment buyer patterns
