# UX Decision Guide for Model-Driven Apps

**Consult this guide FIRST during any UX design phase.** It provides decision trees for
selecting the right control, layout, navigation pattern, and page type for model-driven app
customizations.

## Field-Level Decisions

### Text Fields

| Requirement | Control / Column Type | Notes |
|---|---|---|
| Short text (< 100 chars) | Single Line of Text | Names, titles, codes |
| Medium text (100-2000 chars) | Single Line of Text (increase max length) | Descriptions, summaries |
| Long text (> 2000 chars) | Multiple Lines of Text | Notes, comments |
| Formatted content (bold, lists, links) | Multiple Lines of Text + Rich Text Editor control | Set `Format` to `RichText` |
| Email address | Single Line of Text (Email format) | Enables mailto: link |
| URL | Single Line of Text (URL format) | Enables clickable link |
| Phone number | Single Line of Text (Phone format) | Enables click-to-call |
| Ticker symbol | Single Line of Text (Ticker format) | Rare, links to stock info |

**Decision flow:**
```
Need formatted text? --> Yes --> Rich Text (Multi-line + RichText format)
                    --> No  --> Length > 2000? --> Yes --> Multi-line text
                                              --> No  --> Single Line + appropriate format
```

### Number Fields

| Requirement | Control / Column Type | Notes |
|---|---|---|
| Standard integer | Whole Number | Default control is numeric input |
| Decimal value | Decimal Number | Set precision (0-10 decimal places) |
| Currency amount | Currency | Auto-formats with currency symbol, uses org currency settings |
| Percentage | Whole Number or Decimal + custom label | No native % control; add "%" in label |
| Rating (1-5 stars) | Whole Number + Star Rating PCF control | Requires PCF control installation |
| Slider selection | Whole Number + Slider PCF control | Good for bounded ranges (1-10) |
| Duration | Whole Number (Duration format) | Displays as hours:minutes |

**Decision flow:**
```
Is it money? --> Yes --> Currency column
             --> No  --> Need decimals? --> Yes --> Decimal Number
                                        --> No  --> Duration? --> Yes --> Whole Number (Duration)
                                                              --> No  --> Whole Number
Want visual input? --> Slider for ranges, Star Rating for scores
```

### Choice Fields

| Requirement | Control / Column Type | Notes |
|---|---|---|
| Single selection from list | Choice (Option Set) | Renders as dropdown by default |
| Multiple selections | Choices (Multi-Select Option Set) | Renders as checkbox list |
| Boolean yes/no | Yes/No (Two Option) | Default: dropdown. Can switch to toggle or checkbox |
| On/off toggle | Yes/No + Toggle control | Better UX for enable/disable settings |
| Radio button selection | Choice + Radio Button PCF control | Good for 2-4 options visible at once |
| Status with colors | Status/Status Reason | System columns with built-in color coding |

**Decision flow:**
```
Only 2 options? --> Yes --> Is it on/off or enable/disable? --> Yes --> Yes/No + Toggle
                                                            --> No  --> Yes/No (dropdown)
              --> No  --> Can select multiple? --> Yes --> Choices (Multi-Select)
                                               --> No  --> Few options (2-4)? --> Yes --> Consider radio buttons
                                                                              --> No  --> Choice (dropdown)
```

### Lookup Fields

| Requirement | Control / Column Type | Notes |
|---|---|---|
| Standard lookup | Lookup | Default: type-ahead search with recent items |
| High-volume lookup (1000s of records) | Lookup + custom filtered view | Create a view that pre-filters options |
| Polymorphic lookup (multiple entity types) | Customer lookup or custom polymorphic | Customer = Account + Contact |
| Hierarchical selection | Lookup + tree view | Requires custom PCF for tree navigation |

**Decision flow:**
```
Lookup target has > 5000 records? --> Yes --> Add filtered lookup view
                                  --> No  --> Standard lookup is fine
Need to look up multiple entity types? --> Yes --> Customer type or custom polymorphic
                                        --> No  --> Standard Lookup
```

### Date Fields

| Requirement | Control / Column Type | Notes |
|---|---|---|
| Date only (no time) | Date Only | Calendar picker |
| Date and time | Date and Time | Calendar + time picker |
| User-local time | Date and Time (User Local behavior) | Adjusts to user timezone |
| Timezone-independent | Date and Time (Date Only or Timezone Independent) | Same value regardless of user timezone |

### File and Image Fields

| Requirement | Control / Column Type | Notes |
|---|---|---|
| Single file attachment | File column | Up to 128MB configurable |
| Profile image / avatar | Image column | Stores thumbnail + full image |
| Multiple attachments | Use Notes (annotations) or custom child entity | File column is single-file only |
| Document with versioning | SharePoint integration | Better than Dataverse for document management |

## Form-Level Decisions

### Tabs vs. Sections

| Scenario | Use | Reasoning |
|---|---|---|
| Logically distinct data groups | Tabs | Each tab represents a category (General, Details, History) |
| Related fields within a group | Sections within a tab | Sections subdivide a tab (Address section, Contact section) |
| Progressive disclosure | Tabs (collapsed by default) | Hide advanced fields until user expands |
| All fields fit on one screen | Single tab with sections | Avoid unnecessary tab switching |
| 20+ fields | Multiple tabs | Reduce visual clutter per screen |
| 5-10 fields | Single tab, 2-3 sections | No need for tabs |

**Decision flow:**
```
Total fields > 15? --> Yes --> Group into logical categories
                              --> 3+ categories? --> Yes --> Use tabs (one per category)
                                                  --> No  --> Single tab with sections
                   --> No  --> Single tab with sections is sufficient
```

### Subgrids vs. Related Records Pane

| Scenario | Use | Reasoning |
|---|---|---|
| Always-visible child records | Subgrid on form | User sees related data immediately |
| Occasional child record access | Related records tab/pane | Keeps main form clean |
| Need inline editing | Editable subgrid | Quick updates without opening each record |
| Many relationship types | Related records pane | Handles multiple 1:N relationships |
| 1-5 related records typical | Subgrid | Fits well on form |
| 50+ related records typical | Related records pane or view link | Subgrid pagination is clunky |

### Quick View vs. Inline Fields

| Scenario | Use | Reasoning |
|---|---|---|
| Show parent record summary | Quick View Form | Displays read-only fields from related record |
| Need editable parent fields | Cannot — use navigation instead | Quick view is always read-only |
| Show 2-3 parent fields | Inline lookup fields or Quick View | Quick view for more fields |
| Show many parent fields | Quick View Form | Avoids cluttering the main form |
| Multiple related entities to preview | Multiple Quick View controls | One per relationship |

### Timeline vs. Custom Activity Log

| Scenario | Use | Reasoning |
|---|---|---|
| Emails, calls, appointments, notes | Timeline control (default) | Built-in, handles all activity types |
| Custom activity types | Timeline (if activities) or Subgrid (if not) | Timeline supports custom activities |
| Audit-style log (who changed what) | Audit History or custom subgrid | Timeline is for activities, not audits |
| Simple comment thread | Timeline with Notes | Notes appear in timeline |
| Integration events (API calls, webhooks) | Custom entity + subgrid | Timeline is for user-facing activities |

### Embedded Visuals

| Scenario | Use | Reasoning |
|---|---|---|
| Simple chart (bar, pie, line) | Chart control on form | Built-in, no extra licensing |
| Interactive dashboard | Power BI embedded | Rich visuals, cross-filtering |
| Custom visualization | HTML web resource | Full control, custom JS charting |
| KPI cards | Power BI tiles or HTML web resource | Power BI for live data |

## Grid-Level Decisions

### Grid Type Selection

| Scenario | Use | Reasoning |
|---|---|---|
| Read-only list | Read-Only Grid (default) | Standard view display |
| Inline quick edits | Editable Grid | Edit fields directly in grid rows |
| Rich cell rendering (icons, colors) | Power Apps Grid Control | Supports cell-level formatting |
| Grouping by category | Power Apps Grid Control | Built-in grouping support |
| Hierarchical / nested rows | Hierarchy view or custom | Limited built-in support |
| Kanban-style board | Custom PCF control | No built-in Kanban; requires custom development |
| Card layout (mobile-friendly) | Card Form view | Shows records as cards instead of rows |

**Decision flow:**
```
Need inline editing? --> Yes --> Editable Grid
                     --> No  --> Need rich formatting (icons, colors)? --> Yes --> Power Apps Grid Control
                                                                       --> No  --> Read-Only Grid (default)
Need grouping? --> Yes --> Power Apps Grid Control
Need Kanban? --> Yes --> Custom PCF control
```

## Navigation Decisions

### Side Pane vs. Dialog vs. New Form

| Scenario | Use | Reasoning |
|---|---|---|
| Persistent tool (chat, help, dashboard) | Side Pane | Stays open while user works |
| One-time action (wizard, confirmation) | Modal Dialog | Focused interaction, returns result |
| Full record editing | New Form (openForm) | Full form context and save behavior |
| Quick data entry | Quick Create Form | Lightweight, returns to current context |
| Reference information | Side Pane | User can glance at it while working |
| Multi-step process | Modal Dialog | Prevents user from navigating away mid-process |

**Decision flow:**
```
User needs to interact WHILE working on current form? --> Yes --> Side Pane
User must complete an action before continuing?       --> Yes --> Modal Dialog
User needs full form experience?                      --> Yes --> openForm (new window or inline)
Quick single-record creation?                         --> Yes --> Quick Create Form
```

### Custom Page vs. Web Resource

| Scenario | Use | Reasoning |
|---|---|---|
| Complex UI (React, heavy interactivity) | Custom Page (Canvas) or Code App | Full framework support |
| Simple HTML display | HTML Web Resource | Lighter weight, no Canvas overhead |
| Need Dataverse connectors | Custom Page | Built-in connector support |
| Need direct Xrm.WebApi access | HTML Web Resource | Direct access to client API |
| Responsive / mobile-ready | Custom Page or Code App | Better responsive framework |
| Simple form + submit | HTML Web Resource | No need for full page framework |

### Command Bar Button vs. Form Button

| Scenario | Use | Reasoning |
|---|---|---|
| Action applies to the record (approve, reject) | Command Bar Button | Standard location for record actions |
| Action within a form section | HTML Web Resource with button | Contextual to section content |
| Action always visible | Command Bar Button | Always at top of form |
| Action context-specific (show/hide) | Command Bar + Enable/Display Rules | Dynamic visibility |
| Multiple related actions | Command Bar dropdown/flyout | Groups related actions |

## Page-Level Decisions

### Homepage / Landing

| Scenario | Use | Reasoning |
|---|---|---|
| Standard entity list with charts | Model-Driven Dashboard | Built-in, configurable |
| Custom KPI dashboard | HTML Web Resource or Power BI embed | Full visual control |
| Interactive app (game, tool, calculator) | Code App as Custom Page | Full React/TS capability |
| Simple redirect / launcher | HTML Web Resource | Lightweight landing page |

### Multi-Step Flows

| Scenario | Use | Reasoning |
|---|---|---|
| Linear wizard (step 1-2-3-done) | Modal dialog with HTML web resource | Wizard UI in HTML/JS |
| Branching wizard | Custom Page or Code App | Complex navigation logic |
| Multi-record creation flow | Business Process Flow | Built-in stage/step tracking |
| Approval chain | Power Automate + BPF | Automated routing |
| Form with conditional sections | Single form + JS visibility | Show/hide sections via OnChange |

### Dashboards

| Scenario | Use | Reasoning |
|---|---|---|
| Entity charts + lists | System Dashboard | Built-in, no code needed |
| Cross-entity analytics | Power BI Dashboard | Better aggregation and visuals |
| Real-time metrics | HTML Web Resource + API polling | Custom refresh intervals |
| User-configurable | Personal Dashboard | Users build their own |
| Embedded in form | HTML web resource in form tab | Contextual to current record |

## Decision Summary Matrix

Use this quick-reference matrix when the decision is not obvious:

| Priority | Prefer | Over | Reason |
|---|---|---|---|
| Simplicity | Built-in controls | Custom PCF | Less maintenance |
| Interactivity | Code App / Custom Page | HTML Web Resource | Better framework support |
| Performance | Server-side (plugins) | Client-side (JS) | Fewer round-trips |
| Persistence | Side Pane | Dialog | User keeps context |
| Focus | Modal Dialog | Side Pane | Prevents distraction |
| Mobile | Custom Page / Canvas | HTML Web Resource | Better responsive support |
| Data Display | Power BI | HTML Charts | Better tooling and refresh |
| Quick Actions | Command Bar | Form Buttons | Standard UX location |
| Audit / History | Timeline + Audit | Custom Entity | Built-in and recognized |
| File Management | SharePoint Integration | File Columns | Versioning, permissions |

## Anti-Patterns to Avoid

1. **Overloading a single form** — If a form has 40+ fields, split into tabs or consider
   a multi-form approach with form selector.

2. **Subgrid with 100+ records** — Use a view link or related records pane instead.
   Subgrids with many records cause performance issues.

3. **Modal dialog for persistent tools** — Dialogs block the main form. Use side panes
   for tools the user returns to frequently.

4. **Command bar buttons without enable rules** — Always add rules so buttons are
   disabled/hidden when not applicable. Reduces user confusion.

5. **HTML web resource for complex apps** — If the web resource grows beyond simple
   display, migrate to a Code App / Custom Page for proper framework support.

6. **Client-side aggregation** — Avoid fetching all records in JS to compute totals.
   Use FetchXML aggregate queries, server-side plugins, or Power BI.

7. **Editable grid for complex validation** — Editable grids have limited validation
   support. Use form-based editing if validation rules are complex.

8. **Tab per field** — Do not create a tab for every 2-3 fields. Group logically.
   Tabs should contain at least one meaningful section with multiple fields.
