# Dataverse Design Rules: Permanent Decisions and Critical Gotchas

This resource covers irreversible design decisions, common pitfalls, data migration traps,
and performance optimization. Read this BEFORE designing any Dataverse schema.

## Permanent Design Decisions (Cannot Be Changed After Creation)

These decisions are locked in once you save. Plan carefully.

### 1. Column Data Type

- **Cannot be changed after saving**, with one exception: Text can be converted to Auto Number
- If you create a Whole Number column and later need Decimal, you must create a new column,
  migrate data, update all references, and delete the old column
- Plan data types carefully during design — refer to `columns-attributes.md` for all types

### 2. Table Logical Name

- The logical name (e.g., `cnt_project`) is **permanent**
- The display name ("Project") CAN be changed at any time
- The logical name is used in ALL code references: plugins, JavaScript, Power Automate, Web API URLs
- Choose logical names carefully — you will live with them forever

### 3. Ownership Type

- **Cannot change** between "Organization-owned" and "User or Team-owned" after creation
- Organization-owned: All records belong to the org; no per-user security scoping
- User/Team-owned: Records have owners; security roles scope by User/BU/Org
- If you need record-level security (most apps do), you MUST choose "User or Team" at creation
- See `security-model.md` for how ownership type affects the security model

### 4. File Attachments

- Must be enabled at table creation time via `HasNotes: true` and/or `HasActivities: true`
- **Cannot enable file attachment support after the table is created**
- If you might need file attachments, enable Notes during creation even if not immediately needed

### 5. File Attachments Are MDA-Only

- Canvas apps **cannot access file attachment columns** (File or Image data type)
- If your app will have a Canvas App interface, store files in SharePoint or use Notes (annotations)
- Model-Driven Apps handle file/image columns natively

## Key Constraint Gotchas

### Alternate Keys on Existing Duplicates

- If you create an alternate key on a column that already has duplicate values in existing records,
  Dataverse creates the key definition but **does NOT enforce uniqueness**
- There is **no indication in the designer** that the key is inactive/failed
- The key silently fails validation and does not prevent future duplicates
- **Always check**: Query for duplicates before creating alternate keys on populated tables:
  ```
  GET /cnt_projects?$select=cnt_code&$filter=cnt_code ne null
  // Then check for duplicates in the results
  ```

### Choice (Option Set) Items

#### Deletion Does Not Validate Usage
- Dataverse does **NOT prevent deleting choice items** that are currently in use on records
- Records with the deleted choice value display the **raw numeric ID** instead of the label text
- Always query for records using a choice value before deleting it

#### Choices Cannot Be Sorted
- There is **no way to sort** items in a choice dropdown — they appear in creation order
- If sorted display is important, use a **Lookup column to a custom table** instead
- Custom tables can have views with sorted data

#### Users Cannot Add Choice Items at Runtime
- Choice items can only be added through the Maker Portal or API
- If users need to add/manage options themselves, use a **Lookup to a custom table** instead

### When to Use Lookup Instead of Choice
- Options change frequently
- The list is very long (50+ items)
- Users need to add/update options within the app
- Sorted display is required
- Additional attributes are needed per option (description, category, etc.)

## Data Import and Migration

### Auto-Mapping is Unreliable

- When importing data from Excel, the auto-mapping feature frequently maps columns incorrectly
- **Always verify every column mapping manually** before starting an import
- Column header names in Excel should match display names exactly to improve auto-mapping accuracy
- Test imports with a small subset first

### Never Recreate Master Data Manually

- Do NOT manually recreate reference/master data in target environments
- Manual creation generates **new GUIDs**, which breaks all code references,
  relationships, and lookups that used the original GUIDs
- Use the **Configuration Migration Tool** (included in Power Platform tools) to migrate data
  between environments while preserving GUIDs

### Solution Export/Import Does NOT Include Data

- Solutions contain only schema definitions (tables, columns, views, forms, etc.)
- Record data is NOT included in solution packages
- Use Configuration Migration Tool or Data Import Wizard for data
- Reference data (configuration records, master data) must be migrated separately

## Solution Import Options (Critical Distinction)

Understanding the three import options prevents data loss and unexpected behavior.

### Upgrade (Overwrite Customizations)

- **Adds** new components
- **Updates** existing components
- **Deletes** components that are NOT in the new solution version
- This is a full replacement — anything removed from the solution gets removed from the target
- Use for clean production deployments when you want exact parity with source

### Stage for Upgrade

- Creates a **holding solution** alongside the existing version
- Both old and new versions coexist temporarily
- Allows you to **migrate data** from components that will be deleted before applying the upgrade
- Use when deleting tables or columns that contain data in the target environment
- After data migration, apply the upgrade to complete the process

### Update (Additive Only)

- **Adds** new components
- **Updates** existing components
- Does **NOT delete** anything — components removed from the solution remain in the target
- Source and destination may diverge over time as removed components accumulate
- Use for incremental patches where you do not want to remove anything

## Performance Optimization

### Storage and Data Architecture

- **Store files/attachments in SharePoint or Azure Blob Storage**, not Dataverse
  - Dataverse file storage is expensive and has size limits
  - Use SharePoint integration for document management
  - Use Azure Blob Storage for large binary files

- **Move infrequently-used data to Azure SQL or Data Lake**
  - Logging, auditing, and historical data consume storage
  - Use Synapse Link for Dataverse to replicate to Data Lake
  - Query historical data from Azure SQL instead of Dataverse

- **Delete audit logs and system jobs periodically**
  - System Jobs (`asyncoperations`) accumulate and slow queries
  - Audit logs grow unbounded — configure retention policies
  - Use bulk delete jobs on a schedule

- **Use Dataverse long-term data retention** for old records
  - Moves records to cheaper storage while keeping them queryable
  - Reduces active table size and improves query performance

### Solution Size

- Solution ZIP file size limit is **32 MB**
- If approaching the limit, split into multiple solutions
- Large web resources (images, scripts) consume most of the space
- Compress images before adding as web resources

## Column Design Tips

These common mistakes cause issues that are hard to fix later (remember: data types are permanent).

### Postcodes / ZIP Codes

- Use **Text** (StringAttributeMetadata), NOT Whole Number
- Many countries have letters in postcodes (UK: "SW1A 1AA", Canada: "K1A 0B1")
- Leading zeros are lost with number types (US: "01234" becomes 1234)
- Max length of 20 characters covers all international formats

### Street Addresses

- Set max length to **255+ characters**
- Default max length (100) is too short for many international addresses
- Include apartment/suite numbers, building names, etc.
- Consider separate columns for address components if structured data is needed

### Latitude / Longitude

- Use **Decimal Number** (DecimalAttributeMetadata) with **5+ decimal places**
- 4 decimal places = ~11 meter accuracy
- 5 decimal places = ~1.1 meter accuracy
- 6 decimal places = ~0.11 meter accuracy (sub-meter)
- Do NOT use Float — floating-point precision errors affect coordinate calculations

### Duration

- Use the **Number | Duration** data type
- Stores duration in minutes internally
- Displays in human-readable format (e.g., "2 hours 30 minutes")
- Do NOT use plain Whole Number — you lose the built-in formatting

### Money / Currency

- Always use the **Currency** data type (MoneyAttributeMetadata) for monetary values
- Auto-formats with currency symbols based on user settings
- Handles exchange rates via the Currency table
- Creates a companion `_base` column automatically for base currency conversion
- Do NOT use Decimal for money — you lose formatting and exchange rate support

### Phone Numbers

- Use **Text**, NOT Number
- Phone numbers have leading zeros, plus signs, parentheses, spaces
- International format: "+44 (0) 20 7946 0958"
- Max length of 30 characters covers all international formats with extensions

### Email Addresses

- Use **Text** with max length of **320 characters**
- The RFC 5321 maximum is 254 characters for the full address
- 320 gives headroom for edge cases
- Consider using the built-in Email format type for validation

## Common Anti-Patterns to Avoid

1. **Creating tables as Organization-owned "because it's simpler"** — then discovering
   you need per-user security later (ownership type cannot be changed)

2. **Using Whole Number for codes/identifiers** — losing leading zeros and
   preventing alphanumeric values later

3. **Skipping Notes/Activities at creation** — then needing file attachments later
   and being unable to enable them

4. **Creating alternate keys before data cleanup** — resulting in silently failed keys
   that do not enforce uniqueness

5. **Using Choice columns for growing lists** — then users cannot add new options
   without a maker/admin

6. **Storing config in XML web resources** — use environment variables instead
   (see `environment-variables.md`)

7. **Using Float for coordinates or financial values** — floating-point precision
   errors cause subtle bugs over time
