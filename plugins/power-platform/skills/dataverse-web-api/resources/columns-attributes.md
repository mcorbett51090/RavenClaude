# Columns (Attributes)

Columns define the data points a table can hold. They are managed via the `Attributes`
navigation property of an `EntityDefinition`.

**Endpoint:** `POST /EntityDefinitions(LogicalName='{table}')/Attributes`

The `@odata.type` property determines the column type and its validation rules.

## String Column (StringAttributeMetadata)

```http
POST [org-url]/api/data/v9.2/EntityDefinitions(LogicalName='cnt_project')/Attributes
MSCRM.SolutionUniqueName: ContosoHRModule

{
  "@odata.type": "Microsoft.Dynamics.CRM.StringAttributeMetadata",
  "SchemaName": "cnt_Description",
  "DisplayName": { "@odata.type": "Microsoft.Dynamics.CRM.Label", "LocalizedLabels": [{ "Label": "Description", "LanguageCode": 1033 }] },
  "RequiredLevel": { "Value": "None" },
  "MaxLength": 500,
  "FormatName": { "Value": "Text" }
}
```

**Format options:** `Text`, `Email`, `Url`, `TickerSymbol`, `Phone`

## Memo Column (MemoAttributeMetadata)

Multi-line text. MaxLength up to 1,048,576 characters.

```json
{
  "@odata.type": "Microsoft.Dynamics.CRM.MemoAttributeMetadata",
  "SchemaName": "cnt_Notes",
  "DisplayName": { "@odata.type": "Microsoft.Dynamics.CRM.Label", "LocalizedLabels": [{ "Label": "Notes", "LanguageCode": 1033 }] },
  "RequiredLevel": { "Value": "None" },
  "MaxLength": 10000
}
```

## Boolean Column (BooleanAttributeMetadata)

```json
{
  "@odata.type": "Microsoft.Dynamics.CRM.BooleanAttributeMetadata",
  "SchemaName": "cnt_IsActive",
  "DisplayName": { "@odata.type": "Microsoft.Dynamics.CRM.Label", "LocalizedLabels": [{ "Label": "Is Active", "LanguageCode": 1033 }] },
  "RequiredLevel": { "Value": "None" },
  "DefaultValue": true,
  "OptionSet": {
    "@odata.type": "Microsoft.Dynamics.CRM.BooleanOptionSetMetadata",
    "TrueOption": {
      "Value": 1,
      "Label": { "@odata.type": "Microsoft.Dynamics.CRM.Label", "LocalizedLabels": [{ "Label": "Yes", "LanguageCode": 1033 }] }
    },
    "FalseOption": {
      "Value": 0,
      "Label": { "@odata.type": "Microsoft.Dynamics.CRM.Label", "LocalizedLabels": [{ "Label": "No", "LanguageCode": 1033 }] }
    }
  }
}
```

## Integer Column (IntegerAttributeMetadata)

```json
{
  "@odata.type": "Microsoft.Dynamics.CRM.IntegerAttributeMetadata",
  "SchemaName": "cnt_Quantity",
  "DisplayName": { "@odata.type": "Microsoft.Dynamics.CRM.Label", "LocalizedLabels": [{ "Label": "Quantity", "LanguageCode": 1033 }] },
  "RequiredLevel": { "Value": "None" },
  "Format": "None",
  "MinValue": 0,
  "MaxValue": 100000
}
```

**Format options:** `None` (standard), `Duration` (minutes), `TimeZone` (offset), `Language` (LCID)

## Decimal Column (DecimalAttributeMetadata)

```json
{
  "@odata.type": "Microsoft.Dynamics.CRM.DecimalAttributeMetadata",
  "SchemaName": "cnt_Rate",
  "DisplayName": { "@odata.type": "Microsoft.Dynamics.CRM.Label", "LocalizedLabels": [{ "Label": "Rate", "LanguageCode": 1033 }] },
  "RequiredLevel": { "Value": "None" },
  "Precision": 4,
  "MinValue": 0,
  "MaxValue": 999999.9999
}
```

## Double Column (DoubleAttributeMetadata)

```json
{
  "@odata.type": "Microsoft.Dynamics.CRM.DoubleAttributeMetadata",
  "SchemaName": "cnt_Latitude",
  "DisplayName": { "@odata.type": "Microsoft.Dynamics.CRM.Label", "LocalizedLabels": [{ "Label": "Latitude", "LanguageCode": 1033 }] },
  "RequiredLevel": { "Value": "None" },
  "Precision": 6,
  "MinValue": -90.0,
  "MaxValue": 90.0
}
```

## Money Column (MoneyAttributeMetadata)

```json
{
  "@odata.type": "Microsoft.Dynamics.CRM.MoneyAttributeMetadata",
  "SchemaName": "cnt_Budget",
  "DisplayName": { "@odata.type": "Microsoft.Dynamics.CRM.Label", "LocalizedLabels": [{ "Label": "Budget", "LanguageCode": 1033 }] },
  "RequiredLevel": { "Value": "None" },
  "PrecisionSource": 2,
  "MinValue": 0,
  "MaxValue": 1000000000
}
```

**PrecisionSource:** `0` = attribute precision, `1` = organization currency, `2` = pricing decimal precision

**Note:** Creating a Money column auto-generates a hidden `_Base` column that stores the value
normalized to the org's base currency for exchange rate handling.

## DateTime Column (DateTimeAttributeMetadata)

```json
{
  "@odata.type": "Microsoft.Dynamics.CRM.DateTimeAttributeMetadata",
  "SchemaName": "cnt_StartDate",
  "DisplayName": { "@odata.type": "Microsoft.Dynamics.CRM.Label", "LocalizedLabels": [{ "Label": "Start Date", "LanguageCode": 1033 }] },
  "RequiredLevel": { "Value": "ApplicationRequired" },
  "Format": "DateAndTime",
  "DateTimeBehavior": { "Value": "UserLocal" }
}
```

**Format:** `DateOnly` or `DateAndTime`

**DateTimeBehavior:**
| Value | Behavior |
|---|---|
| `UserLocal` | Adjusts to the viewing user's time zone |
| `DateOnly` | Stores date literal, no time conversion (birthdays) |
| `TimeZoneIndependent` | Stores exact value, ignores time zones (timestamps) |

## Choice Column -- Local (PicklistAttributeMetadata)

Options defined inline with the attribute (not reusable elsewhere):

```json
{
  "@odata.type": "Microsoft.Dynamics.CRM.PicklistAttributeMetadata",
  "SchemaName": "cnt_Priority",
  "DisplayName": { "@odata.type": "Microsoft.Dynamics.CRM.Label", "LocalizedLabels": [{ "Label": "Priority", "LanguageCode": 1033 }] },
  "RequiredLevel": { "Value": "None" },
  "OptionSet": {
    "@odata.type": "Microsoft.Dynamics.CRM.OptionSetMetadata",
    "IsGlobal": false,
    "OptionSetType": "Picklist",
    "Options": [
      { "Value": 100000000, "Label": { "@odata.type": "Microsoft.Dynamics.CRM.Label", "LocalizedLabels": [{ "Label": "Low", "LanguageCode": 1033 }] } },
      { "Value": 100000001, "Label": { "@odata.type": "Microsoft.Dynamics.CRM.Label", "LocalizedLabels": [{ "Label": "Medium", "LanguageCode": 1033 }] } },
      { "Value": 100000002, "Label": { "@odata.type": "Microsoft.Dynamics.CRM.Label", "LocalizedLabels": [{ "Label": "High", "LanguageCode": 1033 }] } }
    ]
  }
}
```

## Choice Column -- Global (Bound to GlobalOptionSetDefinition)

References a pre-existing global option set.

**CRITICAL:** The `GlobalOptionSet@odata.bind` property requires the **MetadataId GUID**, not the
Name. Using `Name='...'` causes: `Guid should contain 32 digits with 4 dashes`.

**Step 1: Look up the MetadataId:**
```http
GET /GlobalOptionSetDefinitions(Name='cnt_projectstatus')?$select=MetadataId
```

**Step 2: Use the GUID in the binding:**
```json
{
  "@odata.type": "Microsoft.Dynamics.CRM.PicklistAttributeMetadata",
  "SchemaName": "cnt_Status",
  "DisplayName": { "@odata.type": "Microsoft.Dynamics.CRM.Label", "LocalizedLabels": [{ "Label": "Status", "LanguageCode": 1033 }] },
  "RequiredLevel": { "Value": "ApplicationRequired" },
  "GlobalOptionSet@odata.bind": "/GlobalOptionSetDefinitions(a1b2c3d4-e5f6-7890-abcd-ef1234567890)"
}
```

## Multi-Select Choice (MultiSelectPicklistAttributeMetadata)

Allows multiple selections. Stored internally as semicolon-separated integers.

```json
{
  "@odata.type": "Microsoft.Dynamics.CRM.MultiSelectPicklistAttributeMetadata",
  "SchemaName": "cnt_Tags",
  "DisplayName": { "@odata.type": "Microsoft.Dynamics.CRM.Label", "LocalizedLabels": [{ "Label": "Tags", "LanguageCode": 1033 }] },
  "RequiredLevel": { "Value": "None" },
  "OptionSet": {
    "@odata.type": "Microsoft.Dynamics.CRM.OptionSetMetadata",
    "IsGlobal": false,
    "OptionSetType": "Picklist",
    "Options": [
      { "Value": 100000000, "Label": { "@odata.type": "Microsoft.Dynamics.CRM.Label", "LocalizedLabels": [{ "Label": "Urgent", "LanguageCode": 1033 }] } },
      { "Value": 100000001, "Label": { "@odata.type": "Microsoft.Dynamics.CRM.Label", "LocalizedLabels": [{ "Label": "Featured", "LanguageCode": 1033 }] } }
    ]
  }
}
```

**Limitation:** Multi-select choices have restrictions in workflows and calculated fields.

## File Column (FileAttributeMetadata)

```json
{
  "@odata.type": "Microsoft.Dynamics.CRM.FileAttributeMetadata",
  "SchemaName": "cnt_Attachment",
  "DisplayName": { "@odata.type": "Microsoft.Dynamics.CRM.Label", "LocalizedLabels": [{ "Label": "Attachment", "LanguageCode": 1033 }] },
  "MaxSizeInKB": 32768
}
```

## Image Column (ImageAttributeMetadata)

```json
{
  "@odata.type": "Microsoft.Dynamics.CRM.ImageAttributeMetadata",
  "SchemaName": "cnt_Photo",
  "DisplayName": { "@odata.type": "Microsoft.Dynamics.CRM.Label", "LocalizedLabels": [{ "Label": "Photo", "LanguageCode": 1033 }] },
  "IsPrimaryImage": true,
  "MaxSizeInKB": 10240
}
```

`IsPrimaryImage: true` designates this as the record avatar image.

## RequiredLevel Values

| Value | Meaning |
|---|---|
| `None` | Optional |
| `SystemRequired` | Required by the system (cannot be set by user) |
| `ApplicationRequired` | Required by the application (user must provide) |
| `Recommended` | Recommended but not enforced |

## Rich Text Memo

The standard `MemoAttributeMetadata` creates a plain multi-line text field. To enable rich text
editing (bold, italic, lists, links, embedded images), set the `FormatName` property.

**Common confusion:** `Format` and `FormatName` are different properties.
- `Format: "Text"` -- the default format for memo columns (plain text). This is the legacy property.
- `FormatName: { "Value": "RichText" }` -- enables the rich text editor. This is what you need.

Setting only `Format: "RichText"` does NOT work. You must use `FormatName`.

```http
POST [org-url]/api/data/v9.2/EntityDefinitions(LogicalName='cnt_project')/Attributes
MSCRM.SolutionUniqueName: ContosoHRModule

{
  "@odata.type": "Microsoft.Dynamics.CRM.MemoAttributeMetadata",
  "SchemaName": "cnt_RichNotes",
  "DisplayName": {
    "@odata.type": "Microsoft.Dynamics.CRM.Label",
    "LocalizedLabels": [{ "Label": "Rich Notes", "LanguageCode": 1033 }]
  },
  "RequiredLevel": { "Value": "None" },
  "MaxLength": 1048576,
  "Format": "Text",
  "FormatName": { "Value": "RichText" }
}
```

**Max length for rich text:** Set to `1048576` (the maximum). Rich text stores HTML markup,
so the actual visible text capacity is significantly less than the character limit. Embedded
images are stored as base64, which consumes considerable space.

On forms, the standard Memo control renders the rich text editor automatically when `FormatName`
is `RichText`. For more control, bind the `RichTextEditorControl` explicitly
(see `resources/forms-ui.md`).

## Auto-Number String

An auto-number column is a `StringAttributeMetadata` with the `AutoNumberFormat` property set.
Dataverse generates the value automatically on record creation.

```http
POST [org-url]/api/data/v9.2/EntityDefinitions(LogicalName='cnt_project')/Attributes
MSCRM.SolutionUniqueName: ContosoHRModule

{
  "@odata.type": "Microsoft.Dynamics.CRM.StringAttributeMetadata",
  "SchemaName": "cnt_InvoiceNumber",
  "DisplayName": {
    "@odata.type": "Microsoft.Dynamics.CRM.Label",
    "LocalizedLabels": [{ "Label": "Invoice Number", "LanguageCode": 1033 }]
  },
  "RequiredLevel": { "Value": "None" },
  "MaxLength": 100,
  "AutoNumberFormat": "INV-{SEQNUM:5}"
}
```

### Format Tokens

| Token | Description | Example |
|---|---|---|
| `{SEQNUM:n}` | Sequential number, zero-padded to `n` digits | `{SEQNUM:5}` produces `00001` |
| `{RANDSTRING:n}` | Random alphanumeric string of length `n` | `{RANDSTRING:4}` produces `A7B2` |
| `{DATETIMEUTC:format}` | UTC datetime in .NET format string | `{DATETIMEUTC:yyyyMMdd}` produces `20250115` |

Tokens can be combined with literal text: `"TKT-{DATETIMEUTC:yyyyMM}-{SEQNUM:4}"` produces `TKT-202501-0001`.

### Seed Value

The sequence starts at 1000 by default. To change the starting value:

```http
POST [org-url]/api/data/v9.2/SetAutoNumberSeed
{
  "EntityName": "cnt_project",
  "AttributeName": "cnt_invoicenumber",
  "Value": 5000
}
```

**Notes:**
- Auto-number fields are read-only after creation (users cannot edit the generated value)
- The sequence counter is global per column -- it does not reset per year or per any partition
- Gaps can occur if records are deleted or if imports fail mid-batch
- An auto-number column can serve as the `IsPrimaryName` column on a table

## Multi-Select Choice Details

Multi-select choice columns (`MultiSelectPicklistAttributeMetadata`) store values as
comma-separated integers internally.

### Querying Multi-Select Values (OData)

Standard `$filter` operators (`eq`, `ne`) do not work with multi-select columns. Use the
dedicated OData functions:

```
# Records where tags contain "High Priority" (value 100000000)
GET /cnt_projects?$filter=Microsoft.Dynamics.CRM.ContainValues(PropertyName='cnt_tags',PropertyValues=['100000000'])

# Records where tags do NOT contain "Archived" (value 100000003)
GET /cnt_projects?$filter=Microsoft.Dynamics.CRM.DoesNotContainValues(PropertyName='cnt_tags',PropertyValues=['100000003'])

# Records where tags contain BOTH "High Priority" AND "Customer Facing"
GET /cnt_projects?$filter=Microsoft.Dynamics.CRM.ContainValues(PropertyName='cnt_tags',PropertyValues=['100000000','100000001'])
```

### Setting Multi-Select Values via API

Pass values as a comma-separated string:

```json
{
  "cnt_tags": "100000000,100000002"
}
```

To clear all selections, set to `null`.

### Limitations

- Cannot be used in calculated fields or rollup fields
- Cannot be used as conditions in classic workflows (use Power Automate)
- Limited support in business rules (show/hide works, but value conditions are restricted)
- Maximum of 150 options per multi-select column
- Not supported in duplicate detection rules
- FetchXml filtering uses `contain-values` and `not-contain-values` conditions

## File Column Details

File columns (`FileAttributeMetadata`) store binary file attachments in Azure Blob Storage
managed by Dataverse.

### Upload via API

**Direct upload (files up to 16 MB):**

```http
PATCH [org-url]/api/data/v9.2/cnt_projects({record-id})/cnt_attachment
Content-Type: application/octet-stream
x-ms-file-name: document.pdf

<binary file content>
```

**Chunked upload (files over 16 MB):**

For large files, use a three-step chunked upload process:

1. **Initialize:** `POST /InitializeFileBlocksUpload` with entity reference and column name
2. **Upload chunks:** `POST /UploadBlock` with each 4 MB chunk and a block ID
3. **Commit:** `POST /CommitFileBlocksUpload` with the list of block IDs and file name

### Download via API

```http
GET [org-url]/api/data/v9.2/cnt_projects({record-id})/cnt_attachment/$value
```

The response includes the binary content with `Content-Type` and `x-ms-file-name` headers.

### MaxSizeInKB Limits

- Minimum: `1` (1 KB)
- Maximum: `131072` (128 MB)
- Default: `32768` (32 MB) if not specified
- The org-wide file size limit may further restrict the effective maximum

**Notes:**
- File columns do not support inline preview on forms -- users see a download link
- File columns cannot be made required (`RequiredLevel` is ignored)
- Deleted files are not recoverable
- File metadata (name, size, MIME type) is accessible via the standard column query

## Image Column Details

Image columns (`ImageAttributeMetadata`) store image files with automatic thumbnail generation.

### CanStoreFullImage Behavior

| `CanStoreFullImage` | Thumbnail (144x144) | Full Image | Use Case |
|---|---|---|---|
| `true` | Stored | Stored | When you need the original image (photos, documents) |
| `false` | Stored | NOT stored | When a small avatar is sufficient (record icons) |

### Thumbnail vs Full Image

- **Thumbnail:** Always generated, always stored. Accessed via the `entityimage` column.
  Max size is 144x144 pixels.
- **Full image:** Only stored when `CanStoreFullImage: true`. Accessed via `entityimage_url`
  or by querying the image column directly.

### IsPrimaryImage

When `IsPrimaryImage: true`:
- The image appears as the record avatar in the form header
- The image appears in grid views next to the record name
- Only one column per table can be the primary image
- Setting a second column to `IsPrimaryImage: true` automatically unsets the first

### Upload via API

```http
PATCH [org-url]/api/data/v9.2/cnt_projects({record-id})/cnt_photo
Content-Type: application/octet-stream

<binary image content>
```

**Supported formats:** PNG, JPG, GIF, BMP

### MaxSizeInKB Limits

- Minimum: `1` (1 KB)
- Maximum: `30720` (30 MB)
- Default: `10240` (10 MB) if not specified

**Notes:**
- Dataverse automatically generates the thumbnail regardless of `CanStoreFullImage`
- Image columns add slight overhead to queries when `$select` includes the image column
- For best performance, avoid selecting image columns in list views (use `$select` to exclude them)
- Image columns cannot be used in calculated fields, rollups, or duplicate detection

## Lookup @odata.bind: Navigation Property Naming

When creating records with lookup references, the `@odata.bind` property name must use the
**column logical name** (always lowercase), NOT the SchemaName (PascalCase).

```json
// CORRECT — lowercase navigation property
{ "pic_player@odata.bind": "/pic_playerprofiles(guid)" }

// WRONG — PascalCase causes silent 400 error
{ "pic_Player@odata.bind": "/pic_playerprofiles(guid)" }
```

**How to find the correct name:** Query the relationship metadata or use the column's logical
name directly. The navigation property name matches the lookup column's logical name.

## Primary Name Column Is Always Required on POST

Every Dataverse table has a primary name column. When creating records via POST, you MUST
include the primary name column or the request returns 400.

**The primary name is NOT always `prefix_name`.** Each table has its own:
- `pic_modename` for game modes
- `pic_levelname` for difficulty levels
- `pic_highscorename` for high scores

**Best practice:** Query `EntityDefinitions(LogicalName='...')/Attributes?$filter=IsPrimaryName eq true&$select=LogicalName`
to discover the actual primary name column before seeding data.

## Picklist Values May Differ From Requested

When creating global option sets, Dataverse may auto-assign different numeric values than
requested. Using assumed values (e.g., `689020000`) causes silent 400 errors.

**Best practice:** After creating an option set, query back the actual values:
```http
GET /GlobalOptionSetDefinitions(Name='prefix_optionsetname')?$select=Options
```
Then use the actual `Value` fields returned by the API
