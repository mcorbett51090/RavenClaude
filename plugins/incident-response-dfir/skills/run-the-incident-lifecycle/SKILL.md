---
name: run-the-incident-lifecycle
description: Run a security incident through the four NIST SP 800-61r2 phases in order — preparation, detection & analysis, containment/eradication/recovery, and post-incident activity — with the contain-before-eradicate and preserve-evidence-first gates enforced at the right steps. Returns a phase-by-phase runbook, the containment strategy, the recovery/eradication plan, and a blameless post-incident review. Used by `dfir-response-lead` (primary); shared with the forensics engineer at the analysis seam.
---

# Skill: run-the-incident-lifecycle

> **Invoked by:** `dfir-response-lead` (primary); `detection-and-forensics-engineer` at the analysis/forensics seam.
>
> **When to invoke:** "we have an active incident — what now?"; "walk us through the response"; after triage classifies an S1–S3.
>
> **Output:** the current phase, the actions for it, the gates that must clear before advancing, and the artifacts (containment plan, eradication/recovery plan, post-incident report).

## When to invoke

Once triage ([`../triage-and-classify-an-incident/SKILL.md`](../triage-and-classify-an-incident/SKILL.md)) confirms an incident. This skill is the spine of the whole response — it keeps the phases in order and refuses to skip the evidence gate.

## Output

A running runbook keyed to the four phases, a contemporaneous timeline, and the phase-exit gates. Each phase produces a concrete artifact.

## Procedure — the four NIST SP 800-61r2 phases

1. **Preparation** (before the incident, revisited during). Confirm you have: the IR plan and roster, access to the tools/logs, out-of-band comms, and legal/regulatory contacts. If mid-incident you find a gap here, note it for the post-incident review — don't stall.
2. **Detection & Analysis.** Validate and scope. Confirm the incident is real (from triage), determine the attack vector, identify affected systems/accounts/data, and build the timeline. Map observed behavior to MITRE ATT&CK (hand to [`../hunt-for-a-threat/SKILL.md`](../hunt-for-a-threat/SKILL.md) / [`../engineer-a-detection/SKILL.md`](../engineer-a-detection/SKILL.md) as needed). **Gate:** before touching a live system to contain, capture volatile evidence per [`../acquire-and-preserve-evidence/SKILL.md`](../acquire-and-preserve-evidence/SKILL.md).
3. **Containment, Eradication & Recovery** — in that order.
   - **Containment** — stop the bleed. Choose short-term (isolate host, disable account, block C2) vs. long-term (rebuild in a clean segment). **Preserve evidence before containing** if containment is destructive (don't hard power-off before memory capture).
   - **Eradication** — remove the root cause: delete malware, close the exploited vuln, rotate compromised credentials/keys, remove persistence. Eradicating symptoms without root cause invites reinfection.
   - **Recovery** — restore to known-good, validate, and monitor closely for recurrence. Return systems to production in a controlled, monitored way; confirm the adversary is out before you declare recovery.
4. **Post-Incident Activity.** Run a **blameless** post-mortem within ~2 weeks: timeline, root cause, what worked, what didn't, and concrete follow-ups (detections to build, controls to add, runbook fixes). Feed lessons back into Preparation. Use [`../../templates/incident-report-postmortem.md`](../../templates/incident-report-postmortem.md).

## Quick reference — phases, gates, artifacts

| Phase | Goal | Exit gate | Artifact |
|---|---|---|---|
| Preparation | Ready to respond | Plan + roster + tools + comms exist | IR plan (living) |
| Detection & Analysis | Confirm + scope | Vector, blast radius, and timeline known; **volatile evidence captured** | Scoped timeline |
| Containment | Stop spread | Evidence preserved; spread halted | Containment plan |
| Eradication | Remove root cause | Root cause removed, persistence gone | Eradication plan |
| Recovery | Restore safely | Restored to known-good + monitored; adversary confirmed out | Recovery plan |
| Post-Incident | Learn | Blameless review done; follow-ups tracked | Post-mortem report |

## Guardrails
- **Contain before you eradicate** — you can't cleanly remove what you haven't first stopped from spreading. See [`../../best-practices/contain-before-you-eradicate.md`](../../best-practices/contain-before-you-eradicate.md).
- **Preserve evidence before you remediate** — the containment/eradication step often destroys volatile evidence; capture it first. See [`../../best-practices/preserve-evidence-before-you-remediate.md`](../../best-practices/preserve-evidence-before-you-remediate.md).
- **Eradicate root cause, not symptoms** — reimaging a host while the exploited vuln stays open is reinfection-in-waiting.
- **The post-mortem is blameless** — root-cause the system, not a person, or you teach the org to hide incidents. See [`../../templates/incident-report-postmortem.md`](../../templates/incident-report-postmortem.md).
