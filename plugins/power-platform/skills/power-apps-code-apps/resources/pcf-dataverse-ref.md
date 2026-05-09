# PCF & Dataverse Query Reference (Supplementary)

This is supplementary reference for understanding Dataverse data structures and
OData query patterns. Code Apps use generated services (NOT the PCF WebApi), but
the underlying Dataverse query syntax is similar.

## IMPORTANT: Code Apps vs PCF

| Use in Code Apps | Do NOT use in Code Apps |
|-----------------|------------------------|
| `ContactService.getAll({ filter: "..." })` | `context.webAPI.retrieveMultipleRecords()` |
| `ContactService.get(id)` | `context.webAPI.retrieveRecord()` |
| `ContactService.create(data)` | `context.webAPI.createRecord()` |
| `ContactService.update(id, data)` | `context.webAPI.updateRecord()` |
| `ContactService.delete(id)` | `context.webAPI.deleteRecord()` |

The information below describes Dataverse patterns for reference when building
complex queries in Code App services.

## OData Query Options

### $select -- Column Projection
```
select: ["fullname", "emailaddress1", "telephone1"]
```
Only fetches specified columns. Reduces payload size.

### $filter -- Filtering
```
filter: "statecode eq 0 and contains(fullname, 'Smith')"
```

**Comparison operators:**
- `eq` (equals), `ne` (not equals)
- `gt` (greater than), `ge` (greater or equal)
- `lt` (less than), `le` (less or equal)

**Logical operators:**
- `and`, `or`, `not`

**String functions:**
- `contains(field, 'value')`
- `startswith(field, 'value')`
- `endswith(field, 'value')`

**Date functions:**
- `year(field)`, `month(field)`, `day(field)`

**Null checks:**
- `field eq null`, `field ne null`

### $orderby -- Sorting
```
orderBy: "fullname asc"
orderBy: "createdon desc, fullname asc"
```

### $top and $skip -- Pagination
```
top: 50        // Return max 50 records
skip: 100      // Skip first 100 records
```

### $expand -- Related Records
```
// Note: Check if supported in Code Apps generated services
// expand may be handled differently than in raw OData
```

## Common Dataverse Entity Patterns

### Standard Columns (most entities have these)
- `statecode` -- Record state (0=Active, 1=Inactive)
- `statuscode` -- Status reason (varies by entity)
- `createdon` -- DateTime of creation
- `modifiedon` -- DateTime of last modification
- `createdby` -- Lookup to creating user
- `modifiedby` -- Lookup to modifying user
- `ownerid` -- Lookup to owner (user or team)

### Contact Entity
- `fullname`, `firstname`, `lastname`
- `emailaddress1`, `emailaddress2`, `emailaddress3`
- `telephone1`, `telephone2`, `mobilephone`
- `address1_line1`, `address1_city`, `address1_stateorprovince`, `address1_postalcode`
- `jobtitle`, `department`
- `parentcustomerid` -- Lookup to Account

### Account Entity
- `name` -- Account name
- `emailaddress1`, `telephone1`, `websiteurl`
- `address1_line1`, `address1_city`, `address1_stateorprovince`
- `revenue`, `numberofemployees`
- `industrycode`, `accountcategorycode`
- `primarycontactid` -- Lookup to Contact

## PCF-Specific Interfaces (NOT for Code Apps, Reference Only)

These interfaces exist in PCF but are NOT available in Code Apps.
Listed here to prevent confusion.

### WebApi (PCF only)
```typescript
// DO NOT USE IN CODE APPS
context.webAPI.createRecord(entityLogicalName: string, data: object): Promise<LookupValue[]>
context.webAPI.retrieveRecord(entityLogicalName: string, id: string, options?: string): Promise<Entity>
context.webAPI.retrieveMultipleRecords(entityLogicalName: string, options?: string, maxPageSize?: number): Promise<RetrieveMultipleResponse>
context.webAPI.updateRecord(entityLogicalName: string, id: string, data: object): Promise<LookupValue[]>
context.webAPI.deleteRecord(entityLogicalName: string, id: string): Promise<LookupValue[]>
```

### DataSet (PCF only)
Properties: `columns`, `error`, `loading`, `records`, `sortedRecordIds`, `sorting`, `filtering`, `paging`, `linking`
Methods: `refresh()`, `getSelectedRecordIds()`, `setSelectedRecordIds()`, `clearSelectedRecordIds()`

### Paging (PCF only)
Properties: `hasNextPage`, `hasPreviousPage`, `pageSize`, `totalResultCount`
Methods: `loadNextPage()`, `loadPreviousPage()`, `loadExactPage()`, `reset()`, `setPageSize()`
Note: Paging methods cannot be called in parallel.

### FilterExpression (PCF only)
```typescript
interface FilterExpression {
  conditions: ConditionExpression[];
  filterOperator: 0 | 1;  // 0=And, 1=Or
  filters: FilterExpression[];  // Nested filters
}

interface ConditionExpression {
  attributeName: string;
  conditionOperator: number;  // Enum: Equal, NotEqual, GreaterThan, Contains, Like, In, Null, etc.
  entityAliasName?: string;
  value: any;
}
```

## Formatting Reference (from PCF, patterns reusable in Code Apps via Intl API)

Common formatting needs in Code Apps (use JavaScript Intl API instead of PCF formatting):

```typescript
// Currency
new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(1234.56)
// "US$1,234.56"

// Date
new Intl.DateTimeFormat('en-US', { dateStyle: 'medium' }).format(new Date())
// "Feb 8, 2026"

// Number
new Intl.NumberFormat('en-US').format(1234567)
// "1,234,567"
```
