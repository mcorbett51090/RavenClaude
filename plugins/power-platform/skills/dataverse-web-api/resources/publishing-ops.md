# Publishing, Custom APIs, and Business Logic

## Publishing (PublishXml)

Creating or updating forms, views, sitemaps, and other UI metadata leaves changes in
a draft/cached state. The `PublishXml` action forces the system to refresh metadata caches.

### Selective Publishing (Recommended)

Publish specific entities to avoid the performance hit of "Publish All":

```http
POST [org-url]/api/data/v9.2/PublishXml
Content-Type: application/json; charset=utf-8

{
  "ParameterXml": "<importexportxml><entities><entity>cnt_project</entity><entity>cnt_employee</entity></entities></importexportxml>"
}
```

### Publish All Customizations

```http
POST [org-url]/api/data/v9.2/PublishAllXml
Content-Type: application/json; charset=utf-8
```

**Warning:** `PublishAllXml` refreshes ALL metadata and can be slow in large environments.
Use selective `PublishXml` whenever possible.

### What Requires Publishing

| Component | Requires Publish? |
|---|---|
| Table (EntityDefinition) | Typically auto-published |
| Column (Attribute) | Typically auto-published |
| Relationship | Typically auto-published |
| System Form | **Yes** |
| Saved Query (View) | **Yes** |
| Sitemap | **Yes** |
| Global Option Set | **Yes** |
| Web Resource | **Yes** |
| App Module | **Yes** (via AddAppComponents) |

### Publish Option Sets

```json
{
  "ParameterXml": "<importexportxml><optionsets><optionset>cnt_projectstatus</optionset></optionsets></importexportxml>"
}
```

### Publish Sitemaps

```json
{
  "ParameterXml": "<importexportxml><sitemaps><sitemap></sitemap></sitemaps></importexportxml>"
}
```

## Global Option Set Management

Global Option Sets (Choices) are independent metadata objects reusable across tables.

**Entity Set:** `GlobalOptionSetDefinitions`

### Create Global Option Set

```http
POST [org-url]/api/data/v9.2/GlobalOptionSetDefinitions
MSCRM.SolutionUniqueName: ContosoHRModule
Content-Type: application/json; charset=utf-8

{
  "@odata.type": "Microsoft.Dynamics.CRM.OptionSetMetadata",
  "Name": "cnt_projectstatus",
  "DisplayName": { "@odata.type": "Microsoft.Dynamics.CRM.Label", "LocalizedLabels": [{ "Label": "Project Status", "LanguageCode": 1033 }] },
  "IsGlobal": true,
  "OptionSetType": "Picklist",
  "Options": [
    { "Value": 100000000, "Label": { "@odata.type": "Microsoft.Dynamics.CRM.Label", "LocalizedLabels": [{ "Label": "Not Started", "LanguageCode": 1033 }] } },
    { "Value": 100000001, "Label": { "@odata.type": "Microsoft.Dynamics.CRM.Label", "LocalizedLabels": [{ "Label": "In Progress", "LanguageCode": 1033 }] } },
    { "Value": 100000002, "Label": { "@odata.type": "Microsoft.Dynamics.CRM.Label", "LocalizedLabels": [{ "Label": "Completed", "LanguageCode": 1033 }] } },
    { "Value": 100000003, "Label": { "@odata.type": "Microsoft.Dynamics.CRM.Label", "LocalizedLabels": [{ "Label": "On Hold", "LanguageCode": 1033 }] } }
  ]
}
```

### Manipulate Individual Options

**Add an option:**
```http
POST [org-url]/api/data/v9.2/InsertOptionValue
{
  "OptionSetName": "cnt_projectstatus",
  "Label": { "@odata.type": "Microsoft.Dynamics.CRM.Label", "LocalizedLabels": [{ "Label": "Cancelled", "LanguageCode": 1033 }] },
  "Value": 100000004
}
```

**Update an option label:**
```http
POST [org-url]/api/data/v9.2/UpdateOptionValue
{
  "OptionSetName": "cnt_projectstatus",
  "Value": 100000001,
  "Label": { "@odata.type": "Microsoft.Dynamics.CRM.Label", "LocalizedLabels": [{ "Label": "Active", "LanguageCode": 1033 }] }
}
```

**Delete an option:**
```http
POST [org-url]/api/data/v9.2/DeleteOptionValue
{
  "OptionSetName": "cnt_projectstatus",
  "Value": 100000004
}
```

**Reorder options:**
```http
POST [org-url]/api/data/v9.2/OrderOption
{
  "OptionSetName": "cnt_projectstatus",
  "Values": [100000000, 100000001, 100000003, 100000002]
}
```

### Merge Behavior in Managed Solutions

When managed solutions update an option set, the behavior is **additive**:
- Solution A adds "Red" → environment has "Red"
- Solution B adds "Blue" → environment has "Red" + "Blue"
- The `OptionValuePrefix` of each publisher prevents value collisions

## Business Rules (workflow)

Business Rules are declarative logic stored in the `workflow` table with `category = 2`.

### Structure

| Property | Description |
|---|---|
| `name` | Rule display name |
| `category` | `2` for Business Rules |
| `primaryentity` | Target table logical name |
| `type` | `1` for Definition, `2` for Activation |
| `clientdata` | JSON string for client-side execution |
| `xaml` | XAML string for server-side execution |

### Activation/Deactivation

```http
PATCH [org-url]/api/data/v9.2/workflows({rule-guid})
{
  "statecode": 1,
  "statuscode": 2
}
```

Set `statecode: 0` and `statuscode: 1` to deactivate.

**Note:** Programmatically CREATING business rules via the API is technically possible
but extremely complex. The `clientdata` JSON and `xaml` schemas are proprietary and
not fully documented. The API is more commonly used to retrieve, activate, deactivate,
or query existing rules.

## Custom APIs (customapi)

Custom APIs extend the Dataverse Web API itself with new Actions or Functions.

### Create Custom API Definition

```http
POST [org-url]/api/data/v9.2/customapis
Content-Type: application/json; charset=utf-8

{
  "name": "cnt_CalculateProjectHealth",
  "displayname": "Calculate Project Health",
  "uniquename": "cnt_CalculateProjectHealth",
  "description": "Calculates the health score for a project",
  "bindingtype": 1,
  "boundentitylogicalname": "cnt_project",
  "isfunction": false,
  "isprivate": false,
  "allowedcustomprocessingsteptype": 0
}
```

**BindingType:** `0` = Unbound (global), `1` = Entity bound, `2` = Entity collection bound

### Define Request Parameters

```http
POST [org-url]/api/data/v9.2/customapirequestparameters
{
  "name": "IncludeHistory",
  "uniquename": "IncludeHistory",
  "displayname": "Include History",
  "type": 0,
  "isoptional": true,
  "logicalentityname": null,
  "CustomAPIId@odata.bind": "/customapis({api-guid})"
}
```

### Define Response Properties

```http
POST [org-url]/api/data/v9.2/customapiresponseproperties
{
  "name": "HealthScore",
  "uniquename": "HealthScore",
  "displayname": "Health Score",
  "type": 3,
  "logicalentityname": null,
  "CustomAPIId@odata.bind": "/customapis({api-guid})"
}
```

**Parameter/Property Types:**
| Value | Type |
|---|---|
| 0 | Boolean |
| 1 | DateTime |
| 2 | Decimal |
| 3 | Integer |
| 4 | Money |
| 5 | Picklist |
| 6 | String |
| 7 | StringArray |
| 8 | Entity |
| 9 | EntityCollection |
| 10 | EntityReference |
| 11 | Float |
| 12 | Guid |

### After Registration

Once the Custom API record and its parameters/response properties are created:
1. The new action/function appears in the `$metadata` CSDL document
2. A plugin assembly must be registered (typically via Plugin Registration Tool)
   to implement the server-side logic
3. The API can be called like any built-in action:

```http
POST [org-url]/api/data/v9.2/cnt_projects({id})/Microsoft.Dynamics.CRM.cnt_CalculateProjectHealth
{
  "IncludeHistory": true
}
```

## $metadata Document

The CSDL metadata document is the definitive schema reference:

```http
GET [org-url]/api/data/v9.2/$metadata
```

This XML document:
- Describes every EntityType, ComplexType, EnumType, Action, and Function
- Is **dynamic** -- custom tables/columns appear immediately after creation
- Follows strict OData v4.0 inheritance (MetadataBase → AttributeMetadata → specific types)
- Is the authoritative source for constructing correct `@odata.type` values
