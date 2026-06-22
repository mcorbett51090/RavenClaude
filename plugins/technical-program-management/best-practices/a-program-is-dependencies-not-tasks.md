# A program is its dependencies, not its tasks

**Stance:** the first artifact of a program is the cross-team dependency map and
the critical path — never a flat task list.

## Why

Tasks belong to teams. Each team already plans, estimates, and tracks its own
work; the TPM duplicating that is waste and noise. What no single team owns — and
what actually kills programs — is the **handoff between teams**: the API that
arrives a week late, the schema two teams interpreted differently, the env that
wasn't provisioned. The program's date is decided by the longest chain of those
handoffs (the critical path), not by the sum of everyone's tasks.

## In practice

- Organize the program plan around cross-team deliverables, each with a producer,
  consumer, due date, and interface contract.
- Derive the critical path; quantify slack on everything else so urgency tracks
  reality, not visibility.
- Let each team own its internal task plan (`project-management`). Track the seams.

## Smell

If your program plan looks like a merged backlog of every team's tickets, you're
doing a PM's job at the wrong altitude — and you'll miss the handoff that slips
the date.
