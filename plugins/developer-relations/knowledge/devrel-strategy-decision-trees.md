# Knowledge — DevRel strategy decision trees

> **Last reviewed:** 2026-06-18 · **Confidence:** High (these are format/channel selection heuristics,
> not volatile facts). Both agents traverse the relevant tree *before* recommending a tactic — the
> Capability Grounding Protocol's pre-action decision-tree traversal.

Don't keyword-match a tactic to a request ("they asked about a conference → submit a talk"). Walk the
tree from the **funnel stage** and the **audience**.

---

## Tree 1 — Which content format?

```mermaid
flowchart TD
    Q[What funnel stage + what does the developer need?] --> S1{Funnel stage}

    S1 -->|Awareness| AW{Do they have a problem<br/>they can name yet?}
    AW -->|No, unaware| AW1[Conceptual blog post / talk<br/>name the problem first]
    AW -->|Yes, searching| AW2[SEO how-to / comparison<br/>meet the search query]

    S1 -->|Activation| AC{Is the goal first working result<br/>or a deeper integration?}
    AC -->|First result| AC1[Runnable sample repo + quickstart<br/>shortest path that works]
    AC -->|Deeper| AC2[Tutorial / guided workshop<br/>one teaching goal per step]

    S1 -->|Retention/Advocacy| RA{Recurring touch<br/>or one-off?}
    RA -->|Recurring| RA1[Newsletter / office hours / changelog<br/>keep building with you]
    RA -->|One-off depth| RA2[Reference architecture / case study<br/>show what good looks like]
```

**Rule of thumb:** format follows funnel stage, not personal preference for video vs. writing.
Awareness teaches the *problem*; activation hands a *runnable path*; retention/advocacy keeps the
relationship warm.

---

## Tree 2 — Build, sponsor, or skip a community?

```mermaid
flowchart TD
    C[Considering a developer community] --> C1{Do you have a<br/>recurring support/feedback need<br/>from developers?}
    C1 -->|No| SKIP[Don't build one yet<br/>you'll have a ghost town]
    C1 -->|Yes| C2{Can you staff a fast<br/>response to questions?}
    C2 -->|No| SP[Sponsor / participate in an<br/>existing community<br/>Stack Overflow, Discord, subreddit]
    C2 -->|Yes| C3{Is there a critical mass<br/>of your developers already talking?}
    C3 -->|No| SP
    C3 -->|Yes| BUILD[Build/own the community<br/>+ commit to the health SLA<br/>response time + resolution]
```

**The trap:** building an owned community (Discord/forum) you can't staff. A 5,000-member channel
where questions sit for a week is a liability — it advertises neglect. Health is response time +
resolution, never headcount. If you can't staff it, *sponsor* an existing one.

---

## Tree 3 — Which channel for a launch / announcement?

```mermaid
flowchart TD
    L[Have something to announce] --> L1{Is it actionable for<br/>a developer right now?}
    L1 -->|No, it's a milestone| L2[Changelog + a short note<br/>don't over-broadcast a non-event]
    L1 -->|Yes, they can use it today| L3{Does it need a walkthrough<br/>to be usable?}
    L3 -->|Yes| L4[Launch blog + runnable sample<br/>+ docs link, then amplify]
    L3 -->|No, drop-in| L5[Changelog + social + community<br/>ping the people it unblocks]
```

**Rule:** don't spend launch capital on a non-event. Reserve the big push for things a developer can
*do something with today*, and always pair an announcement with the runnable path to use it.

---

## How to use these trees

1. Resolve the **funnel stage** first (from [`devrel-funnel-and-metrics.md`](devrel-funnel-and-metrics.md)).
2. Walk the matching tree top-to-bottom to a leaf.
3. State the path you took on the Output Contract `Recommendation:` line, and the metric the leaf
   moves on the `Metric:` line.
4. If the situation outgrows the flat tree (multi-audience, multi-stage campaign), compose leaves and
   say so — don't force one leaf to cover everything.

---

## Provenance

Codifies developer-relations CLAUDE.md §3 house opinions #2 (teach, don't market), #6 (community
health is response/resolution), and the §2 routing rules. These are selection heuristics, not
vendor-specific facts; tooling specifics live in [`devrel-tooling-2026.md`](devrel-tooling-2026.md)
with retrieval dates.

---

_Last reviewed: 2026-06-18 by `claude`_
