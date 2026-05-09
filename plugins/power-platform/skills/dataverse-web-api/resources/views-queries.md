# Views (SavedQuery) and Queries

Views define how lists of data are queried and presented. System views are stored in
`savedquery`; personal views in `userquery`.

**Entity Set:** `savedqueries`

## The Dual-XML Architecture

Every view requires TWO XML definitions that must stay synchronized:

1. **FetchXML** (`fetchxml`) -- The query (what data to retrieve)
2. **LayoutXML** (`layoutxml`) -- The presentation (how to display it)

**CRITICAL:** Every attribute in `layoutxml` MUST also appear in `fetchxml`.
A mismatch causes runtime errors.

## Create a System View

```http
POST [org-url]/api/data/v9.2/savedqueries
MSCRM.SolutionUniqueName: ContosoHRModule
Content-Type: application/json; charset=utf-8
OData-Version: 4.0

{
  "name": "Active Projects",
  "description": "Shows all active projects",
  "returnedtypecode": "cnt_project",
  "querytype": 0,
  "isdefault": true,
  "fetchxml": "<fetch version='1.0' output-format='xml-platform' mapping='logical'><entity name='cnt_project'><attribute name='cnt_projectname' /><attribute name='cnt_startdate' /><attribute name='cnt_budget' /><attribute name='cnt_priority' /><attribute name='statuscode' /><attribute name='createdon' /><order attribute='cnt_projectname' descending='false' /><filter type='and'><condition attribute='statecode' operator='eq' value='0' /></filter></entity></fetch>",
  "layoutxml": "<grid name='resultset' jump='cnt_projectname' select='1' icon='1' preview='1'><row name='result' id='cnt_projectid'><cell name='cnt_projectname' width='250' /><cell name='cnt_startdate' width='150' /><cell name='cnt_budget' width='120' /><cell name='cnt_priority' width='120' /><cell name='statuscode' width='120' /><cell name='createdon' width='150' /></row></grid>"
}
```

## FetchXML Reference

```xml
<fetch version="1.0" output-format="xml-platform" mapping="logical" count="50">
  <entity name="cnt_project">
    <!-- Columns to retrieve -->
    <attribute name="cnt_projectname" />
    <attribute name="cnt_startdate" />
    <attribute name="cnt_budget" />

    <!-- Sorting -->
    <order attribute="cnt_projectname" descending="false" />

    <!-- Filtering -->
    <filter type="and">
      <condition attribute="statecode" operator="eq" value="0" />
      <condition attribute="cnt_budget" operator="gt" value="10000" />
    </filter>

    <!-- Related data (JOIN) -->
    <link-entity name="account" from="accountid" to="cnt_accountid" alias="acct" link-type="inner">
      <attribute name="name" />
      <filter type="and">
        <condition attribute="statecode" operator="eq" value="0" />
      </filter>
    </link-entity>
  </entity>
</fetch>
```

### Common Filter Operators

| Operator | Description | Example |
|---|---|---|
| `eq` | Equals | `value="0"` |
| `ne` | Not equals | `value="1"` |
| `gt` / `ge` | Greater than / or equal | `value="1000"` |
| `lt` / `le` | Less than / or equal | `value="5000"` |
| `like` | Pattern match | `value="%Smith%"` |
| `in` | In list | Uses child `<value>` elements |
| `null` / `not-null` | Null check | No value attribute needed |
| `on` / `on-or-before` / `on-or-after` | Date comparisons | Date value |
| `this-month` / `last-x-days` | Relative date | `value="30"` for last 30 days |

### Link Types

| Type | Description |
|---|---|
| `inner` | Only returns records with matching related data |
| `outer` | Returns all records, null if no match |
| `any` | Returns parent if ANY child matches filter |
| `not any` | Returns parent if NO child matches filter |

## LayoutXML Reference

```xml
<grid name="resultset" object="NNNNN" jump="cnt_projectname" select="1" icon="1" preview="1">
  <row name="result" id="cnt_projectid">
    <cell name="cnt_projectname" width="250" />
    <cell name="cnt_startdate" width="150" />
    <cell name="cnt_budget" width="120" />
    <cell name="acct.name" width="200" />
  </row>
</grid>
```

**CRITICAL: The `object` attribute is REQUIRED on `<grid>`.** The entity's ObjectTypeCode must be
included. Without it, Dataverse returns: "The required attribute 'object' is missing."

```xml
<grid name="resultset" object="10796" jump="cnt_projectname" select="1" icon="1" preview="1">
```

Query the ObjectTypeCode at runtime (it's assigned dynamically when tables are created):
```http
GET [org-url]/api/data/v9.2/EntityDefinitions(LogicalName='cnt_project')?$select=ObjectTypeCode
```

**Grid attributes:**
- `jump` -- Column that links to the record detail
- `select` -- Enable row selection (1 = yes)
- `icon` -- Show entity icon (1 = yes)

**Cell attributes:**
- `name` -- Must match an attribute name from fetchxml
- `width` -- Column width in pixels
- For linked entity attributes, use the alias: `acct.name`

## View Types (querytype)

| Value | Type | Description |
|---|---|---|
| 0 | Public View | Standard system view visible to all users |
| 1 | Advanced Find | Used by the Advanced Find feature |
| 2 | Associated View | Displayed in subgrids on related forms |
| 4 | Quick Find | Used for search functionality |
| 64 | Lookup View | Displayed in lookup dialogs |

## Update a View

```http
PATCH [org-url]/api/data/v9.2/savedqueries({view-guid})
Content-Type: application/json; charset=utf-8

{
  "name": "Active Projects - Updated",
  "fetchxml": "...",
  "layoutxml": "..."
}
```

After updating, call `PublishXml` to make changes visible.

## Default View Management

When setting a custom view as the default, you must also unset the previous default:

```http
// Step 1: Set your custom view as default
PATCH [org-url]/api/data/v9.2/savedqueries({custom-view-guid})
{ "isdefault": true }

// Step 2: Unset the auto-created "Active" view as default
PATCH [org-url]/api/data/v9.2/savedqueries({active-view-guid})
{ "isdefault": false }
```

The default view is the landing page when a user navigates to that entity. Choose the most useful view.

## Removing Views from App Module

Hide unnecessary views (e.g., "Inactive" views) from the app using `RemoveAppComponents`:

```http
POST [org-url]/api/data/v9.2/RemoveAppComponents
{
    "AppId": "{app-module-guid}",
    "Components": [
        {
            "@odata.type": "Microsoft.Dynamics.CRM.savedquery",
            "savedqueryid": "{inactive-view-guid}"
        }
    ]
}
```

The views still exist in the environment but are hidden from the app's navigation.

## Choice/Option Set Column Coloring

Assign colors to option values for visual distinction in views:

```json
{
    "Options": [
        { "Value": 892100000, "Label": { ... }, "Color": "#28a745" },
        { "Value": 892100001, "Label": { ... }, "Color": "#ffc107" },
        { "Value": 892100002, "Label": { ... }, "Color": "#dc3545" }
    ]
}
```

Enable color rendering in views by adding the Power Apps Grid Control with `EnableOptionSetColors` parameter.

## Custom Column Rendering in Views

For custom rendering (status indicators, progress bars, icons), use web resource-backed rendering:

```xml
<cell name="statuscode" width="120"
      imageproviderwebresource="$webresource:cnt_/js/statusRenderer.js"
      imageproviderfunctionname="StatusRenderer.getImage" />
```

The JavaScript function receives the row data and returns an image/icon to display.

## View Design Best Practices

- **Column selection**: Show the most relevant columns at a glance — don't dump every field
- **Column ordering**: Name first, then key data, then dates/metadata last
- **Column widths**: Use appropriate widths (`width='150'` etc.) — avoid cramped or overly wide columns
- **Sorting**: Set a default sort that makes sense (alphabetical for names, descending for scores/dates)
- **Leaderboard views**: Sort by score descending, include ranking-relevant columns
- **Admin views**: Include status columns (`statecode`, `statuscode`) and audit columns (`createdon`, `modifiedby`)
- **Quick Find**: Include searchable columns in the `isquickfindfields` filter
