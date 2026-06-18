---
name: conference-talk-and-cfp
description: Draft or review a CFP abstract and talk that lead with the attendee takeaway — a title and abstract framed around what the attendee can do afterward (not the speaker or the product), concrete takeaways, and reviewer-fit notes for the specific track. Reach for this on "draft a CFP abstract" or "review my talk proposal". Used by `developer-advocate` (primary).
---

# Skill: conference-talk-and-cfp

> **Invoked by:** `developer-advocate` (primary).
>
> **When to invoke:** "draft a CFP abstract for a talk on X"; "review my conference proposal";
> shaping a talk so it gets accepted *and* lands with the audience.
>
> **Output:** title + abstract + 2–4 concrete takeaways + reviewer-fit notes + the §6 Output Contract.

## Procedure

1. **Lead with the attendee takeaway.** The abstract's first job is to answer "what will I be able to
   do after 30 minutes?" — not "who is the speaker" or "what does the product do" (house opinion #5).
2. **State 2–4 concrete takeaways**, each an action or capability the attendee leaves with. "Understand
   X" is weak; "build/diagnose/avoid X" is strong.
3. **Match the track.** Read the conference/track theme and audience level; write reviewer-fit notes
   ("this fits the 'production reliability' track because…"). A great talk on the wrong track is rejected.
4. **Earn trust, don't pitch.** A CFP that's a product ad gets rejected by program committees and
   tuned out by attendees. Teach a transferable lesson; mention the product as the example, not the subject.
5. **Right-size the scope** for the time slot — one clear arc beats five rushed points.
6. **Use the template** [`../../templates/cfp-abstract.md`](../../templates/cfp-abstract.md).

## Worked example

> User: "Draft a CFP abstract — I want to talk about our new caching layer."

- Reframe from "our caching layer" (product) to "how we cut p99 latency 60% without a rewrite" (takeaway).
- Takeaways: spot the cache-stampede failure mode; pick cache-aside vs. read-through; measure the win honestly.
- Track fit: performance/reliability track, intermediate level.
- Product appears as the *example* the lessons came from, not the subject.

## Guardrails

- If the abstract's first sentence is about you or the product, rewrite it — lead with the attendee.
- "Learn about" is not a takeaway; name the action.
- Don't promise more than fits the slot; reviewers reject over-scoped talks.
