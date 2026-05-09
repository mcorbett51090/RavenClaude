# Dataverse Web API Best Practices

## No Placeholder Columns

Never create empty columns intended to be "configured later in Maker Portal." This includes:
- Rollup fields (calculation rules can't be set via API)
- Calculated fields that need complex Maker Portal configuration

**Instead use:**
- **Formula columns** — For simple calculations (concatenation, date math, arithmetic). Set via `FormulaDefinition` property.
- **Plugins** — For server-side automation (auto-calculate on record create/update)
- **Code-based updates** — Query children, compute aggregates, update parent record

## No Rollup Fields

Rollup field configuration via the API is unreliable:
- The API can create the column definition, but the calculation rule must be configured in Maker Portal
- Rollup calculations run asynchronously (every 12 hours by default) — not real-time
- Manual recalculation requires the CalculateRollupField action

**Better alternatives:**
- Code-based aggregation: query child records, compute, update parent
- Plugin on child create/update that recalculates the parent aggregate
- Formula columns for same-record calculations

## Formula Columns

Use for simple, same-record calculations. See `formula-columns.md` for full reference.

When to use formula columns:
- String concatenation (e.g., full name from first + last)
- Date math (e.g., days until due date)
- Simple arithmetic on same-record fields
- Conditional display values

When NOT to use:
- Cross-record aggregations (SUM, COUNT, MAX across related records)
- Complex business logic with side effects
- Calculations requiring external data

## Idempotent Scripts

Always check if a resource exists before creating it. This allows safe re-runs after partial failures.

```powershell
# Pattern: GET first, create only if 404
try {
    $existing = Invoke-RestMethod -Uri "${baseUrl}/EntityDefinitions(LogicalName='$logicalName')" `
        -Headers $headers -Method GET
    Write-Host "Already exists, skipping."
} catch {
    if ($_.Exception.Response.StatusCode -eq 404) {
        # Create it
        Invoke-RestMethod -Uri "${baseUrl}/EntityDefinitions" `
            -Headers $headers -Method POST -Body ($payload | ConvertTo-Json -Depth 20)
    } else { throw }
}
```

## PowerShell on Windows

**Always use `.ps1` scripts for Dataverse API calls.** Never use bash/curl.

Why:
- Bash mangles OData `$` parameters (`$filter`, `$select`) even with escaping
- PowerShell handles `$` correctly with backtick: `` `$filter ``
- `Invoke-RestMethod` returns parsed JSON objects directly
- Error handling with try/catch works reliably

Run scripts: `powershell -ExecutionPolicy Bypass -File "script.ps1"`

### PowerShell Gotchas

- **Colon trap:** `"$var:"` is interpreted as a drive reference. Use `"${var}:"` syntax
- **Write-Host in functions:** Use `Write-Host` (not `Write-Output`) for debug display. `Write-Output` gets captured by variable assignment.
- **JSON depth:** Always use `-Depth 20` with `ConvertTo-Json` — default depth of 2 truncates nested objects

## Token Management

```powershell
# Get token via Azure CLI
$token = az account get-access-token `
    --resource "https://[org].crm6.dynamics.com/" `
    --tenant "[tenant-id]" `
    --query accessToken -o tsv

$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type"  = "application/json; charset=utf-8"
    "OData-Version" = "4.0"
    "MSCRM.SolutionUniqueName" = "MySolution"
}
```

- Tokens expire after ~1 hour
- If a call returns 401, get a fresh token and retry
- **Never use `pac auth token`** — this command does not exist

## Schema Naming Conventions

| Context | Convention | Example |
|---|---|---|
| API paths | Logical name (lowercase) | `EntityDefinitions(LogicalName='cnt_project')` |
| Schema definitions | PascalCase with prefix | `SchemaName = "cnt_Project"` |
| Attribute lookups | Lowercase | `Attributes(LogicalName='cnt_score')` |
| Display names | Human-readable | `"Project Name"` |

## Column Design

- **Choose the right type upfront** — changing column types after creation is destructive (requires delete + recreate)
- **Use appropriate max lengths** for strings (don't default to 4000 when 100 suffices)
- **Set RequiredLevel correctly** — `ApplicationRequired` vs `Recommended` vs `None`
- **Use GlobalOptionSets** for shared picklists across multiple tables

## Helper Function Library Pattern

Centralizing API calls in a `helpers.ps1` file reduces duplication and enforces consistency.
Each script dots-sources it: `. "$PSScriptRoot\helpers.ps1"`

Recommended helper functions:
- `Get-Token` — wraps `az account get-access-token`, returns fresh token
- `Get-Headers` — builds standard headers dict (Auth, Content-Type, OData-Version, Solution)
- `Ensure-Table` — checks if table exists before creating (idempotent)
- `Add-Column` — checks if column exists before creating (idempotent)
- `Add-GlobalChoiceColumn` — looks up MetadataId GUID, binds to global option set

This pattern supports safe re-runs after partial failures.

## Invoke-WebRequest vs Invoke-RestMethod for Debugging

- **`Invoke-WebRequest`** with `-UseBasicParsing` returns the raw response including error bodies
- **`Invoke-RestMethod`** often swallows error details, making debugging harder
- Use `Invoke-WebRequest` when debugging API issues, `Invoke-RestMethod` for production scripts

## Manual JSON for @odata.type Payloads

PowerShell's `ConvertTo-Json` can mangle `@odata.type` properties during serialization. For
payloads containing `@odata.type`, construct the JSON string manually:

```powershell
$json = '{"Components":[{"@odata.type":"Microsoft.Dynamics.CRM.entity","entityid":"' + $guid + '"}]}'
```

Always use `[System.Text.Encoding]::UTF8.GetBytes($json)` for the request body.

## Frontend-Backend Wiring Audit

After building UI components and service functions, ALWAYS verify end-to-end wiring:
- Every service function (e.g., `submitGameSession()`) must have at least one caller
- Every store action must be connected to UI
- Every feature (power-ups, achievements) must have gameplay logic, not just data models
- All catch blocks must have visible error handling (`console.error` at minimum, UI feedback ideally)
- Multi-step async flows should wrap each step independently so partial failures don't block everything

## Never Silently Swallow Errors

Never write catch blocks that return `null` or `[]` silently. This hides real issues:

```typescript
// BAD — silent failure
catch (e) { return null; }

// GOOD — log + return
catch (e) { console.error("[MyApp] operation failed:", e); return null; }

// BEST — log + user feedback
catch (e) { console.error("[MyApp] operation failed:", e); setError("Save failed"); return null; }
```

## Dataverse POST Returns 204 (No Body) by Default

A Dataverse POST that creates a record returns HTTP 204 No Content by default. This means
your `fetchApi` wrapper returns `null` — which is SUCCESS, not failure.

- Only an exception means the record was NOT created
- To get the created record back, add the `Prefer: return=representation` header
- Don't confuse `null` return with failure

## JSX Unicode Escape Sequences

In React/JSX, `\uXXXX` between tags renders as literal text, not the intended character.
Always use actual emoji/unicode characters in JSX source code:

```tsx
// BAD — renders as literal "\uD83C\uDFC6"
<span>\uD83C\uDFC6</span>

// GOOD — renders the trophy emoji
<span>🏆</span>
```
