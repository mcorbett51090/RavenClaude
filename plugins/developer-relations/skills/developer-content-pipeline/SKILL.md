---
name: developer-content-pipeline
description: "Run a sustainable developer-content engine — an editorial calendar mapped to funnel stages, one anchor artifact repurposed into blog/video/docs, sized to real team capacity. Used by developer-advocate (primary)."
---

# Skill: developer-content-pipeline

**Purpose:** Build a content engine that's sustainable (doesn't burn out the team) and
funnel-aware (every piece has a job). Used by `developer-advocate` (primary).

## When to use

- Planning a quarter of developer content
- A content cadence that's either sporadic or burning out the team
- Wanting more output without more people

## The core move: repurpose from an anchor

Don't author N independent pieces. Create one **anchor artifact** (a conference talk, a deep
technical post, a reference implementation) and repurpose it:

```
Anchor (deep-dive / talk)
  ├─ blog post (the written version)
  ├─ short video / clip (the demo)
  ├─ docs PR (the durable reference)
  ├─ social thread (the awareness hook)
  └─ sample repo (the runnable proof)
```

One unit of deep work yields five distribution surfaces across multiple funnel stages.

## Map each piece to a funnel stage

| Content type | Funnel stage | Job |
|--------------|--------------|-----|
| "What is X / why it matters" | Awareness | get heard |
| "Build Y in 20 minutes" | Activation | get them to first success |
| "Deep dive / advanced patterns" | Habit | deepen usage, retain |
| "Community spotlight / contributor story" | Advocacy | celebrate, recruit |

A calendar that's all awareness content while activation is the funnel's leak is misallocated.

## Size to real capacity

- Pick a cadence the team can actually sustain (one solid anchor/month beats four rushed posts).
- Build a backlog so a missed week doesn't break the cadence.
- Honest framing always: developer audiences punish thinly-veiled product pitches with distrust.

## Output

A quarterly editorial calendar: anchors + their repurposed pieces, each tagged with its funnel
stage and owner, sized to capacity. See [`../../templates/talk-abstract-template.md`](../../templates/talk-abstract-template.md)
for the talk anchor.
