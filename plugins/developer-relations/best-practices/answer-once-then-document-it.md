# Answer the question once, then document it

**Status:** Pattern.

**Rule:** A recurring community question is a missing docs/quickstart section. Answer it once well,
then route it to the docs so the next developer finds the answer without asking — and the community
scales past staff capacity.

## Why

A community that depends on staff to answer the same questions forever does not scale; its support
load grows linearly with its size. Every recurring question is also a signal: it marks a precise gap
in the onboarding or docs where developers predictably get stuck. Converting answers into docs both
reduces the repeat load and closes the activation leak that generated the question.

## What it looks like in practice

- Recurring questions are clustered; each cluster becomes a docs/quickstart edit routed to the
  DX/docs engineer.
- Answers link to the (now-updated) docs, reinforcing the canonical source.
- The self-answer ratio and time-to-first-response are tracked as community-health metrics.

## Anti-pattern

A heroic support presence that answers everything in real time but never feeds the answers back into
docs — high effort, no compounding, and a recurring activation leak left wide open.
