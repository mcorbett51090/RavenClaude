# Relationships (RelationshipDefinitions)

Relationships in Dataverse define foreign key links AND cascading behavior rules for
Assign, Share, Delete, Merge, and Reparent operations.

**Entity Set:** `RelationshipDefinitions`

## One-to-Many (1:N) Relationship

Creates a parent-child link with a Lookup column on the child table.

```http
POST [org-url]/api/data/v9.2/RelationshipDefinitions
MSCRM.SolutionUniqueName: ContosoHRModule
Content-Type: application/json; charset=utf-8
OData-Version: 4.0

{
  "@odata.type": "Microsoft.Dynamics.CRM.OneToManyRelationshipMetadata",
  "SchemaName": "cnt_account_project",
  "ReferencedEntity": "account",
  "ReferencingEntity": "cnt_project",
  "Lookup": {
    "@odata.type": "Microsoft.Dynamics.CRM.LookupAttributeMetadata",
    "SchemaName": "cnt_AccountId",
    "DisplayName": {
      "@odata.type": "Microsoft.Dynamics.CRM.Label",
      "LocalizedLabels": [
        { "@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel", "Label": "Account", "LanguageCode": 1033 }
      ]
    },
    "RequiredLevel": { "Value": "ApplicationRequired" }
  },
  "CascadeConfiguration": {
    "Assign": "Cascade",
    "Delete": "RemoveLink",
    "Merge": "Cascade",
    "Reparent": "NoCascade",
    "Share": "Cascade",
    "Unshare": "NoCascade",
    "RollupView": "NoCascade"
  },
  "AssociatedMenuConfiguration": {
    "Behavior": "UseCollectionName",
    "Group": "Details",
    "Label": {
      "@odata.type": "Microsoft.Dynamics.CRM.Label",
      "LocalizedLabels": [
        { "@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel", "Label": "Projects", "LanguageCode": 1033 }
      ]
    },
    "Order": 10000
  }
}
```

### Key Properties

| Property | Description |
|---|---|
| `ReferencedEntity` | Parent (One side) table logical name |
| `ReferencingEntity` | Child (Many side) table logical name |
| `Lookup` | Defines the lookup column created on the child table |

### Cascade Configuration Options

| Behavior | Delete | Assign | Share |
|---|---|---|---|
| `Cascade` | Delete children | Reassign children | Share children |
| `RemoveLink` | Clear lookup value | N/A | N/A |
| `Restrict` | Prevent parent delete | N/A | N/A |
| `NoCascade` | No action on children | No action | No action |
| `Active` | Cascade only for active records | N/A | N/A |
| `UserOwned` | N/A | Cascade if same owner | N/A |

### Associated Menu Configuration

Controls how the child entity appears in the parent form's "Related" tab:

| Property | Description |
|---|---|
| `Behavior` | `UseCollectionName`, `UseLabel`, or `DoNotDisplay` |
| `Group` | `Details`, `Sales`, `Service`, `Marketing`, or `SalesMarketing` |
| `Order` | Sort order (lower = higher priority) |

## Many-to-Many (N:N) Relationship

Peer-to-peer association. Dataverse auto-generates a hidden intersect table.

```http
POST [org-url]/api/data/v9.2/RelationshipDefinitions
MSCRM.SolutionUniqueName: ContosoHRModule
Content-Type: application/json; charset=utf-8
OData-Version: 4.0

{
  "@odata.type": "Microsoft.Dynamics.CRM.ManyToManyRelationshipMetadata",
  "SchemaName": "cnt_project_employee",
  "Entity1LogicalName": "cnt_project",
  "Entity2LogicalName": "cnt_employee",
  "IntersectEntityName": "cnt_project_employee_intersect",
  "Entity1AssociatedMenuConfiguration": {
    "Behavior": "UseCollectionName",
    "Group": "Details",
    "Order": 10000
  },
  "Entity2AssociatedMenuConfiguration": {
    "Behavior": "UseCollectionName",
    "Group": "Details",
    "Order": 10000
  }
}
```

**Note:** N:N relationships do NOT have `CascadeConfiguration` because records are peers.

## Self-Referential Relationships

A table can have a 1:N relationship with itself (e.g., Parent Project -> Sub Projects):

```json
{
  "@odata.type": "Microsoft.Dynamics.CRM.OneToManyRelationshipMetadata",
  "SchemaName": "cnt_project_subproject",
  "ReferencedEntity": "cnt_project",
  "ReferencingEntity": "cnt_project",
  "Lookup": {
    "@odata.type": "Microsoft.Dynamics.CRM.LookupAttributeMetadata",
    "SchemaName": "cnt_ParentProjectId",
    "DisplayName": { "@odata.type": "Microsoft.Dynamics.CRM.Label", "LocalizedLabels": [{ "Label": "Parent Project", "LanguageCode": 1033 }] }
  },
  "CascadeConfiguration": {
    "Assign": "NoCascade",
    "Delete": "RemoveLink",
    "Merge": "NoCascade",
    "Reparent": "NoCascade",
    "Share": "NoCascade",
    "Unshare": "NoCascade"
  }
}
```

## Eligibility Check Functions

Before creating relationships, validate eligibility:

```http
GET [org-url]/api/data/v9.2/CanBeReferenced(EntityName='account')
```

```http
GET [org-url]/api/data/v9.2/CanBeReferencing(EntityName='cnt_project')
```

```http
GET [org-url]/api/data/v9.2/CanManyToMany(EntityName='cnt_project')
```

Each returns `{ "CanBeReferenced": true }` (or similar) indicating whether the table
supports the requested relationship type.

## Polymorphic Lookups

Modern Dataverse supports lookups that reference multiple table types.
The `Targets` array on a `LookupAttributeMetadata` contains multiple entries:

```json
"Targets": ["account", "contact", "lead"]
```

These are typically system-created (e.g., Customer lookup, Regarding lookup) but can
be inspected via the API.
