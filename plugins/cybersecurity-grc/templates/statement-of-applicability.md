# Statement of Applicability (SoA)

> Output of `grc-architect` / the `framework-selection-and-control-mapping` skill. An SoA with exclusions
> marked "N/A" and no justification, or with no crosswalk, is not audit-ready.

## 1. Program scope

- **Primary framework:** <SOC 2 TSC | ISO 27001 + Annex A | NIST CSF 2.0 | NIST 800-53>
- **Report / certification target:** <SOC 2 Type II | ISO 27001 cert | ...>
- **Audit boundary (in scope):** <systems, locations, people, data, third parties>
- **Explicitly out of scope:** <what's excluded from the boundary and why>

## 2. Control applicability + status

| Control (primary) | Applicable? | Justification (if excluded, auditor-defensible) | State | Evidence source |
|---|---|---|---|---|
| <control ref + name> | Yes / No | <why it applies, or why N/A traced to a risk> | designed / implemented / operating-effectively | <artifact / CCM source> |
| | | | | |

_Every "No" needs a justification that traces to the risk register and would survive an auditor. State is one of the three (§4 #4)._

## 3. Crosswalk (map once, attest many)

| Primary control | SOC 2 TSC | ISO 27001 Annex A | NIST CSF 2.0 | NIST 800-53 |
|---|---|---|---|---|
| <control> | <criterion> | <Annex A ref> | <function/category> | <control family> |

_One evidenced control should attest across every column it maps to. Mark recalled control refs `[verify-at-build]`._

## 4. Handoff to technical teams

| What | Routed to |
|---|---|
| The secure code / threat model behind a control objective | `security-engineering` |
| The cloud control config + its evidence source | `aws-cloud` / `azure-cloud` / `gcp-cloud` |
| Privacy/data-handling control mechanics | `data-governance-privacy` |
| Control implementation + evidence + testing | `control-and-evidence-engineer` |
| Gap assessment + auditor liaison + vendor risk | `audit-and-third-party-risk-lead` |

---

```
Status: ...
Files changed: ...
Framework & scope: ...
Control state: ...
Risk addressed: ...
Handoff to technical teams: ...
Open questions: ...
Grounding checks performed: ...
```
