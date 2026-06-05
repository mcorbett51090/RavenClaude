> Live-ops event brief — documents the design, success metrics, content requirements, and go/no-go criteria for a single live-service event before development begins, so the team can size the effort, confirm lead time, and measure outcome.

# Live-Ops Event Brief — [Event Name]

**Game:** [Game Title]
**Event Name:** [Event Name / Internal Codename]
**Event Type:** [Limited-time content / Sale / Seasonal / PvP tournament / Collaboration / Other]
**Target Segment:** [Mobile/F2P | Premium | Live-service | Indie]
**Brief Author:** [Name, Title]
**Brief Date:** [YYYY-MM-DD]
**Development Start:** [YYYY-MM-DD]
**Live Date:** [YYYY-MM-DD]
**Event End Date:** [YYYY-MM-DD]
**Duration:** [X days]

---

## 1. Strategic Objective

> One sentence: what retention or monetization outcome does this event exist to move?

[e.g., "Recover D7 retention lost in the last content drought by delivering a high-frequency daily-login reward loop to lapsed players."]

| Metric | Baseline (last 30d) | Target | How Measured |
|---|---|---|---|
| D7 retention | [X]% | [X]% | Analytics dashboard — cohort view |
| ARPDAU | $[X] | $[X] | Revenue / DAU |
| Event participation rate | — | [X]% of DAU | Event funnel |
| IAP conversion (event bundle) | — | [X]% | Store analytics |

---

## 2. Player Experience Summary

**Hook (what brings the player in):**
> [One sentence: the thing the player sees/hears/reads at game open that makes them engage]

**Core mechanic:**
> [2–3 sentences: what the player does, how often, and what they earn]

**Primary reward:**
> [The headline item or currency. Must be desirable to both payers and non-payers at some tier.]

**Monetization touchpoint:**
> [The IAP offer or accelerator that converts engagement to revenue — and the price point]

**Narrative / theme (if applicable):**
> [Season, IP collaboration, in-game world event — or "none"]

---

## 3. Content Requirements

| Asset Type | Description | Owner | Due Date | Status |
|---|---|---|---|---|
| UI / event menu screen | [Description] | [Name] | [YYYY-MM-DD] | Not started / In progress / Done |
| New game assets (art) | [Description] | | | |
| Reward items / currencies | [List] | | | |
| Push notification copy | [2–3 messages] | | | |
| Store IAP bundle artwork | [Description] | | | |
| QA test plan | [Link or description] | | | |
| Analytics event tags | [List of new event tags needed] | | | |

**Total estimated dev effort:** [X dev days across disciplines]
**Reuse from prior events:** [% of content reused — affects cost estimate]

---

## 4. Economy & Balance

| Economy Variable | Current Value | Event Value | Change Rationale |
|---|---|---|---|
| Primary currency source rate (event) | [X/session] | [X/session] | [Reason] |
| Reward ceiling (per player) | [Unlimited / capped at X] | | |
| Sink for event currency | [Reward shop / direct IAP] | | |
| Inflation risk assessment | Low / Medium / High | | |

> Flag: if the event adds net currency injection > [X]% of current weekly source rate, escalate for economy team review before launch.

---

## 5. Lead-Time Budget

| Task | Lead Time Required | Due Date (back-calculated from live date) |
|---|---|---|
| Design doc finalized | [X days] | [YYYY-MM-DD] |
| Art assets complete | [X days] | |
| Engineering feature complete | [X days] | |
| QA pass | [X days] | |
| Store bundle submitted (if applicable) | [X days — Apple/Google review time] | |
| LiveOps configuration in CMS | [X days] | |
| Soft-enable / smoke test in production | [1–2 days] | |

---

## 6. Go / No-Go Criteria

| Criterion | Required to Launch | Owner | Status |
|---|---|---|---|
| All content assets approved | Yes | [Name] | |
| Analytics tags verified in staging | Yes | | |
| Economy balance sign-off | Yes | | |
| QA sign-off (P0 / P1 bugs = 0) | Yes | | |
| CS briefing complete | Yes | | |
| Rollback plan documented | Yes | | |

**Rollback plan:** [One paragraph: how the event is disabled if a critical bug emerges post-launch]

---

## 7. Post-Event Review (fill after event ends)

| Metric | Target | Actual | Delta |
|---|---|---|---|
| Participation rate | [X]% | | |
| D7 retention lift | [X pp] | | |
| ARPDAU lift | $[X] | | |
| Revenue from event bundle | $[X] | | |
| Player sentiment (store reviews / CS tickets) | Positive / Neutral | | |

**What worked:**
**What didn't:**
**Recommendation for next event:**

---

_Template version: 1.0 — game-development plugin_
