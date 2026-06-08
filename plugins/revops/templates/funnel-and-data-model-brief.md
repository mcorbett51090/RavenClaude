# Funnel & RevOps Data Model — Brief

> Output of `revops-architect` / the `funnel-and-revops-data-model` skill. A funnel with two definitions of any stage,
> no bowtie, or no handoff SLA is not ready to ship.

## 1. The funnel (one definition per stage)

| Stage | One definition (objective criteria) | Instrumented where | Owner |
|---|---|---|---|
| Anonymous → Lead | <criteria> | <one point> | |
| MQL | <criteria sales accepts> | | |
| SAL | <accepted by sales> | | |
| SQL / Opportunity created | <buyer action> | | |
| Opportunity stages | <see forecast spec> | | |
| Closed-won | <signed> | | |
| Onboarded → Renewed → Expanded (bowtie right) | <hands to customer-success-analytics> | | |

_If any stage has two definitions across marketing/sales/CS, fix that before anything else._

## 2. The bowtie

- **Left (acquisition):** <stages>
- **Right (retention/expansion):** <stages — health/churn model routes to `customer-success-analytics`>
- **Connection:** <how closed-won connects to onboarding/renewal as one motion>

## 3. The RevOps data model (CRM-neutral)

| Object | System of record | Key relationships | Required fields |
|---|---|---|---|
| Account | | | |
| Contact | | | |
| Lead | | | |
| Opportunity | | | |
| Activity | | | |

## 4. Marketing↔sales↔CS SLAs / handoffs

| Handoff | Speed SLA | Accept/reject loop | Owner |
|---|---|---|---|
| Marketing → Sales (MQL→SAL) | | | |
| Sales → CS (closed-won → onboarding) | | | |
| CS → Sales (renewal/expansion pipeline) | | | |

## 5. Build handoff

| What | Routed to |
|---|---|
| The Salesforce objects / flows / validation rules | `salesforce` |
| The warehouse revenue mart | `data-platform` |
| The funnel dashboard | `tableau` |
| The post-sale health / churn / NRR model | `customer-success-analytics` |
| PII / comp confidentiality / visibility rules | `security-engineering` / `data-governance-privacy` |

---

```
Status: ...
Files changed: ...
Revenue impact: ...
Definition integrity: ...
Handoff to system teams: ...
Open questions: ...
Grounding checks performed: ...
```
