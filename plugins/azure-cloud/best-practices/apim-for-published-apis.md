# Publish APIs through APIM — not directly from backend compute

**Status:** Pattern
**Domain:** Azure integration / API management
**Applies to:** `azure-cloud`

---

## Why this exists

Exposing backend services (Container Apps, Functions, App Service) directly to consumers without an API gateway gives consumers a direct dependency on the backend URL, authentication mechanism, and version. Every breaking change requires consumer coordination. Azure API Management (APIM) decouples the backend from the consumer: the gateway URL is stable, versioning is managed, rate limiting and authentication policies live in the gateway, and the backend can change without consumer impact. For internal APIs across teams and for any B2B/partner-facing API, APIM is the correct publishing surface.

## How to apply

```bicep
// Bicep — APIM instance (Standard v2 for new deployments)
resource apim 'Microsoft.ApiManagement/service@2023-09-01-preview' = {
  name: 'apim-${appName}-${env}'
  location: location
  sku: {
    name: 'StandardV2'   // Standard v2: injection into VNet without ASE
    capacity: 1
  }
  identity: { type: 'SystemAssigned' }
  properties: {
    publisherEmail: 'api-team@example.com'
    publisherName: 'My Org'
    virtualNetworkType: 'Internal'   // private; expose via Front Door or App Gateway
    virtualNetworkConfiguration: {
      subnetResourceId: apimSubnet.id
    }
  }
}

// API definition pointing to the backend
resource api 'Microsoft.ApiManagement/service/apis@2023-09-01-preview' = {
  parent: apim
  name: 'orders-api'
  properties: {
    displayName: 'Orders API'
    path: 'orders'
    protocols: ['https']
    subscriptionRequired: true
    serviceUrl: 'https://ca-orders-prod.internal.example.com'
  }
}
```

Standard policy pattern — JWT validation + rate limiting:
```xml
<policies>
  <inbound>
    <validate-jwt header-name="Authorization" failed-validation-httpcode="401">
      <openid-config url="https://login.microsoftonline.com/{tenant}/v2.0/.well-known/openid-configuration" />
    </validate-jwt>
    <rate-limit-by-key calls="100" renewal-period="60" counter-key="@(context.Subscription.Id)" />
    <base />
  </inbound>
</policies>
```

**Do:**
- Use `Internal` VNet mode for APIM and expose externally via Front Door or Application Gateway + WAF — APIM itself should not be internet-facing.
- Version APIs from the start (`/v1/`, `/v2/`) — adding versions retroactively is painful.
- Use managed identity on APIM to authenticate to backend services (Key Vault, backends with Entra auth).
- Enable APIM diagnostic settings to Log Analytics.

**Don't:**
- Publish APIM in `External` mode without a WAF in front — the gateway itself needs L7 protection.
- Use APIM for internal service-to-service calls within a single microservice boundary — service discovery and Container Apps traffic splitting handle that.
- Skip subscription keys for partner-facing APIs — even with JWT validation, subscription keys provide a revocable per-consumer credential.

## Edge cases / when the rule does NOT apply

- **Internal service-to-service calls within the same Container Apps environment**: direct service invocation (Dapr or container DNS) is appropriate; APIM adds latency and cost.
- **Simple webhooks from Azure services (Event Grid, Service Bus)**: those call your service directly, not via APIM.

## See also

- [`../agents/integration-engineer.md`](../agents/integration-engineer.md) — owns APIM design and API publishing.
- [`./service-bus-for-commands-event-grid-for-events.md`](./service-bus-for-commands-event-grid-for-events.md) — APIM is the HTTP API gateway; Service Bus/Event Grid handle async messaging.
- [`./private-by-default-paas-data-planes.md`](./private-by-default-paas-data-planes.md) — APIM in Internal mode follows the private-by-default posture.

## Provenance

Codifies house opinion #12 from `CLAUDE.md` §3: "APIM = published APIs." Grounded in `knowledge/azure-integration-decision.md`. Standard Azure integration architecture pattern from the CAF/WAF architecture center.

---

_Last reviewed: 2026-06-05 by `claude`_
