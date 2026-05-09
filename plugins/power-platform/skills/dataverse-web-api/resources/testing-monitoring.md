# MDA Testing & Monitoring Strategies

## Power Apps Monitor Tool

The Monitor tool provides real-time diagnostics for model-driven apps, helping troubleshoot:
- Form events (onLoad, onSave)
- Network/connectivity issues
- Page navigation
- Command bar executions
- Control state changes
- Tab/section visibility
- Unsupported client API calls

### Supported Event Categories

| Event | Description |
|---|---|
| `FormEvents.onsave` | Form save operations |
| `XrmNavigation` | Page navigation events |
| `FormEvents.onload` | Form load operations |
| `FormControls` | Control interactions |
| `TabStateChange` | Tab expand/collapse |
| `ControlStateChange` | Control visibility/disable changes |
| `SectionStateChange` | Section visibility changes |
| `UnsupportedClientApi` | Deprecated or unsupported API calls |

### Access Methods
- **From Power Apps home**: Select app > click "Monitor" in the command bar
- **From app URL**: Append `&monitor=true` to the model-driven app URL

### Entry Properties

Each monitor entry shows:
| Property | Description |
|---|---|
| Id | Unique entry identifier |
| Time | Timestamp of the event |
| Category | Event category (FormEvents, Network, etc.) |
| Operation | Specific operation name |
| Result | Success/Failure status |
| Duration (ms) | Time taken for the operation |
| Data source | Source of the data operation |
| Control | Control that triggered the event |

### Key Features
- **Download logs** as `PowerAppsTraceEvents.json` for offline analysis
- **Collaborative monitoring**: Connect to someone else's session to debug their issues in real time
- **Required role**: System Administrator or System Customizer

---

## Application Insights Integration

Connect your model-driven app to Azure Application Insights for production-grade telemetry.

### Setup
1. Open the app in the Maker Portal
2. Go to the app **Properties** panel
3. Add the Azure Application Insights **Instrumentation Key**
4. **Publish** the app

### Telemetry Tables
| Table | What It Captures |
|---|---|
| `pageViews` | Page loads and navigation |
| `Dependencies` | Outbound requests from the app |
| `Requests` | Dataverse API calls |

### Analysis Panels
- **Performance panel**: Number and average duration of each operation type
- **Failures panel**: Unsuccessful requests and count of impacted users
- **Transaction Search**: Find specific failed transactions and exceptions
- **Logs panel**: Run KQL (Kusto Query Language) queries; pin results, export to Power BI/Excel, or set alert rules

### GOTCHA
When importing/exporting solutions across environments, **verify the Instrumentation Key**. You could accidentally send telemetry from production to a dev Application Insights instance (or vice versa). Check Properties after every solution import.

### Environment-Level Telemetry
Dataverse telemetry is also available at the environment level (not just per-app), providing broader platform diagnostics.

---

## Power Platform Admin Center Analytics

### Environment View
Available analytics pages:
- **Usage** — active users, sessions
- **Location** — geographic distribution of users
- **Toast Errors** — client-side error notifications
- **Service Performance** — API response times, throttling
- **Connectors** — connector usage statistics

### Model-Driven App Analytics
For MDA apps: Select app > **Performance (Preview)**

**IMPORTANT**: Do NOT use "Analytics (Preview)" — that is for canvas apps only. For model-driven apps, use the **Performance** tab.

### Dataverse Analytics
- Active users over time
- API call volumes and patterns
- Plugin execution statistics (count, duration, failures)

### Retention
**Maximum retention: 28 days.** For longer retention, use Application Insights.

---

## Solution Checker

Validates solution components, settings, and configurations through static analysis.

### What It Identifies
- **Accessibility violations** — missing labels, contrast issues
- **Performance problems** — inefficient queries, large payloads
- **Best practice violations** — deprecated API usage, anti-patterns

### Best Practice
Run Solution Checker **BEFORE publishing** to catch problems early. It complements runtime testing by providing static analysis that catches issues before users encounter them.

---

## Power Automate Desktop (PAD) for MDA Testing

### Why PAD?
Test Studio and Test Engine currently only support canvas apps. PAD is the practical approach for automated MDA testing, replicating user interactions through UI automation.

### Architecture
Modularize tests into subflows for maintainability:

1. **Login subflow**: Launch browser to MDA URL, capture login actions with PAD Recorder
2. **Test subflows**: Record interactions (click New, fill fields, click Save, validate results)
3. **Main flow**: Orchestrate subflows in sequence

### Building a Test Flow
1. Create a new PAD flow
2. Use the **Recorder** to capture browser interactions
3. Organize recorded actions into logical subflows (login, record creation, validation, cleanup)
4. Add assertions/validations after each action sequence
5. Chain subflows in the main flow

### Best Practices
- **Generate random data**: Use PAD "Create Random Text" action to avoid duplicate detection rules
- **Set window state to "maximized"**: Ensures reliable UI element targeting
- **Implement error handling**: Add error handlers within flows for graceful failure reporting
- **Modularize but don't over-fragment**: Too many tiny subflows add overhead without clarity
- **Validate test results**: Always check expected outcomes against actual state
- **Regularly update flows**: When the app UI changes, update the corresponding subflows

---

## Mocking Dataverse in Tests

Use Test Engine `networkRequestMocks` in YAML test plans to mock Dataverse API responses.

### Configuration

```yaml
networkRequestMocks:
  - requestURL: "https://*.crm4.dynamics.com/api/data/v9.0/$batch"
    responseDataFile: "mock-response.json"
    headers:
      x-mock-type: "0"
```

### Key Details
- **Request URL pattern**: `https://*.crm4.dynamics.com/api/data/v9.0/$batch`
- **Response file**: Provide a JSON file with the expected Dataverse response
- **`x-mock-type: 0`**: Header value for file-based response mocking
- **Differentiate endpoints**: Use `x-ms-request-method` and `x-ms-request-url` headers to distinguish between different API calls within the same batch endpoint

---

## Testing Tools Decision Matrix

| Tool | Scope | Automation | MDA Support |
|---|---|---|---|
| Monitor | Debugging | Manual | Yes |
| Application Insights | Production telemetry | Automatic | Yes |
| Solution Checker | Static analysis | Manual | Yes |
| PAD | UI testing | Automated | Yes |
| Test Engine | Test plans | Automated | Roadmap (replacing EasyRepro) |
| Playwright | E2E testing | Automated | Yes (code-heavy) |
| Test Studio | Canvas tests | Automated | No |

---

## Recommended Workflow

1. **Check Analytics** in the Power Platform Admin Center (out-of-box information, no setup required)
2. **Monitor app performance** via Application Insights (requires one-time Instrumentation Key setup)
3. **Use Power Apps Monitor** for specific issue investigation (real-time, interactive debugging)
4. **Analyze in depth** with KQL queries in Application Insights Logs panel
5. **Automate regression tests** with PAD flows (run on schedule or before releases)
