# Knowledge — DevRel metrics: the developer pirate funnel, TTFHW, and vanity-metric traps

> **Last reviewed:** 2026-06-17 · **Confidence:** High (DevRel measurement consensus; pirate-funnel / TTFHW are field-standard framings — see Provenance).
>
> The measurement source of truth for this plugin. Defines the developer pirate funnel (AAARRP), the leveraged activation metric (TTFHW), activation/retention/engagement, the qualitative product-feedback loop, and — critically — the **vanity-metric traps** that make a DevRel scorecard look healthy while developers fail. Read alongside the motion-choice tree in [`devrel-strategy-decision-tree.md`](devrel-strategy-decision-tree.md).

---

## 1. The developer pirate funnel (AAARRP)

The classic "pirate funnel" (AARRR) extended for DevRel with a sixth, DevRel-specific stage — **Product-feedback** — because in DevRel the developer's friction is a first-class output, not an afterthought.

| Stage | The developer… | Headline metric | Formula / definition |
|---|---|---|---|
| **Awareness** | encounters the product | qualified awareness | developers reached who match the ICP (not raw views) |
| **Acquisition** | takes a first step | signups / clones / doc visits | count of first-step actions in a window |
| **Activation** | reaches **first hello-world** | **activation rate** | (developers who reach first hello-world) ÷ (acquired developers) |
| **Retention** | comes back and builds | wN retention | (active in week N) ÷ (activated in week 0) |
| **Revenue / Referral** | converts or advocates | conversion / referral rate | (paid or referring developers) ÷ (retained) |
| **Product-feedback** | surfaces friction to PM/eng | feedback throughput | friction items routed to PM/eng per cycle (and % actioned) |

The funnel is only real once **every stage has an observable definition and one metric**. A stage you can't instrument is a slogan.

## 2. Time-to-first-hello-world (TTFHW) — the leveraged number

**Definition:** the elapsed time from a developer's first step (signup / clone / page open) to their first *real* runnable result — a returned API response, a rendered output, a passing call. It is the single most leveraged number in DevRel because it gates **activation**, and activation gates everything downstream.

- **Measure it on a clean machine**, end-to-end, the way a new developer experiences it — not from your already-configured laptop.
- **Every step before first hello-world is overhead to cut**: signups, API keys, manual config, dependency installs that don't gate the result. Deferring the signup past first hello-world is the highest-frequency win (sandbox/demo keys).
- **Report it with the path that produced it** ("90s with a pre-provisioned sandbox key; 12 min if account creation is required first").

```
activation rate = developers reaching first hello-world / acquired developers
TTFHW          = t(first runnable result) − t(first step)        # lower is better
```

## 3. Content engagement (measured honestly)

Content is measured by **what the developer did**, not how many saw it:

- **Completion** — % who finished the tutorial / reached the success check (not page views).
- **Sample runs** — clones-that-run, "Run in sandbox" executions (not stars).
- **Talk-to-trial** — viewers who started a trial (not view count).

## 4. The qualitative product-feedback loop

Quantitative metrics tell you *that* developers leak; **qualitative feedback tells you why**. The DevRel team is the company's most honest source of developer friction — the friction an advocate feels building the sample is the friction every developer feels.

- Make it a **standing artifact** (a recurring DX-feedback digest to PM/eng), not an anecdote in a Slack thread.
- Track **throughput and action rate**: friction items routed per cycle, and the share PM/eng actually ships.
- The loop closes when a routed friction item ships and the corresponding activation metric moves.

## 5. Vanity-metric traps (the failure mode this plugin exists to prevent)

A **vanity metric** measures your *reach*, not the developer's *success*. It goes up with effort and says nothing about whether developers can build. The trap: a scorecard of vanity metrics can be all-green while activation is zero.

| Vanity metric | Why it's a trap | Pair it with / replace it with |
|---|---|---|
| Twitter/X followers | reach, not adoption; bought/bot-able | activation rate |
| GitHub stars | a bookmark, not usage | sample-app runs / week-4 retention |
| Page views / impressions | a click is not a success | content completion / TTFHW |
| Likes / reactions | engagement theater | talk-to-trial rate |
| Total signups | acquisition, not activation | **activation rate** (signup → first hello-world) |
| Conference attendee count | reach, not qualified | qualified-awareness / talk-to-trial |

**The rule:** a vanity metric is never a *headline* KPI. Keep it only as a labeled **leading indicator** for awareness, never as the number the team is judged on. North-star metrics live in the **activation / retention** band of the funnel.

## See also

- [`devrel-strategy-decision-tree.md`](devrel-strategy-decision-tree.md) — picks the motion whose metric lives here.
- [`../skills/measure-devrel-impact/SKILL.md`](../skills/measure-devrel-impact/SKILL.md) — builds the scorecard from these definitions and runs the vanity screen.
- [`../best-practices/optimize-time-to-first-hello-world.md`](../best-practices/optimize-time-to-first-hello-world.md) — the TTFHW rule.
- [`../best-practices/close-the-product-feedback-loop.md`](../best-practices/close-the-product-feedback-loop.md) — the §4 loop as a citable rule.

## Provenance

Codifies field-standard DevRel measurement: the pirate funnel (AARRR, McClure) extended with the DevRel product-feedback stage; TTFHW as the activation lever; and the vanity-vs-actionable distinction (Croll & Yoskovitz, *Lean Analytics*) applied to developer audiences. Consensus framings as of the review date; volatile platform-specific reach numbers are not quoted here without a retrieval date.

---

_Last reviewed: 2026-06-17 by `claude`_
