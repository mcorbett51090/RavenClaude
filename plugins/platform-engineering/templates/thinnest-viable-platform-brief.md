# Thinnest Viable Platform — Brief

> Output of `platform-architect` / the `internal-developer-platform-design` skill. Fill every section; an empty
> "Non-goals" or "Cognitive load removed" section is a sign the platform isn't scoped as a product yet.

## 1. The problem (cognitive load worth removing)

| Toil / decision teams re-derive | How many teams hit it | Load removed if paved (concrete) |
|---|---|---|
| <e.g. wiring CI for a new service> | <2+ / one> | <hours per new service; decisions not made> |
| | | |

_If no row has 2+ teams, stop — solve it for the one team and revisit. A platform needs shared, repeated load._

## 2. Thinnest viable platform — the paths to pave first

| Golden path | Why first (leverage) | Self-service interface | Build owner (route to) |
|---|---|---|---|
| <new service> | <highest load removed> | <portal action / CLI / templated PR> | <devops-cicd / terraform-iac / ...> |
| <get an environment> | | | |

## 3. The platform API (exposed capabilities)

| Capability | Interface | Versioned? | No human in the loop? |
|---|---|---|---|
| | | | |

## 4. Operating model (Team Topologies)

- **Platform team product owner:** <name/role>
- **Interaction mode per consumer team:** <X-as-a-Service / facilitating / collaboration>
- **How consumer feedback drives the roadmap:** <mechanism>

## 5. Build vs buy (per layer)

| Layer | Decision | TCO trade named | Exit posture if wrong |
|---|---|---|---|
| Developer portal | <build Backstage / buy Port·Cortex·OpsLevel / managed Backstage> | | |
| Software catalog | | | |
| Scaffolder/templates | | | |
| Provisioning | <Terraform modules / Crossplane / Score / Kratix> | | |

## 6. Explicit non-goals (what the platform will NOT do)

- <e.g. we will not run teams' databases for them>
- <e.g. we will not forbid leaving the paved road>

## 7. Adoption baseline (so we can prove it's a product later)

- **Paved-road coverage today:** <% of services / "0, greenfield">
- **DORA baseline:** <deploy freq / lead time / change-fail / MTTR, or "to be measured">
- **DevEx signal:** <survey / instrumented>
- **Platform SLO target:** <availability/latency of the self-service surface>

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
