# Business Rules

Business rules provide no-code client-side logic for model-driven app forms. They are stored
as `workflow` records with `Category=2` and contain XAML definitions.

## Important Caveat

Business rules are stored as XAML in the `xaml` property of a `workflow` record. Constructing
XAML programmatically is **fragile and error-prone**. The XAML schema is undocumented, changes
between platform versions, and small errors produce cryptic failures.

**Recommended approach:** Use the Maker Portal to create business rules for simple scenarios.
For anything beyond basic show/hide or set-required, use JavaScript form scripts instead --
they are more flexible, debuggable, and version-controllable.

## When Business Rules Are the Right Choice

Business rules are better than JS form scripts when:

- **Simple show/hide:** Toggle field visibility based on another field's value
- **Set required level:** Make a field required/optional based on conditions
- **Set default value:** Auto-populate a field when a form loads or a value changes
- **No code deployment needed:** Business rules are configuration, not code
- **Offline and mobile:** Business rules work in offline mode and on mobile apps
- **Non-developer audience:** Business analysts can create and maintain them

## API Pattern

Business rules are created via the `workflows` entity set.

```http
POST [org-url]/api/data/v9.2/workflows
MSCRM.SolutionUniqueName: ContosoHRModule
Content-Type: application/json; charset=utf-8
OData-Version: 4.0

{
  "name": "Set Priority Required When High Value",
  "type": 1,
  "category": 2,
  "primaryentity": "cnt_project",
  "scope": 1,
  "statecode": 1,
  "statuscode": 2,
  "xaml": "<Activity ...>...</Activity>"
}
```

### Workflow Record Properties

| Property | Value | Description |
|---|---|---|
| `type` | `1` | Definition (not instance) |
| `category` | `2` | Business Rule (vs 0=Workflow, 3=Action) |
| `scope` | `1` | Entity scope (runs on all forms + server-side) |
| `scope` | `2` | All Forms |
| `scope` | `3` | Specific form (requires `formid`) |
| `statecode` | `1` | Activated |
| `statuscode` | `2` | Activated |
| `primaryentity` | string | Logical name of the entity |

### Scope Values

| Scope | Behavior |
|---|---|
| `1` (Entity) | Runs on all forms AND server-side (covers API create/update too) |
| `2` (All Forms) | Runs on all forms only (client-side) |
| `3` (Form) | Runs on a specific form only (set `formid` to the form GUID) |

**Recommendation:** Use Entity scope (`1`) when the rule should enforce data quality even
for API/import operations. Use Form scope (`3`) for UI-only rules like show/hide.

## XAML Structure Overview

The XAML body follows this general structure:

```xml
<Activity x:Class="RuleDefinition"
  xmlns="http://schemas.microsoft.com/netfx/2009/xaml/activities"
  xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
  xmlns:mxswa="clr-namespace:Microsoft.Xrm.Sdk.Workflow.Activities;assembly=Microsoft.Xrm.Sdk.Workflow">
  <mxswa:RuleDefinitions>
    <mxswa:RuleDefinition Name="SetPriorityRequired" Id="{RULE-GUID}">
      <mxswa:Conditions>
        <mxswa:Condition Id="{COND-GUID}">
          <mxswa:Condition.Operand>
            <mxswa:AttributeOperand AttributeName="cnt_budget" EntityName="cnt_project" />
          </mxswa:Condition.Operand>
          <mxswa:Condition.Operator>GreaterThan</mxswa:Condition.Operator>
          <mxswa:Condition.Value>
            <mxswa:LiteralOperand Value="100000" Type="System.Decimal" />
          </mxswa:Condition.Value>
        </mxswa:Condition>
      </mxswa:Conditions>
      <mxswa:ThenActions>
        <mxswa:SetRequiredLevelAction AttributeName="cnt_priority" EntityName="cnt_project"
          RequiredLevel="ApplicationRequired" Id="{ACTION-GUID}" />
      </mxswa:ThenActions>
      <mxswa:ElseActions>
        <mxswa:SetRequiredLevelAction AttributeName="cnt_priority" EntityName="cnt_project"
          RequiredLevel="None" Id="{ACTION-GUID-2}" />
      </mxswa:ElseActions>
    </mxswa:RuleDefinition>
  </mxswa:RuleDefinitions>
</Activity>
```

**Warning:** The above is a simplified illustration. Real XAML includes additional namespaces,
serialization metadata, and workflow activity wrappers. Always prefer the Maker Portal for
creating business rules. The API approach is only recommended for automated migration or
CI/CD pipelines where you are copying XAML from an exported solution.

## Supported Actions

| Action | XAML Element | Description |
|---|---|---|
| Set Field Value | `<SetAttributeValueAction>` | Set a field to a specific value or another field's value |
| Set Visibility | `<SetVisibilityAction>` | Show or hide a field on the form |
| Set Business Required | `<SetRequiredLevelAction>` | Make a field required, recommended, or optional |
| Show Error Message | `<SetValidationMessageAction>` | Display a validation error on a field |
| Set Default Value | `<SetAttributeValueAction>` | Pre-populate a field value (same element as Set Field Value) |
| Lock/Unlock Field | `<SetControlStateAction>` | Make a field read-only or editable |

## Supported Condition Operators

- `Equal`, `NotEqual`
- `GreaterThan`, `GreaterThanOrEqual`
- `LessThan`, `LessThanOrEqual`
- `Contains`, `DoesNotContain` (for text fields)
- `BeginsWith`, `DoesNotBeginWith`
- `EndsWith`, `DoesNotEndWith`
- `ContainData` (is not null), `DoesNotContainData` (is null)

## Limitations

- **No cross-entity data:** Cannot look up values from related records
- **No async operations:** Cannot call external APIs or perform async work
- **No complex calculations:** Limited to simple comparisons and value assignments
- **No looping:** Cannot iterate over collections
- **Limited conditions:** Only field-level conditions on the current record
- **Single entity:** Each business rule operates on exactly one entity
- **No custom messages:** Error messages are static text only
- **Execution order:** When multiple rules exist, execution order is not guaranteed
- **Conflict resolution:** If two rules set conflicting values on the same field, the result is unpredictable

## Decision Guide: Business Rule vs JS Form Script vs Plugin

| Criteria | Business Rule | JS Form Script | Plugin (C#) |
|---|---|---|---|
| **Complexity** | Simple conditions + actions | Any client-side logic | Any server-side logic |
| **Runs where** | Forms + optionally server | Forms only | Server only (all triggers) |
| **Cross-entity data** | No | Yes (via Web API calls) | Yes (via Org Service) |
| **Offline support** | Yes | Limited | No |
| **Mobile support** | Yes | Yes (Unified Interface) | Yes (server-side) |
| **Debugging** | Limited (trace logs) | Browser DevTools | Plugin Trace Log |
| **Deployment** | Configuration (no code) | Web resource deployment | Plugin assembly deployment |
| **Version control** | Export solution XML | JS files in source control | C# project in source control |
| **Performance** | Fast (built-in engine) | Depends on implementation | Depends on implementation |
| **Async capability** | No | Yes (promises, fetch) | Yes (async plugin) |
| **External calls** | No | Yes (fetch API) | Yes (HttpClient) |
| **Best for** | Show/hide, required level, defaults | Form UX, validation, API calls | Data integrity, integrations, automation |

### When to Use Each

**Use Business Rules when:**
- Toggling visibility based on a field value
- Setting a field as required when another field has a specific value
- Setting a default value on form load
- Showing a validation message for simple conditions
- The logic owner is a business analyst, not a developer

**Use JS Form Scripts when:**
- You need to call external APIs or fetch related record data
- Complex validation logic with multiple conditions
- Dynamic form manipulation (adding/removing tabs, sections)
- Custom notifications or dialogs
- Integration with external libraries or systems
- The logic needs to be version-controlled in a code repository

**Use Plugins when:**
- Data integrity must be enforced regardless of entry point (API, import, workflow)
- Business logic runs on server events (create, update, delete, associate)
- Cross-entity operations (update related records, cascade logic)
- Integration with external systems on data change
- Performance-critical operations that should not depend on client execution
- Logic that must run even when forms are not involved

## Activating and Deactivating via API

**Activate:**

```http
PATCH [org-url]/api/data/v9.2/workflows({rule-id})
{
  "statecode": 1,
  "statuscode": 2
}
```

**Deactivate:**

```http
PATCH [org-url]/api/data/v9.2/workflows({rule-id})
{
  "statecode": 0,
  "statuscode": 1
}
```

## Retrieving Business Rules

```
GET [org-url]/api/data/v9.2/workflows?$filter=category eq 2 and primaryentity eq 'cnt_project'&$select=name,statecode,scope,xaml
```

**Note:** The `xaml` field can be very large. Use `$select` to exclude it when you only
need metadata about the rules.
