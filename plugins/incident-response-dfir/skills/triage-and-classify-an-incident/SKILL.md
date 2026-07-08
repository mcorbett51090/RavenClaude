---
name: triage-and-classify-an-incident
description: Decide whether an alert or report is a genuine security incident (the is-it-an-incident gate), then classify its severity/priority from a business-impact × scope matrix so the response tier is set by impact, not by how loud the alert looks. Returns the incident verdict, the severity level + the rule that picked it, and the response tier it triggers. Used by `dfir-response-lead` (primary).
---

# Skill: triage-and-classify-an-incident

> **Invoked by:** `dfir-response-lead` (primary).
>
> **When to invoke:** "is this an incident?"; "what severity is this?"; "does this page someone?"; a fresh alert or report lands.
>
> **Output:** the is-it-an-incident verdict, the severity/priority level + the matrix rule that picked it, and the response tier (who is engaged, on what cadence).

## When to invoke

At the front door of every alert or report — before any containment or forensics. Under-classifying wastes the window; over-classifying burns the team on false positives. This skill makes the call defensible.

## Output

A short verdict block: **event vs incident**, **severity (S1–S4) + reasoning**, **response tier**, and the immediate next action (escalate to lifecycle, tune the detection, or close as benign).

## Procedure

1. **Gate: is this an incident?** An *event* is any observable occurrence; an *adverse event* has negative consequence; a *security incident* is a violation (or imminent threat of violation) of security policy, acceptable-use, or standard practice (NIST SP 800-61r3, CSF 2.0-aligned; supersedes r2). If it's a confirmed false positive → route to detection tuning, not the lifecycle. If unconfirmed → treat as a suspected incident and proceed (you can downgrade).
2. **Scope the impact.** What is affected and how badly? Confidentiality (data exposed?), Integrity (data/systems altered?), Availability (service down?). Note whether regulated/personal data is in scope — that changes the notification obligations (hand to the lead).
3. **Scope the spread.** One host or many? A sandbox or a domain controller / crown-jewel system? Contained to one account or lateral movement observed?
4. **Classify severity from impact × scope.** Use the matrix below. Severity is the *business* consequence, not the alarm's tone — a quiet alert on a DC outranks a loud one on a test box.
5. **Set the response tier.** Severity selects who is engaged and the comms cadence: analyst-only vs. full incident-commander activation with legal/exec on standby.
6. **Record and hand off.** Timestamp the triage decision, and hand to [`run-the-incident-lifecycle`](../run-the-incident-lifecycle/SKILL.md) if S1–S3, or to [`../engineer-a-detection/SKILL.md`](../engineer-a-detection/SKILL.md) if it was a false positive worth tuning.

## Quick reference — severity matrix

| Severity | Impact × scope | Examples | Response tier |
|---|---|---|---|
| **S1 — Critical** | High impact, wide/critical scope | Active data exfiltration, ransomware spreading, DC/crown-jewel compromise, confirmed breach of regulated data | Full IC activation; exec + legal engaged; 24/7 cadence |
| **S2 — High** | High impact, contained; or medium impact spreading | Single-host compromise with malware, credential theft, targeted intrusion not yet lateral | IC + on-call responders; ~hourly cadence |
| **S3 — Medium** | Medium impact, contained | Isolated malware on a non-critical endpoint, policy violation with limited exposure | SOC analyst + lead; business-hours cadence |
| **S4 — Low** | Low impact / suspected | Blocked phishing, unsuccessful exploit attempt, informational alert to investigate | Analyst triage; no activation |

> Impact axis: Critical / High / Medium / Low. Scope axis: crown-jewel/wide → single/isolated. Take the higher of the two when in doubt.

## Guardrails
- **Severity drives the response, not the noise** — classify by impact × scope, never by how alarming the alert *looks*. See [`../../best-practices/severity-drives-the-response-not-the-noise.md`](../../best-practices/severity-drives-the-response-not-the-noise.md).
- **When unconfirmed, treat as suspected and proceed** — you can downgrade later; you can't recover the window you lost waiting for certainty.
- **Regulated/personal data in scope flips the clock** — flag it to the lead immediately so the notification timeline (GDPR 72h etc.) starts at awareness. See [`../../best-practices/notification-timelines-are-legal-deadlines-not-guidelines.md`](../../best-practices/notification-timelines-are-legal-deadlines-not-guidelines.md).
- **Re-triage as facts change** — severity is not set once; a "contained single host" that turns out lateral is now S1.
