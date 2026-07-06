# Incident Report & Post-Mortem — <incident ID / name>

> Template for a **blameless** post-incident report. Blameless means we root-cause the *system and the process*, never a person — because the moment people fear being named, they stop reporting incidents and the org goes blind. Complete within ~2 weeks of resolution.

**Incident ID:** <ID> · **Severity:** <S1–S4> · **Status:** Resolved · **Author:** <name> · **Date:** <YYYY-MM-DD>

## 1. Executive summary
- 2–4 sentences: what happened, impact, how it was resolved, and the top follow-up. Plain language for leadership.

## 2. Impact
- **Confidentiality:** <data exposed? whose? how much?>
- **Integrity:** <data/systems altered?>
- **Availability:** <downtime, duration, users affected>
- **Regulated/personal data:** <in scope? notification obligations triggered?>
- **Business impact:** <cost, reputation, contractual>

## 3. Timeline (contemporaneous, timestamped, UTC)
| Time (UTC) | Event | Source |
|---|---|---|
| | Initial detection / first indicator | |
| | Triage / severity declared | |
| | Evidence captured | |
| | Containment actions | |
| | Eradication | |
| | Recovery / all-clear | |
| | Notifications sent | |

- **Time to detect (TTD):** <> · **Time to contain (TTC):** <> · **Time to recover (TTR):** <>

## 4. Detection & analysis
- How was it detected (alert / hunt / report / third party)?
- Attack vector and MITRE ATT&CK techniques observed (list technique IDs).
- Scope: systems, accounts, data affected.

## 5. Root cause (blameless)
- The **technical** root cause (the vulnerability/misconfiguration/gap that allowed it).
- The **process/systemic** contributing factors (what in the system — not who — let this happen and go undetected).
- Use "the process allowed X" / "the system lacked Y," never "person Z failed."

## 6. Response assessment
- **What worked well.**
- **What didn't / what slowed us down** (framed as process/tooling gaps).
- **Gaps found** (detection coverage, runbook, access, comms).

## 7. Follow-up actions
| Action | Type (detection / control / process / runbook) | Owner | Due | Status |
|---|---|---|---|---|
| | | | | |

- Feed these back into the IR plan and the detection backlog.

## 8. Evidence & chain of custody
- Reference to the evidence acquired and the chain-of-custody log location. Retention per policy.

## 9. Lessons learned
- The durable takeaways — what the org now does differently.
