---
name: design-instructor-pay-model
description: "Design the instructor/trainer pay model: rev-share vs flat hourly vs per-head, worked at low and high attendance, plus the practical 1099-vs-W2 classification flag and a no-show / late-cancel policy with an enforcement mechanism."
---

# Design Instructor Pay Model

How you pay the people who run the schedule decides whether the studio survives a slow week. Choose the model on **who carries attendance risk**.

## The three models

| Model | Who carries attendance risk | Incentive it creates | Watch out for |
|---|---|---|---|
| **Flat hourly** | The studio | Show up, teach well | Empty class still costs full pay |
| **Per-head** | The instructor | Drive their own draw | Punishes instructor for the studio's marketing |
| **Rev-share** (% of class revenue) | Shared | Aligned both ways | Volatile; a slow week can underpay |

## Rules
- **Work an example at both low and high attendance.** A pay model that pays fairly at 15 and bankrupts the studio at 4 (or starves the instructor at 4 and overpays at 15) hasn't been tested. Show the math at both.
- **Rev-share usually needs a floor.** If driving attendance is the studio's job, don't put all that risk on the instructor — a per-class minimum keeps it fair.
- **Match the model to who controls the draw.** A named-talent instructor who brings their own following can carry per-head; a studio-branded class shouldn't.

## The 1099-vs-W2 flag (flag it; don't rule on it)
Lean toward **employee (W2)** as control rises:

- **Behavioral control** — you set their schedule, sequence, music, attire, methods.
- **Financial control** — you provide the space, equipment, and clients; they don't market independently.
- **Relationship** — ongoing/indefinite, integral to the business.

Misclassification is expensive (back taxes, penalties, benefits). **Surface the risk plainly and defer the binding determination to `people-operations-hr` and the studio's counsel** — and the actual 1099/payroll filing to `accounting-bookkeeping`.

## No-show / late-cancel policy (or expect ghost capacity)
Define all three or it's decoration:

1. **Window** — how late a cancel is "late" (e.g. < 12h `[verify-at-use]`).
2. **Penalty** — a fee or a forfeited class credit.
3. **Enforcement mechanism** — wired into the booking system, applied automatically. The fee exists to *protect capacity*, not to earn revenue.

## Anti-patterns
- A pay doc with no classification view (the hook flags this).
- A pay model tested at one attendance level.
- A no-show policy with no enforcement mechanism.

Output via [`../../templates/class-schedule-and-pay-plan.md`](../../templates/class-schedule-and-pay-plan.md). Traverse the pay-model and no-show trees in [`../../knowledge/fitness-studio-operations-decision-trees.md`](../../knowledge/fitness-studio-operations-decision-trees.md) first.
