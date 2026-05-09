# Custom APIs in Dataverse

Custom APIs are the modern way to define reusable business operations in Dataverse.
They supersede Custom Actions (Process-based) and provide a typed, RESTful interface
callable from any client: plugins, Power Automate, JavaScript, canvas apps, and external code.

This resource goes deeper than the basic coverage in `publishing-ops.md`.

## Custom API vs Custom Action (Legacy)

| Feature | Custom API | Custom Action (Legacy) |
|---|---|---|
| Definition | Stored in Dataverse tables | Workflow Process (XAML) |
| Parameters | Typed, defined in metadata | Workflow arguments |
| Business logic | Plugin code (required) | Workflow steps or plugin |
| Discoverability | Metadata API, $metadata | Process definitions |
| Private option | Yes (hide from other developers) | No |
| Privilege control | Built-in Execute Privilege Name | Manual security checks |
| Function support | Yes (HTTP GET, read-only) | No (POST only) |
| Announcement | 2021, actively developed | Being superseded |

**Recommendation**: Always use Custom APIs for new development. Custom Actions remain
supported but receive no new investment.

## Binding Types

### Global (Unbound) — `bindingtype: 0`
- Not tied to any specific table
- Called directly by name: `POST /api/data/v9.2/cnt_MyCustomApi`
- Use for cross-table operations, utility functions, or business processes
  that span multiple tables

### Entity (Bound) — `bindingtype: 1`
- Tied to a specific table
- Called in the context of a single record or table
- Appears as an action on the entity in the $metadata document
- Call syntax: `POST /api/data/v9.2/cnt_projects({id})/Microsoft.Dynamics.CRM.cnt_MyBoundApi`
- Use when the operation logically belongs to one table (e.g., "approve this record")

### EntityCollection (Bound) — `bindingtype: 2`
- Tied to a collection of a specific table
- Returns or operates on multiple records
- Call syntax: `POST /api/data/v9.2/cnt_projects/Microsoft.Dynamics.CRM.cnt_MyCollectionApi`
- Use for batch operations on a table (e.g., "recalculate all scores")

## Function vs Action

### Function (HTTP GET, Read-Only)
- Set `isfunction: true`
- Input parameters are passed as **URL parameters** (query string)
- Must NOT modify data (read-only semantics)
- Called with HTTP GET
- Example: `GET /api/data/v9.2/cnt_CalculateScore(PlayerId='{guid}')`
- Use for: retrieving computed values, validation checks, status queries

### Action (HTTP POST, Modifies Data)
- Set `isfunction: false`
- Input parameters are passed in the **request body as JSON**
- Can create, update, or delete data
- Called with HTTP POST
- Example: `POST /api/data/v9.2/cnt_SubmitApplication` with JSON body
- Use for: business operations, state changes, multi-step processes

## Key Features

### Private APIs
- Set `isprivate: true` to hide from other developers
- Private APIs do not appear in $metadata or API documentation
- Other developers cannot discover or call them
- Use for internal implementation details that should not be public contracts

### Execute Privilege Name
- Define a custom privilege name that controls who can call the API
- Users without the privilege get an "Insufficient privilege" error
- Create a matching privilege in a security role and assign to users
- If not set, any authenticated user with basic access can call the API

### Execution Stage
- Custom APIs and virtual tables are the **ONLY components** that execute business logic
  in the **MainOperation** stage of the event pipeline
- Other plugins run in Pre/Post validation or Pre/Post operation stages
- This means Custom API plugin code IS the operation, not a hook around it

### Plugin Requirement
- Custom APIs **always require plugin code** for business logic implementation
- The plugin is registered as the MainOperation step
- Without a plugin, the API executes successfully but does nothing

## API Payloads

### Create a Custom API Definition

```http
POST /customapis
MSCRM.SolutionUniqueName: {solution}

{
  "uniquename": "cnt_CalculatePlayerRanking",
  "name": "cnt_CalculatePlayerRanking",
  "displayname": "Calculate Player Ranking",
  "description": "Recalculates the ranking position for a player based on their game scores",
  "bindingtype": 0,
  "boundentitylogicalname": null,
  "isfunction": false,
  "isprivate": false,
  "allowedcustomprocessingsteptype": 0,
  "executeprivilegename": null,
  "plugintypeid@odata.bind": "/plugintypes({plugin-guid})"
}
```

#### allowedcustomprocessingsteptype Values
| Value | Meaning |
|---|---|
| 0 | None — no additional processing steps allowed |
| 1 | Async Only — other plugins can register async steps |
| 2 | Sync and Async — other plugins can register sync or async steps |

Set to 1 or 2 if you want other developers to be able to register additional
plugin steps (pre/post) on your Custom API.

### Create Request Parameters

```http
POST /customapirequestparameters
MSCRM.SolutionUniqueName: {solution}

{
  "uniquename": "PlayerId",
  "name": "PlayerId",
  "displayname": "Player ID",
  "description": "The GUID of the player to recalculate ranking for",
  "type": 12,
  "isoptional": false,
  "logicalentityname": null,
  "CustomAPIId@odata.bind": "/customapis({api-guid})"
}
```

#### Parameter Type Codes
| Code | Type | Description |
|---|---|---|
| 0 | Boolean | true/false |
| 1 | DateTime | Date and time value |
| 2 | Decimal | Decimal number |
| 3 | Entity | Single record (full entity) |
| 4 | EntityCollection | Collection of records |
| 5 | EntityReference | Reference to a record (table + GUID) |
| 6 | Float | Floating-point number |
| 7 | Integer | Whole number |
| 8 | Money | Currency value |
| 9 | Picklist | Choice/option set value |
| 10 | String | Text |
| 11 | StringArray | Array of strings |
| 12 | Guid | Unique identifier |

#### logicalentityname
- Set this when the parameter type is Entity (3), EntityCollection (4), or EntityReference (5)
- Specifies which table the entity parameter refers to
- Leave null for other parameter types

### Create Response Properties

Same structure as request parameters, but POST to `/customapiresponseproperties`:

```http
POST /customapiresponseproperties
MSCRM.SolutionUniqueName: {solution}

{
  "uniquename": "NewRanking",
  "name": "NewRanking",
  "displayname": "New Ranking",
  "description": "The player's new ranking position after recalculation",
  "type": 7,
  "logicalentityname": null,
  "CustomAPIId@odata.bind": "/customapis({api-guid})"
}
```

## Creation Methods

### 1. Web API (Recommended for Automation)
- Use the payloads above via PowerShell scripts
- Best for CI/CD pipelines and automated deployments
- Idempotent scripts should check existence first

### 2. Power Apps Maker Portal
- Navigate to Tables > Custom API in the Dataverse default solution
- Create records directly in the Custom API, Request Parameter, and Response Property tables
- Good for one-off creation and exploration

### 3. Plug-in Registration Tool (GUI)
- Visual Studio-based tool for registering plugins
- Can also create Custom API definitions through the GUI
- Good for developers already using the tool for plugin registration

### 4. Solution Files (Export/Import)
- Custom API definitions are included in solution exports
- Can be version-controlled as XML files
- Import to target environments via solution import

## Calling Custom APIs

### From Web API (JavaScript / External Code)

#### Action (POST)
```javascript
// Unbound action
const response = await fetch(
    `${orgUrl}/api/data/v9.2/cnt_CalculatePlayerRanking`,
    {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json",
            "OData-Version": "4.0"
        },
        body: JSON.stringify({
            "PlayerId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        })
    }
);
const result = await response.json();
console.log(result.NewRanking);
```

#### Function (GET)
```javascript
// Unbound function
const response = await fetch(
    `${orgUrl}/api/data/v9.2/cnt_GetPlayerStats(PlayerId='a1b2c3d4-e5f6-7890-abcd-ef1234567890')`,
    {
        method: "GET",
        headers: {
            "Authorization": `Bearer ${token}`,
            "OData-Version": "4.0"
        }
    }
);
const result = await response.json();
```

#### Bound Action
```javascript
// Action bound to a specific record
const response = await fetch(
    `${orgUrl}/api/data/v9.2/cnt_players(${playerId})/Microsoft.Dynamics.CRM.cnt_ApprovePlayer`,
    {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json",
            "OData-Version": "4.0"
        },
        body: JSON.stringify({})
    }
);
```

### From Xrm.WebApi (Form Scripts)
```javascript
var request = {
    PlayerId: "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    getMetadata: function() {
        return {
            boundParameter: null,
            operationType: 0,  // 0 = Action, 1 = Function
            operationName: "cnt_CalculatePlayerRanking",
            parameterTypes: {
                "PlayerId": {
                    typeName: "Edm.Guid",
                    structuralProperty: 1  // 1 = PrimitiveType
                }
            }
        };
    }
};

Xrm.WebApi.online.execute(request).then(
    function(response) { return response.json(); }
).then(function(result) {
    console.log("New ranking: " + result.NewRanking);
});
```

### From Power Automate
1. Add a "Perform an unbound action" step (or "bound action" for entity-bound)
2. Select the Custom API by name from the action list
3. Fill in the input parameters
4. Use the output properties in subsequent steps

### From Plugins (C#)
```csharp
var request = new OrganizationRequest("cnt_CalculatePlayerRanking");
request["PlayerId"] = new Guid("a1b2c3d4-e5f6-7890-abcd-ef1234567890");
var response = service.Execute(request);
int newRanking = (int)response["NewRanking"];
```

## Testing Custom APIs

### With Postman
1. Set up a Postman environment with your Dataverse org URL and OAuth token
2. For Actions: `POST {{orgUrl}}/api/data/v9.2/cnt_CalculatePlayerRanking`
   with JSON body containing input parameters
3. For Functions: `GET {{orgUrl}}/api/data/v9.2/cnt_GetPlayerStats(PlayerId='...')`
4. Check the response for output properties

### With PowerShell
```powershell
$token = az account get-access-token --resource "https://org.crm6.dynamics.com/" `
    --tenant "your-tenant-id" --query accessToken -o tsv

$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type"  = "application/json; charset=utf-8"
    "OData-Version" = "4.0"
}

$body = @{
    "PlayerId" = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
} | ConvertTo-Json

$result = Invoke-RestMethod -Uri "https://org.crm6.dynamics.com/api/data/v9.2/cnt_CalculatePlayerRanking" `
    -Method POST -Headers $headers -Body $body

Write-Host "New ranking: $($result.NewRanking)"
```

### Verify Registration
Query the Custom API definition to confirm it was created correctly:
```http
GET /customapis?$filter=uniquename eq 'cnt_CalculatePlayerRanking'&$expand=CustomAPIRequestParameters,CustomAPIResponseProperties
```

## Common Gotchas

1. **Missing plugin**: Custom API with no plugin executes with HTTP 200 but does nothing.
   Always register the plugin BEFORE or at the same time as the API definition.

2. **Wrong binding type call syntax**: Bound APIs must be called with the entity path prefix;
   global APIs must NOT include an entity path. Mixing them up returns 404.

3. **Function with side effects**: If your function modifies data, Dataverse may not
   roll back changes on error. Use Actions for data modifications.

4. **Parameter name case sensitivity**: Parameter names in the request body must match
   the `uniquename` exactly (case-sensitive).

5. **Plugin type ID**: The `plugintypeid` must reference the specific plugin TYPE
   (step class), not the plugin assembly. Query `/plugintypes` to find the correct GUID.

6. **Solution awareness**: Always include `MSCRM.SolutionUniqueName` header when creating
   Custom APIs, parameters, and response properties. Otherwise they land in the Default Solution.
