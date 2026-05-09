# Common Plugin Patterns

## Auto-Numbering on Create

Generate sequential identifiers when records are created.

```csharp
// Register: Create of cnt_project, PreOperation, Sync
public void Execute(IServiceProvider serviceProvider)
{
    var context = (IPluginExecutionContext)serviceProvider.GetService(typeof(IPluginExecutionContext));
    var service = ((IOrganizationServiceFactory)serviceProvider
        .GetService(typeof(IOrganizationServiceFactory))).CreateOrganizationService(context.UserId);
    var trace = (ITracingService)serviceProvider.GetService(typeof(ITracingService));

    if (context.MessageName != "Create") return;
    var target = (Entity)context.InputParameters["Target"];

    // Get the next number from a counter record
    var query = new QueryExpression("cnt_autonumberconfig")
    {
        ColumnSet = new ColumnSet("cnt_prefix", "cnt_nextnumber"),
        Criteria = new FilterExpression
        {
            Conditions = { new ConditionExpression("cnt_entityname", ConditionOperator.Equal, "cnt_project") }
        }
    };
    var configs = service.RetrieveMultiple(query);

    if (configs.Entities.Count > 0)
    {
        var config = configs.Entities[0];
        var prefix = config.GetAttributeValue<string>("cnt_prefix") ?? "PRJ";
        var nextNum = config.GetAttributeValue<int>("cnt_nextnumber");

        // Set the auto-number field
        target["cnt_projectnumber"] = $"{prefix}-{nextNum:D5}"; // PRJ-00001

        // Increment the counter
        var update = new Entity("cnt_autonumberconfig", config.Id);
        update["cnt_nextnumber"] = nextNum + 1;
        service.Update(update);
    }
}
```

## Field Validation

Validate fields and prevent save with user-friendly error messages.

```csharp
// Register: Create/Update of cnt_project, PreValidation, Sync
// Filtering attributes: cnt_budget, cnt_enddate, cnt_startdate
public void Execute(IServiceProvider serviceProvider)
{
    var context = (IPluginExecutionContext)serviceProvider.GetService(typeof(IPluginExecutionContext));
    var target = (Entity)context.InputParameters["Target"];

    // Budget validation
    if (target.Contains("cnt_budget"))
    {
        var budget = target.GetAttributeValue<Money>("cnt_budget");
        if (budget != null && budget.Value < 0)
        {
            throw new InvalidPluginExecutionException(
                "Budget cannot be negative. Please enter a valid budget amount.");
        }
        if (budget != null && budget.Value > 10000000)
        {
            throw new InvalidPluginExecutionException(
                "Budget exceeds $10M. Projects of this size require executive approval. " +
                "Please submit via the Large Project Request form.");
        }
    }

    // Date validation
    if (target.Contains("cnt_startdate") && target.Contains("cnt_enddate"))
    {
        var start = target.GetAttributeValue<DateTime>("cnt_startdate");
        var end = target.GetAttributeValue<DateTime>("cnt_enddate");
        if (end < start)
        {
            throw new InvalidPluginExecutionException(
                "End date cannot be before the start date.");
        }
    }
}
```

## Cascading Updates (Rollup Replacement)

Update parent record statistics when child records change. This replaces unreliable
rollup fields with real-time, code-driven aggregation.

```csharp
// Register: Create/Update/Delete of cnt_gamescore, PostOperation, Sync
// Filtering attributes (for Update): cnt_score
public void Execute(IServiceProvider serviceProvider)
{
    var context = (IPluginExecutionContext)serviceProvider.GetService(typeof(IPluginExecutionContext));
    var service = ((IOrganizationServiceFactory)serviceProvider
        .GetService(typeof(IOrganizationServiceFactory))).CreateOrganizationService(context.UserId);
    var trace = (ITracingService)serviceProvider.GetService(typeof(ITracingService));

    Guid playerId;

    if (context.MessageName == "Delete")
    {
        // For delete, get player ID from pre-image
        var preImage = context.PreEntityImages["PreImage"];
        var playerRef = preImage.GetAttributeValue<EntityReference>("cnt_player");
        if (playerRef == null) return;
        playerId = playerRef.Id;
    }
    else
    {
        var target = (Entity)context.InputParameters["Target"];
        var playerRef = target.GetAttributeValue<EntityReference>("cnt_player");
        if (playerRef == null)
        {
            // Field not in update payload — check pre-image
            if (context.PreEntityImages.Contains("PreImage"))
            {
                playerRef = context.PreEntityImages["PreImage"]
                    .GetAttributeValue<EntityReference>("cnt_player");
            }
            if (playerRef == null) return;
        }
        playerId = playerRef.Id;
    }

    // Query all scores for this player
    var query = new QueryExpression("cnt_gamescore")
    {
        ColumnSet = new ColumnSet("cnt_score"),
        Criteria = new FilterExpression
        {
            Conditions =
            {
                new ConditionExpression("_cnt_player_value", ConditionOperator.Equal, playerId),
                new ConditionExpression("statecode", ConditionOperator.Equal, 0)
            }
        }
    };
    var scores = service.RetrieveMultiple(query);

    // Calculate aggregates
    int gamesPlayed = scores.Entities.Count;
    int totalScore = 0;
    int highScore = 0;
    foreach (var score in scores.Entities)
    {
        var val = score.GetAttributeValue<int>("cnt_score");
        totalScore += val;
        if (val > highScore) highScore = val;
    }

    // Update parent player record
    var playerUpdate = new Entity("cnt_player", playerId);
    playerUpdate["cnt_gamesplayed"] = gamesPlayed;
    playerUpdate["cnt_totalscore"] = totalScore;
    playerUpdate["cnt_highscore"] = highScore;
    service.Update(playerUpdate);

    trace.Trace("Updated player {0}: {1} games, high={2}, total={3}",
        playerId, gamesPlayed, highScore, totalScore);
}
```

## Duplicate Detection

Check for duplicate records before creation.

```csharp
// Register: Create of cnt_project, PreValidation, Sync
public void Execute(IServiceProvider serviceProvider)
{
    var context = (IPluginExecutionContext)serviceProvider.GetService(typeof(IPluginExecutionContext));
    var service = ((IOrganizationServiceFactory)serviceProvider
        .GetService(typeof(IOrganizationServiceFactory))).CreateOrganizationService(context.UserId);
    var target = (Entity)context.InputParameters["Target"];

    var projectName = target.GetAttributeValue<string>("cnt_projectname");
    if (string.IsNullOrEmpty(projectName)) return;

    var query = new QueryExpression("cnt_project")
    {
        ColumnSet = new ColumnSet("cnt_projectname"),
        Criteria = new FilterExpression
        {
            Conditions =
            {
                new ConditionExpression("cnt_projectname", ConditionOperator.Equal, projectName),
                new ConditionExpression("statecode", ConditionOperator.Equal, 0)
            }
        },
        TopCount = 1
    };
    var existing = service.RetrieveMultiple(query);

    if (existing.Entities.Count > 0)
    {
        throw new InvalidPluginExecutionException(
            $"A project named '{projectName}' already exists. Please use a unique name.");
    }
}
```

## Error Handling Best Practices

```csharp
try
{
    // Plugin logic
}
catch (InvalidPluginExecutionException)
{
    throw; // Already user-friendly, re-throw as-is
}
catch (FaultException<OrganizationServiceFault> ex)
{
    trace.Trace("Org service fault: {0}", ex.Detail.Message);
    throw new InvalidPluginExecutionException(
        "A data operation failed. Please try again or contact support.", ex);
}
catch (Exception ex)
{
    trace.Trace("Unexpected error: {0}\n{1}", ex.Message, ex.StackTrace);
    throw new InvalidPluginExecutionException(
        "An unexpected error occurred. Please contact your administrator.", ex);
}
```

**Rules:**
- Always throw `InvalidPluginExecutionException` for user-visible errors
- Always include the original exception as the inner exception
- Never expose technical details (SQL errors, stack traces) to users
- Always log the full exception to the tracing service
- Use `trace.Trace()` extensively during development

## Low-Code Plugins (Power Fx) — Preview

Low-code plugins use Power Fx instead of C#. Requires the **Dataverse Accelerator** app and System Administrator/Customizer role.

Two types:
- **Instant**: Reusable logic invoked manually (from Power Apps, flows, Web API). Can be global or table-specific.
- **Automated**: Triggered automatically on table events (Create, Update, Delete). Always tied to a table.

Advantages over pro-code:
- No NuGet packages, DLLs, or registration tools
- Can integrate with 1000+ Power Platform connectors
- Changes in one place, logic runs server-side

Example (duplicate detection):
```
If(!IsBlank(LookUp([@Contacts], Email=ThisRecord.Email)),
    Error("You have existing contacts with the same Email Address")
)
```

**WARNING**: Still in preview as of 2024. NOT recommended for production environments. May cause problems with other solution components.

## Custom Workflow Activities (Legacy)

Custom workflow activities extend classic workflows with C# code. While being deprecated in favor of Power Automate + low-code plugins, they still exist in many production systems.

```csharp
public sealed class IncrementBy100 : CodeActivity
{
    [RequiredArgument]
    [Input("Input Value")]
    public InArgument<int> InputValue { get; set; }

    [Output("Output Value")]
    public OutArgument<int> OutputValue { get; set; }

    protected override void Execute(CodeActivityContext executionContext)
    {
        IWorkflowContext context = executionContext.GetExtension<IWorkflowContext>();
        IOrganizationServiceFactory serviceFactory = executionContext.GetExtension<IOrganizationServiceFactory>();
        IOrganizationService service = serviceFactory.CreateOrganizationService(context.InitiatingUserId);

        int input = InputValue.Get(executionContext);
        OutputValue.Set(executionContext, input + 100);
    }
}
```

Key differences from plugins:
| Aspect | Plugin | Custom Workflow Activity |
|---|---|---|
| Base class | `IPlugin` or `PluginBase` | `CodeActivity` |
| Context | `IPluginExecutionContext` | `IWorkflowContext` |
| Service resolution | `IServiceProvider.GetService()` | `CodeActivityContext.GetExtension()` |
| Parameters | Unsecure/secure config strings | `InArgument<T>` / `OutArgument<T>` |
| Trigger | Entity events | Workflow step execution |
