# Environment Variables in Dataverse

Environment variables store configuration values that can differ between environments
(dev, test, production) without modifying code or solution files. They are the recommended
approach for configurable settings in Power Platform solutions.

## Types and Use Cases

| Type | Value | Use Case |
|---|---|---|
| Data source | Connection reference | SharePoint site, Dataverse environment, SAP ERP connection references that differ per environment |
| JSON | JSON string | Multiple config values grouped together (mailbox IDs, queue IDs, approval team names) |
| Secret | Azure Key Vault reference | Credentials, API keys, connection strings stored securely in Azure Key Vault |
| Text | String | Configurable text values (e.g., reminder days before event, email subjects, URL prefixes) |
| Boolean | true/false | Feature flags (enable/disable features per environment) |
| Decimal | Numeric | Configurable business values (discount percentages, thresholds, limits) |

## Default Value vs Current Value

Environment variables have TWO value slots:

- **Default value**: Stored in the variable definition. Travels with the solution on export/import.
- **Current value**: Stored as a separate `environmentvariablevalue` record. Overrides the default.

### Resolution Logic
1. If a **current value** exists, it is used
2. Otherwise, the **default value** is used
3. If neither exists, the variable returns empty/null

### Key Rules
- Set the **default value** for values that are the SAME across all environments
- Set the **current value** for per-environment overrides (different connection, different URL, etc.)
- **IMPORTANT**: Before exporting a solution, remove the current value from the source environment
  if you do NOT want it propagated to the target. Current values travel with managed solutions.
- During solution import, if a current value already exists in the target, it is NOT overwritten

## API Operations

### Create an Environment Variable Definition

```http
POST /environmentvariabledefinitions
MSCRM.SolutionUniqueName: {solution}

{
  "schemaname": "cnt_ReminderDaysBeforeEvent",
  "displayname": "Reminder Days Before Event",
  "description": "Number of days before an event to send a reminder email",
  "type": 100000000,
  "defaultvalue": "7"
}
```

#### Type Codes
| Type | Code |
|---|---|
| String (Text) | 100000000 |
| Number (Decimal) | 100000001 |
| Boolean | 100000002 |
| JSON | 100000003 |
| Data source | 100000004 |
| Secret | 100000005 |

### Set a Current Value

```http
POST /environmentvariablevalues

{
  "schemaname": "cnt_ReminderDaysBeforeEvent",
  "value": "14",
  "EnvironmentVariableDefinitionId@odata.bind": "/environmentvariabledefinitions({definition-id})"
}
```

### Query Variable with Values

```http
GET /environmentvariabledefinitions?$filter=schemaname eq 'cnt_ReminderDaysBeforeEvent'&$expand=environmentvariabledefinitions_environmentvariablevalue($select=value)
```

### Update Current Value

```http
PATCH /environmentvariablevalues({value-id})

{
  "value": "21"
}
```

### Delete Current Value (Revert to Default)

```http
DELETE /environmentvariablevalues({value-id})
```

## Usage Across Technologies

### Power Automate

Environment variables are available directly in the expression box:
1. In a flow action, click the expression tab or dynamic content
2. Search for the environment variable by display name
3. Select it — Power Automate resolves the value at runtime

### Custom Pages / Canvas Apps

Query the `Environment Variable Definitions` and `Environment Variable Values` tables:
```
// In a canvas app formula
LookUp(
    'Environment Variable Values',
    'Environment Variable Definition'.'Schema Name' = "cnt_ReminderDaysBeforeEvent",
    Value
)
```

If no current value exists, fall back to:
```
LookUp(
    'Environment Variable Definitions',
    'Schema Name' = "cnt_ReminderDaysBeforeEvent",
    'Default Value'
)
```

### JavaScript Web Resources

Query via Xrm.WebApi in form scripts or HTML web resources:
```javascript
async function getEnvVariable(schemaName) {
    const result = await Xrm.WebApi.retrieveMultipleRecords(
        "environmentvariabledefinition",
        `?$filter=schemaname eq '${schemaName}'` +
        `&$expand=environmentvariabledefinitions_environmentvariablevalue($select=value)` +
        `&$select=defaultvalue,schemaname`
    );

    if (result.entities.length === 0) return null;

    const definition = result.entities[0];
    const values = definition.environmentvariabledefinitions_environmentvariablevalue;

    // Current value takes precedence over default
    if (values && values.length > 0) {
        return values[0].value;
    }
    return definition.defaultvalue;
}
```

### Plugins (C#)

Query via IOrganizationService:
```csharp
public string GetEnvironmentVariable(IOrganizationService service, string schemaName)
{
    var query = new QueryExpression("environmentvariabledefinition")
    {
        ColumnSet = new ColumnSet("defaultvalue"),
        Criteria = new FilterExpression
        {
            Conditions =
            {
                new ConditionExpression("schemaname", ConditionOperator.Equal, schemaName)
            }
        }
    };

    var link = query.AddLink("environmentvariablevalue", "environmentvariabledefinitionid",
        "environmentvariabledefinitionid", JoinOperator.LeftOuter);
    link.Columns.AddColumn("value");
    link.EntityAlias = "val";

    var results = service.RetrieveMultiple(query);
    if (results.Entities.Count == 0) return null;

    var entity = results.Entities[0];
    // Current value takes precedence
    if (entity.Contains("val.value"))
    {
        return ((AliasedValue)entity["val.value"]).Value?.ToString();
    }
    return entity.GetAttributeValue<string>("defaultvalue");
}
```

## Why Environment Variables Over XML Web Resources

Historically, developers stored configuration in XML web resources. Environment variables
are the modern replacement and are better in every way:

| Concern | XML Web Resource | Environment Variable |
|---|---|---|
| Solution-aware | Yes, but clunky | Yes, first-class |
| Multi-environment | Must manually update XML per env | Default/current value separation |
| Concurrent editing | Risk data loss (file overwrite) | Record-level, no conflicts |
| Secrets | Stored in plain text | Azure Key Vault integration |
| Discoverability | Must know the web resource name | Listed in solution, searchable |
| Migration | Manual copy or scripting | Travels with solution import |
| Type safety | Raw text parsing | Typed (Boolean, Decimal, JSON, etc.) |
| ALM | Requires custom tooling | Built-in support in pipelines |

## Secret Variables (Azure Key Vault)

For credentials, API keys, and other sensitive values:

1. Store the secret in Azure Key Vault
2. Create an environment variable of type Secret
3. Set the value to the Key Vault secret reference URL:
   `https://{vault-name}.vault.azure.net/secrets/{secret-name}`
4. Grant the Dataverse application access to the Key Vault via Azure RBAC
5. At runtime, Dataverse retrieves the secret from Key Vault

### Important Notes
- Secret values are NOT stored in Dataverse — only the Key Vault reference
- Secret values cannot be read via the Dataverse API (returns the reference URL, not the secret)
- Each environment should have its own Key Vault (or different secrets per environment)
- Secrets are resolved server-side only (plugins, Power Automate); not available client-side

## Best Practices

- **Name with publisher prefix**: `cnt_MyVariable` — keeps variables in your solution namespace
- **Use JSON type for grouped config**: Instead of 10 separate variables, use one JSON variable
  with a structured object
- **Document each variable**: Fill in the description field explaining purpose, expected format, and valid values
- **Remove current values before export**: Unless you explicitly want to propagate the value
- **Use secrets for anything sensitive**: Never store credentials in Text-type variables
- **Validate at startup**: In plugins/flows, validate that required environment variables exist
  and have values before proceeding
