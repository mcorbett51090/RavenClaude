# Renewal & Account Lifecycle (domain-neutral)

> **Last reviewed:** 2026-06-03
> **Read when:** designing the renewal-risk workflow; deciding what makes an account a renewal *risk* vs merely *due*; setting QBR cadence; distinguishing expansion signals from churn signals; calibrating the *who-do-I-call-today?* actionability bar; setting touch-cadence by tier.
> **Scope:** domain-neutral. Universal CS lifecycle mechanics. Segment-specific overlays (K-12 budget cycle, academic calendar, corporate fiscal year, board-approval timing) belong in a vertical plugin — they change the *clock*, not the *mechanics*.

This file is the source of truth behind the `renewal-workflow-design` skill and supports both plugin agents. It is consistent with the unified-CS-analytics build plan's renewal-risk framing.

---

## 1. The renewal-risk rule: proximity × engagement

The central rule of renewal risk:

> **Renewal proximity alone is not risk. Risk = proximity × engagement.**

Every account eventually reaches 90 days to renewal. That fact, by itself, says nothing about whether the renewal is safe. A healthy, engaged, expanding account 60 days from renewal is not a risk; a disengaged, declining account 60 days out is an emergency.

- **Proximity** (`days_to_renewal`) is the **gate** — it sets the *urgency* of acting on everything else. It is context, never a standalone risk term.
- **Engagement** (usage trend, health-score trend, support/escalation signal, champion presence) is what turns proximity into risk.
- The renewal-risk workflow keys off the **product** of the two: a Red health tier *and* a near renewal date is the top of the call list; a Red tier with a distant renewal is a recovery project with runway; a Green tier near renewal is a confirm-and-expand conversation.

---

## 2. The renewal workflow

A renewal is earned over the months before the date, not negotiated in the final week. The workflow is a sequence of checks, each gated on the health signals:

| Stage | When | What the workflow checks |
|---|---|---|
| **Watch** | Renewal enters the ~180-day window | Account appears on the renewal watchlist; current health tier recorded as the baseline |
| **Confirm** | ~120 days | Is the named decision-maker / sponsor still in role and engaged? (Sponsor silence is a leading risk signal.) Is the value-evidence — the outcomes the account now has — assembled and sourced? |
| **Multi-thread** | ~90 days | Is the relationship single-threaded to one champion (a single point of failure) or multi-threaded across champion + economic buyer + operational owner? A single thread at 90 days is itself a risk flag. |
| **Decide** | ~90-60 days | The CSM makes an internal **expand / maintain / recover** call from the health tier + adoption trajectory + organizational readiness (see §4). |
| **Close** | ~30-7 days | "No surprises" — the account already knows the posture and the pricing; the conversation confirms, it doesn't convince. |

> The exact day-counts are the *default* SaaS clock. Vertical overlays compress or shift them (e.g. a budget-build window that decides the renewal months before the date). The overlay changes the clock; the stages and their health-gates stay the same.

**The principle:** missed stages are the leading indicator. A renewal where the sponsor was never confirmed, or the value-evidence was never assembled, or the relationship stayed single-threaded, is diagnosable as at-risk at 90 days — while there's still time to act. The workflow exists to make those misses visible early.

---

## 3. QBR cadence

The Quarterly Business Review is the recurring health checkpoint between renewals.

- **A QBR with no commitments is a status meeting.** Every QBR ends with named action items, named owners, and dates — and the CSM tracks them *between* QBRs. An untracked commitment resurfaces as a finding at the next one.
- **Cadence is tier-aware** (see §6): healthy accounts get the standard quarterly rhythm; at-risk accounts get a tighter cadence; the lowest-engagement accounts get a recovery cadence that is not "wait for the next QBR."
- **QBR attendance is itself a signal.** A sponsor who skips two consecutive reviews is a *ghost sponsor* — a leading risk indicator that feeds back into the health tier (champion/sponsor silence).
- **Provenance on every QBR claim.** A slide saying "usage is up 18%" needs the source, the date range, and the comparison baseline. The account's finance owner will ask.

---

## 4. Expansion vs churn signals

The same account-health view that surfaces churn risk also surfaces expansion readiness — but they are *opposite* ends, and conflating them is a classic error.

| | Expansion signals | Churn signals |
|---|---|---|
| Health tier | Top-tier, stable or rising | Declining or bottom-tier |
| Usage trend | Rising, hitting capacity / breadth limits | Falling slope |
| Adoption | Broad and deepening | Narrow and fragile |
| Org readiness | New budget, new sponsor energy, new use cases | Sponsor lost, org change against us |
| Renewal posture | Confirm-and-grow | Recover-or-exit |

**The discipline:** do **not** run an expansion motion on a Yellow or Red account during the renewal window. It conflates the relationship, burns the renewal, and signals the CSM is on quota rather than on the account's success. Expansion fires when the account has *earned value* and the health tier supports it — not on a calendar quota. (CS is not sales: the job is to make the account succeed at what they bought, not to close more.)

---

## 5. The "who do I call today?" actionability bar

The whole point of the analytics is a CS leader opening one view and getting an actionable call list — fast.

> **The bar:** a leader sorts by `(tier = Red AND days_to_renewal < 90)` and gets an actionable call list in **under two minutes** (ideally seconds), with **every Red showing why** (its 2-3 driving signals, each with value / threshold / window).

Everything in the data model and the BI surface is in service of that sort. If producing the call list requires the leader to compute anything mentally, cross-reference two screens, or trust an unexplained "Red," the design has failed the actionability bar — redesign it.

A useful renewal view therefore shows, per account:
- the health tier + **why** (the driving signals)
- days to renewal and the renewal-opportunity stage
- the recommended next action / save-play for the current state
- a short history (trend sparkline) for context

---

## 6. Touch-cadence by tier

The health tier drives not just *who* to call but *how often*:

| Tier | Cadence | Posture |
|---|---|---|
| **Green** | Standard rhythm (e.g. quarterly QBR + light monthly pulse) | Maintain; watch for expansion readiness |
| **Yellow** | Tighter (e.g. monthly sync + weekly signal review) | Investigate which signals dropped; light-touch recovery |
| **Red** | Recovery cadence (not "wait for the next QBR") | Mandatory save-play; frequent review until the tier clears or the account is confirmed recoverable/not |

Independent **red-flag triggers** (champion departure, active-user collapse, explicit "evaluating alternatives") override the tier cadence and fire a recovery motion *immediately* — they don't wait for the next scheduled touch.

---

## 7. Anti-patterns

- Renewal proximity treated as risk on its own (every account at 90 days flagged, regardless of engagement)
- A renewal "confirmed safe" at T-7 with no play run beforehand (it was a status meeting, not a renewal motion)
- An expansion pitch into a Yellow/Red renewal (conflates the relationship, burns the renewal)
- A QBR that ends with no named commitments / owners / dates
- A sponsor assumed still-in-role and never confirmed (the most common renewal failure mode)
- A single-threaded relationship at 90 days treated as fine (one champion departure evaporates the renewal)
- A "who do I call today?" view that needs mental computation or shows an unexplained Red
- A renewal-risk call made off renewal date alone, ignoring the engagement multiplier

---

## References

- Skill: [`../skills/renewal-workflow-design/SKILL.md`](../skills/renewal-workflow-design/SKILL.md)
- Companion knowledge: [`cs-health-metrics-and-churn-indicators.md`](cs-health-metrics-and-churn-indicators.md)
- Template: [`../templates/cs-health-data-model.md`](../templates/cs-health-data-model.md)
- Vertical motion exemplar (segment overlays): [`../../edtech-partner-success/skills/renewal-play-design/SKILL.md`](../../edtech-partner-success/skills/renewal-play-design/SKILL.md)
