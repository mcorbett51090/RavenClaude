# Use Front Door for global HTTP entry points, App Gateway for regional WAF

**Status:** Pattern
**Domain:** Azure networking / load balancing
**Applies to:** `azure-cloud`

---

## Why this exists

Azure Front Door and Application Gateway are both L7 load balancers with WAF, but they solve different problems. Front Door is a **global** anycast network: it routes users to the nearest healthy origin, accelerates traffic over the Microsoft backbone, and provides a single HTTPS entry point for multi-region active-active apps. Application Gateway is **regional**: it terminates TLS inside a VNet, routes to backends in the same region, and is the right WAF for a single-region internal front end. Deploying a regional Application Gateway when you need global routing produces unnecessary complexity; deploying Front Door when all traffic is regional and the backend is private adds latency and cost.

## How to apply

**Decision shortcut:**

| Requirement | Pick |
|---|---|
| Multi-region active-active or failover | Front Door |
| Global CDN + DDoS + WAF for public app | Front Door Premium |
| Single-region VNet-internal WAF + routing | Application Gateway v2 |
| Internal APIM or AKS ingress WAF inside VNet | Application Gateway v2 |
| Both global entry + private regional inspection | Front Door + App Gateway (layered) |

```bicep
// Bicep — Front Door with WAF policy (Premium for private origins via Private Link)
resource wafPolicy 'Microsoft.Network/FrontDoorWebApplicationFirewallPolicies@2024-02-01' = {
  name: 'waf-${appName}-${env}'
  location: 'global'
  sku: { name: 'Premium_AzureFrontDoor' }
  properties: {
    policySettings: { mode: 'Prevention', enabledState: 'Enabled' }
    managedRules: {
      managedRuleSets: [
        { ruleSetType: 'Microsoft_DefaultRuleSet', ruleSetVersion: '2.1' }
        { ruleSetType: 'Microsoft_BotManagerRuleSet', ruleSetVersion: '1.0' }
      ]
    }
  }
}

resource frontDoor 'Microsoft.Cdn/profiles@2023-07-01-preview' = {
  name: 'afd-${appName}-${env}'
  location: 'global'
  sku: { name: 'Premium_AzureFrontDoor' }
}
```

**Do:**
- Use Front Door Premium (not Standard) when backends are private — Premium supports Private Link origins.
- Enable WAF on Front Door in `Prevention` mode with `Microsoft_DefaultRuleSet` + `Microsoft_BotManagerRuleSet`.
- Lock down Application Gateway / Container Apps / App Service to accept traffic only from Front Door (use `X-Azure-FDID` header validation).
- Use Front Door rules engine for URL rewriting, caching headers, and geo-routing.

**Don't:**
- Use Front Door Standard when you need Private Link origins — Standard doesn't support them.
- Expose the Application Gateway public IP without validating the Front Door header — it bypasses WAF.
- Use Application Gateway for global multi-region routing — it is a single-region resource.

## Edge cases / when the rule does NOT apply

- **Internal-only apps with no public exposure**: neither Front Door nor Application Gateway is needed; use an internal Load Balancer or private Container Apps ingress.
- **Very low-traffic dev environments**: Front Door's per-request fee adds up; a simple Application Gateway or direct Container Apps ingress is cost-effective.

## See also

- [`../agents/network-engineer.md`](../agents/network-engineer.md) — owns Front Door and Application Gateway design.
- [`./private-by-default-paas-data-planes.md`](./private-by-default-paas-data-planes.md) — the origin (App Service, Container Apps) must be private even when the entry point is Front Door.

## Provenance

Codifies the `network-engineer` decision scope from `CLAUDE.md` §1: "Front Door/App Gateway/WAF, firewall/egress." Grounded in `knowledge/azure-networking-and-connectivity.md` and the Azure Load Balancing options decision guide.

---

_Last reviewed: 2026-06-05 by `claude`_
