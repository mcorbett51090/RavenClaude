# Plugin Anatomy

## The IPlugin Interface

Every plugin implements `Microsoft.Xrm.Sdk.IPlugin`:

```csharp
using Microsoft.Xrm.Sdk;
using System;

namespace Contoso.Plugins
{
    public class ProjectValidation : IPlugin
    {
        public void Execute(IServiceProvider serviceProvider)
        {
            // 1. Get the execution context
            var context = (IPluginExecutionContext)serviceProvider
                .GetService(typeof(IPluginExecutionContext));

            // 2. Get the organization service (for CRUD operations)
            var serviceFactory = (IOrganizationServiceFactory)serviceProvider
                .GetService(typeof(IOrganizationServiceFactory));
            var service = serviceFactory.CreateOrganizationService(context.UserId);

            // 3. Get the tracing service (for logging)
            var trace = (ITracingService)serviceProvider
                .GetService(typeof(ITracingService));

            try
            {
                trace.Trace("Plugin executing for message: {0}", context.MessageName);

                // Plugin logic here
            }
            catch (InvalidPluginExecutionException)
            {
                throw; // Re-throw user-facing errors
            }
            catch (Exception ex)
            {
                trace.Trace("Error: {0}", ex.ToString());
                throw new InvalidPluginExecutionException(
                    "An error occurred in ProjectValidation. Please contact your administrator.",
                    ex);
            }
        }
    }
}
```

## IPluginExecutionContext Properties

| Property | Type | Description |
|---|---|---|
| `MessageName` | string | Operation: "Create", "Update", "Delete", "Retrieve", etc. |
| `Stage` | int | Pipeline stage (10, 20, 30, 40) |
| `Depth` | int | Call depth (1 = original, 2+ = triggered by another plugin) |
| `PrimaryEntityName` | string | Logical name of the target entity |
| `PrimaryEntityId` | Guid | ID of the target record |
| `InputParameters` | ParameterCollection | Operation inputs (e.g., "Target" entity) |
| `OutputParameters` | ParameterCollection | Operation outputs (PostOperation only) |
| `PreEntityImages` | EntityImageCollection | Field values BEFORE the operation |
| `PostEntityImages` | EntityImageCollection | Field values AFTER the operation |
| `SharedVariables` | ParameterCollection | Data shared across pipeline stages |
| `UserId` | Guid | ID of the user who triggered the operation |
| `InitiatingUserId` | Guid | Original user (even through impersonation) |
| `OrganizationId` | Guid | Organization identifier |
| `IsInTransaction` | bool | Whether executing inside a database transaction |

## Accessing the Target Entity

```csharp
// For Create/Update — the entity being created/modified
if (context.InputParameters.Contains("Target") &&
    context.InputParameters["Target"] is Entity target)
{
    var name = target.GetAttributeValue<string>("cnt_projectname");
    var budget = target.GetAttributeValue<Money>("cnt_budget");
    var status = target.GetAttributeValue<OptionSetValue>("cnt_status");
}

// For Delete — only EntityReference is available
if (context.InputParameters.Contains("Target") &&
    context.InputParameters["Target"] is EntityReference targetRef)
{
    var deletedId = targetRef.Id;
    var entityName = targetRef.LogicalName;
}
```

## IOrganizationService Operations

```csharp
// Create
var newTask = new Entity("task");
newTask["subject"] = "Follow up";
newTask["regardingobjectid"] = new EntityReference("cnt_project", context.PrimaryEntityId);
Guid taskId = service.Create(newTask);

// Retrieve
var project = service.Retrieve("cnt_project", projectId,
    new ColumnSet("cnt_projectname", "cnt_budget", "cnt_status"));

// Update
var update = new Entity("cnt_project", projectId);
update["cnt_status"] = new OptionSetValue(892100001);
service.Update(update);

// Delete
service.Delete("cnt_project", projectId);

// RetrieveMultiple (QueryExpression)
var query = new QueryExpression("cnt_task")
{
    ColumnSet = new ColumnSet("subject", "cnt_status"),
    Criteria = new FilterExpression
    {
        Conditions =
        {
            new ConditionExpression("_cnt_projectid_value", ConditionOperator.Equal, projectId),
            new ConditionExpression("statecode", ConditionOperator.Equal, 0)
        }
    }
};
var tasks = service.RetrieveMultiple(query);
```

## Constructor Pattern (Configuration)

Plugins can receive unsecure and secure configuration strings:

```csharp
public class ConfigurablePlugin : IPlugin
{
    private readonly string _unsecureConfig;
    private readonly string _secureConfig;

    public ConfigurablePlugin(string unsecureConfig, string secureConfig)
    {
        _unsecureConfig = unsecureConfig;
        _secureConfig = secureConfig;
    }

    public void Execute(IServiceProvider serviceProvider)
    {
        // Use _unsecureConfig and _secureConfig
    }
}
```

- **Unsecure config:** Stored in the assembly, visible to all with read access
- **Secure config:** Stored separately, only accessible to system administrators

## Depth Guard

Prevent infinite loops when a plugin triggers itself:

```csharp
if (context.Depth > 2)
{
    trace.Trace("Depth limit reached ({0}), exiting.", context.Depth);
    return;
}
```

## PluginBase Template Pattern (pac plugin init)

The `pac plugin init` command generates a `PluginBase` abstract class that simplifies plugin development. Instead of implementing `IPlugin` directly, you extend `PluginBase`:

```csharp
public class MyPlugin : PluginBase
{
    public MyPlugin(string unsecure, string secure) : base(typeof(MyPlugin))
    {
    }

    protected override void ExecutePluginCode(LocalPluginContext localContext)
    {
        if (localContext == null)
            throw new InvalidPluginExecutionException(nameof(localContext));

        ITracingService tracingService = localContext.TracingService;
        IPluginExecutionContext context = localContext.PluginExecutionContext;
        IOrganizationService service = localContext.OrganizationService;

        // Business logic here
    }
}
```

`LocalPluginContext` provides convenience properties:
- `localContext.TracingService` — direct property (no manual service resolution)
- `localContext.PluginExecutionContext` — cast to IPluginExecutionContext
- `localContext.OrganizationService` — pre-resolved service

When to use which:
- Raw `IPlugin` — more transparent, better for learning, simple plugins
- `PluginBase` — less boilerplate, generated by CLI, better for production projects with many plugins

## Critical Plugin Constraints

- **Timeout**: 2 minutes regardless of sync or async
- **Assembly size**: 16 MB maximum (cannot be modified)
- **Max custom workflow activities**: 50 per assembly
- **No multi-threading/parallel calls**: Causes connection corruption and SQL errors
- **Avoid `ExecuteMultipleRequest`/`ExecuteTransactionRequest`** in plugins (use in integration scenarios only)
- **Avoid `ColumnSet(true)`**: Only retrieve columns you actually need
- **No `SetTimeout`, `Sleep`, `Wait`**: No delays in plugin code
- **Don't stack synchronous plugins**: Multiple sync plugins on same table + event = unresponsive app

## Filtering Attributes (Critical for Update Events)

When registering a plugin on the **Update** event, ALWAYS define filtering attributes. Without them, the plugin fires on EVERY field change including autosave, causing performance issues:
- In Plugin Registration Tool: specify which columns trigger the plugin
- Only trigger when relevant columns actually change
- Example: If your plugin only cares about `statuscode` changes, filter to only `statuscode`

## Execution Order

When multiple plugins are registered on the same message + stage:
1. System JavaScript (Microsoft internal)
2. Custom JavaScript (form scripts)
3. Business Rules
4. Plugins execute in registration **Execution Order** (lower number = earlier)

## Plugin Solution Management

- Manage plugins in a **single solution** to avoid PluginAssembly/PluginType mismatch
- Always use **Upgrade** import option when deploying plugin solutions to target environments
