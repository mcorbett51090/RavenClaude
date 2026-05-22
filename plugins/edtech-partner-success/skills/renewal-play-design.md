---
name: renewal-play-design
description: Design renewal motions that earn the renewal instead of negotiating it — T-180/T-120/T-90/T-60/T-30/T-0 sequence, sponsor-confirmation arc, value-evidence pack, multi-thread the buying committee, decision-memo support, expand/maintain/contract decision rule, and segment-specific overlays (K-12 budget cycle, higher-ed academic calendar, corp L&D fiscal year). Reach for this skill 120-90 days before a renewal date, when a renewal "should be safe" but no movement has happened, or when designing the firm's renewal playbook. Used by `success-playbook-designer` (primary) + `partner-success-manager`.
---

# Skill: renewal-play-design

> **Invoked by:** `success-playbook-designer` (primary — when authoring or refreshing the firm's renewal play), `partner-success-manager` (when executing the renewal motion on a specific partner).
>
> **When to invoke:** 120-90 days before a renewal date; when a renewal "should be safe" but no movement has happened in the last touchpoints; when designing the firm-wide renewal playbook for a new segment or product surface.
>
> **Output:** a sequenced renewal motion with named milestones, sponsor-confirmation checks, value-evidence pack, multi-thread coverage map, and a renew/expand/recover/exit decision.

## The core opinion this skill encodes

A renewal you have to *negotiate* at T-7 is a renewal you already lost the narrative on. **The renewal is earned in months -6 to -2, not in the final week.** A renewal play is the sequenced motion that builds the partner's *own internal* case for renewal so the conversation at T-30 is "confirm the redline," not "convince me to stay."

Most renewal misses are diagnosable at T-90: sponsor never confirmed, value-evidence pack missing, single-thread to one champion, no decision-memo support. This skill exists to make those misses visible while there's time to act.

See also: [`../knowledge/renewal-pricing-conversations-edtech.md`](../knowledge/renewal-pricing-conversations-edtech.md) for the K-12 renewal-clock-at-120-180-days reality (K-12 is not 90).

## The renewal timeline

Default for SaaS-shaped EdTech renewals. **Compress earlier for K-12** (start at T-180 because the January-March budget-build window is the real decision-maker, not the renewal date itself).

| Milestone | When | What | Skill / Template |
|---|---|---|---|
| T-180 | Sponsor confirmation arc starts | Verify the named sponsor is still in role, still the decision-maker, still engaged | [`executive-sponsor-mapping.md`](executive-sponsor-mapping.md) |
| T-120 | Value-evidence pack assembled | 3-5 specific outcomes the partner now has that they didn't pre-purchase, tied to the original success plan | [`success-plan-authoring.md`](success-plan-authoring.md) |
| T-90 | Multi-thread the buying committee | Champion + economic buyer + IT/ops + skeptic all confirmed engaged | [`executive-sponsor-mapping.md`](executive-sponsor-mapping.md) |
| T-60 | Economic-buyer confirmation | Renewal conversation with the actual budget-holder, not just the champion | — |
| T-30 | Decision memo lands | Partner's exec has an internal memo to take into approval (PSM helps it exist; partner authors) | [`../templates/renewal-decision-memo.md`](../templates/renewal-decision-memo.md) |
| T-7 | Redline | Commercial close; "no surprises" delivered | — |
| T-0 | Renewal in hand | Captured in profile; expansion-readiness check kicks off if applicable | [`expansion-play-design.md`](expansion-play-design.md) |

**If any milestone is missed, the play branches into a recovery sub-play** — see [`recovery-play-design.md`](recovery-play-design.md). Don't keep marching forward as if the milestone happened; missed milestones are the leading indicator.

## The sponsor-confirmation arc (T-180)

The named sponsor on the partner profile is the person *we believe* makes the decision. Verify, don't assume:

- **Is the sponsor still in role?** (LinkedIn, partner's directory, recent QBR attendance) — turnover is high in K-12 superintendents (~23% 2024-25) and L&D leaders.
- **Is this still the right exec?** Org changes since contract signature may have moved the decision authority up or down or sideways.
- **Has the sponsor attended the last 2 QBRs?** Attendance is a sponsor-health signal. Two no-shows = potential ghost sponsor (see [`executive-sponsor-mapping.md`](executive-sponsor-mapping.md)).
- **Does the sponsor have a successor named?** If sponsor is rumored to be leaving, who's next.

The output of T-180 is a written, dated update to the partner profile's stakeholder section. Verbal confirmation doesn't count (default to written, per the team constitution).

## The value-evidence pack (T-120)

3-5 specific outcomes the partner now has that they didn't pre-purchase, tied to the original success plan. **Tied to the original goals, not to internal KPIs.**

Each outcome:

- **Outcome statement** — in the partner's framing, not ours
- **Driver** — what specifically the partner did with the product that produced the outcome
- **Measurement** — the data, with source, date range, comparison baseline (per `qbr-composition.md` data-pull discipline)
- **Period** — when this materialized (so the partner can place it in their own narrative)

**Anti-pattern:** generic value claims ("engagement up 18%"). The partner's CFO will discount any number without a baseline and a source. Every number gets provenance.

The value-evidence pack is reusable into:

- The renewal QBR deck
- The partner's internal decision memo
- The advocacy-program ask (if the partner is top-quartile and is willing — see [`advocacy-program-design.md`](advocacy-program-design.md))

## Multi-thread the buying committee (T-90)

Single-thread to one champion = single point of failure. By T-90 the play needs all four roles confirmed engaged:

- **Champion** — internal advocate; usually the day-to-day user-leader; carries the narrative
- **Economic buyer** — actually controls the budget line; often *not* the champion; usually a tier above
- **IT / operational owner** — owns the technical reality (rostering, SSO, integrations) and can kill a renewal on integration debt alone
- **Skeptic** — every committee has one; better surfaced now than at T-30. Find them, hear their concern, address it in the value-evidence pack.

The multi-thread coverage gap visualization (see [`executive-sponsor-mapping.md`](executive-sponsor-mapping.md)) makes the gaps visible. A blank cell at T-90 = a touchpoint to schedule, not a worry to file.

## Decision-memo support (T-30)

The partner's exec writes the internal memo that recommends renewal to *their* approval body (district board, university procurement, corporate finance). **The PSM does NOT write the memo.** The PSM helps it exist:

- Shares the value-evidence pack in a form the exec can paste
- Shares 1-2 peer-segment reference points (anonymized; via [`advocacy-program-design.md`](advocacy-program-design.md))
- Shares the multi-year math (if applicable; see segment overlays below)
- Shares the comparable-cost framing (what the alternative looks like)

See [`../templates/renewal-decision-memo.md`](../templates/renewal-decision-memo.md) for the PSM-side artifact that becomes input to the partner's memo.

## The expand / maintain / contract decision rule

At T-90 the PSM makes an internal recommendation. Three inputs:

| Input | Expand | Maintain | Contract / Exit |
|---|---|---|---|
| Health score | Top-quartile | Mid-quartile, stable | Bottom-quartile or declining |
| Adoption trajectory | Improving + room to grow | Steady at target | Declining or stuck |
| Organizational readiness | New budget / new sponsor energy | Status quo | Org change against us / sponsor lost |

- **Expand** → trigger [`expansion-play-design.md`](expansion-play-design.md) *after* the renewal closes, not bundled in
- **Maintain** → renew flat (or with standard increase) and continue
- **Contract / exit** → trigger [`recovery-play-design.md`](recovery-play-design.md) immediately; the renewal motion *is* the recovery

**Anti-pattern:** running an expansion motion on a yellow account during the renewal window. It conflates the relationship, burns the renewal, and signals to the partner that the PSM is on quota. Don't do it.

## Segment-specific overlays

### K-12

- **The renewal clock starts at T-180**, not T-120. K-12 budget-build window is January-March in most districts; renewals in July-September are *decided* in that window.
- **Board approval timing** matters. Many districts have a board consent-agenda meeting in April-June; the recommendation lands there. Miss that window and the renewal slips into the next fiscal year (or doesn't happen).
- **Multi-year is the exception, not the rule** — annual-appropriation principle means most districts can't commit beyond the current fiscal year. Frame multi-year as a price-hold, not a budget-commitment.
- **State data-privacy law re-triggers at renewal** in NY (Ed Law §2-d), IL (SOPPA), CA (SOPIPA). Re-confirm DPA currency before T-60.
- **Superintendent turnover** ~23% in 2024-25. Confirm sponsor at T-180 and again at T-90.

See [`../knowledge/renewal-pricing-conversations-edtech.md`](../knowledge/renewal-pricing-conversations-edtech.md) for the full K-12 renewal context.

### Higher-ed

- **The academic calendar drives decisions.** Renewals dated July 1 are decided in March-April faculty-governance windows.
- **Procurement-led RFPs** are more common than in K-12. Incumbent win rates 60-90% when the relationship is healthy; defending an incumbent RFP is a separate play (loop in `partner-profile-curator` for the history).
- **CIO / VPSA + budget committee** often the actual economic buyer, not the dean or department head who's the day-to-day champion.

### Corporate L&D

- **Fiscal year drives the budget reset.** A January-end FY means October-November is the decision window; a June-end FY means February-March.
- **L&D budgets are first-cut.** When the partner's company hits a budget squeeze, L&D moves before sales tools or compliance tools. Build the renewal narrative around outcome-vs-cost-of-alternative, not just outcome.
- **Multi-year is more accessible** than in K-12 (no annual-appropriation constraint), and a multi-year commit can be a useful budget-defense for the L&D leader internally.

## The "no surprises" sequence

By T-7 the partner should already know:

- The recommended renewal posture (flat / increase X% / multi-year)
- The pricing (no last-minute surprises; see `renewal-pricing-conversations-edtech.md`)
- The DPA / contractual changes (re-triggered state-privacy law, AI-feature disclosures, sub-processor changes)
- Any expansion-conversation status (deferred to post-renewal, or active but unbundled)
- The named individual on the partner side who's signing

**Surprises at T-7 are the #1 reason a "safe" renewal slips.** The play is built to remove them.

## Anti-patterns this skill flags

- **Renewal pitched at T-7.** The PSM hasn't been running a play; they've been running a status meeting.
- **Sponsor never confirmed.** Default-assumed-still-in-role is the most common renewal failure mode.
- **Expansion pitched during a yellow renewal.** Conflates the conversation, burns the renewal.
- **Generic value claims.** "Engagement up 18%" with no baseline gets discounted to zero in the partner's internal memo.
- **No decision-memo support.** PSM hands over a deck and hopes; the partner exec gets to approval with no shareable artifact.
- **Single-thread to one champion.** Champion leaves at T-45 and the renewal evaporates.
- **K-12 motion run on a SaaS clock.** Starting at T-90 means the budget-build window already closed.
- **Running the renewal motion without the partner profile open.** Prior incidents, named contacts, what they care about — all live there.

## Hygiene checklist

Before declaring the renewal play "executing":

- [ ] Sponsor confirmed in role, in writing, within last 30 days
- [ ] Value-evidence pack assembled with sourced numbers + date ranges
- [ ] Multi-thread coverage gap map updated; no blank cells at T-90
- [ ] Renewal decision memo (PSM-side) drafted per template
- [ ] Expand/maintain/contract recommendation written down with rationale
- [ ] Segment-specific overlay applied (K-12 budget cycle / higher-ed academic calendar / corp L&D FY)
- [ ] DPA / data-privacy / AI-feature disclosures re-checked for currency
- [ ] No expansion ask bundled into a yellow / red renewal
- [ ] All commitments from prior QBRs reconciled (delivered, deferred, or explicitly dropped)

## When NOT to invoke

- The partner is in active recovery (red health). The renewal motion *is* the recovery — use [`recovery-play-design.md`](recovery-play-design.md) and adapt the renewal sub-play out of it, not the other way around.
- The contract auto-renews and the partner isn't economically reviewing it (rare in EdTech; common in some corp L&D). The play collapses to a sponsor-confirmation arc + light QBR.
- The renewal date is < 30 days out and no play was ever started. At that point the play library is recovery-only; running the standard renewal play in 30 days creates the illusion of process and burns trust.

## Refresh triggers

- Renewals close successfully but the multi-year attach rate drops — the value-evidence pack isn't selling depth
- A pattern of T-30 surprises emerges — the no-surprises sequence isn't catching them
- Segment mix shifts (more corp L&D, less K-12) — segment-overlay weighting needs re-tuning
- Regulatory change re-triggers DPA review for a segment

## References

- [`../knowledge/renewal-pricing-conversations-edtech.md`](../knowledge/renewal-pricing-conversations-edtech.md) — segment-specific renewal context
- [`../knowledge/k12-psm-operating-cadence.md`](../knowledge/k12-psm-operating-cadence.md) — K-12 calendar discipline
- [`../templates/renewal-decision-memo.md`](../templates/renewal-decision-memo.md) — the PSM-side artifact
- [`executive-sponsor-mapping.md`](executive-sponsor-mapping.md) — sponsor + multi-thread discipline
- [`expansion-play-design.md`](expansion-play-design.md) — post-renewal expansion motion
- [`recovery-play-design.md`](recovery-play-design.md) — when renewal is at risk
- [`partner-health-scoring.md`](partner-health-scoring.md) — health gate inputs
- [`qbr-composition.md`](qbr-composition.md) — renewal-QBR variant
- [`success-plan-authoring.md`](success-plan-authoring.md) — original goals as the basis for the value-evidence pack
