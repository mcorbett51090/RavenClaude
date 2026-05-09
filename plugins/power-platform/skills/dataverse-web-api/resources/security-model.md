# MDA Security Model Design

Comprehensive guide to the 7-layer security model in Model-Driven Apps and Dataverse.
Security is cumulative and restrictive — users get the LEAST privilege unless explicitly granted more.

## The 7 Security Layers (In Order)

Security in Dataverse/MDA is applied in layers. Each layer must be configured correctly
for a user to access the system. Missing any layer blocks access entirely.

### Layer 1: Microsoft Entra ID (Authentication)

- Every user must have a Microsoft Entra ID (formerly Azure AD) account
- This is the authentication gate — proves identity
- Users are synced to Dataverse as `systemuser` records
- Without an Entra ID account, nothing else matters
- Guest users (B2B) can be granted access but require explicit configuration

### Layer 2: Product License Assignment

- Users need appropriate licenses assigned in Microsoft 365 Admin Center
- **Power Apps per app plan**: Access to a single app (cheapest)
- **Power Apps per user plan**: Access to unlimited apps
- **Dynamics 365 licenses**: Include Power Apps access for that workload
- **Power Apps Developer plan**: Free, single-user dev environment only
- Without a license, users cannot open any Power Apps environment

### Layer 3: Security Groups (Environment Access)

- Security groups control WHICH USERS can access WHICH ENVIRONMENTS
- Configured in Power Platform Admin Center > Environment > Settings
- An environment can be associated with a Microsoft Entra security group
- Only members of that group can access the environment
- If no security group is set, ALL licensed users can access the environment
- Best practice: Always assign a security group to production environments

### Layer 4: Security Roles (Granular Access Control)

- Security roles define what a user can DO within an environment
- Roles are assigned to users or teams
- A user can have MULTIPLE roles — permissions are ADDITIVE (union of all roles)
- Without at least one security role, a user cannot open any app in the environment

#### Built-in Roles
| Role | Purpose |
|---|---|
| System Administrator | Full access to everything; can customize and administer |
| System Customizer | Full customization access; limited data access |
| Basic User | Minimum role for running apps; read access to standard tables |
| Environment Maker | Can create resources (flows, apps) but not access data |
| Delegate | Act on behalf of another user |

#### Role Design Rules
- **ALWAYS copy the Basic User role and modify** — never create roles from scratch
- Basic User includes essential privileges for system tables (user settings, etc.)
- Creating from scratch risks missing critical base privileges, causing cryptic errors
- Limit System Administrator role to 2-3 admins maximum
- Assign least-privilege roles based on job descriptions

#### 4 Access Scopes
| Scope | Icon | Description |
|---|---|---|
| User | Single circle | Only records owned by the user |
| Business Unit | Filled circle | Records owned by anyone in the user's BU |
| Parent-Child BU | Double circle | Records in user's BU and all child BUs |
| Organization | Full circle | All records across the entire org |

#### 8 Privileges
| Privilege | Description |
|---|---|
| Create | Create new records |
| Read | View records |
| Write | Update existing records |
| Delete | Remove records |
| Append | Associate a record with the current record (add child) |
| Append To | Allow the current record to be associated as child |
| Assign | Change record ownership |
| Share | Grant access to other users/teams |

### Layer 5: App-Level Security

- Security roles can be assigned directly to an app module
- Only users with one of the app's assigned roles can see/open the app
- Users without the specific role do not see the app in their app list
- This restricts access to specific apps WITHOUT changing data permissions

#### Configuring via API
Associate a security role with an app module:
```http
POST /appmodules({appmodule-id})/appmoduleroles_association/$ref
{
  "@odata.id": "https://{org}.api.crm.dynamics.com/api/data/v9.2/roles({role-id})"
}
```

#### Configuring via Maker Portal
1. Open the app in the App Designer
2. Click "Manage Roles" in the command bar
3. Check the roles that should have access
4. Save and Publish

### Layer 6: Table/Record-Level Security (CRUD Permissions)

- Defined within security roles at the table level
- Each table gets a row in the security role matrix with all 8 privileges
- Scope (User/BU/Parent-Child/Org) is set per privilege per table
- Missing table permissions = user cannot see any records in that table

#### Access Types for External Users (Portal/External Access)
| Type | Description |
|---|---|
| Global access | Access all records regardless of relationship |
| Contact access | Access records linked to the user's contact |
| Account access | Access records linked to the user's account |
| Self access | Access only the user's own contact record |

#### Record Ownership
- **User-owned tables**: Records have an owner (user or team); security scope applies
- **Organization-owned tables**: All records belong to the org; only Organization scope applies
- IMPORTANT: Ownership type is set at table creation and CANNOT be changed later

### Layer 7: Column-Level Security

- Controls access to individual columns (fields) within a table
- More granular than table-level security
- Implemented via **Column Security Profiles**

#### Setup Process
1. Enable field security on the column (set `IsSecured = true` on the attribute metadata)
2. Create a Column Security Profile
3. Add field permissions to the profile (Read, Create, Update per column)
4. Assign users or teams to the profile

#### API: Create Column Security Profile
```http
POST /fieldsecurityprofiles
MSCRM.SolutionUniqueName: {solution}

{
  "name": "Salary Access Profile",
  "description": "Grants access to salary-related columns"
}
```

#### API: Add Field Permission
```http
POST /fieldpermissions

{
  "entityname": "cnt_employee",
  "attributelogicalname": "cnt_salary",
  "canread": 4,
  "cancreate": 4,
  "canupdate": 4,
  "fieldsecurityprofileid@odata.bind": "/fieldsecurityprofiles({profile-id})"
}
```
Permission values: 0 = Not Allowed, 4 = Allowed

#### GOTCHA: Column Security and Alternate Keys
- **Cannot apply column-level security to columns used in alternate keys**
- Dataverse does not prevent you from trying, but it causes runtime errors
- Plan your alternate keys and column security strategy together during design phase
- If a column needs to be secured AND serve as a key, you need to redesign

#### Field Security Overrides Role Permissions
- If column security is enabled on a column, the Column Security Profile permissions
  OVERRIDE the security role permissions for that specific column
- A user with Organization-level Read on the table may still NOT see a secured column
  unless they are in a profile that grants Read on that column

## BPF (Business Process Flow) Security

- Security roles can be applied to specific Business Process Flows
- System Administrator and System Customizer see ALL BPFs by default
- Other users need minimum **Read-level privileges on the Process (workflow) table** to use business rules
- A user must have the BPF's assigned security role to see and interact with it
- If multiple BPFs exist for one table, the user sees only the ones their role permits

#### Configuring BPF Security
1. Open the BPF in the designer
2. Click "Enable Security Roles" in the command bar
3. Select which roles can access this BPF
4. Save and Activate

## Sharing Records

Share individual records with specific users or teams, granting targeted privileges
beyond what their security role provides.

### Share Privileges
When sharing a record, you can grant any combination of:
- **Read** — View the record
- **Write** — Update the record
- **Delete** — Delete the record
- **Append** — Associate child records
- **Assign** — Change ownership
- **Share** — Re-share with others

### API: Share a Record
```http
POST /GrantAccess
{
  "Target": {
    "cnt_projectid": "{record-id}",
    "@odata.type": "Microsoft.Dynamics.CRM.cnt_project"
  },
  "PrincipalAccess": {
    "Principal": {
      "systemuserid": "{user-id}",
      "@odata.type": "Microsoft.Dynamics.CRM.systemuser"
    },
    "AccessMask": "ReadAccess,WriteAccess"
  }
}
```

### Cascade Share Behavior
- Relationships can be configured with cascade sharing rules
- When a parent record is shared, child records can be automatically shared
- Cascade behaviors: `Cascade`, `Active`, `UserOwned`, `NoCascade`
- Configure during relationship creation via `CascadeConfiguration.Share`

### Revoking Shared Access
```http
POST /RevokeAccess
{
  "Target": {
    "cnt_projectid": "{record-id}",
    "@odata.type": "Microsoft.Dynamics.CRM.cnt_project"
  },
  "Revokee": {
    "systemuserid": "{user-id}",
    "@odata.type": "Microsoft.Dynamics.CRM.systemuser"
  }
}
```

## Best Practices

### Security Design
- **Copy Basic User role** as starting point for all custom roles
- **Least privilege**: Start with minimum access, add more as needed
- **Limit System Administrator**: Maximum 2-3 users with this role
- **Test with non-admin accounts**: Always verify security works by logging in as a regular user
- **Document role assignments**: Maintain a matrix of roles vs. job functions

### Code and Plugin Security
- **Never run plugins under admin context** unless absolutely necessary — plugin code may access
  data the triggering user should not see. Use `IPluginExecutionContext.InitiatingUserId` to
  check the actual user
- **Never modify Dataverse data except via SDK or Web API** — direct database modifications
  bypass ALL security layers
- **Service accounts**: If plugins need elevated access, use a dedicated service account with
  only the specific permissions needed

### Authentication Hardening
- **Enable MFA** (Multi-Factor Authentication) for ALL accounts
- **Use Azure Conditional Access policies** to enforce device compliance, location restrictions
- **Disable unused accounts** promptly when employees leave
- **Review security role assignments** quarterly
- **Monitor sign-in logs** in Entra ID for suspicious activity

### Teams
- Use **Owner teams** when records need to be owned by a group
- Use **Access teams** for dynamic, ad-hoc record sharing
- Use **Microsoft Entra group teams** to sync group membership automatically
- Team members inherit the team's security roles

### Hierarchy Security
- Enable hierarchy security for reporting-line-based access
- Manager hierarchy: Managers can access their reports' records
- Position hierarchy: Custom hierarchy independent of reporting line
- Use when security requirements follow organizational structure
