---
name: hunt-for-a-threat
description: Run a hypothesis-driven threat hunt — turn a testable claim about adversary activity into named data sources and queries, guided by MITRE ATT&CK, and rank findings up David Bianco's pyramid of pain so effort goes at TTPs (expensive for the adversary to change) rather than hashes and IPs (trivial to change). Returns the hypothesis, the data sources + queries, findings, and any detections/incidents to spin up. Used by `detection-and-forensics-engineer` (primary).
---

# Skill: hunt-for-a-threat

> **Invoked by:** `detection-and-forensics-engineer` (primary).
>
> **When to invoke:** "hunt for signs of X"; "are we compromised even though nothing alerted?"; proactively on a schedule; after threat intel names a new TTP.
>
> **Output:** a stated hypothesis, the data sources and queries, the findings ranked on the pyramid of pain, and the follow-ups (a new detection, an incident, or "no evidence found — hypothesis rejected").

## When to invoke

Threat hunting is *proactive* — it assumes a breach that the existing detections missed and goes looking. Invoke it on a cadence, after new intel, or when an incident suggests the adversary was present longer than the alerts show.

## Output

The hunt writeup: hypothesis, scope, data sources, queries run, findings, and disposition (build a detection, open an incident, or reject the hypothesis with evidence).

## Procedure

1. **Form a testable hypothesis.** Not "let's look around" — a specific, falsifiable claim: *"An adversary is using WMI (T1047) for lateral movement between workstations in the last 30 days."* A hunt you can't reject isn't a hunt.
2. **Pick the ATT&CK technique(s) and data sources.** Map the hypothesis to tactic/technique, then to the telemetry that would show it (process creation, WMI logs, network flows, auth events). If the data source doesn't exist, the finding is "we're blind here" — a gap to hand to detection/observability.
3. **Aim high on the pyramid of pain.** Hunt for **TTPs and tools**, not just IOCs. Hashes/IPs/domains are cheap for the adversary to rotate; behaviors (how they move, persist, exfil) are expensive to change — finding those actually costs the adversary.
4. **Run the queries and analyze.** Query the SIEM/EDR/data lake. Reduce noise by baselining "normal" first, then look for the deviation the hypothesis predicts. Pivot on any hit (same host? same account? spread?).
5. **Disposition the findings.**
   - **Malicious activity found** → open an incident ([`../triage-and-classify-an-incident/SKILL.md`](../triage-and-classify-an-incident/SKILL.md)) and preserve evidence ([`../acquire-and-preserve-evidence/SKILL.md`](../acquire-and-preserve-evidence/SKILL.md)).
   - **Benign-but-repeatable behavior worth alerting** → build a detection ([`../engineer-a-detection/SKILL.md`](../engineer-a-detection/SKILL.md)).
   - **Nothing found** → record the rejected hypothesis and the coverage it validated; that's a successful hunt too.
6. **Feed the loop.** Every hunt should leave behind either a detection, an incident, or documented coverage — never just a vibe.

## Quick reference — the pyramid of pain (bottom = cheap for adversary, top = painful)

| Level | Indicator | Pain to adversary if you detect it |
|---|---|---|
| Bottom | Hash values | Trivial — recompile |
| ↓ | IP addresses | Easy — rotate |
| ↓ | Domain names | Simple — re-register |
| ↓ | Network/host artifacts | Annoying |
| ↓ | Tools | Challenging — retool |
| **Top** | **TTPs (behaviors)** | **Tough — change how they operate** |

Hunt as high as the data allows — TTP-level detections are the ones that hold.

## Guardrails
- **A hunt is a testable hypothesis, not browsing** — if you can't state what would reject it, refine it first.
- **Climb the pyramid** — a hunt that only chases hashes/IPs finds this campaign, not the next; hunt behaviors.
- **Baseline before you alarm** — "unusual" only means something against a known-normal; establish normal first.
- **A confirmed find is an incident** — don't keep investigating quietly; classify and preserve evidence. See [`../../best-practices/preserve-evidence-before-you-remediate.md`](../../best-practices/preserve-evidence-before-you-remediate.md).
