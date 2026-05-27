# ControlManifest.Input.xml Reference

The `ControlManifest.Input.xml` file is the declaration file for every PCF control. It defines the control's identity, properties, data bindings, required resources, and platform features. The PCF build pipeline reads this file to generate TypeScript interfaces (`IInputs`, `IOutputs`) and validate the control at compile time.

---

## `<control>` Element

The root element that identifies the control.

```xml
<control
  namespace="MyCompany.Controls"
  constructor="MyControl"
  version="1.0.0"
  display-name-key="MyControl_DisplayName"
  description-key="MyControl_Description"
  control-type="standard | virtual"
>
  <!-- child elements -->
</control>
```

| Attribute | Required | Description |
|---|---|---|
| `namespace` | Yes | Dot-separated namespace (e.g., `Contoso.Controls`). Combined with `constructor` to form the unique control identifier. |
| `constructor` | Yes | The TypeScript class name that implements `StandardControl` or `ReactControl`. |
| `version` | Yes | Semantic version (`major.minor.patch`). Increment on every update. |
| `display-name-key` | Yes | Key into the .resx file for the display name shown in the customization UI. |
| `description-key` | Yes | Key into the .resx file for the description shown in the customization UI. |
| `control-type` | No | `"standard"` (default) for DOM-based controls. `"virtual"` for React virtual controls. When `virtual`, the control class must implement `ReactControl` and `updateView()` must return a `React.ReactElement`. |

---

## `<type-group>` Element

Allows a single property to accept multiple column types. Define a type group and reference it from a property's `of-type-group` attribute.

```xml
<type-group name="numericTypes">
  <type>Whole.None</type>
  <type>Decimal</type>
  <type>FP</type>
  <type>Currency</type>
</type-group>

<property name="value" display-name-key="Value" of-type-group="numericTypes" usage="bound" required="true" />
```

The control can then be bound to any column matching one of the types in the group. At runtime, check `context.parameters.value.type` to determine which specific type was bound.

---

## `<property>` Element

Declares an input or output property for the control.

```xml
<property
  name="value"
  display-name-key="Value_DisplayName"
  description-key="Value_Description"
  of-type="Whole.None"
  usage="bound"
  required="true"
  default-value="0"
/>
```

| Attribute | Required | Description |
|---|---|---|
| `name` | Yes | Property name. Used in code as `context.parameters.<name>`. Must be valid TypeScript identifier. |
| `display-name-key` | Yes | Localization key for the property label in the customization UI. |
| `description-key` | No | Localization key for the property description/tooltip. |
| `of-type` | Yes* | The data type. See Property Type Reference below. *Use `of-type-group` instead to accept multiple types. |
| `of-type-group` | Yes* | Reference to a `<type-group>` name. *Mutually exclusive with `of-type`. |
| `usage` | Yes | `"bound"` = bound to a column (read/write, appears in IInputs and IOutputs). `"input"` = configuration-only parameter (read-only, appears only in IInputs). |
| `required` | Yes | `"true"` or `"false"`. Whether the property must be configured when adding the control to a form. |
| `default-value` | No | Default value used when no column is bound or no value is configured. |

### Property Type Reference

| `of-type` Value | Maps To | Description |
|---|---|---|
| `SingleLine.Text` | `string` | Single line of text (max 4000 chars) |
| `SingleLine.Email` | `string` | Email-formatted text |
| `SingleLine.Phone` | `string` | Phone-formatted text |
| `SingleLine.URL` | `string` | URL-formatted text |
| `SingleLine.Ticker` | `string` | Stock ticker symbol text |
| `SingleLine.TextArea` | `string` | Single line text shown as text area |
| `Multiple` | `string` | Multiple lines of text / Memo (up to 1,048,576 chars) |
| `Whole.None` | `number` | Whole number (integer), no specific format |
| `Whole.Duration` | `number` | Duration in minutes |
| `Whole.Language` | `number` | Language code |
| `Whole.TimeZone` | `number` | Timezone code |
| `Decimal` | `number` | Decimal number (up to 10 decimal places) |
| `FP` | `number` | Floating point number |
| `Currency` | `number` | Currency-formatted decimal |
| `TwoOptions` | `boolean` | Boolean / Yes-No / Two Options |
| `DateAndTime.DateOnly` | `Date` | Date without time component |
| `DateAndTime.DateAndTime` | `Date` | Date with time component |
| `OptionSet` | `number` | Choice / Option set (value is the numeric option value) |
| `MultiSelectOptionSet` | `number[]` | Multi-select choice (array of numeric option values) |
| `Lookup.Simple` | `EntityReference` | Lookup to a single entity type |
| `Enum` | `number` | Enumeration value |

---

## `<data-set>` Element

Used in dataset controls to declare the dataset binding. Replaces `<property>` for the primary data source.

```xml
<data-set
  name="dataSet"
  display-name-key="DataSet_DisplayName"
  description-key="DataSet_Description"
  cds-data-set-options="displayCommandBar:true;displayViewSelector:true"
>
  <property-set
    name="titleColumn"
    display-name-key="Title_Column"
    description-key="Column to use as card title"
    of-type="SingleLine.Text"
    usage="input"
    required="true"
  />
  <property-set
    name="dateColumn"
    display-name-key="Date_Column"
    description-key="Column to use for date positioning"
    of-type="DateAndTime.DateAndTime"
    usage="input"
    required="false"
  />
</data-set>
```

| Attribute | Required | Description |
|---|---|---|
| `name` | Yes | Dataset name. Used as `context.parameters.<name>` in code. Conventionally `"dataSet"`. |
| `display-name-key` | Yes | Localization key for the dataset label. |
| `description-key` | No | Localization key for the dataset description. |
| `cds-data-set-options` | No | Semicolon-separated options: `displayCommandBar:true/false`, `displayViewSelector:true/false`. Controls whether the platform renders the command bar and view selector above the control. |

### `<property-set>` (Child of `<data-set>`)

Declares configurable column mappings within the dataset. These are input parameters that let the form customizer specify which columns map to which roles in your control.

| Attribute | Required | Description |
|---|---|---|
| `name` | Yes | Property set name. Accessed via dataset column configuration. |
| `display-name-key` | Yes | Localization key for the label. |
| `of-type` | Yes | Expected column type (same values as `<property>` `of-type`). |
| `usage` | Yes | Typically `"input"` for column mapping configuration. `"bound"` is also valid for primary value columns. |
| `required` | Yes | Whether this column mapping must be configured. |

---

## `<resources>` Element

Declares all files the control needs at runtime.

```xml
<resources>
  <code path="index.ts" order="1" />
  <css path="css/MyControl.css" order="1" />
  <resx path="strings/MyControl.1033.resx" version="1.0.0" />
  <img path="img/icon.png" />
  <platform-library name="React" version="16.14.0" />
  <platform-library name="Fluent" version="9.46.2" />
</resources>
```

| Element | Purpose |
|---|---|
| `<code path="index.ts" order="1" />` | The entry point TypeScript file. Always `index.ts` with order `1`. |
| `<css path="..." order="N" />` | CSS files to include. Order determines load sequence. |
| `<resx path="..." version="..." />` | Resource files for localization (`.resx` format). The `1033` convention = English locale. |
| `<img path="..." />` | Image files (icons, graphics) used by the control. |
| `<platform-library name="React" version="..." />` | **Required for virtual controls.** Declares that the platform should provide React. Do NOT bundle your own React — the platform hosts it. |
| `<platform-library name="Fluent" version="..." />` | **Optional for virtual controls.** Declares Fluent UI React dependency provided by the platform. |

> **Canonical version source:** the React/Fluent v8/v9 version numbers (allowed-vs-runtime-loaded), the "can't declare Fluent v8 and v9 in the same manifest" rule, GA status, the CLI `>=1.37` rebuild note, and the no-auto-convert gotcha live in [`../../../knowledge/pcf-react-fluent-platform-libraries.md`](../../../knowledge/pcf-react-fluent-platform-libraries.md). That file also holds the **`## Decision Tree: PCF — Which React surface?`** (virtual control vs code-app vs canvas control vs Power Pages vs web resource). Quote versions from there, not from the examples below — examples can drift.

---

## `<feature-usage>` Element

Declares device and platform features the control requires. The platform uses these declarations to determine capability requirements and permission prompts.

```xml
<feature-usage>
  <uses-feature name="Device.captureAudio" required="false" />
  <uses-feature name="Device.captureImage" required="true" />
  <uses-feature name="Device.captureVideo" required="false" />
  <uses-feature name="Device.getBarcodeValue" required="false" />
  <uses-feature name="Device.getCurrentPosition" required="true" />
  <uses-feature name="Device.pickFile" required="false" />
  <uses-feature name="Utility" required="true" />
  <uses-feature name="WebAPI" required="true" />
</feature-usage>
```

| Feature | Description |
|---|---|
| `Device.captureAudio` | Access device microphone for audio recording |
| `Device.captureImage` | Access device camera for photo capture |
| `Device.captureVideo` | Access device camera for video capture |
| `Device.getBarcodeValue` | Access barcode scanner |
| `Device.getCurrentPosition` | Access GPS/location services |
| `Device.pickFile` | Access file picker dialog |
| `Utility` | Access utility functions (resource strings, environment info) |
| `WebAPI` | Access `context.webAPI` for Dataverse CRUD operations |

Set `required="true"` if the control cannot function without the feature. Set `required="false"` if the feature enhances but is not essential (the control degrades gracefully without it).

---

## Complete Manifest Examples

### Field Control Manifest

A standard field control bound to a whole number column with configuration properties.

```xml
<?xml version="1.0" encoding="utf-8" ?>
<manifest>
  <control
    namespace="Contoso.Controls"
    constructor="StarRatingControl"
    version="1.0.0"
    display-name-key="StarRating_DisplayName"
    description-key="StarRating_Description"
    control-type="standard"
  >
    <property
      name="value"
      display-name-key="StarRating_Value"
      description-key="StarRating_Value_Desc"
      of-type="Whole.None"
      usage="bound"
      required="true"
    />
    <property
      name="maxStars"
      display-name-key="StarRating_MaxStars"
      description-key="StarRating_MaxStars_Desc"
      of-type="Whole.None"
      usage="input"
      required="false"
      default-value="5"
    />
    <property
      name="activeColor"
      display-name-key="StarRating_ActiveColor"
      description-key="StarRating_ActiveColor_Desc"
      of-type="SingleLine.Text"
      usage="input"
      required="false"
      default-value="#FFD700"
    />
    <resources>
      <code path="index.ts" order="1" />
      <css path="css/StarRating.css" order="1" />
      <resx path="strings/StarRatingControl.1033.resx" version="1.0.0" />
    </resources>
  </control>
</manifest>
```

### Dataset Control Manifest

A dataset control for rendering records as a kanban board.

```xml
<?xml version="1.0" encoding="utf-8" ?>
<manifest>
  <control
    namespace="Contoso.Controls"
    constructor="KanbanBoardControl"
    version="1.0.0"
    display-name-key="KanbanBoard_DisplayName"
    description-key="KanbanBoard_Description"
    control-type="standard"
  >
    <data-set
      name="dataSet"
      display-name-key="KanbanBoard_DataSet"
      description-key="KanbanBoard_DataSet_Desc"
      cds-data-set-options="displayCommandBar:true;displayViewSelector:true"
    >
      <property-set
        name="stageColumn"
        display-name-key="KanbanBoard_StageColumn"
        description-key="KanbanBoard_StageColumn_Desc"
        of-type="OptionSet"
        usage="input"
        required="true"
      />
      <property-set
        name="titleColumn"
        display-name-key="KanbanBoard_TitleColumn"
        description-key="KanbanBoard_TitleColumn_Desc"
        of-type="SingleLine.Text"
        usage="input"
        required="true"
      />
      <property-set
        name="descriptionColumn"
        display-name-key="KanbanBoard_DescColumn"
        description-key="KanbanBoard_DescColumn_Desc"
        of-type="Multiple"
        usage="input"
        required="false"
      />
    </data-set>
    <resources>
      <code path="index.ts" order="1" />
      <css path="css/KanbanBoard.css" order="1" />
      <resx path="strings/KanbanBoardControl.1033.resx" version="1.0.0" />
    </resources>
    <feature-usage>
      <uses-feature name="WebAPI" required="true" />
      <uses-feature name="Utility" required="true" />
    </feature-usage>
  </control>
</manifest>
```

### React Virtual Control Manifest

A React virtual field control using Fluent UI platform libraries.

```xml
<?xml version="1.0" encoding="utf-8" ?>
<manifest>
  <control
    namespace="Contoso.Controls"
    constructor="ColorPickerControl"
    version="1.0.0"
    display-name-key="ColorPicker_DisplayName"
    description-key="ColorPicker_Description"
    control-type="virtual"
  >
    <property
      name="value"
      display-name-key="ColorPicker_Value"
      description-key="ColorPicker_Value_Desc"
      of-type="SingleLine.Text"
      usage="bound"
      required="true"
    />
    <property
      name="showAlpha"
      display-name-key="ColorPicker_ShowAlpha"
      description-key="ColorPicker_ShowAlpha_Desc"
      of-type="TwoOptions"
      usage="input"
      required="false"
      default-value="false"
    />
    <property
      name="presetColors"
      display-name-key="ColorPicker_Presets"
      description-key="ColorPicker_Presets_Desc"
      of-type="SingleLine.Text"
      usage="input"
      required="false"
      default-value="#FF0000,#00FF00,#0000FF,#FFD700,#FF69B4,#00CED1"
    />

    <type-group name="textTypes">
      <type>SingleLine.Text</type>
      <type>SingleLine.TextArea</type>
    </type-group>

    <resources>
      <code path="index.ts" order="1" />
      <platform-library name="React" version="16.14.0" />
      <platform-library name="Fluent" version="9.46.2" />
      <resx path="strings/ColorPickerControl.1033.resx" version="1.0.0" />
    </resources>
  </control>
</manifest>
```

---

## Solution Packaging Workflow

PCF controls must be packaged in a Dataverse solution for production deployment. The workflow is:

### Step 1: Initialize a Solution Project

```bash
mkdir MySolution && cd MySolution
pac solution init --publisher-name "Contoso" --publisher-prefix "con" --outputDirectory .
```

This creates a `.cdsproj` file and supporting MSBuild infrastructure.

### Step 2: Add PCF Control Reference

```bash
pac solution add-reference --path ../MyControl
```

This adds a project reference from the solution project to the PCF control project. You can add multiple controls to a single solution.

### Step 3: Build the Solution

```bash
msbuild /t:build /restore
```

Or with .NET CLI:

```bash
dotnet build
```

This compiles all referenced PCF controls, bundles them, and produces a solution `.zip` file in `bin/Debug/` (or `bin/Release/`).

**Build output:**
- `bin/Debug/MySolution.zip` — Unmanaged solution (for development environments)
- Use `/p:configuration=Release` for a managed solution build

### Step 4: Import to Environment

```bash
pac solution import --path bin/Debug/MySolution.zip --publish-changes
```

The `--publish-changes` flag automatically publishes the solution after import, making the control available immediately.

### Step 5: Verify Deployment

After import, the control appears in:
- **Form editor** → Field properties → Controls tab → Add Control → search by display name
- **View editor** → Custom controls for dataset controls
- **Solution explorer** → Custom Controls component

### Version Management

Increment the version in `ControlManifest.Input.xml` before every build:

```bash
pac pcf version --strategy manifest
```

This auto-increments the patch version. For major/minor bumps, edit the manifest manually.

### CI/CD Integration

For automated pipelines:

```bash
# Restore dependencies
npm ci --prefix ../MyControl

# Build the control
npm run build --prefix ../MyControl

# Build the solution
dotnet build MySolution.cdsproj -c Release

# Import to target environment
pac auth create --environment https://target-org.crm.dynamics.com
pac solution import --path bin/Release/MySolution_managed.zip --publish-changes
```
