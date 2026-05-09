# Web Resource Deployment via API

## Create a Web Resource

```http
POST [org-url]/api/data/v9.2/webresourceset
MSCRM.SolutionUniqueName: ContosoHRModule
Content-Type: application/json; charset=utf-8

{
    "name": "cnt_/js/formscript.js",
    "displayname": "Project Form Script",
    "description": "OnLoad, OnSave, OnChange handlers for the Project form",
    "webresourcetype": 3,
    "content": "dmFyIENvbnRvc28gPSBDb250b3NvIHx8IHt9Ow==",
    "languagecode": 1033
}
```

**Key properties:**

| Property | Description |
|---|---|
| `name` | Unique name with publisher prefix (e.g., `cnt_/js/formscript.js`) |
| `displayname` | Human-readable name shown in the UI |
| `webresourcetype` | Type ID (see types-reference.md) |
| `content` | **Base64-encoded** file content |
| `languagecode` | Language code (1033 for English) |

## Base64 Encoding in PowerShell

```powershell
# Encode a file
$content = Get-Content -Path "C:\src\formscript.js" -Raw
$bytes = [System.Text.Encoding]::UTF8.GetBytes($content)
$base64 = [Convert]::ToBase64String($bytes)

# Encode inline content
$js = @"
var Contoso = Contoso || {};
Contoso.ProjectForm = {
    onLoad: function(ctx) {
        var fc = ctx.getFormContext();
        console.log("Form loaded");
    }
};
"@
$base64 = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($js))
```

## Update a Web Resource

```http
PATCH [org-url]/api/data/v9.2/webresourceset({webresource-guid})
Content-Type: application/json; charset=utf-8

{
    "content": "dXBkYXRlZCBjb250ZW50..."
}
```

After updating, **you must publish** for changes to take effect.

## Add to Solution

If not created with the `MSCRM.SolutionUniqueName` header, add explicitly:

```http
POST [org-url]/api/data/v9.2/AddSolutionComponent
{
    "ComponentId": "{webresource-guid}",
    "ComponentType": 61,
    "SolutionUniqueName": "ContosoHRModule",
    "AddRequiredComponents": false
}
```

**ComponentType 61** = Web Resource.

## Publishing

Web resources must be published after creation or update:

```http
POST [org-url]/api/data/v9.2/PublishXml
{
    "ParameterXml": "<importexportxml><webresources><webresource>{webresource-guid}</webresource></webresources></importexportxml>"
}
```

Or publish all customizations:

```http
POST [org-url]/api/data/v9.2/PublishAllXml
```

## Size Limits

- **Default:** 5MB per web resource
- **Configurable:** Organization setting `maxuploadfilesize` (in bytes)
- **For large libraries:** Minify, split into multiple resources, or use CDN references

## Querying Existing Web Resources

```http
GET [org-url]/api/data/v9.2/webresourceset
    ?$filter=startswith(name,'cnt_/')
    &$select=name,displayname,webresourcetype,modifiedon
    &$orderby=name
```

## Deployment Script Pattern (PowerShell)

```powershell
function Deploy-WebResource {
    param(
        [string]$FilePath,
        [string]$Name,
        [string]$DisplayName,
        [int]$Type,
        [string]$Solution
    )

    $content = Get-Content -Path $FilePath -Raw
    $base64 = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($content))

    # Check if exists
    $existing = $null
    try {
        $filter = "name eq '$Name'"
        $result = Invoke-RestMethod -Uri "${baseUrl}/webresourceset?`$filter=$filter&`$select=webresourceid" `
            -Headers $headers -Method GET
        if ($result.value.Count -gt 0) {
            $existing = $result.value[0]
        }
    } catch {}

    if ($existing) {
        # Update
        Invoke-RestMethod -Uri "${baseUrl}/webresourceset($($existing.webresourceid))" `
            -Headers $headers -Method PATCH `
            -Body (@{ content = $base64 } | ConvertTo-Json)
        Write-Host "Updated: $Name"
    } else {
        # Create
        $payload = @{
            name = $Name
            displayname = $DisplayName
            webresourcetype = $Type
            content = $base64
            languagecode = 1033
        }
        $createHeaders = $headers.Clone()
        $createHeaders["MSCRM.SolutionUniqueName"] = $Solution
        Invoke-RestMethod -Uri "${baseUrl}/webresourceset" `
            -Headers $createHeaders -Method POST `
            -Body ($payload | ConvertTo-Json)
        Write-Host "Created: $Name"
    }
}

# Usage
Deploy-WebResource -FilePath ".\src\formscript.js" -Name "cnt_/js/formscript.js" `
    -DisplayName "Project Form Script" -Type 3 -Solution "ContosoHRModule"
```

## Deploying a React App as a Web Resource

When you need a React/TypeScript app embedded inside an MDA (Code Apps cannot be embedded),
use `vite-plugin-singlefile` to produce a single HTML file.

### Setup
```bash
npm install -D vite-plugin-singlefile
```

### Vite Config
```typescript
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { viteSingleFile } from "vite-plugin-singlefile";

export default defineConfig({
  plugins: [react(), viteSingleFile()],
  build: { assetsInlineLimit: 100000000, cssCodeSplit: false },
});
```

### Build and Deploy
```powershell
# Build produces a single index.html
npm run build

# Upload to Dataverse
$html = Get-Content -Path "dist/index.html" -Raw
$b64 = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($html))
Deploy-WebResource -Name "cnt_/html/myapp.html" -DisplayName "My React App" -Type 1 -Content $b64
```

### Sitemap Integration
```xml
<SubArea Id="Home" Title="My App" Url="/WebResources/cnt_/html/myapp.html" Client="All" />
```

### Xrm Availability in Web Resources

Web resources loaded via MDA sitemap run in an iframe. `Xrm` is NOT directly available.

**Fallback chain for getting current user ID:**
```javascript
function getGlobalContext() {
  // 1. Direct Xrm (form context)
  if (typeof Xrm !== "undefined" && Xrm?.Utility?.getGlobalContext)
    return Xrm.Utility.getGlobalContext();
  // 2. Parent Xrm (web resource in MDA iframe)
  try {
    if (typeof parent !== "undefined" && parent.Xrm?.Utility?.getGlobalContext)
      return parent.Xrm.Utility.getGlobalContext();
  } catch { /* cross-origin blocked */ }
  return null;
}

// 3. WhoAmI fallback (always works in authenticated context)
async function getCurrentUserIdAsync() {
  const ctx = getGlobalContext();
  if (ctx?.userSettings?.userId) return ctx.userSettings.userId.replace(/[{}]/g, "");
  const resp = await fetch("/api/data/v9.2/WhoAmI", { headers: { "OData-Version": "4.0" } });
  const data = await resp.json();
  return data.UserId;
}
```

## Best Practices

1. **Version your source** — keep web resource source in version control, deploy via scripts
2. **Minify for production** — reduce file size and improve load times
3. **Use descriptive names** — `cnt_/js/project/formscript.js` not `cnt_/js/script1.js`
4. **Idempotent deployment** — always check-exists-before-create
5. **Publish in batches** — one `PublishXml` call with all web resource GUIDs is more efficient
6. **Use `PublishAllXml` as fallback** — selective `PublishXml` with web resource name format
   sometimes fails; `PublishAllXml` always works
