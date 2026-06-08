# Contract Playbook — <contract type, e.g. "Inbound NDA">

> Output of `legal-ops-lead` / `contract-review-specialist`. **Not legal advice** — a qualified lawyer sets and
> confirms the positions, tiers, and escalation triggers below. An empty "Escalation triggers" or "Walk-away" line
> means the playbook isn't safe to self-serve yet.

## 1. Scope & routing

- **Contract type:** <e.g. inbound NDA / vendor MSA / sales order form>
- **Self-serve or escalate by default?** <self-serve the standard case / always escalate>
- **Pre-approved standard template:** <link / "none — escalate">
- **Self-serve value/risk ceiling:** <above this, always a lawyer>

## 2. Key-clause positions (set by a lawyer)

| Clause | Standard (preferred) | Fallback (acceptable) | Walk-away (never) | Risk tier of a deviation | Approver |
|---|---|---|---|---|---|
| Limitation of liability | | | | | |
| Indemnity | | | | | |
| IP ownership | | | | | |
| Term / termination | | | | | |
| Confidentiality | | | | | |

## 3. Escalation triggers (bright lines — stop and get a lawyer)

- <e.g. any deviation beyond the fallback column>
- <e.g. value above the self-serve ceiling>
- <e.g. touches personal data / a DPA → route to data-governance-privacy first>
- <e.g. security addendum / right-to-audit → route to security-reviewer>
- <e.g. non-standard governing law or jurisdiction>

## 4. Self-serve flow

| Step | Who | Interface | Lawyer in the loop? |
|---|---|---|---|
| Intake | business team | <structured intake form> | No |
| Use standard template | business team | <template> | No (within bounds) |
| Sign | business team | <e-signature> | No |
| Any escalation trigger hit | → lawyer | <escalation path> | Yes |

## 5. Matter & metrics

- **Matter created?** <owner / type / status / SLA>
- **Metrics this feeds:** <self-serve rate, cycle time, escalation mix — each paired with a decision>

---

```
Status: ...
Files changed: ...
Not legal advice: ...
Risk / approval routing: ...
Handoff: ...
Open questions: ...
Grounding checks performed: ...
```
