# Risk Register

> Output of `grc-architect` / `control-and-evidence-engineer` / the `risk-register-and-assessment` skill. A row with
> no treating control, no treatment decision, or no owner is not ready. Risk drives controls, not the reverse.

## 1. Scoring scale (state it, apply it consistently)

- **Likelihood:** <e.g. 1 Rare → 5 Almost-certain>
- **Impact:** <e.g. 1 Negligible → 5 Severe>
- **Risk score:** likelihood × impact; **risk appetite / threshold:** <where mitigation becomes mandatory>
- **Methodology:** <ISO 27005 | NIST 800-30 | other — mark `[verify-at-build]`>

## 2. The register

| ID | Asset | Threat | Likelihood | Impact | Inherent score | Treating control | Treatment (mitigate/accept/transfer/avoid) | Residual score | Owner | Review date |
|---|---|---|---|---|---|---|---|---|---|---|
| R-01 | <asset> | <threat> | <1-5> | <1-5> | <L×I> | <control ref> | <decision> | <L×I after> | <name> | <date> |
| | | | | | | | | | | |

_Flag any top risk with **no treating control** (the real exposure) and any control with **no risk** behind it (cost without benefit). An "accept" with no owner/sign-off is just an ignored risk._

## 3. Top risks → control roadmap

| Risk | Control to build/strengthen | Routed to |
|---|---|---|
| <highest residual> | <control> | `control-and-evidence-engineer` (implement + evidence) |
| | | `security-engineering` / cloud plugins (technical config) |

## 4. Feeds

- Drives the **Statement of Applicability** (`grc-architect`) — exclusions justified against this register.
- Drives the **control-testing cadence + evidence plan** (`control-and-evidence-engineer`).

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
