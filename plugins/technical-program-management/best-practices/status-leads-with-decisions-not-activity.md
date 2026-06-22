# Status leads with decisions and asks, not activity

**Stance:** the top line of every program status is the change in risk/critical
path, the decision needed, and the explicit ask — not a list of what got done.

## Why

Executives read status to make decisions and unblock the program, not to audit
effort. An activity-led update ("Team A did X, Team B did Y") forces the reader to
reverse-engineer what matters and what you need from them — most won't, so the
status fails its only job. And rolling up an **average** of green/yellow/red hides
the one red dependency that decides the date.

## In practice

Open every status with, in order:

1. **What changed** in the risk / critical-path picture since last time.
2. **The decision needed** (if any) — framed as a specific choice with a deadline.
3. **The ask** — what you need from the reader, by when.

Then, and only then, the supporting detail. Roll up the **worst** dependency, not
the average. Use the
[`program-status-update`](../templates/program-status-update.md) template.

## Smell

A status whose first sentence is "This week the team…" — and a program that's
been "green" for six weeks and then slips. Green-with-a-red-dependency is a lie.
