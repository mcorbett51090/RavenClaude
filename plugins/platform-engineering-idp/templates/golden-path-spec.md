# Golden Path Spec — `<path name>`

> The opinionated, supported, easiest-by-design way to ship `<the common service shape>`. Fill every
> section. A path with no escape hatch, or where the supported way is harder than DIY, is not done.

## 1. The shape this paves

- **Common service/workload shape:** `<e.g. stateless HTTP service in Node>`
- **% of teams/services it fits:** `<~80%? if not, gather the common shape first>`
- **Cognitive load removed:** `<what wait/decision/boilerplate disappears>`

## 2. The supported journey

| Step | Supported default | Self-service entry |
|---|---|---|
| Create | `<software template / scaffolder>` | `<portal action / CLI>` |
| Build | `<CI pipeline — route mechanics to devops-cicd>` | auto on push |
| Deploy | `<rollout strategy — devops-cicd / cloud-native-kubernetes>` | auto / button |
| Run | `<runtime, scaling, defaults>` | n/a |

## 3. Baked-in defaults (free with the path)

- [ ] CI wiring
- [ ] Observability / telemetry (route to observability-sre)
- [ ] Security baseline (route verdicts to ravenclaude-core/security-reviewer)
- [ ] Owner + software-catalog entry (`catalog-info.yaml`)
- [ ] TechDocs scaffold (content -> technical-writing-docs)

## 4. The escape hatch

- **How to step off the road:** `<allowed + unsupported — describe>`
- **What "off-road" means:** `<no platform support / SLA for the deviation>`
- **Fold-back rule:** if `<N>` teams take the same escape, pave it as a new supported variant.

## 5. Ergonomics check

- [ ] Doing it the paved way is **easier** than rolling your own (if not, remove friction first).

## 6. Handoffs

- Create step / template / catalog -> `idp-portal-engineer`
- Pipeline / rollout -> `devops-cicd`
- Cluster / Helm / Argo -> `cloud-native-kubernetes`
- IaC modules -> `terraform-iac`
- Adoption measurement -> `devex-metrics-engineer`

_Authored: `<date>` · Owner: `<platform team / person>`_
