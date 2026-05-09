# Plugin Registration and Deployment

## Scaffolding with pac CLI

```bash
# Initialize a new plugin project
pac plugin init --namespace Contoso.Plugins

# This creates:
# ├── Contoso.Plugins.csproj
# ├── Plugin1.cs (template)
# └── nuget.config
```

The generated project targets .NET Framework 4.6.2 and references the Dataverse SDK.

## Building

```bash
# Build the assembly
dotnet build -c Release

# Output: bin/Release/net462/Contoso.Plugins.dll
```

## Plugin Registration Tool (PRT)

The PRT is the primary GUI tool for registering plugins.

### Install

```bash
pac tool prt
```

This downloads and opens the Plugin Registration Tool.

### Registration Steps

1. **Connect** to your Dataverse environment
2. **Register New Assembly:**
   - Click "Register" → "Register New Assembly"
   - Browse to your `.dll` file
   - Isolation Mode: Sandbox (recommended) or None (on-premises only)
   - Location: Database (stores in Dataverse, recommended)
   - Click "Register Selected Plugins"

3. **Register New Step:**
   - Right-click the plugin class → "Register New Step"
   - Configure:
     - **Message:** Create, Update, Delete, etc.
     - **Primary Entity:** Target entity logical name (e.g., `cnt_project`)
     - **Filtering Attributes:** (Update only) Comma-separated attribute list
     - **Event Pipeline Stage:** PreValidation (10), PreOperation (20), PostOperation (40)
     - **Execution Mode:** Synchronous or Asynchronous
     - **Execution Order:** Numeric order (lower = first)

4. **Register Entity Images** (if needed):
   - Right-click the step → "Register New Image"
   - Configure image type (Pre/Post/Both), name, and attributes

### Sandbox vs Non-Sandbox

| Aspect | Sandbox (IsolationMode=2) | None (IsolationMode=1) |
|---|---|---|
| File system | No access | Full access (on-premises) |
| Registry | No access | Full access (on-premises) |
| Network | Limited (allow-listed endpoints) | Full access |
| Availability | Online + On-Premises | On-Premises only |
| Recommended | Yes (default) | No (legacy only) |

Sandbox plugins can make HTTP calls to allow-listed external endpoints only.
For broader integration, use Azure Functions with Dataverse webhooks.

## Solution Packaging

### Add to Solution via PRT

After registering, add the assembly to your solution:
1. Open your solution in the Maker Portal
2. Add existing → Assembly → Select your assembly
3. Add existing → SDK Message Processing Step → Select your steps

### Add to Solution via API

```http
POST [org-url]/api/data/v9.2/AddSolutionComponent
{
    "ComponentId": "{assembly-guid}",
    "ComponentType": 91,
    "SolutionUniqueName": "ContosoHRModule",
    "AddRequiredComponents": true
}
```

Component Types:
- 91 = Plugin Assembly
- 92 = SDK Message Processing Step
- 93 = SDK Message Processing Step Image

## Debugging with Plugin Trace Log

### Enable Tracing

In the Power Platform admin center or via API:
- **Off:** No tracing (production default)
- **Exception:** Only log when errors occur
- **All:** Log all `trace.Trace()` calls (development)

### Viewing Traces

```http
GET [org-url]/api/data/v9.2/plugintracelogs
    ?$filter=typename eq 'Contoso.Plugins.ProjectValidation'
    &$orderby=createdon desc
    &$top=10
    &$select=messageblock,exceptiondetails,createdon
```

Or view in Maker Portal: Settings → Plugin Trace Log

### Writing Trace Messages

```csharp
trace.Trace("Starting validation for entity: {0}", context.PrimaryEntityName);
trace.Trace("Budget value: {0}", budget?.Value);
trace.Trace("Query returned {0} results", results.Entities.Count);
```

**Tips:**
- Trace messages are concatenated into `messageblock` for the trace log entry
- Include operation context (message name, entity, record ID) for debugging
- Log before and after key operations
- Remove verbose tracing for production (or rely on "Exception" trace level)

## Performance Constraints

| Constraint | Limit |
|---|---|
| Synchronous timeout | 2 minutes |
| Asynchronous timeout | 24 hours |
| Assembly size | 16 MB |
| Maximum depth | 8 (recursive plugin calls) |
| Concurrent connections | Limited by sandbox |
| Memory | Shared sandbox process |

### Performance Best Practices

1. **Use filtering attributes** — don't fire on every Update
2. **Use entity images** — avoid unnecessary Retrieve calls
3. **Minimize queries** — batch operations where possible
4. **Guard on depth** — prevent infinite recursion
5. **Async for non-critical** — notifications, logging, integrations
6. **Avoid large queries** — use `TopCount` and filter precisely
7. **Release resources** — don't hold service references beyond `Execute()`

## Update Workflow

When updating plugin code:

1. Build the new assembly
2. In PRT: Right-click assembly → "Update"
3. Browse to the new `.dll`
4. Click "Update Selected Plugins"

No need to re-register steps unless the class name changed or new steps are needed.

Steps and images persist across assembly updates.
