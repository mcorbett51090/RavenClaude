# Engineering Management — frameworks & 2025–2026 context

> Research-grounded context for the team's house opinions (CLAUDE.md §3). Frameworks and figures here are dated and should be re-verified at use — management research evolves and benchmark thresholds shift (§3 #8). Treat every threshold as `[unverified — training knowledge]` unless a dated source is attached.

## DORA — a system signal, not a scoreboard (§3 #3)

The four keys (deploy frequency, lead time for change, change-fail rate, time to restore) come from the DORA / *Accelerate* research program and the annual State of DevOps reports. Two durable points the agents lean on:

- They measure the **delivery system's** capability — they were never designed to rank individuals, and using them that way triggers Goodhart's law (the metric gets gamed, the signal dies). [unverified — training knowledge]
- "Elite/high/medium/low" threshold bands shift between annual reports — **quote them with the report year + retrieval date**, never from memory (§3 #8).
- Later DORA work added a **reliability** key and emphasizes that throughput and stability move together in healthy systems — speed is not traded against quality.

## Career ladders & growth (§3 #2 #4)

- A written **career framework / ladder** (expectations per level across scope, autonomy, impact, and craft) is what makes growth conversations and promotions defensible instead of political. Public examples (e.g. the progression.fyi collection, dropbox/CircleCI-style ladders) are reference donors — adapt, don't copy.
- **Promotion is recognition of impact already operating at the next level**, evidenced over time — not a reward for tenure or a retention bribe. A promo packet is dated behavioral evidence mapped to the ladder.
- **Continuous note-taking beats recency bias.** Reviews reconstructed the week they're due overweight the last month and underweight quiet, durable contribution (§3 #4).

## Performance & underperformance (§3 #1 #4 #5)

- **Structured, behavioral signal reduces bias.** "Great attitude", "culture fit", and "communication issues" are where unexamined bias hides; the fix is naming the **observable behavior, the date, and the impact** (§3 #4).
- **System-before-person** is an ordering, not a denial: check unclear expectations, missing context, wrong-altitude assignments, blocked dependencies, and personal/health circumstances *before* concluding individual underperformance (§3 #5). Genuine misfit exists — but it's the last hypothesis, not the first.
- **A PIP is an HR/legal instrument**, not a management hack — its content and legality route to `people-operations-hr` and qualified counsel (§2). This team helps the manager set fair, documented expectations and support; it does not author binding HR process.

## Hiring (§3 #6)

- **Structured interviews** (consistent questions, a rubric, evidence-based scoring, a debrief that surfaces dissent) predict performance better and bias less than unstructured "did I click with them?" interviews — a durable, well-replicated finding in the I/O-psychology literature. [unverified — training knowledge; re-verify before quoting effect sizes]
- A **debrief that holds the bar the same on Tuesday and Friday** beats fatigue- and order-driven calibration drift. Disagreement is data — surface it, don't average it away.

## Tech-debt & codebase health (§3 #7)

- Frame debt as **carrying cost vs roadmap value**, sized per case, with a **standing maintenance-capacity slice** rather than an all-or-nothing crusade. The original "technical debt" metaphor (Cunningham) is about *deliberate, communicated* trade-offs, not just mess.
- Prefer **incremental (strangler-fig) paydown on measured hotspots** over a big-bang rewrite — the rewrite is the highest-risk, longest-payback option.

## How to use this file

- These are **durable framings**, not live facts. When a deliverable needs a *number* (a DORA band, a span range, a ramp time, an effect size), fetch it live and cite source + date, or mark it `[unverified — training knowledge]` (§3 #8).
- Route every HR / legal / compensation determination to the qualified authority (§2). This team supports the manager's craft; it does not replace HR, counsel, or a real conversation with a human.
