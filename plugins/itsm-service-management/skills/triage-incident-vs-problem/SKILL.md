---
name: triage-incident-vs-problem
description: "Classify an issue as an incident (restore service now), a problem (remove the recurring cause), or a major incident (declare command), and open the right record. Reach for this when something is broken or keeps breaking."
---

# Skill: Triage incident vs problem

Two different jobs with two different success metrics. Get the classification right or you firefight forever (§2 #1).

## Step 1 — Is it a major incident?
Check the major-incident criteria (broad impact / critical service down / high urgency). If yes, declare it and switch to the major-incident process (commander + comms) — see the [`major-incident-runbook`](../../templates/major-incident-runbook.md).

## Step 2 — Incident or problem?
- **Incident** — service is degraded/down *now*; the job is to **restore** it fast (a workaround counts). Metric: time-to-restore.
- **Problem** — the underlying **cause** of one or more incidents; the job is to **remove** it. Metric: recurrence eliminated.
- A recurring incident is the signal to open a *problem* alongside restoring the *incident*.

## Step 3 — Prioritize the incident
Impact × urgency → priority. Restore with the fastest safe path; a documented workaround is a legitimate restoration.

## Step 4 — Drive the problem to root cause
Open a problem record, run RCA, and log the **known error** (cause + workaround) so the next occurrence is fast to handle.

## Step 5 — Feed the permanent fix forward
The permanent fix usually needs a change → hand to the change-and-release-manager. Traverse the routing tree in [`../../knowledge/itsm-decision-trees.md`](../../knowledge/itsm-decision-trees.md).
