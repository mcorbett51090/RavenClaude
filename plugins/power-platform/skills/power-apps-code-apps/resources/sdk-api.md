# Power Apps Code Apps SDK API Reference

Package: `@microsoft/power-apps` v1.0.3
Install: `npm install @microsoft/power-apps`

## BREAKING CHANGE: `initialize()` Removed in v1.0

The `initialize()` function was **completely removed** in SDK v1.0.
Data calls and context retrieval can be made immediately without waiting for initialization.
Any code calling `initialize()` is outdated.

## Module Exports (Sub-path Imports)

```typescript
import { getContext, setConfig } from "@microsoft/power-apps/app";
import { /* data types */ } from "@microsoft/power-apps/data";
import { /* telemetry types */ } from "@microsoft/power-apps/telemetry";
import { /* metadata */ } from "@microsoft/power-apps/data/metadata/dataverse";
import { /* executors */ } from "@microsoft/power-apps/data/executors";
```

## App Module -- `@microsoft/power-apps/app`

### `getContext(): Promise<IContext>`

Returns the application context. Available immediately (no initialization needed).
**Returns a Promise -- use `await`.**

```typescript
interface IContext {
  app: IAppContext;
  user: IUserContext;
  host: IHostContext;
}

interface IAppContext {
  appId: string;           // Unique app identifier
  environmentId: string;   // Power Platform environment ID
  queryParams: Record<string, string>; // URL query parameters
}

interface IUserContext {
  fullName: string;            // User's display name
  objectId: string;            // Entra ID object ID
  tenantId: string;            // Entra ID tenant ID
  userPrincipalName: string;   // UPN (e.g., user@contoso.com)
}

interface IHostContext {
  sessionId: string;   // Current session identifier
}
```

**Usage:**
```typescript
import { getContext } from "@microsoft/power-apps/app";

const ctx = await getContext();
console.log(`User: ${ctx.user.fullName}`);
console.log(`Environment: ${ctx.app.environmentId}`);
console.log(`Session: ${ctx.host.sessionId}`);
```

### `setConfig(config: IConfig): void`

Configures the SDK, primarily for telemetry forwarding.

```typescript
import type { IConfig } from "@microsoft/power-apps/app";
import type { ILogger } from "@microsoft/power-apps/telemetry";

interface IConfig {
  logger?: ILogger;
}

interface ILogger {
  logMetric?: (value: Metric) => void;
}
```

**Usage with Application Insights:**
```typescript
import { setConfig } from "@microsoft/power-apps/app";

setConfig({
  logger: {
    logMetric: (value) => {
      appInsights.trackEvent(
        { name: value.type },
        value.data
      );
    },
  },
});
```

**Built-in Metric types forwarded:**

```typescript
type SessionLoadSummaryMetricData = {
  successfulAppLaunch: boolean;
  appLoadResult: 'optimal' | 'other';
  appLoadNonOptimalReason: 'interactionRequired' | 'throttled' | 'screenNavigatedAway' | 'other';
  timeToAppInteractive: number;
};

type NetworkRequestMetricData = {
  url: string;
  method: string;
  duration: number;
  statusCode: number;
  responseSize: number;
};
```

## Generated Services Pattern

When you run `pac code add-data-source`, the CLI generates typed files:

```
generated/
  services/
    ContactService.ts
    AccountService.ts
  models/
    ContactModel.ts
    AccountModel.ts
```

### Tabular Service Methods

All tabular (table-based) data sources expose these methods:

```typescript
// Create a new record
async create(record: Partial<ContactModel>): Promise<ContactModel>

// Get a single record by ID
async get(id: string): Promise<ContactModel>

// Get multiple records with query options
async getAll(options?: IGetAllOptions): Promise<ContactModel[]>

// Update an existing record
async update(id: string, record: Partial<ContactModel>): Promise<void>

// Delete a record
async delete(id: string): Promise<void>
```

### Dataverse Service Methods (Additional)

Dataverse-connected services expose all tabular methods PLUS:

```typescript
async getMetadata(options?: GetEntityMetadataOptions): Promise<IOperationResult<Partial<EntityMetadata>>>
```

```typescript
interface GetEntityMetadataOptions {
  metadata?: string[];       // Entity-level props (e.g., ["Privileges","DisplayName","IsCustomizable"])
  schema?: {
    columns?: "all" | string[];   // "all" or array of column logical names
    oneToMany?: boolean;          // Include one-to-many relationship metadata
    manyToOne?: boolean;          // Include many-to-one (lookup) metadata
    manyToMany?: boolean;         // Include many-to-many relationship metadata
  };
}
```

**Response includes:** `Attributes` (AttributeMetadata[]), `OneToManyRelationships`,
`ManyToOneRelationships`, `ManyToManyRelationships`.

### IGetAllOptions Interface

```typescript
interface IGetAllOptions {
  maxPageSize?: number;   // Records per page (server-side pagination)
  select?: string[];      // Column projection (e.g., ["fullname", "email"])
  filter?: string;        // OData $filter expression
  orderBy?: string[];     // OData $orderby (e.g., ["fullname asc", "createdon desc"])
  top?: number;           // Limit total records returned
  skip?: number;          // Skip N records (offset pagination)
  skipToken?: string;     // Server-side continuation token
}
```

### IOperationResult&lt;T&gt; Interface

Service methods return `IOperationResult<T>`:

```typescript
interface IOperationResult<T> {
  success: boolean;           // Whether the operation succeeded
  data: T;                    // The result data (record or array)
  error: Error | undefined;   // Error details if success is false
  skipToken: string | undefined;  // Continuation token for pagination
  count: number | undefined;      // Total record count (if requested)
}
```

**Usage with getAll():**
```typescript
const result = await ContactService.getAll({
  select: ["fullname", "emailaddress1"],
  top: 10,
});

if (result.success) {
  const contacts = result.data; // ContactModel[]
  console.log(`Found ${result.count} contacts`);
} else {
  console.error("Query failed:", result.error);
}
```

### Data Access Examples

**Basic query:**
```typescript
import { ContactService } from "./generated/services/ContactService";

const allContacts = await ContactService.getAll();
```

**Filtered query with projection:**
```typescript
const smiths = await ContactService.getAll({
  select: ["fullname", "emailaddress1", "telephone1"],
  filter: "contains(fullname, 'Smith')",
  orderBy: "fullname asc",
  top: 25,
});
```

**Create a record:**
```typescript
const newContact = await ContactService.create({
  fullname: "Jane Doe",
  emailaddress1: "jane@contoso.com",
});
```

**Update a record:**
```typescript
await ContactService.update(contactId, {
  telephone1: "+1-555-0100",
});
```

**Delete a record:**
```typescript
await ContactService.delete(contactId);
```

**Get metadata:**
```typescript
const meta = await AccountsService.getMetadata({
  metadata: ["Privileges", "DisplayName"],
  schema: {
    columns: ["fullname", "emailaddress1"],
    manyToOne: true,
  },
});
```

**Create with type safety (Dataverse):**
```typescript
const result = await AccountsService.create(
  newAccount as Omit<Accounts, 'accountid'>
);
```

### Formatted Values vs Raw Values

**CRITICAL:** Formatted (display) values are NOT OData columns and cannot be used in `select`.

| Field Type | Display Value (NOT queryable) | Raw Value (queryable) |
|---|---|---|
| Lookup | `pic_playername` (display name) | `_pic_player_value` (GUID) |
| Choice | `pic_difficultyname` (label text) | `pic_difficulty` (integer value) |
| DateTime | `createdon@OData.Community.Display.V1.FormattedValue` | `createdon` (ISO string) |

**Wrong — causes OData error:**
```typescript
const scores = await GameScoreService.getAll({
  select: ["pic_score", "pic_playername"], // ERROR: pic_playername is not a column
});
```

**Right:**
```typescript
const scores = await GameScoreService.getAll({
  select: ["pic_score", "_pic_player_value"], // GUID of the related player
});
```

For display names, resolve after the query by fetching the related record, or use Dataverse's
`$expand` equivalent if available.

### Type Casting for Model Fields

**All generated model fields are typed as `string`**, regardless of the actual Dataverse column type.
You must explicitly cast numeric fields.

**Wrong — string comparison:**
```typescript
// "9" > "10" evaluates to true (string comparison)!
if (record.pic_score > record.pic_highscore) { ... }
```

**Right — numeric casting:**
```typescript
if (Number(record.pic_score) > Number(record.pic_highscore)) { ... }
```

Always use `Number()` when:
- Comparing numeric values
- Performing arithmetic
- Passing to APIs that expect numbers

### TypeScript verbatimModuleSyntax

When `tsconfig.json` has `"verbatimModuleSyntax": true` (common in modern configs),
you must use `import type` for type-only imports:

**Wrong:**
```typescript
import { IGetAllOptions } from "@microsoft/power-apps/data"; // Error with verbatimModuleSyntax
```

**Right:**
```typescript
import type { IGetAllOptions } from "@microsoft/power-apps/data";
import type { IContext } from "@microsoft/power-apps/app";
```

Rule of thumb: if you're only using the import for type annotations (not runtime values),
use `import type`.

## Non-Tabular Service Pattern (e.g., Office 365 Users)

Non-tabular connectors generate service methods that match the connector's API actions:

```typescript
import { Office365UsersService } from './generated/services/Office365UsersService';
import type { User } from './generated/models/Office365UsersModel';

// Get current user's profile
const me = await Office365UsersService.MyProfile_V2("id,displayName,jobTitle,userPrincipalName");

// Get a specific user's photo
const photo = await Office365UsersService.UserPhoto_V2(userId);
```

Each connector generates different method names matching its available actions.
Check the generated service file for available methods.

## OData Filter Syntax (Code Apps use OData, NOT FetchXML)

| Operation | Syntax | Example |
|-----------|--------|---------|
| Equals | `eq` | `"status eq 'Active'"` |
| Not equals | `ne` | `"status ne 'Inactive'"` |
| Greater than | `gt` | `"revenue gt 1000000"` |
| Less than | `lt` | `"age lt 30"` |
| Greater or equal | `ge` | `"createdon ge 2024-01-01"` |
| Less or equal | `le` | `"modifiedon le 2024-12-31"` |
| And | `and` | `"status eq 'Active' and revenue gt 100"` |
| Or | `or` | `"city eq 'Seattle' or city eq 'Portland'"` |
| Contains | `contains()` | `"contains(fullname, 'Smith')"` |
| Starts with | `startswith()` | `"startswith(name, 'A')"` |
| Ends with | `endswith()` | `"endswith(email, '@contoso.com')"` |
| Not | `not` | `"not contains(name, 'test')"` |

## Vite Plugin Configuration

```typescript
// vite.config.ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { powerApps } from "@microsoft/power-apps-vite/plugin";

export default defineConfig({
  plugins: [react(), powerApps()],
});
```

The `@microsoft/power-apps-vite` (^1.0.2) plugin:
- Configures the build output for Power Platform compatibility
- Manages the bridge between local dev server and the Power Apps host
- Must be listed AFTER framework plugins (e.g., react())

## Key Dependencies (Internal)

The SDK internally depends on:
- `@pa-client/powerapps-player-services`
- `@microsoft/powerapps-player-actions`
- `@microsoft/powerapps-data`

These are NOT public APIs. Do not import from them directly.

## Anti-Patterns to Avoid

| Wrong (Do NOT do this) | Right (Do this instead) |
|------------------------|------------------------|
| `import { initialize } from "@microsoft/power-apps"` | Removed. Just call APIs directly. |
| `context.webAPI.retrieveMultipleRecords()` | `ContactService.getAll()` |
| `Xrm.WebApi.retrieveRecord()` | `ContactService.get(id)` |
| `fetch("/api/data/v9.2/contacts")` | `ContactService.getAll()` |
| `import { PublicClientApplication } from "@azure/msal-browser"` | Auth is handled by the host. |
| Using FetchXML | Use OData $filter syntax |
| `context.parameters.myField` | Use `getContext()` for app context |
| Using formatted values in `select` | Use raw fields: `_field_value` for lookups, `field` for choices |
| Treating model fields as numbers | Cast with `Number(record.field)` for numeric operations |
| Creating placeholder columns | Use formula columns, plugins, or code-based computation |
| Configuring rollup fields in Maker Portal | Use code-based aggregation or plugins instead |
| `import { Type }` with verbatimModuleSyntax | Use `import type { Type }` for type-only imports |
