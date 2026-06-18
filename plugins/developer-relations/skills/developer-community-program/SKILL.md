---
name: developer-community-program
description: Design or evaluate a developer-community program by its health, not its size — decide build-vs-sponsor-vs-skip, set the response-time and resolution SLA, instrument the health metrics (response time, resolution rate, unanswered-question rate), and design the member-to-advocate path. Reach for this on "should we run a Discord/forum?" or "is our community worth it?". Used by `devrel-strategist` (primary).
---

# Skill: developer-community-program

> **Invoked by:** `devrel-strategist` (primary).
>
> **When to invoke:** "should we build a community?"; "is our Discord/forum worth it?"; "how do we
> run our community?"; evaluating a community's health.
>
> **Output:** a build/sponsor/skip recommendation + the health SLA + the health metric set + the §6 Output Contract.

## Procedure

1. **Traverse the build-vs-sponsor-vs-skip tree**
   ([`../../knowledge/devrel-strategy-decision-trees.md`](../../knowledge/devrel-strategy-decision-trees.md), Tree 2):
   no recurring need → skip; can't staff fast response → sponsor an existing channel; recurring need +
   staffable + critical mass → build/own with a health SLA.
2. **Set the health SLA** for an owned community: target response time and resolution rate. An owned
   channel you can't staff is worse than no channel — it advertises neglect.
3. **Instrument health, not size** ([`../../knowledge/devrel-funnel-and-metrics.md`](../../knowledge/devrel-funnel-and-metrics.md)):
   - median first-response time,
   - resolution rate,
   - unanswered-question rate,
   - questions answered by *members* (the advocacy signal), not just staff.
   Member count is context, never the headline (house opinion #6).
4. **Design the member→advocate path** — how a helped developer becomes one who helps others
   (recognition, contributor ladder, UGC amplification).
5. **Decide the spend honestly.** If the health metrics can't be hit with the available staffing,
   recommend *sponsor* over *build*, or *skip*.

## Worked example

> User: "We have a 5k-member Discord but it feels dead. Worth keeping?"

- Health check: median first-response = 2 days, unanswered rate = 40%. That's an unhealthy owned channel.
- Tree: recurring need yes, but staffing can't hit a fast SLA → the honest call is shrink scope to a
  staffable core + sponsor an existing channel for overflow, or commit real staffing.
- Metric: target first-response < 4h, resolution > 70%; member count demoted to context.
- Advocate path: spotlight the 3 members already answering; give them a contributor role.

## Guardrails

- Member count is a vanity metric — never the headline for community health.
- Don't recommend building an owned community you can't staff to its SLA.
- A dead 5k channel is a *liability*, not an asset — say so plainly.
