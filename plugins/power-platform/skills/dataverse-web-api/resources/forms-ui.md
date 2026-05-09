# Forms (SystemForm)

The Dataverse UI is data-driven, defined by XML stored in the `systemform` table.
Programmatic form creation requires constructing valid FormXml.

**Entity Set:** `systemforms`

## Form Types

| Type Code | Name | Description |
|---|---|---|
| 2 | Main | Primary editing interface with tabs, sections, subgrids |
| 6 | Quick View | Read-only embedded form in parent records |
| 7 | Quick Create | Simplified strip for rapid data entry |
| 11 | Card | Used in Unified Interface views and mobile lists |

## Create a Main Form

```http
POST [org-url]/api/data/v9.2/systemforms
MSCRM.SolutionUniqueName: ContosoHRModule
Content-Type: application/json; charset=utf-8
OData-Version: 4.0

{
  "name": "Project Main Form",
  "description": "Primary form for project management",
  "objecttypecode": "cnt_project",
  "type": 2,
  "formxml": "<form><tabs><tab name='general' id='{TAB-GUID}' IsUserDefined='1' locklevel='0' showlabel='true' expanded='true'><labels><label description='General' languagecode='1033' /></labels><columns><column width='100%'><sections><section name='general_section' id='{SECTION-GUID}' IsUserDefined='1' showlabel='true' showbar='false' columns='2'><labels><label description='General Information' languagecode='1033' /></labels><rows><row><cell id='{CELL-GUID-1}'><labels><label description='Project Name' languagecode='1033' /></labels><control id='cnt_projectname' classid='{4273EDBD-AC1D-40D3-9FB2-095C621B552D}' datafieldname='cnt_projectname' /></cell><cell id='{CELL-GUID-2}'><labels><label description='Start Date' languagecode='1033' /></labels><control id='cnt_startdate' classid='{5B773807-9FB2-42DB-97C3-7A91EFF8ADFF}' datafieldname='cnt_startdate' /></cell></row><row><cell id='{CELL-GUID-3}'><labels><label description='Budget' languagecode='1033' /></labels><control id='cnt_budget' classid='{533B9E00-756B-4312-95A0-DC888F4EADCF}' datafieldname='cnt_budget' /></cell><cell id='{CELL-GUID-4}'><labels><label description='Priority' languagecode='1033' /></labels><control id='cnt_priority' classid='{3EF39988-22BB-4F0B-BBBE-64B5A3748AEE}' datafieldname='cnt_priority' /></cell></row></rows></section></sections></column></columns></tab></tabs></form>"
}
```

## FormXml Hierarchy

```
<form>
  └─ <tabs>
       └─ <tab>                    ← Horizontal divisions (like tab strips)
            ├─ <labels>            ← Tab display name
            └─ <columns>
                 └─ <column>       ← Layout columns (1, 2, or 3)
                      └─ <sections>
                           └─ <section>   ← Vertical groups of fields
                                ├─ <labels>
                                └─ <rows>
                                     └─ <row>
                                          └─ <cell>
                                               ├─ <labels>
                                               └─ <control>  ← Bound to a column
```

## Control Element

The `<control>` element binds a UI control to a data field:

```xml
<control id="cnt_projectname" classid="{4273EDBD-AC1D-40D3-9FB2-095C621B552D}" datafieldname="cnt_projectname" />
```

| Attribute | Description |
|---|---|
| `id` | Unique control identifier |
| `classid` | GUID of the control type (determines rendering) |
| `datafieldname` | Logical name of the bound attribute |

### Common Control Class IDs

| ClassID | Control Type |
|---|---|
| `{4273EDBD-AC1D-40D3-9FB2-095C621B552D}` | Single-line text |
| `{5B773807-9FB2-42DB-97C3-7A91EFF8ADFF}` | DateTime |
| `{533B9E00-756B-4312-95A0-DC888F4EADCF}` | Money / Currency |
| `{3EF39988-22BB-4F0B-BBBE-64B5A3748AEE}` | Picklist (Choice) |
| `{B0C6723A-8503-4FD7-BB28-C8A06AC933C2}` | Boolean (Two Options) |
| `{C3EFE0C3-0EC6-42BE-8349-CBD9079DFD8E}` | Lookup |
| `{E7A81278-8635-4D9E-8D4D-59480B391C5B}` | Multi-line text (Memo) |
| `{270BD3DB-D9AF-4782-9025-509E298DEC0A}` | Integer |
| `{67FAC785-CD58-4F9F-ABB3-4B7DDC6ED5ED}` | Subgrid |
| `{62B0DF79-0464-470F-8AC7-4A5D44D5F2E5}` | Notes (Timeline) |

## Subgrid Control

To embed a list of related records in a form:

```xml
<cell id='{CELL-GUID}'>
  <labels><label description='Related Tasks' languagecode='1033' /></labels>
  <control id='subgrid_tasks' classid='{67FAC785-CD58-4F9F-ABB3-4B7DDC6ED5ED}'>
    <parameters>
      <TargetEntityType>task</TargetEntityType>
      <ViewId>{view-guid}</ViewId>
      <RelationshipName>cnt_project_tasks</RelationshipName>
      <EnableViewPicker>true</EnableViewPicker>
    </parameters>
  </control>
</cell>
```

## Quick Create Form (type 7)

Simpler structure -- typically a single section:

```json
{
  "name": "Project Quick Create",
  "objecttypecode": "cnt_project",
  "type": 7,
  "formxml": "<form><tabs><tab name='general'><columns><column><sections><section name='quickcreate'><rows><row><cell><control id='cnt_projectname' classid='{4273EDBD-AC1D-40D3-9FB2-095C621B552D}' datafieldname='cnt_projectname' /></cell></row><row><cell><control id='cnt_priority' classid='{3EF39988-22BB-4F0B-BBBE-64B5A3748AEE}' datafieldname='cnt_priority' /></cell></row></rows></section></sections></column></columns></tab></tabs></form>"
}
```

## Practical Pattern: Template-Based Form Creation

Programmatically generating FormXml from scratch is complex. A recommended pattern:

1. **Retrieve** an existing form's XML: `GET /systemforms({guid})?$select=formxml`
2. **Parse** the XML string
3. **Inject** new tabs, sections, or controls
4. **POST** the modified XML as a new form record

This avoids manually constructing valid GUIDs and ensures structural correctness.

## After Creating/Updating Forms

Always call `PublishXml` to make form changes visible to users:

```http
POST [org-url]/api/data/v9.2/PublishXml
{ "ParameterXml": "<importexportxml><entities><entity>cnt_project</entity></entities></importexportxml>" }
```

## Multi-Tab Form Structure

Complex entities benefit from multiple tabs. Each tab, section, and cell needs a unique GUID.

```xml
<form>
  <tabs>
    <tab name="general" id="{TAB-1-GUID}" IsUserDefined="1" locklevel="0" showlabel="true" expanded="true">
      <labels><label description="General" languagecode="1033" /></labels>
      <columns>
        <column width="100%">
          <sections>
            <section name="info" id="{SEC-1-GUID}" IsUserDefined="1" showlabel="true" showbar="false" columns="2">
              <labels><label description="General Information" languagecode="1033" /></labels>
              <rows>
                <!-- Field rows here -->
              </rows>
            </section>
          </sections>
        </column>
      </columns>
    </tab>
    <tab name="details" id="{TAB-2-GUID}" IsUserDefined="1" locklevel="0" showlabel="true" expanded="true">
      <labels><label description="Details" languagecode="1033" /></labels>
      <!-- Second tab content -->
    </tab>
    <tab name="related" id="{TAB-3-GUID}" IsUserDefined="1" locklevel="0" showlabel="true" expanded="true">
      <labels><label description="Related Records" languagecode="1033" /></labels>
      <!-- Subgrids for related records -->
    </tab>
  </tabs>
</form>
```

**Key rules:**
- Every `<tab>`, `<section>`, and `<cell>` needs a unique `id='{guid}'`
- Use PowerShell `[guid]::NewGuid()` to generate GUIDs dynamically
- `IsUserDefined='1'` is required on tabs and sections for custom forms
- `columns` attribute on `<section>` controls the column layout (1, 2, or 3)

## Subgrid Controls (Detailed)

Embed a list of related records in a form. **The associated view MUST be created first.**

```xml
<cell id="{CELL-GUID}" colspan="2">
  <labels><label description="Game Scores" languagecode="1033" /></labels>
  <control id="subgrid_scores" classid="{67FAC785-CD58-4F9F-ABB3-4B7DDC6ED5ED}">
    <parameters>
      <TargetEntityType>pic_gamescore</TargetEntityType>
      <ViewId>{associated-view-guid}</ViewId>
      <RelationshipName>pic_Player_GameScores</RelationshipName>
      <EnableViewPicker>true</EnableViewPicker>
    </parameters>
  </control>
</cell>
```

**Parameters:**
| Parameter | Description |
|---|---|
| `TargetEntityType` | Logical name of the related entity |
| `ViewId` | GUID of the view to display (must exist before creating the form) |
| `RelationshipName` | Schema name of the relationship |
| `EnableViewPicker` | Allow users to switch between views |

## Quick View Controls

Embed read-only fields from a related (parent) record inline on the current form:

```xml
<cell id="{CELL-GUID}">
  <labels><label description="Player Details" languagecode="1033" /></labels>
  <control id="quickview_player" classid="{5C5600E0-1D6E-4205-A272-BE80DA87FD42}">
    <parameters>
      <QuickForms>{quick-view-form-guid}</QuickForms>
      <RelationshipName>pic_Player_GameScores</RelationshipName>
    </parameters>
  </control>
</cell>
```

Use when you want to show parent record details (e.g., player name and stats) on a child record form
(e.g., game score) without navigating away.

## Quick Create Forms (Detailed)

Type 7 forms with minimal structure. Keep to 3-5 fields max.

```json
{
  "name": "Score Quick Create",
  "objecttypecode": "pic_gamescore",
  "type": 7,
  "formxml": "<form><tabs><tab name='general'><columns><column><sections><section name='quickcreate'><rows><row><cell><control id='pic_score' classid='{270BD3DB-D9AF-4782-9025-509E298DEC0A}' datafieldname='pic_score' /></cell></row><row><cell><control id='pic_difficulty' classid='{3EF39988-22BB-4F0B-BBBE-64B5A3748AEE}' datafieldname='pic_difficulty' /></cell></row><row><cell><control id='pic_player' classid='{C3EFE0C3-0EC6-42BE-8349-CBD9079DFD8E}' datafieldname='pic_player' /></cell></row></rows></section></sections></column></columns></tab></tabs></form>"
}
```

**Quick Create rules:**
- **`IsUserDefined='1'` IS required** on tabs and sections (despite appearing simpler)
- **`<labels>` elements ARE required** on tabs and sections
- **`width='100%'` IS required** on `<column>` elements
- **Unique `id='{guid}'`** is required on `<tab>`, `<section>`, and `<cell>` elements
- Single section, single column layout
- Only include fields essential for record creation
- Lookup fields auto-populate when created from a parent record's subgrid

**Corrected minimal quick create XML:**
```xml
<form><tabs><tab name='general' id='{TAB-GUID}' IsUserDefined='1'><labels><label description='General' languagecode='1033' /></labels><columns><column width='100%'><sections><section name='quickcreate' id='{SECTION-GUID}' IsUserDefined='1' columns='1'><labels><label description='Quick Create' languagecode='1033' /></labels><rows><row><cell id='{CELL-GUID}'><labels><label description='Name' languagecode='1033' /></labels><control id='cnt_name' classid='{4273EDBD-AC1D-40D3-9FB2-095C621B552D}' datafieldname='cnt_name' /></cell></row></rows></section></sections></column></columns></tab></tabs></form>
```

## Complete Control ClassID Reference

| ClassID | Control Type | Use For |
|---|---|---|
| `{4273EDBD-AC1D-40D3-9FB2-095C621B552D}` | Single-line text | Names, titles, short strings |
| `{E7A81278-8635-4D9E-8D4D-59480B391C5B}` | Multi-line text (Memo) | Descriptions, notes |
| `{5B773807-9FB2-42DB-97C3-7A91EFF8ADFF}` | DateTime | Dates and times |
| `{533B9E00-756B-4312-95A0-DC888F4EADCF}` | Money / Currency | Financial values |
| `{3EF39988-22BB-4F0B-BBBE-64B5A3748AEE}` | Picklist (Choice) | Option sets, dropdowns |
| `{B0C6723A-8503-4FD7-BB28-C8A06AC933C2}` | Boolean (Two Options) | Yes/No toggles |
| `{C3EFE0C3-0EC6-42BE-8349-CBD9079DFD8E}` | Lookup | Related record references |
| `{270BD3DB-D9AF-4782-9025-509E298DEC0A}` | Integer (Whole Number) | Counts, quantities |
| `{0D2C745A-E5A8-4C8F-BA63-C6D3BB604660}` | Float | Decimal numbers |
| `{67FAC785-CD58-4F9F-ABB3-4B7DDC6ED5ED}` | Subgrid | Related record lists |
| `{62B0DF79-0464-470F-8AC7-4A5D44D5F2E5}` | Notes (Timeline) | Activity timeline |
| `{5C5600E0-1D6E-4205-A272-BE80DA87FD42}` | Quick View Form | Embedded related record |
| `{9FDF5F91-88B1-47f4-AD53-C11EFC01A01D}` | Web Resource | Custom HTML/JS control |
| `{9C5CA0A1-AB4D-4781-BE7E-8DFBE867B8A2}` | Timer | Countdown/SLA timer |

## JavaScript Web Resource Events on Forms

Register form event handlers via the `<events>` and `<clientresources>` elements in FormXml:

```xml
<form>
  <tabs><!-- ... form content ... --></tabs>
  <events>
    <event name="onload" application="false" active="true">
      <Handlers>
        <Handler functionName="MyNamespace.onFormLoad" libraryName="cnt_/js/formscript.js"
                 handlerUniqueId="{HANDLER-GUID}" enabled="true" parameters="" passExecutionContext="true" />
      </Handlers>
    </event>
    <event name="onsave" application="false" active="true">
      <Handlers>
        <Handler functionName="MyNamespace.onFormSave" libraryName="cnt_/js/formscript.js"
                 handlerUniqueId="{HANDLER-GUID}" enabled="true" parameters="" passExecutionContext="true" />
      </Handlers>
    </event>
  </events>
  <clientresources>
    <iabordenavigationgroup>
      <clientIncludes>
        <clientInclude src="$webresource:cnt_/js/formscript.js" type="JScript" />
      </clientIncludes>
    </iabordenavigationgroup>
  </clientresources>
</form>
```

**Event types:** `onload`, `onsave`, `onchange` (field-level, registered on the control)

## Form Design Best Practices

- **Group related fields** into logical sections (e.g., "Player Info", "Statistics", "Score History")
- **Multiple tabs** for complex entities — first tab has the most important data
- **Separate read-only fields** (rollups, computed, audit) from editable fields
- **Include subgrids** for related records — makes the form a complete dashboard
- **Quick Create**: only 3-5 essential fields for rapid data entry
- **Consider user flow**: what fields do users need to see/fill first?
- **Logical tab ordering**: most-used tab first, configuration/admin last

## Advanced Control Bindings

Beyond the standard control ClassIDs, Dataverse forms support advanced controls via the
`controlDescription` and `controlDescriptions` pattern in FormXml. This pattern associates
a custom or specialized control with a standard form cell.

**WARNING:** The `controlDescription` element as a direct child of `<control>` may fail with:
`The element 'control' has invalid child element 'controlDescription'. List of possible elements
expected: 'labels, parameters'.` This is a known inconsistency — the XML schema validation
rejects it even though the documentation shows it. **Recommended approach:** Create forms with
basic controls first (standard classid-based), then use the Maker Portal or form customization
API to apply advanced controls (Toggle, RichText, Star Rating) afterwards.

### Rich Text Editor Control

Bind the `RichTextEditorControl` to a memo field with `FormatName: "RichText"` for a
full-featured rich text editing experience with toolbar (bold, italic, lists, links, images).

```xml
<cell id="{CELL-GUID}">
  <labels><label description="Detailed Notes" languagecode="1033" /></labels>
  <control id="cnt_detailednotes" classid="{E7A81278-8635-4D9E-8D4D-59480B391C5B}" datafieldname="cnt_detailednotes">
    <controlDescription forControl="cnt_detailednotes">
      <customControl name="MscrmControls.RichTextEditor.RichTextEditorControl" formFactor="0">
        <parameters>
          <value type="SingleLine.Text">cnt_detailednotes</value>
        </parameters>
      </customControl>
      <customControl name="MscrmControls.RichTextEditor.RichTextEditorControl" formFactor="1">
        <parameters>
          <value type="SingleLine.Text">cnt_detailednotes</value>
        </parameters>
      </customControl>
      <customControl name="MscrmControls.RichTextEditor.RichTextEditorControl" formFactor="2">
        <parameters>
          <value type="SingleLine.Text">cnt_detailednotes</value>
        </parameters>
      </customControl>
    </controlDescription>
  </control>
</cell>
```

**Notes:**
- The base `classid` remains the standard Memo ClassId `{E7A81278-...}`
- `formFactor` values: `0` = all, `1` = tablet, `2` = phone. Specify multiple `customControl`
  elements for responsive behavior, or use `0` for all form factors.
- The `controlDescription` element wraps the `customControl` and must reference the control `id`
  via the `forControl` attribute.

### Address Input Control

Bind the composite address control to a street field, mapping individual address columns:

```xml
<cell id="{CELL-GUID}">
  <labels><label description="Mailing Address" languagecode="1033" /></labels>
  <control id="cnt_street" classid="{4273EDBD-AC1D-40D3-9FB2-095C621B552D}" datafieldname="cnt_street">
    <controlDescription forControl="cnt_street">
      <customControl name="Microsoft.AddressInputUCI" formFactor="0">
        <parameters>
          <Street type="SingleLine.Text">cnt_street</Street>
          <City type="SingleLine.Text">cnt_city</City>
          <State type="SingleLine.Text">cnt_state</State>
          <ZipPostal type="SingleLine.Text">cnt_postalcode</ZipPostal>
          <Country type="SingleLine.Text">cnt_country</Country>
          <Latitude type="FP">cnt_latitude</Latitude>
          <Longitude type="FP">cnt_longitude</Longitude>
        </parameters>
      </customControl>
    </controlDescription>
  </control>
</cell>
```

**Notes:**
- All referenced columns (`cnt_street`, `cnt_city`, etc.) must exist before creating the form
- The control provides Bing Maps autocomplete when environment settings enable it
- `Latitude` and `Longitude` are optional -- include only if you have Double columns for geolocation

### PCF Control Binding on Forms

Bind any PCF (PowerApps Component Framework) custom control to a form field using the
`controlDescription` pattern:

```xml
<cell id="{CELL-GUID}">
  <labels><label description="Progress" languagecode="1033" /></labels>
  <control id="cnt_progress" classid="{270BD3DB-D9AF-4782-9025-509E298DEC0A}" datafieldname="cnt_progress">
    <controlDescription forControl="cnt_progress">
      <customControl name="contoso_Contoso.ProgressBar" formFactor="0">
        <parameters>
          <value type="Whole.None">cnt_progress</value>
          <maxValue type="Whole.None" static="true">100</maxValue>
          <color type="SingleLine.Text" static="true">#0078D4</color>
        </parameters>
      </customControl>
    </controlDescription>
  </control>
</cell>
```

**Key points:**
- `name` is the PCF manifest name in format `{publisher}_{namespace}.{ControlName}`
- Parameters map to the PCF manifest's `property` elements
- Use `static="true"` for constant values that are not bound to a column
- The `type` attribute must match the PCF manifest's property type
- `formFactor="0"` applies to all form factors (web, tablet, phone)

### Power BI Embed on Forms

Embed a Power BI report directly on a model-driven app form using the `PowerBIControl`:

**ClassId:** `{8C54228C-1B25-4909-A12A-F2B968BB592F}` (PowerBIControl)

```xml
<cell id="{CELL-GUID}" colspan="2" rowspan="6">
  <labels><label description="Project Analytics" languagecode="1033" /></labels>
  <control id="powerbi_analytics" classid="{8C54228C-1B25-4909-A12A-F2B968BB592F}">
    <parameters>
      <PowerBIGroupId>{workspace-guid}</PowerBIGroupId>
      <PowerBIReportId>{report-guid}</PowerBIReportId>
      <TileUrl>https://app.powerbi.com/reportEmbed</TileUrl>
      <PowerBIFilter>{"Filter": "[Table]/[Column] eq '[fieldvalue]'"}</PowerBIFilter>
    </parameters>
  </control>
</cell>
```

**Notes:**
- The Power BI workspace must be shared with the app users
- Use `PowerBIFilter` to filter the report by the current record's field values
- Power BI Embedded license or Pro license is required for users
- The cell should have `colspan` and `rowspan` for adequate display space
- No `datafieldname` needed -- this is a display-only control

### Timer Control

Display a countdown or elapsed timer on forms, commonly used for SLA tracking.

**ClassId:** `{9C5CA0A1-AB4D-4781-BE7E-8DFBE867B8A2}` (Timer Control)

```xml
<cell id="{CELL-GUID}" colspan="2">
  <labels><label description="SLA Timer" languagecode="1033" /></labels>
  <control id="timer_sla" classid="{9C5CA0A1-AB4D-4781-BE7E-8DFBE867B8A2}">
    <parameters>
      <TimerType>Countdown</TimerType>
      <FailureTimeField>cnt_sladuedate</FailureTimeField>
      <WarningTimeField>cnt_slawarningdate</WarningTimeField>
      <SuccessCondition>
        <Condition field="cnt_status" operator="eq" value="100000002" />
      </SuccessCondition>
      <FailureCondition>
        <Condition field="cnt_status" operator="eq" value="100000003" />
      </FailureCondition>
      <PauseCondition>
        <Condition field="cnt_status" operator="eq" value="100000001" />
      </PauseCondition>
    </parameters>
  </control>
</cell>
```

**Properties:**
| Parameter | Description |
|---|---|
| `TimerType` | `Countdown` (time remaining) or `CountUp` (time elapsed) |
| `FailureTimeField` | DateTime field representing the deadline |
| `WarningTimeField` | DateTime field for the warning threshold |
| `SuccessCondition` | Condition that stops the timer with a success state |
| `FailureCondition` | Condition that stops the timer with a failure state |
| `PauseCondition` | Condition that pauses the timer (e.g., "On Hold" status) |

### Iframe Control

Embed external web content in a form using an inline frame.

```xml
<cell id="{CELL-GUID}" colspan="2" rowspan="4">
  <labels><label description="External Dashboard" languagecode="1033" /></labels>
  <control id="iframe_dashboard" classid="{FD2A7985-3187-4571-97AE-C4D19B0FCB86}">
    <parameters>
      <Url>https://app.example.com/dashboard</Url>
      <Security>true</Security>
      <Scrolling>auto</Scrolling>
      <Border>true</Border>
      <PassParameters>true</PassParameters>
    </parameters>
  </control>
</cell>
```

**ClassId:** `{FD2A7985-3187-4571-97AE-C4D19B0FCB86}` (IFrame)

**Parameters:**
| Parameter | Description |
|---|---|
| `Url` | The external URL to embed |
| `Security` | `true` to restrict cross-frame scripting |
| `Scrolling` | `auto`, `yes`, or `no` for scrollbar behavior |
| `Border` | Show or hide the iframe border |
| `PassParameters` | When `true`, appends record context to the URL query string: `id`, `orgname`, `type`, `typename`, `userlcid` |

**Security restrictions:**
- The external URL must be in the organization's allowed iframe origins
- Cross-origin scripting is blocked by default (`Security: true`)
- Record context is passed as query parameters only when `PassParameters` is `true`
- The iframe URL receives: `?id={recordid}&orgname={orgname}&type={entitytypecode}&typename={entitylogicalname}&userlcid={lcid}`

### Toggle / Flip Switch

Bind a Boolean (Yes/No) field to a toggle switch instead of the default checkbox:

```xml
<cell id="{CELL-GUID}">
  <labels><label description="Is Active" languagecode="1033" /></labels>
  <control id="cnt_isactive" classid="{B0C6723A-8503-4FD7-BB28-C8A06AC933C2}" datafieldname="cnt_isactive">
    <controlDescription forControl="cnt_isactive">
      <customControl name="MscrmControls.FieldControls.ToggleControl" formFactor="0">
        <parameters>
          <value type="TwoOptions">cnt_isactive</value>
        </parameters>
      </customControl>
    </controlDescription>
  </control>
</cell>
```

**Notes:**
- The base `classid` remains the Boolean ClassId `{B0C6723A-...}`
- The `customControl` name is `MscrmControls.FieldControls.ToggleControl`
- Renders as a sliding toggle switch instead of a checkbox
- No additional configuration needed -- True/False labels come from the option set definition

### Star Rating

Bind an integer or decimal field to a star rating control for visual numeric input:

```xml
<cell id="{CELL-GUID}">
  <labels><label description="Customer Rating" languagecode="1033" /></labels>
  <control id="cnt_rating" classid="{270BD3DB-D9AF-4782-9025-509E298DEC0A}" datafieldname="cnt_rating">
    <controlDescription forControl="cnt_rating">
      <customControl name="MscrmControls.FieldControls.RatingControl" formFactor="0">
        <parameters>
          <value type="Whole.None">cnt_rating</value>
          <max type="Whole.None" static="true">5</max>
        </parameters>
      </customControl>
    </controlDescription>
  </control>
</cell>
```

**Notes:**
- The base `classid` is the Integer ClassId `{270BD3DB-...}` (or Decimal for non-integer ratings)
- `max` defines the number of stars (typically 5 or 10)
- The integer value maps directly to the number of filled stars
- Works best with `MinValue: 0` and `MaxValue: 5` (or matching the `max` parameter)

## Updated Control ClassIDs Reference Table

The following table adds new control GUIDs not covered in the Complete Control ClassID Reference
table above. Refer to both tables for the full set.

| ClassID | Control Type | Use For |
|---|---|---|
| `{3B80A7E4-E0C0-4035-BCFE-47B720B85E44}` | Power Apps Grid Control | Modern grid with editing, filtering, colors |
| `{9CDEA8CD-B23A-4ACA-B5B1-96C89569E7F3}` | Editable Grid (Legacy) | Legacy inline editing grid |
| `{8C54228C-1B25-4909-A12A-F2B968BB592F}` | Power BI Control | Embedded Power BI reports on forms |
| `{FD2A7985-3187-4571-97AE-C4D19B0FCB86}` | IFrame | External web content embedding |

The following are bound via `controlDescription` (no separate ClassId -- they override a base control):

| Custom Control Name | Type | Use For |
|---|---|---|
| `MscrmControls.RichTextEditor.RichTextEditorControl` | Rich Text Editor | Full HTML editing for memo fields |
| `MscrmControls.FieldControls.ToggleControl` | Toggle / Flip Switch | Visual toggle for Yes/No fields |
| `MscrmControls.FieldControls.RatingControl` | Star Rating | Visual star rating for integer/decimal fields |
| `Microsoft.AddressInputUCI` | Address Input | Composite address entry with autocomplete |

## Embedded Canvas App on Forms

Canvas apps can be embedded directly in model-driven forms for custom UX. Requires the classic form designer.

### Setup (Classic Designer)
1. Select a column position, drag a column from Field Explorer
2. Double-click it, go to the **Controls** tab
3. Click "Add Control...", select "Canvas app", click Add
4. Enable for Web/Phone/Tablet
5. Click "Customize" to create the canvas app

### Integration Object: `ModelDrivenFormIntegration`
- `.Item` property carries current record column data (READ-ONLY)
- `.OnDataRefresh` fires when the selected record changes

### Host Form Actions (callable from canvas app)
| Action | Description |
|---|---|
| `SaveForm()` | Save the host form |
| `RefreshForm(false)` | Refresh host form data |
| `NavigateToMainForm(entity, formName, recordId)` | Navigate to another form |
| `NavigateToView(entity, viewName)` | Navigate to a view |
| `OpenQuickCreateForm(entity)` | Open quick create dialog |

### Critical Limitations
- `ModelDrivenFormIntegration.Item` is **READ-ONLY**; use Dataverse connector to write back
- Does NOT provide related table column values; use `LookUp`/`Filter` expressions
- Max **3 embedded canvas apps** for web client; **1 for tablet/phone**
- Must publish canvas app AND MDA form separately
- Always bind to a **required column** with a guaranteed value
- NOT displayed when creating new records (requires existing row context)
- Canvas app ID changes per environment — store in config table or environment variable

## Interactive Dashboards

Two layout types for data-driven, real-time filtering:
- **Multi-stream**: Multiple views from one or more entities
- **Single-stream**: Focused view with stream on left, charts/tiles on right

Configuration requires a date field and time frame for the top filter section.
Users can click items to interactively filter other dashboard components.

**GOTCHA**: Interactive dashboards cannot be created from the modern solution UI — must use the classic solution editor.

## Chart Color Customization

Color codes can be applied to **Choice**, **Yes/No**, and **Status Reason** column types only.
Set color codes per option value (e.g., green=Approved, yellow=In Progress, red=Rejected).
Configure via column properties in the Maker Portal.
