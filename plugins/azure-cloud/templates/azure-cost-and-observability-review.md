# Azure cost & observability review — <SCOPE / DATE>

> Owned by `azure-ops-engineer`. A client-ready deliverable. See `knowledge/azure-observability-and-finops.md`.

## Current state
- Scope: <subscription(s) / resource groups>
- Top cost drivers (Cost Management → group by meter): <list>
- Log Analytics ingestion: <GB/day>; retention: <days>

## Observability findings
| Gap | Fix |
|---|---|
| <no distributed tracing> | OpenTelemetry → workspace-based App Insights |
| <noisy/expensive logs> | sampling; Basic Logs for debug/audit tables |
| <no alerts> | metric/log alerts on <signals> |

## FinOps recommendations (priority order)
- [ ] Log Analytics cost: sampling / Basic Logs / commitment tier / daily cap — est. saving <$>
- [ ] Budgets + cost alerts per subscription (thresholds + recipients)
- [ ] Reservations / savings plan for steady compute — est. saving <$>
- [ ] Rightsize SKUs (Advisor recommendations): <list>
- [ ] Tag-based chargeback gaps: <untagged resources>

## Governance
- [ ] Azure Policy + Defender for Cloud coverage across subscriptions
- [ ] Diagnostic settings routed to Log Analytics/SIEM

## Projected impact
- Monthly cost: <before → after>; key risks: <list>
