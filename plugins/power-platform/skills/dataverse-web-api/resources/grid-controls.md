# Grid Controls

Dataverse offers several grid control types for displaying tabular data in views and on forms.
Choosing the right grid depends on whether you need inline editing, nested drill-down, or custom layouts.

## Power Apps Grid Control (Modern)

The modern replacement for the default read-only grid. Provides filtering, inline editing,
option set color coding, and pagination out of the box.

**ClassId:** `{3B80A7E4-E0C0-4035-BCFE-47B720B85E44}` (PowerAppsGridControl)

### Enable via FormXml (Subgrid on a Form)

```xml
<cell id="{CELL-GUID}" colspan="2">
  <labels><label description="Active Projects" languagecode="1033" /></labels>
  <control id="subgrid_projects" classid="{3B80A7E4-E0C0-4035-BCFE-47B720B85E44}">
    <parameters>
      <TargetEntityType>cnt_project</TargetEntityType>
      <ViewId>{view-guid}</ViewId>
      <EnableEditing>true</EnableEditing>
      <EnableFiltering>true</EnableFiltering>
      <EnableOptionSetColors>true</EnableOptionSetColors>
      <EnableJumpBar>true</EnableJumpBar>
      <AllowNestedGrids>false</AllowNestedGrids>
      <EnablePagination>true</EnablePagination>
    </parameters>
  </control>
</cell>
```

### Key Properties

| Property | Type | Description |
|---|---|---|
| `EnableEditing` | boolean | Allow inline editing of cells directly in the grid |
| `EnableFiltering` | boolean | Show column filter dropdowns in the header row |
| `EnableOptionSetColors` | boolean | Render option set values with their configured colors |
| `EnableJumpBar` | boolean | Show alphabetical jump bar for quick navigation |
| `AllowNestedGrids` | boolean | Enable parent-child drill-down within the grid |
| `EnablePagination` | boolean | Show page controls (vs infinite scroll) |

### Inline Editing Configuration

When `EnableEditing` is `true`, all editable columns in the view are editable by default.
To restrict which columns are editable, configure the view's `layoutxml` with
`disableInlineEditing="1"` on specific `<cell>` elements:

```xml
<layoutxml>
  <grid name="resultset" object="10796" jump="cnt_name" select="1" icon="1" preview="1">
    <row name="result" id="cnt_playerid">
      <cell name="cnt_name" width="200" />
      <cell name="cnt_score" width="150" />
      <cell name="createdon" width="150" disableInlineEditing="1" />
    </row>
  </grid>
</layoutxml>
```

In this example, `cnt_name` and `cnt_score` are editable inline, but `createdon` is read-only.

### Column-Level Formatting

Option set colors are configured on the option set definition itself (each option's `Color` property).
When `EnableOptionSetColors` is `true`, the grid renders colored badges automatically.

For icon-based formatting, use a custom PCF control or configure conditional formatting
through the Maker Portal (Power Apps Grid Control supports basic conditional formatting rules).

## Editable Grid (Legacy)

> ⚠️ **Deprecated March 2026.** Per Microsoft Learn ("important changes coming"), the **Editable Grid** control **and** the legacy **Power Apps read-only grid** control are deprecated — **security fixes only, no new features.** They are **not removed** (the ClassIds below still function in existing apps), but use the **Power Apps Grid Control** (top of this file) for **all new and migrated development**. This deprecation targets the legacy Editable Grid and the legacy read-only grid control — **not** the classic default Subgrid (`{67FAC785-…}`) documented below, which remains the standard read-only subgrid. `[verify-at-use — Microsoft Learn "important changes coming", 2026-06]`

The older editable grid control. Deprecated March 2026 (above); the Power Apps Grid Control is the
replacement for new development.

**ClassId:** `{9CDEA8CD-B23A-4ACA-B5B1-96C89569E7F3}`

### Enable via FormXml

```xml
<cell id="{CELL-GUID}" colspan="2">
  <labels><label description="Task List" languagecode="1033" /></labels>
  <control id="subgrid_tasks" classid="{9CDEA8CD-B23A-4ACA-B5B1-96C89569E7F3}">
    <parameters>
      <TargetEntityType>cnt_task</TargetEntityType>
      <ViewId>{view-guid}</ViewId>
      <RelationshipName>cnt_project_tasks</RelationshipName>
      <EnableViewPicker>true</EnableViewPicker>
      <EnableEditableGrid>true</EnableEditableGrid>
    </parameters>
  </control>
</cell>
```

### Save Modes

The legacy editable grid supports three save modes:

| Mode | Behavior |
|---|---|
| Individual cell | Saves immediately when the user tabs out of a cell |
| Row | Saves when the user moves to another row |
| Manual | User must click a Save button explicitly |

Save mode is configured in the Maker Portal or via the `SaveMode` parameter if supported.

### Key Differences from Power Apps Grid Control

- No built-in filtering UI
- No option set color coding
- No nested grid support
- Less performant with large datasets
- Still useful when you need the specific legacy editable grid events/callbacks

## Nested / Hierarchical Grids

Enable parent-child drill-down within a single grid. The user clicks a parent row and sees
child records expand inline below it.

**Requirement:** The entities must have a 1:N relationship, and the child entity must have
a self-referential relationship OR the grid must be configured with `AllowNestedGrids`.

```xml
<control id="subgrid_hierarchy" classid="{3B80A7E4-E0C0-4035-BCFE-47B720B85E44}">
  <parameters>
    <TargetEntityType>cnt_category</TargetEntityType>
    <ViewId>{view-guid}</ViewId>
    <AllowNestedGrids>true</AllowNestedGrids>
    <EnableEditing>false</EnableEditing>
  </parameters>
</control>
```

Nested grids work best with hierarchical data (e.g., categories with subcategories,
organizational units, task breakdowns).

## Subgrid on Forms

Standard subgrid configuration for embedding related record lists in a main form.
Uses the default read-only grid ClassId.

**ClassId:** `{67FAC785-CD58-4F9F-ABB3-4B7DDC6ED5ED}` (default Subgrid)

```xml
<cell id="{CELL-GUID}" colspan="2">
  <labels><label description="Related Orders" languagecode="1033" /></labels>
  <control id="subgrid_orders" classid="{67FAC785-CD58-4F9F-ABB3-4B7DDC6ED5ED}">
    <parameters>
      <TargetEntityType>cnt_order</TargetEntityType>
      <ViewId>{associated-view-guid}</ViewId>
      <RelationshipName>cnt_customer_orders</RelationshipName>
      <EnableViewPicker>true</EnableViewPicker>
    </parameters>
  </control>
</cell>
```

### Subgrid Parameters

| Parameter | Required | Description |
|---|---|---|
| `TargetEntityType` | Yes | Logical name of the related entity |
| `ViewId` | Yes | GUID of the view to display (must exist before form creation) |
| `RelationshipName` | Yes* | Schema name of the 1:N relationship (*required for related records) |
| `EnableViewPicker` | No | Allow users to switch views. Default: `false` |
| `IsUserView` | No | Show user-created personal views |
| `AutoExpand` | No | Automatically expand the subgrid on form load |

**Note:** For unrelated entity subgrids (e.g., "All Active Contacts" on an Account form),
omit `RelationshipName` and the subgrid shows all records from the target entity filtered
by the specified view.

## Kanban-Style Views

Kanban board views (drag cards between columns) are **not natively supported** as a standard
grid control in Dataverse/Model-Driven Apps. Here are the available approaches:

### Option 1: Custom PCF Dataset Control

Build a custom PCF (PowerApps Component Framework) control that renders a Kanban board.
This is the most flexible approach:

- Create a PCF dataset control that reads records and groups by a choice column
- Implement drag-and-drop to update the choice value
- Register the PCF control and bind it to a view via FormXml `controlDescription`

### Option 2: Code App or HTML Web Resource

Build a standalone drag-and-drop board using React/Vue in a Code App or HTML web resource:

- Query records via the Dataverse Web API
- Group by status/stage column
- Update records on drag-and-drop
- Embed in the model-driven app as a dashboard or form web resource

### Option 3: Board View (Limited Availability)

Power Apps has introduced a Board view type in some environments:

- Available as a view type in the Maker Portal
- Groups records by a choice column into swim lanes
- Limited configuration options compared to custom PCF
- Not available in all regions or license tiers

## Decision Matrix: Which Grid Type to Use

| Requirement | Recommended Grid |
|---|---|
| Read-only list of related records | Default Subgrid (`{67FAC785-...}`) |
| Inline editing with modern UX | Power Apps Grid Control (`{3B80A7E4-...}`) |
| Column filtering and jump bar | Power Apps Grid Control |
| Legacy inline editing (existing apps) | Editable Grid (`{9CDEA8CD-...}`) — **deprecated March 2026**; prefer the Power Apps Grid Control |
| Hierarchical/tree data | Power Apps Grid Control with `AllowNestedGrids` |
| Kanban/board layout | Custom PCF or Code App |
| Option set color coding | Power Apps Grid Control with `EnableOptionSetColors` |
| High-volume data with pagination | Power Apps Grid Control with `EnablePagination` |

## FormXml Examples Summary

### Upgrading an Existing Subgrid to Power Apps Grid Control

Replace the `classid` on the control element:

```xml
<!-- Before: default read-only subgrid -->
<control id="subgrid_items" classid="{67FAC785-CD58-4F9F-ABB3-4B7DDC6ED5ED}">

<!-- After: Power Apps Grid Control with editing -->
<control id="subgrid_items" classid="{3B80A7E4-E0C0-4035-BCFE-47B720B85E44}">
  <parameters>
    <TargetEntityType>cnt_lineitem</TargetEntityType>
    <ViewId>{view-guid}</ViewId>
    <RelationshipName>cnt_order_lineitems</RelationshipName>
    <EnableEditing>true</EnableEditing>
    <EnableFiltering>true</EnableFiltering>
    <EnableOptionSetColors>true</EnableOptionSetColors>
    <EnablePagination>true</EnablePagination>
  </parameters>
</control>
```

### Full Form with Power Apps Grid Control Subgrid

```xml
<form>
  <tabs>
    <tab name="general" id="{TAB-GUID}" IsUserDefined="1" locklevel="0" showlabel="true" expanded="true">
      <labels><label description="General" languagecode="1033" /></labels>
      <columns>
        <column width="100%">
          <sections>
            <section name="info" id="{SEC-1-GUID}" IsUserDefined="1" showlabel="true" showbar="false" columns="2">
              <labels><label description="Details" languagecode="1033" /></labels>
              <rows>
                <row><cell id="{CELL-1}"><labels><label description="Name" languagecode="1033" /></labels>
                  <control id="cnt_name" classid="{4273EDBD-AC1D-40D3-9FB2-095C621B552D}" datafieldname="cnt_name" /></cell></row>
              </rows>
            </section>
            <section name="grid_section" id="{SEC-2-GUID}" IsUserDefined="1" showlabel="true" showbar="false" columns="1">
              <labels><label description="Line Items" languagecode="1033" /></labels>
              <rows>
                <row><cell id="{CELL-2}" colspan="1">
                  <labels><label description="Items" languagecode="1033" /></labels>
                  <control id="subgrid_items" classid="{3B80A7E4-E0C0-4035-BCFE-47B720B85E44}">
                    <parameters>
                      <TargetEntityType>cnt_lineitem</TargetEntityType>
                      <ViewId>{view-guid}</ViewId>
                      <RelationshipName>cnt_order_lineitems</RelationshipName>
                      <EnableEditing>true</EnableEditing>
                      <EnableFiltering>true</EnableFiltering>
                      <EnableOptionSetColors>true</EnableOptionSetColors>
                      <EnablePagination>true</EnablePagination>
                    </parameters>
                  </control>
                </cell></row>
              </rows>
            </section>
          </sections>
        </column>
      </columns>
    </tab>
  </tabs>
</form>
```
