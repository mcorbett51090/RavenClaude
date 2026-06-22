---
description: Charter a cross-team program — turn a fuzzy mandate into a measurable outcome, a named sponsor, in/out-of-scope boundaries, the teams on the hook, and a starting RAID, before any planning begins.
argument-hint: "[the mandate, e.g. 'ship the new billing platform across teams by Q3']"
---

# Charter a program

You are running `/technical-program-management:charter-a-program`. Charter the
program described in `$ARGUMENTS` using the `technical-program-manager` discipline:
no measurable outcome and no named sponsor → it's a request, not a program.

## When to use this

A multi-team effort has been handed down with a fuzzy outcome. If the work is a
single team's plan, route to `project-management`. If it's about people/headcount,
route to `engineering-management`. Confirm it's a program via tree 1 in
[`../knowledge/tpm-engagement-decision-trees.md`](../knowledge/tpm-engagement-decision-trees.md).

## Steps

1. **Write the outcome as one measurable sentence** — metric + target + date. Push
   back until it's measurable; you can't close what you can't measure.
2. **Name the single sponsor** (funding + tie-break authority). Two sponsors is
   zero sponsors.
3. **Draw the scope boundary — out-of-scope first** (it protects the date).
4. **List the teams and each team's one deliverable** into the program.
5. **Seed the RAID** with known risks, assumptions, issues, dependencies.
6. **Fill the [`program-charter`](../templates/program-charter.md) template** and get
   explicit sponsor sign-off before planning.

## Guardrails

- Never proceed to planning without a measurable outcome and a named sponsor.
- Don't absorb a single team's task plan — route it to `project-management`.
