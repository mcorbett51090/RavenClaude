# Interview for the Job, Not the Feature

**Status:** Absolute rule
**Domain:** Product discovery / customer interviews
**Applies to:** `product-management`

---

## Why this exists

Customer interviews structured around a feature ("what do you think of this design?") produce feedback on the feature, not insight into the underlying problem. Customers are excellent reporters of their own past behavior and the struggles it caused; they are poor predictors of whether a proposed solution will actually help them. The Jobs-to-be-Done framing (what job were you hiring a product to do, what triggered the search, what made you choose this one, what were you doing before) elicits the causal mechanism behind behavior, not just an opinion on a mockup. A product team that builds on feature feedback without first understanding the underlying job is optimizing against the wrong signal.

## How to apply

Structure discovery interviews to surface job, trigger, and struggle — never show a mockup until the job is understood.

```
Interview Structure — Jobs-to-be-Done Pattern
──────────────────────────────────────────────────────
Opening (5 min):
  "I want to understand how you [do the thing this product helps with].
   I'm not going to show you anything — I want to hear about your experience."

Job and context (15 min):
  "Tell me about the last time you [job the product addresses]."
  "What were you trying to accomplish?"
  "What triggered you to [start the process]?"
  "Walk me through what you actually did — step by step."

Struggle (10 min):
  "What was the hardest part of that?"
  "What didn't work the way you expected?"
  "What did you try before?"
  "What did you give up on and why?"

Pull (5 min — if the user has adopted your product):
  "What made you decide to try [product]?"
  "What almost made you not try it?"
  "When did you first feel like it was working?"

Wrap:
  "Is there anything I should have asked but didn't?"
```

**Do:**
- Record (with consent) or take verbatim notes; paraphrased notes lose the language customers use to describe their own struggles, which is the raw material for positioning and PRD language.
- Aim for 5–10 interviews before drawing conclusions; one interview is an anecdote.
- Keep the interviewer role and the note-taker role separate when possible; conducting and synthesizing simultaneously degrades both.

**Don't:**
- Show a mockup or feature concept in the first interview; save solution feedback for prototype testing, not problem discovery.
- Ask hypothetical future-behavior questions ("would you use X?"); people are unreliable reporters of future behavior and reliable reporters of past behavior.
- Lead with a pain point you already believe exists; the job is to discover what they actually struggle with, not confirm what you already think.

## Edge cases / when the rule does NOT apply

- **Usability testing** (structured test of an existing design) — showing the prototype is the point; the JTBD protocol does not apply, but problem-context framing at the opening still helps.
- **Quantitative survey research** — the JTBD interview pattern is qualitative; surveys address different questions at scale.

## See also

- [`../agents/product-discovery-lead.md`](../agents/product-discovery-lead.md) — owns the customer interview process, JTBD synthesis, and opportunity identification.
- [`./love-the-problem-not-the-solution.md`](./love-the-problem-not-the-solution.md) — the upstream house opinion; this doc operationalizes it at the interview-protocol level.

## Provenance

Codifies the product-discovery-lead's interview discipline from the product-management plugin's CLAUDE.md §2 #2 (discovery is continuous) and the JTBD framework (Bob Moesta / Clayton Christensen). The structured interview pattern is drawn from Teresa Torres' continuous discovery framework and Intercom's JTBD research practice.

---

_Last reviewed: 2026-06-05 by `claude`_
