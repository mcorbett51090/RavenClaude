# Tables (EntityDefinitions)

Tables are the core structural element. The `EntityMetadata` type defines the physical schema,
behavioral capabilities, and primary identification of a table.

**Entity Set:** `EntityDefinitions`

## Create a Table

```http
POST [org-url]/api/data/v9.2/EntityDefinitions
MSCRM.SolutionUniqueName: ContosoHRModule
Content-Type: application/json; charset=utf-8
OData-Version: 4.0

{
  "@odata.type": "Microsoft.Dynamics.CRM.EntityMetadata",
  "SchemaName": "cnt_Project",
  "DisplayName": {
    "@odata.type": "Microsoft.Dynamics.CRM.Label",
    "LocalizedLabels": [
      { "@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel", "Label": "Project", "LanguageCode": 1033 }
    ]
  },
  "DisplayCollectionName": {
    "@odata.type": "Microsoft.Dynamics.CRM.Label",
    "LocalizedLabels": [
      { "@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel", "Label": "Projects", "LanguageCode": 1033 }
    ]
  },
  "Description": {
    "@odata.type": "Microsoft.Dynamics.CRM.Label",
    "LocalizedLabels": [
      { "@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel", "Label": "Tracks project records", "LanguageCode": 1033 }
    ]
  },
  "OwnershipType": "UserOwned",
  "HasNotes": true,
  "HasActivities": true,
  "IsActivity": false,
  "IsAuditEnabled": { "Value": true },
  "IsConnectionsEnabled": { "Value": true },
  "IsQuickCreateEnabled": true,
  "Attributes": [
    {
      "@odata.type": "Microsoft.Dynamics.CRM.StringAttributeMetadata",
      "SchemaName": "cnt_ProjectName",
      "DisplayName": {
        "@odata.type": "Microsoft.Dynamics.CRM.Label",
        "LocalizedLabels": [
          { "@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel", "Label": "Project Name", "LanguageCode": 1033 }
        ]
      },
      "Description": {
        "@odata.type": "Microsoft.Dynamics.CRM.Label",
        "LocalizedLabels": [
          { "@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel", "Label": "The name of the project", "LanguageCode": 1033 }
        ]
      },
      "IsPrimaryName": true,
      "RequiredLevel": { "Value": "ApplicationRequired" },
      "MaxLength": 200,
      "FormatName": { "Value": "Text" }
    }
  ]
}
```

## CRITICAL: Primary Name Attribute

Every table MUST have exactly one `StringAttributeMetadata` with `IsPrimaryName: true`
in the `Attributes` array at creation time. This field:
- Appears in lookup (foreign key) dropdowns
- Is the record's display identifier
- Cannot be added after table creation as the primary name

## Core Properties (Set at Creation)

| Property | Type | Description | Immutable? |
|---|---|---|---|
| `SchemaName` | string | Database name, must include publisher prefix | Yes |
| `DisplayName` | Label | Singular UI name | No |
| `DisplayCollectionName` | Label | Plural UI name | No |
| `OwnershipType` | enum | `UserOwned` or `OrganizationOwned` | Yes |
| `Description` | Label | Documentation text | No |

## Behavioral Capabilities

| Property | Type | Effect |
|---|---|---|
| `IsActivity` | bool | Makes table an Activity type (inherits from ActivityPointer) |
| `HasActivities` | bool | Enables task/email/appointment association |
| `HasNotes` | bool | Enables annotation (Note) attachments |
| `IsAuditEnabled` | BooleanManagedProperty | Tracks data change history |
| `IsConnectionsEnabled` | BooleanManagedProperty | Allows ad-hoc connections |
| `IsQuickCreateEnabled` | bool | Allows Quick Create forms |

## Table Types

### Standard Table
Default type. Set `IsActivity: false` or omit it.

### Activity Table
Set `IsActivity: true`. Inherits from `ActivityPointer`, gains start/end dates,
activity party fields, and appears in activity feeds. Cannot be changed after creation.

### Virtual Table
Set `IsVirtual: true`. Requires additional Data Provider configuration for
external data source mapping. Does not store data in Dataverse.

### Elastic Table
Set `TableType` to `Elastic`. Designed for high-scale data scenarios with
different performance characteristics than standard tables.

## Retrieve Table Metadata

```http
GET [org-url]/api/data/v9.2/EntityDefinitions(LogicalName='cnt_project')
```

With specific properties:
```http
GET [org-url]/api/data/v9.2/EntityDefinitions(LogicalName='cnt_project')?$select=SchemaName,DisplayName,OwnershipType
```

## Update Table Metadata

```http
PUT [org-url]/api/data/v9.2/EntityDefinitions(LogicalName='cnt_project')
Content-Type: application/json; charset=utf-8

{
  "HasNotes": true,
  "Description": {
    "@odata.type": "Microsoft.Dynamics.CRM.Label",
    "LocalizedLabels": [
      { "@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel", "Label": "Updated description", "LanguageCode": 1033 }
    ]
  }
}
```

## Localization

The `Label` complex type supports multiple languages simultaneously:

```json
"DisplayName": {
  "@odata.type": "Microsoft.Dynamics.CRM.Label",
  "LocalizedLabels": [
    { "@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel", "Label": "Project", "LanguageCode": 1033 },
    { "@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel", "Label": "Projet", "LanguageCode": 1036 },
    { "@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel", "Label": "Projekt", "LanguageCode": 1031 }
  ]
}
```
