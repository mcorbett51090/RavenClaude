# App Modules, Sitemaps, and Application Composition

Model-Driven Apps are modular collections of entities, forms, and views tailored
to specific roles. The Web API exposes `appmodule` and `sitemap` entities for management.

## App Module (appmodule)

**Entity Set:** `appmodules`

### Create an App Module

```http
POST [org-url]/api/data/v9.2/appmodules
MSCRM.SolutionUniqueName: ContosoHRModule
Content-Type: application/json; charset=utf-8
OData-Version: 4.0

{
  "name": "HR Manager",
  "uniquename": "HRManager",
  "description": "Application for HR managers to manage projects and employees",
  "clienttype": 4,
  "webresourceid": "{icon-webresource-guid}"
}
```

**CRITICAL RULES:**
- **`uniquename` must NOT include the publisher prefix.** Use `"HRManager"`, NOT `"cnt_HRManager"`.
  The platform auto-prefixes with the solution publisher's prefix. Including it manually causes
  `InvalidAppModuleAggregatedErrors` (0x80050135).
- **`webresourceid` is a direct GUID string**, NOT an `@odata.bind` reference. Using
  `webresourceid@odata.bind` causes an OData primitive type error.
- **`webresourceid` is required.** You can use a default system icon: `953b9fac-1e5e-e611-80d6-00155ded156f`
- Valid properties: `name`, `uniquename`, `clienttype`, `webresourceid`, `description`, `formfactor`, `navigationtype`, `url`
- `appversion` is NOT a valid property.

**ClientType Values:**
| Value | Type |
|---|---|
| 1 | Web |
| 2 | Mobile |
| 4 | Unified Interface (recommended) |

### Finding Unpublished App Modules

**CRITICAL:** Newly created app modules are UNPUBLISHED and will NOT appear in normal
`GET /appmodules` queries. Use the special function:

```http
GET [org-url]/api/data/v9.2/appmodules/Microsoft.Dynamics.CRM.RetrieveUnpublishedMultiple()
```

Common issues:
- A freshly created app returns 404 on `GET /appmodules({guid})` — it's unpublished, not missing
- `InvalidAppModuleAggregatedErrors` when re-creating often means the `uniquename` is taken by an unpublished ghost
- Always check for existing unpublished apps before creating new ones
- Delete ghost/duplicate apps before retrying creation

### Add App Module to Solution

```http
POST [org-url]/api/data/v9.2/AddSolutionComponent
{
    "ComponentId": "{app-module-guid}",
    "ComponentType": 80,
    "SolutionUniqueName": "ContosoHRModule",
    "AddRequiredComponents": false
}
```

## AddAppComponents Action

Adds components to the app module scope. **Use entity-specific `@odata.type` values.**

**IMPORTANT:** Do NOT use generic component type codes (1, 26, 60). The correct format uses
the actual Dataverse entity type name and entity-specific ID field names.

```http
POST [org-url]/api/data/v9.2/AddAppComponents
Content-Type: application/json; charset=utf-8

{
    "AppId": "{app-module-guid}",
    "Components": [
        {
            "@odata.type": "Microsoft.Dynamics.CRM.entity",
            "entityid": "{entity-metadata-id}"
        },
        {
            "@odata.type": "Microsoft.Dynamics.CRM.savedquery",
            "savedqueryid": "{view-guid}"
        },
        {
            "@odata.type": "Microsoft.Dynamics.CRM.systemform",
            "formid": "{form-guid}"
        },
        {
            "@odata.type": "Microsoft.Dynamics.CRM.sitemap",
            "sitemapid": "{sitemap-guid}"
        }
    ]
}
```

**Supported @odata.type values:**
| Type | ID Field | Description |
|---|---|---|
| `Microsoft.Dynamics.CRM.entity` | `entityid` | Table (use MetadataId from EntityDefinitions) |
| `Microsoft.Dynamics.CRM.savedquery` | `savedqueryid` | System View |
| `Microsoft.Dynamics.CRM.systemform` | `formid` | Form |
| `Microsoft.Dynamics.CRM.sitemap` | `sitemapid` | Sitemap |

**Common mistakes:**
- `"#Microsoft.Dynamics.CRM.AppModuleComponent"` does NOT exist in the OData model
- Without `@odata.type`: "Invalid property 'id' was found in entity 'crmbaseentity'"
- Entity `entityid` uses the table's **MetadataId** (from `EntityDefinitions`), not a record GUID
- Can batch all components in one call, or add individually

## RemoveAppComponents Action

Remove components from an app module (e.g., hide unnecessary "Inactive" views):

```http
POST [org-url]/api/data/v9.2/RemoveAppComponents
{
    "AppId": "{app-module-guid}",
    "Components": [
        {
            "@odata.type": "Microsoft.Dynamics.CRM.savedquery",
            "savedqueryid": "{view-to-remove-guid}"
        }
    ]
}
```

## Site Map (sitemap)

The navigation structure (left-hand menu) is defined by the sitemap entity.

**Entity Set:** `sitemaps`

### Create a Sitemap

```http
POST [org-url]/api/data/v9.2/sitemaps
MSCRM.SolutionUniqueName: ContosoHRModule
Content-Type: application/json; charset=utf-8

{
  "sitemapxml": "<SiteMap>...</SiteMap>",
  "sitemapnameunique": "cnt_HRManagerSiteMap"
}
```

**CRITICAL:** `sitemapnameunique` is REQUIRED — the API returns "cannot be null or empty" without it.

### SitemapXml Structure

```xml
<SiteMap>
  <Area Id="HR" Title="Human Resources" ShowGroups="true">
    <Group Id="Projects" Title="Projects">
      <SubArea Id="cnt_project" Entity="cnt_project" Title="Projects" />
      <SubArea Id="cnt_milestone" Entity="cnt_milestone" Title="Milestones" />
    </Group>
    <Group Id="People" Title="People">
      <SubArea Id="cnt_employee" Entity="cnt_employee" Title="Employees" />
    </Group>
  </Area>
  <Area Id="Settings" Title="Settings" ShowGroups="true">
    <Group Id="Config" Title="Configuration">
      <SubArea Id="cnt_config" Url="/main.aspx?pagetype=webresource&amp;webresourceName=cnt_configpage" Title="Configuration" />
    </Group>
  </Area>
</SiteMap>
```

### SubArea Types

| Attribute | Description |
|---|---|
| `Entity` | References a Dataverse table by logical name |
| `Url` | Links to a web resource or external URL |
| `GetStartedPagePath` | Getting started page for the area |

### Associate Sitemap with App Module

**Option 1 (Preferred): Add via AddAppComponents**

```http
POST [org-url]/api/data/v9.2/AddAppComponents
{
    "AppId": "{app-module-guid}",
    "Components": [
        {
            "@odata.type": "Microsoft.Dynamics.CRM.sitemap",
            "sitemapid": "{sitemap-guid}"
        }
    ]
}
```

**Option 2: $ref navigation property** (unreliable — may return "undeclared property" errors)

```http
POST [org-url]/api/data/v9.2/appmodules({app-guid})/appmodulesitemap/$ref
{
  "@odata.id": "[org-url]/api/data/v9.2/sitemaps({sitemap-guid})"
}
```

## Publishing with App Module

Include the `<appmodules>` section in PublishXml to publish the app module itself:

```http
POST [org-url]/api/data/v9.2/PublishXml
{
    "ParameterXml": "<importexportxml><appmodules><appmodule>{app-module-guid}</appmodule></appmodules><entities><entity>cnt_project</entity></entities></importexportxml>"
}
```

## ValidateApp Function

Diagnostic tool to check an app module for missing dependencies:

```http
GET [org-url]/api/data/v9.2/ValidateApp(AppModuleId={app-guid})
```

Returns `ValidationSuccess: true` if no issues, or a list of validation problems.

## Complete App Setup Sequence

1. Create Publisher → `POST /publishers`
2. Create Solution → `POST /solutions`
3. Create Tables → `POST /EntityDefinitions` (with solution header)
4. Create Columns → `POST /EntityDefinitions({id})/Attributes`
5. Create Relationships → `POST /RelationshipDefinitions`
6. Create Views → `POST /savedqueries`
7. Create Forms → `POST /systemforms`
8. Publish entities → `PublishXml`
9. Create App Module → `POST /appmodules`
10. Add to Solution → `AddSolutionComponent` (ComponentType=80)
11. Add Components to App → `AddAppComponents` (entities, views, forms)
12. Create Sitemap → `POST /sitemaps` (with `sitemapnameunique`)
13. Add Sitemap to App → `AddAppComponents` (sitemap)
14. Publish All → `PublishXml` (include `<appmodules>`)
15. Validate → `ValidateApp`
