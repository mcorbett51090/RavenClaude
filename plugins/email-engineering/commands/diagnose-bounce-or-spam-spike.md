---
description: "Diagnose a sudden bounce-rate or spam-complaint spike — classify the bounce/complaint types, find the source stream, and produce the suppression + remediation steps to protect sender reputation."
argument-hint: "[the spike, e.g. 'hard bounce rate jumped to 8% after a list import']"
---

# Diagnose a bounce or spam spike

You are running `/email-engineering:diagnose-bounce-or-spam-spike`. For the spike in `$ARGUMENTS`, find the cause and stop the bleeding — the feedback-loop discipline of the `email-sending-engineer` and the reputation lens of the `email-deliverability-architect`.

## When to use this

Bounce rate or spam-complaint rate jumped, or a domain's Postmaster reputation dropped. Time-sensitive — reputation damage compounds.

## Steps

1. **Classify** the events: hard bounce (suppress permanently) vs soft bounce (bounded retry) vs spam complaint (suppress + strong negative signal) — per `skills/bounce-complaint-suppression/SKILL.md`.
2. **Find the source stream** — which subdomain/campaign/list drove the spike? A list import, a cold blast, or a compromised signup form are the usual culprits.
3. **Stop sending** from the offending stream while you remediate; don't push harder.
4. **Enforce suppression** as a hard pre-send gate; reconcile with the ESP's suppression list.
5. **Remediate the list** — drop the bad import, confirm opt-in, add double-opt-in / form protection if a bot filled it.
6. **Plan recovery** — reputation recovers by sending wanted mail to engaged recipients at a controlled volume (a mini warm-up), watching Postmaster.

## Guardrails

- Never re-send to a hard bounce or complainer — it's the fastest way to a blocklist.
- A complaint is worse than a bounce; honor it instantly and globally.
- Bought/scraped lists hit spam traps — a sudden spike right after an import is the tell.
