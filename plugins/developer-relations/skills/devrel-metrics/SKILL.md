---
name: devrel-metrics
description: "Build a DevRel metric set that measures outcomes — the developer funnel, leading vs lagging indicators, the vanity-metric ban, and honest attribution (name the dark funnel rather than invent a number). Used by devrel-lead (primary)."
---

# Skill: devrel-metrics

**Purpose:** Replace vanity dashboards with a metric set that maps to the developer funnel and
is honest about what the data can and can't show. Used by `devrel-lead` (primary).

## When to use

- A DevRel dashboard that's all impressions/stars/followers
- Defending DevRel's value to leadership
- Setting OKRs for the program

## The rule: every metric maps to a funnel stage

A metric is legitimate **only** if it maps to awareness, activation, habit, or advocacy
(see `devrel-strategy` for the funnel). If it doesn't, it's reach — an input, not an outcome.

| Vanity input (reach) | Reframe as the outcome metric |
|----------------------|-------------------------------|
| Twitter followers | New developers attributed to content (awareness → activation) |
| Talk attendees | Quickstart completions in the week after the talk |
| GitHub stars | Weekly active developers / retained developers |
| Newsletter subscribers | % of subscribers who completed the core action |
| Discord member count | Median first-response time + % questions answered |

Vanity inputs aren't *banned from existence* — they're banned as **success criteria.** Track
reach as a leading signal; never report it as the outcome.

## Leading vs lagging

- **Leading** (move first, you can act on them): quickstart completion rate, time-to-first-success,
  first-response time, content reach.
- **Lagging** (the result, slow to move): retained developers at 30/90 days, organic-referral
  share, revenue-attributed-to-developers.

Pair one leading + one lagging per funnel stage. Acting only on lagging metrics is driving by
the rear-view mirror.

## Honest attribution (the dark-funnel problem)

Developer journeys are mostly invisible — a developer reads a blog post, lurks for months, then
signs up "directly." Do **not** invent an attribution number the data can't support.

- Use **self-reported attribution** ("how did you hear about us?") as the honest primary signal.
- Name the dark funnel explicitly when reporting: "X% direct/unattributable — likely
  content-and-community-influenced but not individually traceable."
- Per the inherited Grounding Protocol: cite the source/date of any quantitative claim or mark
  it `[unverified]`. A fabricated funnel number that drives a roadmap decision is the exact
  failure this protocol prevents.

## Output

A metric set: north-star (an activation/habit outcome) + 1–2 guardrails + one leading & one
lagging per stage, each with a definition, an owner, and a source. Plus an attribution note
that's honest about the dark funnel.
