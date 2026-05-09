# Advanced Column Types

Specialized column types that go beyond basic string/number/choice fields. Each requires
specific metadata properties and has unique behaviors.

## Rich Text (Memo)

A multi-line text column that supports HTML formatting (bold, italic, lists, links, images).

**Important distinction:**
- `Format: "Text"` is the default for memo columns (plain multi-line text)
- `FormatName: "RichText"` enables the rich text editor -- you must set `FormatName`, not `Format`

```http
POST [org-url]/api/data/v9.2/EntityDefinitions(LogicalName='cnt_project')/Attributes
MSCRM.SolutionUniqueName: ContosoHRModule

{
  "@odata.type": "Microsoft.Dynamics.CRM.MemoAttributeMetadata",
  "SchemaName": "cnt_DetailedDescription",
  "DisplayName": {
    "@odata.type": "Microsoft.Dynamics.CRM.Label",
    "LocalizedLabels": [{ "Label": "Detailed Description", "LanguageCode": 1033 }]
  },
  "RequiredLevel": { "Value": "None" },
  "MaxLength": 1048576,
  "Format": "Text",
  "FormatName": { "Value": "RichText" }
}
```

**Max length considerations:**
- Default memo: `MaxLength` up to 1,048,576 characters
- Rich text stores HTML markup, so the effective text capacity is lower than the character limit
- Images embedded in rich text are stored as base64, consuming significant character space
- Recommended: set `MaxLength` to 1048576 (max) for rich text to avoid truncation

**Form binding:** Use the standard Memo control ClassId `{E7A81278-8635-4D9E-8D4D-59480B391C5B}`
on the form. The rich text editor renders automatically when `FormatName` is `RichText`.
For more advanced rich text configuration, bind the `RichTextEditorControl` explicitly
(see `resources/forms-ui.md` for control binding details).

## Address Composite

Dataverse does not have a single "Address" column type. Address data is composed of
individual columns bound together with the Address Input Control on forms.

### Step 1: Create Individual Address Columns

```http
POST [org-url]/api/data/v9.2/EntityDefinitions(LogicalName='cnt_project')/Attributes
MSCRM.SolutionUniqueName: ContosoHRModule

{
  "@odata.type": "Microsoft.Dynamics.CRM.StringAttributeMetadata",
  "SchemaName": "cnt_Street",
  "DisplayName": { "@odata.type": "Microsoft.Dynamics.CRM.Label", "LocalizedLabels": [{ "Label": "Street", "LanguageCode": 1033 }] },
  "RequiredLevel": { "Value": "None" },
  "MaxLength": 500,
  "FormatName": { "Value": "Text" }
}
```

Create separate columns for: `Street`, `City`, `State`, `PostalCode`, `Country`.
Optionally: `Latitude` (Double), `Longitude` (Double).

### Step 2: Bind with Address Input Control on Form

The Address Input Control (`Microsoft.AddressInputUCI`) provides a unified address entry
experience with autocomplete. Bind it via the `controlDescriptions` pattern in FormXml:

```xml
<cell id="{CELL-GUID}">
  <labels><label description="Address" languagecode="1033" /></labels>
  <control id="cnt_street" classid="{4273EDBD-AC1D-40D3-9FB2-095C621B552D}" datafieldname="cnt_street">
    <controlDescription forControl="cnt_street">
      <customControl name="Microsoft.AddressInputUCI" formFactor="2">
        <parameters>
          <Street type="SingleLine.Text">cnt_street</Street>
          <City type="SingleLine.Text">cnt_city</City>
          <State type="SingleLine.Text">cnt_state</State>
          <ZipPostal type="SingleLine.Text">cnt_postalcode</ZipPostal>
          <Country type="SingleLine.Text">cnt_country</Country>
        </parameters>
      </customControl>
    </controlDescription>
  </control>
</cell>
```

**Notes:**
- The primary `datafieldname` is typically the street column
- All address sub-columns must exist before creating the form
- The control provides Bing Maps autocomplete when configured in the environment settings

## File Column

Stores file attachments (any file type) up to the configured size limit.

```http
POST [org-url]/api/data/v9.2/EntityDefinitions(LogicalName='cnt_project')/Attributes
MSCRM.SolutionUniqueName: ContosoHRModule

{
  "@odata.type": "Microsoft.Dynamics.CRM.FileAttributeMetadata",
  "SchemaName": "cnt_ProjectDocument",
  "DisplayName": {
    "@odata.type": "Microsoft.Dynamics.CRM.Label",
    "LocalizedLabels": [{ "Label": "Project Document", "LanguageCode": 1033 }]
  },
  "MaxSizeInKB": 131072
}
```

**Key behaviors:**
- `MaxSizeInKB`: maximum file size in kilobytes (max: 131072 = 128 MB)
- No inline preview on forms -- users see a download link
- Files are stored in Azure Blob Storage (managed by Dataverse)
- No `RequiredLevel` support -- file columns cannot be made required

**Upload via API:**

```http
PATCH [org-url]/api/data/v9.2/cnt_projects({record-id})/cnt_projectdocument
Content-Type: application/octet-stream
x-ms-file-name: report.pdf

<binary file content>
```

**Download via API:**

```http
GET [org-url]/api/data/v9.2/cnt_projects({record-id})/cnt_projectdocument/$value
```

**Chunked upload for large files (>16 MB):**

Use the `InitializeFileBlocksUpload`, `UploadBlock`, and `CommitFileBlocksUpload` actions
for files exceeding 16 MB. Each chunk should be 4 MB.

## Image Column

Stores image files with automatic thumbnail generation.

```http
POST [org-url]/api/data/v9.2/EntityDefinitions(LogicalName='cnt_project')/Attributes
MSCRM.SolutionUniqueName: ContosoHRModule

{
  "@odata.type": "Microsoft.Dynamics.CRM.ImageAttributeMetadata",
  "SchemaName": "cnt_ProjectLogo",
  "DisplayName": {
    "@odata.type": "Microsoft.Dynamics.CRM.Label",
    "LocalizedLabels": [{ "Label": "Project Logo", "LanguageCode": 1033 }]
  },
  "IsPrimaryImage": false,
  "CanStoreFullImage": true,
  "MaxSizeInKB": 10240
}
```

**Key properties:**

| Property | Description |
|---|---|
| `IsPrimaryImage` | When `true`, the image displays as the record avatar in headers and grids |
| `CanStoreFullImage` | When `true`, stores the original file. When `false`, only stores a 144x144 thumbnail |
| `MaxSizeInKB` | Maximum image size in kilobytes (max: 30720 = 30 MB) |

**Notes:**
- Only one column per table can be `IsPrimaryImage: true`
- Dataverse always generates a thumbnail regardless of `CanStoreFullImage`
- Supported formats: PNG, JPG, GIF, BMP
- The thumbnail is stored as `entityimage` and the full image as `entityimage_url`

**Upload via API:**

```http
PATCH [org-url]/api/data/v9.2/cnt_projects({record-id})/cnt_projectlogo
Content-Type: application/octet-stream

<binary image content>
```

## Auto-Number

A string column that auto-generates formatted sequential or random identifiers.
Useful for invoice numbers, ticket IDs, case references.

```http
POST [org-url]/api/data/v9.2/EntityDefinitions(LogicalName='cnt_project')/Attributes
MSCRM.SolutionUniqueName: ContosoHRModule

{
  "@odata.type": "Microsoft.Dynamics.CRM.StringAttributeMetadata",
  "SchemaName": "cnt_ProjectNumber",
  "DisplayName": {
    "@odata.type": "Microsoft.Dynamics.CRM.Label",
    "LocalizedLabels": [{ "Label": "Project Number", "LanguageCode": 1033 }]
  },
  "RequiredLevel": { "Value": "None" },
  "MaxLength": 100,
  "AutoNumberFormat": "PRJ-{SEQNUM:5}-{DATETIMEUTC:yyyyMMdd}"
}
```

### Format Tokens

| Token | Description | Example Output |
|---|---|---|
| `{SEQNUM:n}` | Sequential number, zero-padded to `n` digits | `{SEQNUM:5}` -> `00001` |
| `{RANDSTRING:n}` | Random alphanumeric string of length `n` | `{RANDSTRING:4}` -> `A7B2` |
| `{DATETIMEUTC:format}` | Current UTC datetime in .NET format | `{DATETIMEUTC:yyyyMMdd}` -> `20250115` |

**Example formats:**
- Invoice: `"INV-{SEQNUM:5}"` -> `INV-00001`, `INV-00002`
- Ticket: `"TKT-{DATETIMEUTC:yyyyMM}-{SEQNUM:4}"` -> `TKT-202501-0001`
- Case: `"CASE-{RANDSTRING:6}"` -> `CASE-X8K2M4`
- Mixed: `"PRJ-{SEQNUM:5}-{DATETIMEUTC:yyyyMMdd}"` -> `PRJ-00001-20250115`

**Seed value:** The sequence starts at 1000 by default. To change the seed:

```http
POST [org-url]/api/data/v9.2/SetAutoNumberSeed
{
  "EntityName": "cnt_project",
  "AttributeName": "cnt_projectnumber",
  "Value": 5000
}
```

**Notes:**
- Auto-number is read-only after creation -- users cannot manually edit the value
- The sequence is gap-free only within a single environment (imports/deletes create gaps)
- `SEQNUM` is globally unique per column, not per record type
- Auto-number columns can be the primary name column

## Multi-Select Option Set

Allows users to select multiple values from a predefined list.

```http
POST [org-url]/api/data/v9.2/EntityDefinitions(LogicalName='cnt_project')/Attributes
MSCRM.SolutionUniqueName: ContosoHRModule

{
  "@odata.type": "Microsoft.Dynamics.CRM.MultiSelectPicklistAttributeMetadata",
  "SchemaName": "cnt_ProjectTags",
  "DisplayName": {
    "@odata.type": "Microsoft.Dynamics.CRM.Label",
    "LocalizedLabels": [{ "Label": "Project Tags", "LanguageCode": 1033 }]
  },
  "RequiredLevel": { "Value": "None" },
  "OptionSet": {
    "@odata.type": "Microsoft.Dynamics.CRM.OptionSetMetadata",
    "IsGlobal": false,
    "OptionSetType": "Picklist",
    "Options": [
      { "Value": 100000000, "Label": { "@odata.type": "Microsoft.Dynamics.CRM.Label", "LocalizedLabels": [{ "Label": "High Priority", "LanguageCode": 1033 }] } },
      { "Value": 100000001, "Label": { "@odata.type": "Microsoft.Dynamics.CRM.Label", "LocalizedLabels": [{ "Label": "Customer Facing", "LanguageCode": 1033 }] } },
      { "Value": 100000002, "Label": { "@odata.type": "Microsoft.Dynamics.CRM.Label", "LocalizedLabels": [{ "Label": "Internal", "LanguageCode": 1033 }] } },
      { "Value": 100000003, "Label": { "@odata.type": "Microsoft.Dynamics.CRM.Label", "LocalizedLabels": [{ "Label": "Archived", "LanguageCode": 1033 }] } }
    ]
  }
}
```

**Storage:** Values are stored internally as comma-separated integers (e.g., `"100000000,100000002"`).

**Setting values via API:**

```json
{
  "cnt_projecttags": "100000000,100000002"
}
```

**Querying (OData filter):**

```
$filter=Microsoft.Dynamics.CRM.ContainValues(PropertyName='cnt_projecttags',PropertyValues=['100000000'])
```

Use `ContainValues` or `DoesNotContainValues` OData functions for multi-select filtering.

**Limitations:**
- Cannot be used in calculated or rollup fields
- Cannot be used as a condition in classic workflows (use Power Automate instead)
- Limited support in business rules
- Maximum of 150 options per multi-select column

## Currency (Money)

Stores monetary values with currency-aware precision and exchange rate support.

```http
POST [org-url]/api/data/v9.2/EntityDefinitions(LogicalName='cnt_project')/Attributes
MSCRM.SolutionUniqueName: ContosoHRModule

{
  "@odata.type": "Microsoft.Dynamics.CRM.MoneyAttributeMetadata",
  "SchemaName": "cnt_ProjectBudget",
  "DisplayName": {
    "@odata.type": "Microsoft.Dynamics.CRM.Label",
    "LocalizedLabels": [{ "Label": "Project Budget", "LanguageCode": 1033 }]
  },
  "RequiredLevel": { "Value": "None" },
  "PrecisionSource": 2,
  "MinValue": 0,
  "MaxValue": 1000000000
}
```

### PrecisionSource Values

| Value | Source | Description |
|---|---|---|
| `0` | Attribute | Uses the `Precision` property on this column (0-4 decimal places) |
| `1` | Organization | Uses the org-level currency precision setting |
| `2` | Pricing | Uses the pricing decimal precision (most common for financial data) |

### Exchange Rate Behavior

When you create a Money column, Dataverse automatically creates:
- A hidden `_Base` column (e.g., `cnt_projectbudget_base`) that stores the value in the org's base currency
- Conversion uses the exchange rate from the `transactioncurrency` table

**Transaction vs Base currency:**
- Transaction currency: the currency selected on the record (e.g., EUR)
- Base currency: the org's default currency (e.g., USD)
- The `_Base` column = transaction value * exchange rate

**Setting currency on a record:**

```json
{
  "cnt_projectbudget": 50000.00,
  "transactioncurrencyid@odata.bind": "/transactioncurrencies({currency-guid})"
}
```

If no currency is specified, the record uses the user's default currency.

## Column Type Quick Reference

| Column Type | OData Type | Key Properties |
|---|---|---|
| Rich Text | `MemoAttributeMetadata` | `FormatName: "RichText"`, `MaxLength` |
| Address | Multiple `StringAttributeMetadata` | Individual columns + Address Input Control |
| File | `FileAttributeMetadata` | `MaxSizeInKB` |
| Image | `ImageAttributeMetadata` | `IsPrimaryImage`, `CanStoreFullImage`, `MaxSizeInKB` |
| Auto-Number | `StringAttributeMetadata` | `AutoNumberFormat` |
| Multi-Select | `MultiSelectPicklistAttributeMetadata` | `OptionSet` with `Options` array |
| Currency | `MoneyAttributeMetadata` | `PrecisionSource`, `MinValue`, `MaxValue` |
