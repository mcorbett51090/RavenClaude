# Azure architecture spec — <WORKLOAD>

> Owned by `azure-architect`. Decision-tree-justified; WAF-aligned.

## Services (from the decision trees)
| Layer | Service | Why |
|---|---|---|
| Compute | <App Service / Container Apps / Functions / Static Web Apps / AKS> | |
| Data | <Azure SQL / Cosmos / PostgreSQL Flexible Server> (non-Fabric) or Fabric → microsoft-fabric | |
| Integration | <Logic Apps / Service Bus / Event Grid / APIM> | |
| Identity | <managed identity / WIF> | |
| Networking | <Private Endpoints / hub-spoke / Front Door+WAF> | |

## Well-Architected
- **Reliability:** <zone-redundancy / paired-region / RTO-RPO>
- **Security:** <private-by-default / least-privilege+PIM / Defender> → core/security-reviewer
- **Cost:** <SKU choices / budgets / Log Analytics control> — target: <$/mo>
- **Operational excellence:** <IaC / observability / alerts>
- **Performance:** <scaling / caching / region>

## Cross-plugin seams
- Fabric data → microsoft-fabric · Power Automate → power-platform · Claude app → claude-app-engineering · UI → web-design · app code → ravenclaude-core

## Hand-offs
- <which agent builds each layer>
