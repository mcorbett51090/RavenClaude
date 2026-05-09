# Power Platform CLI (pac) Reference for Code Apps

## Installation

Three installation methods:

1. **VS Code Extension** (recommended): Install "Power Platform Tools" from VS Code marketplace
2. **.NET Tool**: `dotnet tool install --global Microsoft.PowerApps.CLI.Tool`
3. **Windows MSI**: Download from Microsoft

Additionally, the standalone npm CLI:
```bash
npm install -g @microsoft/power-apps-cli
```
Current version: 0.6.7. Binary command: `power-apps`

## Authentication

### Create Auth Profile
```bash
pac auth create
# Interactive browser login (default)

pac auth create --deviceCode
# Device code flow (for headless environments)

pac auth create --applicationId <client-id> --clientSecret <secret> --tenant <tenant-id>
# Service principal authentication

pac auth create --cloud UsGov
# Government cloud (options: Public, UsGov, UsGovHigh, UsGovDod, China)
```

### Manage Auth Profiles
```bash
pac auth list                    # List all profiles
pac auth select --index <n>      # Switch active profile
pac auth delete --index <n>      # Remove a profile
pac auth clear                   # Remove all profiles
pac auth who                     # Show current identity
```

## Environment Management

```bash
pac env list                                    # List all environments
pac env select --environment <env-id-or-url>    # Select active environment
pac env who                                     # Show current environment details
pac env list-settings                           # List environment settings
```

The `--environment` flag accepts either a GUID or an absolute HTTPS URL.
When omitted, the active auth profile's organization is used.

## Code Apps Commands (pac code)

### Initialize a New Code App
```bash
pac code init --displayname "My App Name"
```
Registers the app in the selected Power Platform environment and generates `power.config.json`.

**All `pac code init` flags:**

| Flag | Alias | Required | Description |
|------|-------|:---:|-------------|
| `--displayName` | `-n` | Yes | Display name for the app |
| `--appUrl` | `-a` | No | Local URL for the app |
| `--buildPath` | `-b` | No | Build assets directory |
| `--description` | `-d` | No | App description |
| `--environment` | `-env` | No | Target Dataverse environment |
| `--fileEntryPoint` | `-f` | No | Entry point file for the app |
| `--logoPath` | `-l` | No | Path to app logo image |
| `--region` | `-c` | No | Hosting region |

### Add Data Sources

Requires PAC CLI version **1.51.1 or later** (released December 2025).

```bash
# Add Dataverse table
pac code add-data-source -a dataverse -t <table-logical-name>
pac code add-data-source -a dataverse -t contact

# Add non-tabular connector (e.g., Office 365 Users)
pac code add-data-source -a <apiName> -c <connectionId>

# Add tabular connector (e.g., SQL, SharePoint)
pac code add-data-source -a <apiName> -c <connectionId> -t <tableId> -d <datasetName>

# Add SQL stored procedure
pac code add-data-source -a <apiId> -c <connectionId> -d <dataSourceName> -sp <storedProcedureName>

# Add with connection reference (for ALM / solution-aware)
pac code add-data-source -a <apiName> -cr <connectionReferenceLogicalName> -s <solutionID>
```

Flags:
- `-a` -- API name (e.g., `dataverse`, `shared_sql`, `shared_office365users`)
- `-c` -- Connection ID
- `-t` -- Table logical name or table ID
- `-d` -- Dataset name
- `-sp` -- Stored procedure name
- `-cr` -- Connection reference logical name (for ALM)
- `-s` -- Solution ID

### Remove Data Sources
```bash
pac code delete-data-source -a <apiName> -ds <dataSourceName>
```

### List Available Data
```bash
pac code list-datasets               # List available datasets/connectors
pac code list-tables                  # List tables in a dataset
pac code list-connection-references   # List connection references
pac code list-sqlStoredProcedures     # List SQL stored procedures
pac code list-environment-variables   # List environment variables
```

### Deploy
```bash
npm run build | pac code push
# Build and push to the selected environment

npm run build | pac code push --solutionName MySolution
# Deploy into a specific solution (for ALM)
```

The `pac code push` command:
- Accepts the build output via stdin (piped from npm run build)
- Publishes a new version to the environment
- Returns the Power Apps URL for the deployed app

### Run Local Server
```bash
pac code run
pac code run --port 5173
pac code run --appUrl http://localhost:5173
```
Runs a local server for connector data access during development.

| Flag | Alias | Description |
|------|-------|-------------|
| `--appUrl` | `-a` | Local URL for the app |
| `--port` | `-p` | Port for local server |

### List Code Apps
```bash
pac code list-codeapps
# Lists all code apps in the current environment
```

## Project Scaffolding (Templates)

### Starter Template (Recommended)
```bash
npx degit github:microsoft/PowerAppsCodeApps/templates/starter my-app
```
Includes: React, Tailwind CSS, TanStack Query, React Router, Zustand, Radix UI

### Minimal Template
```bash
npx degit github:microsoft/PowerAppsCodeApps/templates/vite my-app
```
Includes: Vite + React (minimal setup)

### After Scaffolding
```bash
cd my-app
npm install
pac auth create                              # If not already authenticated
pac env select --environment <env-id>        # Select target environment
pac code init --displayname "My App"         # Register the code app
npm run dev                                  # Start local dev server
```

## Build Configuration

### package.json Scripts
```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview"
  }
}
```

The build pipeline: TypeScript compilation (`tsc -b`) then Vite production build (`vite build`).

### Key Dependencies
```json
{
  "dependencies": {
    "@microsoft/power-apps": "^1.0.3"
  },
  "devDependencies": {
    "@microsoft/power-apps-vite": "^1.0.2",
    "typescript": "~5.x",
    "vite": "^6.x",
    "@vitejs/plugin-react": "^4.x"
  }
}
```

## Solution and ALM Commands

### Solution Management
```bash
pac solution list                              # List solutions in environment
pac solution export --name MySolution --path ./export
pac solution import --path ./MySolution.zip
pac solution clone --name MySolution           # Clone for .cdsproj workflow
pac solution pack --zipfile out.zip --folder ./src
pac solution unpack --zipfile in.zip --folder ./src
pac solution check --path ./MySolution.zip     # Run solution checker
```

### Solution Deployment
```bash
# Push code app into a specific solution
npm run build | pac code push --solutionName MySolution

# For managed solution deployment across environments,
# use Power Platform Pipelines (Dev -> Test -> Prod)
```

### Connection References
```bash
pac code list-connection-references
# Lists connection references for environment-agnostic deployments
```

## Canvas App Commands (for Migration)

```bash
pac canvas unpack --msapp ./MyApp.msapp --sources ./src
# Unpack a .msapp file to .pa.yaml source format (Preview)

pac canvas pack --sources ./src --msapp ./MyApp.msapp
# Pack .pa.yaml sources back to .msapp (Preview)

pac canvas download --name "My App" --extract-to-directory ./src
# Download canvas app and extract to directory

pac canvas list
# List all canvas apps in environment

pac canvas validate --directory ./src
# Validate .pa.yaml source files
```

## Other Useful Commands

```bash
pac telemetry enable                    # Enable telemetry
pac telemetry disable                   # Disable telemetry
# Or set env var: PP_TOOLS_TELEMETRY_OPTOUT=1

pac copilot mcp --run                   # Start MCP server (AI integration)

pac power-fx repl                       # Interactive Power Fx REPL (150+ functions)

pac complete --shell powershell         # Tab completion setup
pac complete --shell bash
pac complete --shell zsh
```

## Common Workflows

### Full Dev Loop
```bash
# 1. Scaffold
npx degit github:microsoft/PowerAppsCodeApps/templates/starter my-app
cd my-app && npm install

# 2. Auth and init
pac auth create
pac env select --environment <env-id>
pac code init --displayname "My App"

# 3. Add data
pac code add-data-source --dataset Contacts
pac code add-data-source --dataset Accounts

# 4. Develop
npm run dev
# Edit src/ files, hot reload in browser

# 5. Deploy
npm run build | pac code push
```

### Environment Switching
```bash
pac auth list                          # See all profiles
pac auth select --index 2              # Switch to profile #2
pac env select --environment <new-env> # Select new environment
npm run build | pac code push          # Deploy to new environment
```
