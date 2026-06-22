---
name: community-health-review
description: "Diagnose a developer community by the metrics that matter — answered-question rate, time-to-first-response, returning contributors, and sentiment — not member or follower count. Use to assess a forum/Discord/Discussions/Stack Overflow presence and design ops that fix unanswered questions."
---

# Skill: Community-health review

Score a developer community by whether developers get unblocked and come back — not
by how many people joined. A community is a garden, not a megaphone.

## When to use

- You don't know whether your developer community is healthy or dying.
- Questions sit unanswered and you need an ops design to fix it.
- Leadership is tracking member/follower count and missing the real signal.

## Procedure

1. **Measure the health metrics, not vanity:**
   - **Answered-question rate** — % of questions that get a useful answer.
   - **Time-to-first-response** — how long a question waits.
   - **Returning contributors** — people who come back and help others.
   - **Sentiment** — tone of threads (frustrated vs. productive).
   Member/follower/message counts are context, not health.
2. **Find the unanswered questions.** An unanswered question is a public signal the
   community is dying — and it compounds (developers stop asking).
3. **Design triage + response SLAs** so the answered-question rate and
   time-to-first-response improve: who watches, how fast, how it escalates.
4. **Capture canonical answers** back into docs/samples (route to
   `devrel-content-engineer`) so the same question isn't re-asked forever, and route
   recurring **pain** to `developer-advocate` for the product-feedback loop.
5. **Design the contributor ladder** — user → answerer → contributor → ambassador —
   with recognition that rewards genuine help, not volume (no pay-to-post).
6. **Capture it** in the
   [`community-health-review`](../../templates/community-health-review.md) template.

## Output

A scored health review (answered-question rate, TTFR, returning contributors,
sentiment), an ops design, and a contributor-ladder plan.

## Anti-patterns

- Reporting community health as member/follower count.
- Letting first questions go unanswered (the broken-window effect).
- Pay-to-post incentives that reward volume over genuine help.
