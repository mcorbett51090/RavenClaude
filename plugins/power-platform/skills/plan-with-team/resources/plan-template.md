# Consolidated Plan Template

The Lead uses this template to merge all three agents' outputs into one document.

---

## [App Name] — Implementation Plan

### 1. Overview

**Purpose:** [One paragraph describing what the app does and who it's for]

**Personas:**
| Persona | Access Level | Key Tasks |
|---|---|---|
| [Name] | [Read/Write/Admin] | [Top 3 tasks] |

### 2. Solution Structure

**Publisher:**
- Friendly Name: [name]
- Unique Name: [name]
- Prefix: [prefix]
- Option Value Prefix: [number]

**Solution:**
- Unique Name: [name]
- Version: 1.0.0.0
- Description: [description]

### 3. Data Model

#### 3.1 Tables

For each table, include:
- Schema name, display name (singular/plural)
- Ownership type
- Behavioral flags (HasNotes, HasActivities, IsAuditEnabled, etc.)
- Primary Name column details
- All columns with: name, type, @odata.type, required level, constraints
- All relationships with: type, related table, cascade config

#### 3.2 Global Option Sets

| Name | Options (Value: Label) |
|---|---|
| [set name] | [value]: [label], ... |

#### 3.3 Relationship Diagram

Text-based ERD showing table connections:
```
[Account] 1──N [Project] N──N [Employee]
                    │
                    1
                    │
                    N
              [Milestone]
```

### 4. App Design

#### 4.1 App Module
- Name, unique name, client type
- Security roles with access

#### 4.2 Sitemap
- Area > Group > SubArea hierarchy

#### 4.3 Forms
For each table:
- Main Form: tab/section/field layout
- Quick Create Form: field list
- Quick View Forms (if any)

#### 4.4 Views
For each table:
- Default view: columns, filter, sort
- Additional views with their querytype
- Quick Find view configuration

#### 4.5 User Flows
Step-by-step task completion paths for each persona's key tasks.

### 5. Skeptic Review — Resolved Issues

| # | Severity | Area | Issue | Resolution |
|---|---|---|---|---|
| 1 | Critical | [area] | [what was found] | [how it was fixed] |
| 2 | High | [area] | [what was found] | [how it was fixed] |

### 6. Skeptic Review — Accepted Risks

| # | Severity | Area | Issue | Justification for Acceptance |
|---|---|---|---|---|
| 1 | Low | [area] | [what was found] | [why we're accepting it] |

### 7. Implementation Sequence

The recommended build order (each step maps to Dataverse Web API operations):

1. Create Publisher → `POST /publishers`
2. Create Solution → `POST /solutions`
3. Create Global Option Sets → `POST /GlobalOptionSetDefinitions`
4. Create Tables (with Primary Name) → `POST /EntityDefinitions`
5. Create Columns → `POST /EntityDefinitions({id})/Attributes`
6. Create Relationships → `POST /RelationshipDefinitions`
7. Create Views → `POST /savedqueries`
8. Create Forms → `POST /systemforms`
9. Publish → `PublishXml`
10. Create App Module → `POST /appmodules`
11. Add Components to App → `AddAppComponents`
12. Create Sitemap → `POST /sitemaps`
13. Associate Sitemap → `POST /appmodules({id})/appmodulesitemap/$ref`
14. Final Publish → `PublishXml`
15. Validate → `ValidateApp`

### 8. Security Model

#### Security Roles
| Role Name | Based On | Tables | Key Permissions |
|---|---|---|---|
| _e.g., App User_ | _Basic User_ | _Table1: Read(BU), Write(User), Create(BU)_ | _Full access to own records, read BU records_ |

#### Column-Level Security Profiles
| Profile | Columns Protected | Users/Teams |
|---|---|---|
| _e.g., Financial Data_ | _Revenue, Cost, Margin_ | _Finance Team_ |

#### App-Level Security
| App Module | Security Roles Required |
|---|---|
| _e.g., Sales App_ | _Sales User, Sales Manager_ |

### 9. Environment Variables

| Variable Name | Type | Default Value | Purpose |
|---|---|---|---|
| _e.g., prefix_ApiBaseUrl_ | _Text_ | _https://api.example.com_ | _External API endpoint_ |
| _e.g., prefix_EnableFeatureX_ | _Boolean_ | _true_ | _Feature flag_ |

### 10. Control Selection Matrix

#### Field Control Mapping

| Field | Column Type | Recommended Control | ClassID / Notes |
|---|---|---|---|
| [field name] | [String/Memo/Int/Bool/etc.] | [Standard/RichText/Toggle/Rating/etc.] | [ClassID or justification] |

*Map every form field to its recommended control type. Default controls are fine for most fields — only specify advanced controls where they improve UX.*

#### Grid/View Display Strategy

| Entity | View Name | Grid Type | Editable? | Notes |
|---|---|---|---|---|
| [entity] | [view name] | [Standard/PowerAppsGrid/EditableGrid/PCF] | [Yes/No] | [Inline editing cols, nested grids, etc.] |

#### Command Bar Customization

| Entity | Button Label | Location | Action Type | Handler |
|---|---|---|---|---|
| [entity] | [label] | [Form/Grid/Both] | [JS/PowerFx/URL] | [namespace.function or Fx expression] |

#### Side Pane Usage Plan

| Pane ID | Title | Content Type | Trigger | Width |
|---|---|---|---|---|
| [id] | [title] | [WebResource/CustomPage/EntityForm] | [Command bar button/Auto-open] | [px] |

#### Home Page Strategy

| Approach | Description | When to Use |
|---|---|---|
| Code App | Custom React/Vue interactive frontend | Complex interactions, games, wizards |
| HTML Dashboard | Web resource with charts/KPIs | Read-only summaries, simple dashboards |
| Power BI Embed | Embedded Power BI report | Analytics, drill-down, slicers |
| MDA Dashboard | Standard charts + lists | Simple layouts, quick setup |

**Selected approach:** [choice + justification]

#### Wizard/Onboarding Flow Plan (if applicable)

| Step | Title | Content | Navigation |
|---|---|---|---|
| 1 | [title] | [fields or instructions] | [Next/Back/Finish] |

### 11. Parallelization Strategy

#### Dependency Graph

```
[Sequential] Publisher + Solution
     ↓
[Parallel] Global Option Sets | Table A | Table B | Table C
     ↓
[Parallel per table] Columns (need option set GUIDs)
     ↓
[Sequential] Relationships (need both tables)
     ↓
[Parallel per table] Views + Forms
     ↓
[Sequential] Sitemap → App Module → Publish + Validate
```

#### Agent Team Composition

**Option A: One Agent Per Table** (recommended for 3+ tables)
- Main agent: Publisher, Solution, Option Sets, Relationships, Sitemap, App Module, Publish
- Table agents: Each creates their table + columns + views + forms

**Option B: Schema + UX Split** (recommended for 1-2 tables)
- Schema agent: Publisher, Solution, Tables, Columns, Relationships
- UX agent: Views, Forms, Sitemap
- Main agent: App Module, Publish

#### Which steps are parallelizable?

| Step | Parallel? | Dependencies |
|---|---|---|
| Publisher + Solution | No | Must be first |
| Global Option Sets | Yes | After solution |
| Tables | Yes | After solution |
| Columns per table | Yes (across tables) | After own table + option set GUIDs |
| Relationships | No | After both tables exist |
| Views per table | Yes (across tables) | After own table's columns |
| Forms per table | Yes (across tables) | After own table's views (for subgrids) |
| Sitemap | No | After entities exist |
| App Module | No | After everything |
| Publish + Validate | No | Must be last |

### 12. Open Questions

[Any unresolved decisions that need user input before implementation]
