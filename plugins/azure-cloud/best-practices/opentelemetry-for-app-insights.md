# Instrument apps with OpenTelemetry — not the App Insights SDK directly

**Status:** Pattern
**Domain:** Azure observability
**Applies to:** `azure-cloud`

---

## Why this exists

The Application Insights SDK is a proprietary instrumentation library tied to one backend. OpenTelemetry (OTel) is the CNCF standard: vendor-neutral, portable, and actively maintained. Azure Monitor now has a first-class OTel distro (`azure-monitor-opentelemetry`) that exports to workspace-based Application Insights — so you get the full App Insights UX without the SDK lock-in. Apps instrumented with OTel can switch backends (Grafana, Jaeger, Honeycomb) without a code change. The house opinion (#11) is explicit: "Observability = OpenTelemetry + workspace-based App Insights."

## How to apply

```python
# Python — Azure Monitor OTel distro
from azure.monitor.opentelemetry import configure_azure_monitor

configure_azure_monitor(
    connection_string="InstrumentationKey=...",
    # or set APPLICATIONINSIGHTS_CONNECTION_STRING env var
)

# From here, use standard OTel APIs — no App Insights SDK imports needed
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

def process_order(order_id: str) -> None:
    with tracer.start_as_current_span("process_order") as span:
        span.set_attribute("order.id", order_id)
        # ...
```

```javascript
// Node.js — Azure Monitor OTel distro
const { useAzureMonitor } = require("@azure/monitor-opentelemetry");
useAzureMonitor(); // reads APPLICATIONINSIGHTS_CONNECTION_STRING

const { trace } = require("@opentelemetry/api");
const tracer = trace.getTracer("my-service");
```

Use workspace-based Application Insights (not classic):
```bicep
resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: 'appi-${appName}-${env}'
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalyticsWorkspace.id  // workspace-based — required
    IngestionMode: 'LogAnalytics'
    RetentionInDays: 90
  }
}
```

**Do:**
- Use workspace-based App Insights — classic (non-workspace) is on a deprecation path.
- Set `APPLICATIONINSIGHTS_CONNECTION_STRING` as an app setting (Key Vault reference) rather than the instrumentation key.
- Add custom spans for business operations (order placed, payment processed) — auto-instrumentation captures HTTP/DB but not your domain events.
- Emit custom metrics from spans using OTel metrics API for SLO tracking.

**Don't:**
- Import `applicationinsights` (classic SDK) in new services — use the OTel distro.
- Use the instrumentation key in place of the connection string — it is deprecated.
- Create one App Insights per resource; share the workspace-based instance across services in an environment for correlated querying.

## Edge cases / when the rule does NOT apply

- **Legacy services already on the App Insights SDK with stable instrumentation**: don't migrate for migration's sake; migrate when the service is refactored anyway.
- **Azure Functions with built-in App Insights integration**: Functions auto-instruments using App Insights by default; for new Functions, confirm the OTel distro is compatible with your runtime version before switching.

## See also

- [`../agents/azure-ops-engineer.md`](../agents/azure-ops-engineer.md) — owns observability design including App Insights and OTel.
- [`./ops-diagnostic-settings-to-log-analytics-from-day-one.md`](./ops-diagnostic-settings-to-log-analytics-from-day-one.md) — infrastructure logs go to Log Analytics; app traces go to workspace-based App Insights on the same workspace.

## Provenance

Codifies house opinion #11 from `CLAUDE.md` §3: "Observability = OpenTelemetry + workspace-based App Insights." Grounded in `knowledge/azure-observability-and-finops.md`. Azure Monitor OTel distro is the Microsoft-recommended path for new applications as of 2024.

---

_Last reviewed: 2026-06-05 by `claude`_
