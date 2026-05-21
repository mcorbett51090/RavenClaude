# Control narrative — [Control ID] [Control name]

> SOC1 / SOC2 / regulator-facing control narrative. Names owner, frequency, evidence type. Maps to regulation.

**Control ID:** [e.g., C-AML-001]
**Control name:** [e.g., "Sanctions screening — customer onboarding"]
**Process owner:** [named person + role]
**Last reviewed:** [YYYY-MM-DD]
**Tested by (2nd line):** [named person + role + last test date]
**Tested by (3rd line / external):** [if applicable]
**Confidentiality:** internal | regulator-only

---

## Control objective

[1 sentence: what risk does this control address?]

## Control activity

[1-3 sentences: what specifically does the control do? Who, when, how. Concrete enough that a tester knows exactly what to look for.]

## Frequency

Daily | Weekly | Monthly | Quarterly | Annually | Per-event (specify trigger) | Continuous (automated)

## Trigger / condition (for event-driven controls)

[Trigger description, if applicable.]

## Inputs

- [Input source 1 — system / file / report]
- [Input source 2]

## Outputs / evidence

- [Output 1 — what gets produced when the control fires]
- [Evidence type — system log entry, signed report, ticket, alert disposition]

## IPE (Information Produced by Entity)

If this control relies on a management-prepared report:
- [Report name]
- [Source of the data]
- [Completeness / accuracy check on the report itself]

## Exception handling

- **What constitutes an exception:** [...]
- **Who can authorize an exception:** [named role]
- **Where exceptions are logged:** [register / system]
- **Review cadence on the exception register:** [...]

## Regulatory mapping

| Regulator | Regime | Citation | Requirement (1-line) |
|---|---|---|---|
| [BMA / OFAC / FFIEC / NAIC] | [Insurance Act / BSA / Solvency II] | §XX(YY)(z) | [requirement] |

## Testing approach (2nd / 3rd line)

- **Frequency of testing:** [monthly / quarterly / annually]
- **Sample size:** [number / methodology]
- **Test procedure:** [how the tester confirms the control operated]
- **Last test result:** [pass / exception / fail; ref to test workpaper]

## Design effectiveness (most recent assessment)

✅ Effective | ⚠️ Effective with observation | 🔴 Ineffective

## Operating effectiveness (most recent assessment)

✅ Effective | ⚠️ Effective with observation | 🔴 Ineffective

## Open observations / remediation in progress

| # | Observation | Severity | Remediation | Owner | Target date |
|---|---|---|---|---|---|

---

**Sources:** [System config, policy reference, prior test workpapers.]
