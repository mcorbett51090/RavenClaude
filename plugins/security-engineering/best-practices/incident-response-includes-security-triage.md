# Triage the security angle of every production incident, not just the operational one

**Status:** Pattern
**Domain:** Incident response / application security
**Applies to:** `security-engineering`

---

## Why this exists

A production incident that looks like an operational failure — a service crash, an unexpected data shape, an authentication anomaly — may have a security cause: a credential compromise, an injection attack, a misconfigured access control. Treating it purely as an ops incident and closing it after service restoration means the underlying security event goes uninvestigated. If an attacker caused the incident, they still have access. The security triage question must be asked at every incident, not only when the alert says "security."

## How to apply

Add a security triage step to the incident response process, ideally in the first 30 minutes after stabilization. The triage does not require a security engineer on every bridge — the IC or ops lead asks the three security questions and escalates only if any answer is concerning.

```markdown
# Incident security triage checklist (IC asks during stabilization)

1. **Unauthorized access?**
   - Were there anomalous authentication events (failed logins, unusual geos/IPs)?
   - Were any credentials, tokens, or API keys involved in or near the failure?

2. **Data exposure?**
   - Could the failure have exposed sensitive data (PII, credentials, financial data) to
     unauthorized parties?
   - Are there any error messages that might have leaked internal structure?

3. **Suspicious pattern?**
   - Does the failure pattern match an attack signature (rate spike, injection probe,
     credential stuffing, unusual access pattern)?

→ If ANY answer is uncertain or "yes": escalate to security-engineering immediately.
→ If all answers are "no": record in the postmortem, continue ops triage.
```

**Do:**
- Add the security triage checklist to the incident response template — it takes 3 minutes and is never skipped.
- Route security-flagged incidents to `security-engineering` *while the incident is open*, not as a follow-up ticket.
- Preserve logs, audit trails, and access records during the incident — do not cycle them or scale down the service before security has a chance to review.

**Don't:**
- Assume an incident has no security angle because it started as an ops alert — operational symptoms often have security causes.
- Block incident restoration on completing the security triage — restore first, triage second (but immediately second).
- Let a security-escalated incident close without a security verdict from `ravenclaude-core/security-reviewer`.

## Edge cases / when the rule does NOT apply

Pure infrastructure failures (hardware fault, cloud provider incident, network partition) with no application involvement and no data access path typically don't require security triage. Still record "security triage: N/A — infrastructure failure" in the postmortem.

## See also

- [`../agents/appsec-engineer.md`](../agents/appsec-engineer.md) — owns the security triage process and the escalation path.
- [`./assume-breach-and-design-for-it.md`](./assume-breach-and-design-for-it.md) — the assumption of breach makes security triage of every incident the natural default.

## Provenance

Codifies the NIST SP 800-61 Incident Response lifecycle, specifically the "Containment + Evidence Preservation" phase, and the practice of security-parallel incident triage recommended by CISA's incident response playbooks.

---

_Last reviewed: 2026-06-05 by `claude`_
