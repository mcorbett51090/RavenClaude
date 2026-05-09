# Solutions & Application Lifecycle Management (ALM)

## The Publisher

The Publisher defines the customization prefix and option value prefix. Create it first.

**Entity Set:** `publishers`

### Create Publisher

```http
POST [org-url]/api/data/v9.2/publishers
Content-Type: application/json; charset=utf-8
OData-Version: 4.0

{
  "friendlyname": "Contoso Corp",
  "uniquename": "contoso",
  "customizationprefix": "cnt",
  "customizationoptionvalueprefix": 10000,
  "description": "Publisher for Contoso Corp customizations"
}
```

**Key Properties:**
| Property | Description | Constraints |
|---|---|---|
| `uniquename` | System identifier | Immutable after creation |
| `customizationprefix` | Prepended to all schema names | 2-8 lowercase characters |
| `customizationoptionvalueprefix` | Numeric seed for option set values | Prevents collisions between publishers |

## The Solution Container

Solutions group components into deployable packages.

**Entity Set:** `solutions`

### Create Solution

```http
POST [org-url]/api/data/v9.2/solutions
Content-Type: application/json; charset=utf-8
OData-Version: 4.0

{
  "uniquename": "ContosoHRModule",
  "friendlyname": "Contoso HR Module",
  "version": "1.0.0.0",
  "description": "HR management module for Contoso",
  "publisherid@odata.bind": "/publishers({publisher-guid})"
}
```

**Key Properties:**
| Property | Description |
|---|---|
| `uniquename` | Immutable solution identifier |
| `version` | Format: `major.minor.build.revision` |
| `ismanaged` | Boolean -- managed (read-only in target) vs unmanaged |
| `publisherid` | Linked via `@odata.bind` annotation |

## Adding Components to Solutions

### Method 1: At Creation Time (Recommended)

Include the `MSCRM.SolutionUniqueName` header when creating any component:

```http
POST [org-url]/api/data/v9.2/EntityDefinitions
MSCRM.SolutionUniqueName: ContosoHRModule
Content-Type: application/json; charset=utf-8

{ ... table definition ... }
```

### Method 2: After Creation (AddSolutionComponent)

Add existing components to a solution:

```http
POST [org-url]/api/data/v9.2/AddSolutionComponent
Content-Type: application/json; charset=utf-8

{
  "ComponentId": "{component-guid}",
  "ComponentType": 1,
  "SolutionUniqueName": "ContosoHRModule",
  "AddRequiredComponents": false
}
```

**Component Type Codes:**
| Code | Type |
|---|---|
| 1 | Entity (Table) |
| 2 | Attribute (Column) |
| 3 | Relationship |
| 9 | Option Set |
| 10 | Entity Relationship |
| 24 | System Form |
| 26 | Saved Query (View) |
| 60 | System Form |
| 80 | App Module |

## ALM Best Practices

1. **Never create components in the Default Solution** -- always use `MSCRM.SolutionUniqueName`
2. **Use segmented solutions** -- break large projects into smaller architectural modules
3. **Version systematically** -- increment version on every change
4. **Use AddSolutionComponent** to construct patch or subset solutions
5. **Export/Import** for CI/CD -- use `ExportSolution` and `ImportSolution` actions for pipeline automation

## Token Acquisition

**IMPORTANT:** `pac auth token` does not exist. Use Azure CLI instead.

### Azure CLI Pattern

```powershell
# Login (one-time per session)
az login --tenant "[tenant-id]" --use-device-code

# Get token for Dataverse
$token = az account get-access-token `
    --resource "https://[org].crm6.dynamics.com/" `
    --tenant "[tenant-id]" `
    --query accessToken -o tsv

# Use in headers
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type"  = "application/json; charset=utf-8"
    "OData-Version" = "4.0"
}
```

Tokens expire after ~1 hour. If a 401 is returned, get a fresh token and retry.

## Solution Import Options (Critical Distinction)

When importing a solution to a target environment, three options exist:

| Option | Behavior | When to Use |
|---|---|---|
| **Upgrade** | Adds, updates, AND deletes components not in new version | Standard deployment. Full replacement. |
| **Stage for Upgrade** | Creates a holding solution (`solutionName_upgrade`); you migrate data, then apply | When deleting tables that contain data |
| **Update** | Adds and updates ONLY; does NOT delete missing components | When you need to preserve components that were removed from source |

**IMPORTANT**: Always use **Upgrade** for standard deployments. Use **Stage for Upgrade** when you need to preserve data from tables being removed. Avoid **Update** unless you specifically need to keep divergent components.

## Managed vs Unmanaged Solutions

| Property | Unmanaged | Managed |
|---|---|---|
| Environment | Development only | Non-dev (test, production) |
| Deleting solution | Only removes solution record; components stay | Removes ALL components |
| Customization | Full access | Controlled by managed properties |
| Use case | Active development | Distribution/deployment |

## Managed Properties

Control what consumers of your managed solution can customize:
- **Tables**: Allow changing display name, creating new forms/views/charts, but NOT creating new columns
- **Columns**: Allow changing display name, requirement level, additional properties
- Set via Maker Portal on each component before exporting as managed

## Solution Versioning (Major.Minor.Build.Revision)

- **Patches**: Can only change Build and Revision numbers
- **Clone solution**: Can only change Major and Minor (Build/Revision reset to zero)
- Clone version must be >= base solution version

## Solution Layering

Order of precedence (highest to lowest):
1. Unmanaged customizations (Active layer)
2. Managed solution(s) — latest installed takes precedence
3. Default solution (System layer)

## Deployment Methods

1. **Manual export/import** — via Maker Portal (for both technical and citizen developers)
2. **Power Platform Build Tools** — Azure DevOps CI/CD pipelines
3. **Power Platform CLI** — `pac solution export`, `pac solution import` from terminal
4. **Power Platform Pipelines** — Low-code, citizen-developer-friendly, built-in
   - Requires all environments have Dataverse database
   - Target environments must be managed environments
   - Max 7 stages per pipeline

## Configuration Migration Tool

- Solution export/import does NOT include data
- Never recreate master data manually (generates new GUIDs, breaks code references)
- Use the **Configuration Migration tool** from the Power Platform SDK for data migration
- Also supports Excel export/import for simpler scenarios

## Idempotent Script Pattern

Always check if a resource exists before creating it. This allows safe re-runs after partial failures.

```powershell
function Ensure-Entity {
    param([string]$LogicalName, [hashtable]$Payload)

    try {
        $existing = Invoke-RestMethod -Uri "$baseUrl/EntityDefinitions(LogicalName='$LogicalName')" `
            -Headers $headers -Method GET
        Write-Host "Table '$LogicalName' already exists, skipping."
        return $existing.MetadataId
    } catch {
        if ($_.Exception.Response.StatusCode -eq 404) {
            Write-Host "Creating table '$LogicalName'..."
            $result = Invoke-RestMethod -Uri "$baseUrl/EntityDefinitions" `
                -Headers $headers -Method POST -Body ($Payload | ConvertTo-Json -Depth 20)
            Write-Host "Created table '$LogicalName'."
            return $result.MetadataId
        }
        throw
    }
}
```
