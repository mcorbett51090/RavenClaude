# Golden Path — Spec

> Output of `golden-paths-and-adoption-engineer` / the `golden-path-and-self-service` skill. A path with no owner,
> no version, no policy check, or no adoption metric is not ready to ship.

## 1. The path

- **Name:** <e.g. "Provision a new prod-ready service">
- **Worn?** <which 2+ teams keep re-deriving this>
- **Cognitive load removed (concrete):** <decisions/toil this takes off the consuming team>

## 2. Self-service flow (no human in the loop)

| Step | Interface | Provisioning primitive | Human in the loop? |
|---|---|---|---|
| Request | <portal action / CLI / templated PR> | — | <must be No> |
| Provision | — | <Terraform module / Crossplane composition / Score / Kratix> | <must be No> |
| Running | <what the team gets back> | — | — |

_If any step is "human in the loop = Yes", it's a queue, not self-service. Redesign the human out or say why it's unavoidable._

## 3. Guardrails-as-defaults

| Requirement | Encoded as the default? | Policy-as-code check | Advisory or blocking? |
|---|---|---|---|
| <secure defaults> | <yes — in the template/module> | <OPA/Conftest/Kyverno rule> | <advisory / blocking if irreversible> |
| <required tags/labels> | | | |
| <network/cost posture> | | | |

## 4. Path lifecycle

- **Owner (a team):** <name>
- **Version:** <semver of the path>
- **Deprecation/migration story:** <how consumers move when the path changes>

## 5. Adoption + outcomes metrics

| Metric | How collected | Vanity risk flagged |
|---|---|---|
| Paved-road coverage (% of services on the path) | | |
| DORA — deploy freq / lead time / change-fail / MTTR | | |
| DevEx/SPACE signal | | <paired with throughput?> |
| Platform SLO (self-service surface) | <route to observability-sre> | |

## 6. Build handoff

| What | Routed to |
|---|---|
| The Terraform module / Crossplane composition | `terraform-iac` / `cloud-native-kubernetes` |
| The pipeline the path wires | `devops-cicd` |
| The portal action exposing the path | `developer-portal-engineer` |
| The platform SLO | `observability-sre` |
| What "secure default" means | `security-engineering` / `data-governance-privacy` |

---

```
Status: ...
Files changed: ...
Cognitive load removed: ...
Paved-road posture: ...
Handoff to build teams: ...
Open questions: ...
Grounding checks performed: ...
```
