---
name: devrel-strategy
description: "Design a DevRel program around the developer funnel — pick the north-star + guardrail metrics, locate the weakest stage, and decide where to invest. Used by devrel-lead (primary)."
---

# Skill: devrel-strategy

**Purpose:** Turn a vague "we should do DevRel" into a program with a funnel, metrics, and an
investment plan tied to the weakest stage. Used by `devrel-lead` (primary).

## When to use

- Standing up a DevRel program from scratch
- A quarterly/annual planning cycle for an existing program
- Diagnosing why the funnel is leaking and where to invest next

## The developer funnel

```
Awareness  →  Activation  →  Habit  →  Advocacy
```

| Stage | The developer has… | Leading indicator | Lagging indicator |
|-------|--------------------|--------------------|--------------------|
| Awareness | heard of the product | content reach, search impressions, referral traffic | new sign-ups / repo visits |
| Activation | run something real and seen it work | quickstart completion rate, time-to-first-success | % of sign-ups reaching first core action |
| Habit | used it on a cadence | weekly active developers, return rate | retained developers at 30/90 days |
| Advocacy | told others / contributed / referred | PRs from outside, community answers, referrals | organic-referral share of new developers |

## The method

1. **Map the funnel to your product.** Define what "first core action" concretely means
   (the moment a developer sees real value). This is the activation event.
2. **Pick the north-star.** It must be an activation or habit *outcome* — e.g. "weekly active
   developers who completed the core action." Never reach.
3. **Add guardrails.** 1–2 guardrail metrics that must not regress (e.g. time-to-first-success,
   community first-response time).
4. **Find the weakest stage.** Read the leading indicators; the lowest-converting step is the leak.
5. **Invest at the leak, not the loudest channel.** More awareness spend on a broken activation
   step just fills a leaky bucket faster (see `devrel-metrics` for the vanity-metric ban).
6. **Assign an owner + source to every metric.** An ownerless or sourceless metric is untrusted.

## Anti-patterns

- A 30-metric dashboard (none of them are the north-star).
- Funding more content when the data says the quickstart is the bottleneck.
- A north-star that's a reach number (followers, impressions, stars).

## Output

A one-page program: funnel definition, north-star + guardrails (each with owner + source),
the named weakest stage, and 2–3 ranked interventions. Hand activation work to
`docs-and-samples-engineer`, habit/advocacy work to `community-manager`, awareness/content to
`developer-advocate`.
