# Azure landing zone plan — <ORG>

> Owned by `azure-architect`. See `knowledge/azure-landing-zones-and-governance.md`.

## Management-group hierarchy (flat, 3-4 levels)
```
Tenant Root
├── Platform        (Connectivity / Identity / Management / Security subs)
├── Landing Zones   (archetypes: corp, online)
├── Sandbox
└── Decommissioned
```

## Subscriptions (one per environment, under an archetype MG)
| Subscription | Archetype MG | Environment | Owner | Budget |
|---|---|---|---|---|
| | corp / online | dev / test / prod | | |

- Vending: <subscription-vending AVM module? policy/RBAC/budget stamped at creation?>

## Governance (universal)
- **Policy** assigned at MG scope: <initiatives>
- **RBAC**: scoped to sub/RG, platform teams via **PIM**
- **Tags**: owner / cost-center / environment / application
- **Naming**: `abbr-workload-env-region-instance`
- **Defender for Cloud + Cost Management (budgets+alerts) + Network Watcher**: on everywhere

## Connectivity & reliability
- Topology: <hub-spoke | Virtual WAN> → `network-engineer`
- Reliability: zone-redundant prod; paired-region BCDR

## Open decisions
- <decision + owner>
