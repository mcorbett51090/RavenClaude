# Common PCF Control Patterns

This reference covers 11 common PCF control patterns. For each pattern: when to use it, manifest properties needed, key implementation notes, and OOB alternatives.

---

## 1. Slider / Range Input

**Type:** Field control
**Bind to:** Whole Number, Decimal Number, Floating Point Number columns

### When to Use

When users need to select a numeric value within a defined range and a visual slider provides better UX than a text input. Common for ratings (1-10), percentages (0-100), priority scores, or any bounded numeric input.

### Manifest Properties

```xml
<property name="value" display-name-key="Value" of-type="Whole.None" usage="bound" required="true" />
<property name="minValue" display-name-key="Minimum" of-type="Whole.None" usage="input" required="false" default-value="0" />
<property name="maxValue" display-name-key="Maximum" of-type="Whole.None" usage="input" required="false" default-value="100" />
<property name="step" display-name-key="Step" of-type="Whole.None" usage="input" required="false" default-value="1" />
<property name="showValue" display-name-key="Show Value Label" of-type="TwoOptions" usage="input" required="false" default-value="true" />
```

### Key Implementation Notes

- Read `context.parameters.value.raw` for current value; write back via `getOutputs()`
- Display current numeric value next to the slider for accessibility
- Respect `context.mode.isControlDisabled` — disable the slider when the form is read-only
- Use `context.parameters.value.attributes?.MinValue` and `MaxValue` to read column-level constraints as fallback defaults
- For React virtual: use Fluent UI `<Slider>` component

### OOB Alternative

Power Apps provides a basic numeric input. No OOB slider exists — this is a strong PCF use case.

---

## 2. Toggle / Switch

**Type:** Field control
**Bind to:** Two Options (Boolean) columns

### When to Use

When a boolean field would benefit from a clear on/off visual toggle instead of the default dropdown or checkbox. Common for enable/disable flags, active/inactive status, yes/no preferences.

### Manifest Properties

```xml
<property name="value" display-name-key="Value" of-type="TwoOptions" usage="bound" required="true" />
<property name="onLabel" display-name-key="On Label" of-type="SingleLine.Text" usage="input" required="false" default-value="On" />
<property name="offLabel" display-name-key="Off Label" of-type="SingleLine.Text" usage="input" required="false" default-value="Off" />
```

### Key Implementation Notes

- `context.parameters.value.raw` returns `true` or `false` (boolean)
- Use `context.parameters.value.attributes?.Options` to read the option labels from metadata
- Toggle state change triggers `notifyOutputChanged()` → `getOutputs()` returns the new boolean
- For React virtual: use Fluent UI `<Switch>` component
- Respect disabled state and provide clear visual distinction between on/off

### OOB Alternative

Dataverse provides a checkbox and a dropdown for boolean fields. The toggle/switch pattern provides a more modern, mobile-friendly UX.

---

## 3. Star Rating

**Type:** Field control
**Bind to:** Whole Number columns (typically 1-5 or 1-10)

### When to Use

When collecting or displaying a rating score. Common for customer satisfaction, product reviews, quality assessments, or any ordinal scale.

### Manifest Properties

```xml
<property name="value" display-name-key="Rating" of-type="Whole.None" usage="bound" required="true" />
<property name="maxStars" display-name-key="Max Stars" of-type="Whole.None" usage="input" required="false" default-value="5" />
<property name="allowHalf" display-name-key="Allow Half Stars" of-type="TwoOptions" usage="input" required="false" default-value="false" />
<property name="starSize" display-name-key="Star Size (px)" of-type="Whole.None" usage="input" required="false" default-value="24" />
<property name="activeColor" display-name-key="Active Color" of-type="SingleLine.Text" usage="input" required="false" default-value="#FFD700" />
```

### Key Implementation Notes

- Render stars as SVG or Unicode (★/☆) for crisp scaling at any size
- Support hover preview — highlight stars up to the hovered position before click confirms
- Handle click on star N → set value to N, click on current value → clear (set to null)
- If `allowHalf` is true, detect click position within each star (left half = N-0.5, right half = N) — requires `Decimal` type instead of `Whole.None`
- Keyboard accessibility: arrow keys to increment/decrement, Enter to confirm
- For React virtual: build a custom `<StarRating>` component or use a community React rating library

### OOB Alternative

No OOB star rating exists. This is one of the most popular PCF control patterns.

---

## 4. Color Picker

**Type:** Field control
**Bind to:** SingleLine.Text columns (stores hex value like `#FF5733`)

### When to Use

When users need to select a color — for category coding, theming, visual tags, or status indicators.

### Manifest Properties

```xml
<property name="value" display-name-key="Color" of-type="SingleLine.Text" usage="bound" required="true" />
<property name="showAlpha" display-name-key="Show Alpha Channel" of-type="TwoOptions" usage="input" required="false" default-value="false" />
<property name="presetColors" display-name-key="Preset Colors (comma-separated)" of-type="SingleLine.Text" usage="input" required="false" default-value="#FF0000,#00FF00,#0000FF,#FFD700,#FF69B4" />
```

### Key Implementation Notes

- Store the color as a hex string (`#RRGGBB` or `#RRGGBBAA`) in the text column
- Display a color swatch showing the current color, with a click to open the picker
- Provide preset color swatches for quick selection alongside a full spectrum picker
- Use the native `<input type="color">` for simplicity, or a library like `react-color` for richer UX
- Validate input format — strip invalid characters, normalize to uppercase hex
- For React virtual: use Fluent UI `<ColorPicker>` or `<SwatchPicker>` components

### OOB Alternative

No OOB color picker exists. Text fields display the hex string as plain text, which is not user-friendly.

---

## 5. Rich Text Editor

**Type:** Field control
**Bind to:** Multiple Lines of Text (Memo) columns

### When to Use

When users need to author formatted content — meeting notes, descriptions, email templates, knowledge articles. The default multiline text field is plain text only.

### Manifest Properties

```xml
<property name="value" display-name-key="Content" of-type="Multiple" usage="bound" required="true" />
<property name="toolbar" display-name-key="Toolbar Options" of-type="SingleLine.Text" usage="input" required="false" default-value="bold,italic,underline,link,list,heading" />
<property name="maxLength" display-name-key="Max Length" of-type="Whole.None" usage="input" required="false" default-value="100000" />
<property name="height" display-name-key="Editor Height (px)" of-type="Whole.None" usage="input" required="false" default-value="300" />
```

### Key Implementation Notes

- Wrap a proven editor library: **Quill**, **TinyMCE**, **ProseMirror**, or **Tiptap**
- Store HTML in the memo column — Dataverse memo columns support up to 1,048,576 characters
- Sanitize HTML on save to prevent XSS (strip `<script>`, `onclick`, etc.)
- Debounce `notifyOutputChanged()` — do not call on every keystroke; use a 300-500ms debounce
- Handle the editor's `destroy()` properly — editors like TinyMCE need explicit cleanup
- Load editor CSS from `<resources><css>` in the manifest to avoid flash of unstyled content
- Consider image handling: inline base64 (bloats data), or upload to Dataverse file storage and insert URL
- For React virtual: use Tiptap (React-native) or wrap Quill with `react-quill`

### OOB Alternative

Dataverse has a built-in rich text editor control for multiline text fields (enable in column properties). The OOB editor supports basic formatting. Build a custom PCF only if you need advanced features (tables, embedded media, custom toolbars, markdown mode).

---

## 6. Map / Location Picker

**Type:** Field control
**Bind to:** Floating Point Number columns (latitude + longitude) or SingleLine.Text (address)

### When to Use

When capturing or displaying geographic locations — delivery addresses, site locations, territory boundaries, asset positions.

### Manifest Properties

```xml
<property name="latitude" display-name-key="Latitude" of-type="FP" usage="bound" required="true" />
<property name="longitude" display-name-key="Longitude" of-type="FP" usage="bound" required="true" />
<property name="zoom" display-name-key="Default Zoom" of-type="Whole.None" usage="input" required="false" default-value="13" />
<property name="mapProvider" display-name-key="Map Provider" of-type="SingleLine.Text" usage="input" required="false" default-value="bing" />
<property name="apiKey" display-name-key="API Key" of-type="SingleLine.Text" usage="input" required="false" />
```

### Key Implementation Notes

- Use Bing Maps SDK (free tier for Power Platform) or Google Maps JavaScript API
- Load the map SDK dynamically in `init()` — do not bundle it (too large)
- Store the API key in an environment variable, not hardcoded — read via `context.webAPI` or pass as input property
- Place a draggable marker for location selection; update lat/lng on marker drag end
- Include a search/geocode input for address-to-coordinates conversion
- Call `context.mode.trackContainerResize(true)` and resize the map on `updateView` when dimensions change
- Use `context.mode.setFullScreen(true)` to give the map more space when needed
- In `destroy()`, remove the map instance and all event listeners to prevent memory leaks
- For React virtual: use `@vis.gl/react-google-maps` or a Bing Maps React wrapper

### OOB Alternative

Power Apps has a basic map control in canvas apps. For model-driven apps, there is no OOB map on forms — PCF is the way to go.

---

## 7. Kanban Board

**Type:** Dataset control
**Bind to:** Views of any entity with an option set column representing stages

### When to Use

When managing records through a pipeline or workflow — sales opportunities by stage, tasks by status, support tickets by priority, project items by sprint status.

### Manifest Properties (Manifest uses `<data-set>`)

```xml
<data-set name="dataSet" display-name-key="Records" cds-data-set-options="displayCommandBar:true;displayViewSelector:true">
  <property-set name="stageColumn" display-name-key="Stage Column" of-type="SingleLine.Text" usage="input" required="true" />
  <property-set name="titleColumn" display-name-key="Title Column" of-type="SingleLine.Text" usage="input" required="true" />
  <property-set name="descriptionColumn" display-name-key="Description Column" of-type="SingleLine.Text" usage="input" required="false" />
</data-set>
```

### Key Implementation Notes

- Read the option set values for the stage column from column metadata to build lane headers dynamically
- Group `dataSet.sortedRecordIds` by the stage column value to populate each lane
- Implement drag-and-drop between lanes using HTML5 Drag and Drop API or a library like `@dnd-kit/core`
- On drop: update the record's stage column via `context.webAPI.updateRecord()`, then call `dataSet.refresh()`
- Show record count per lane in the lane header
- Support clicking a card to open the record form via `dataSet.openDatasetItem()`
- Handle large datasets: use paging (`dataSet.paging.setPageSize(100)`) and lazy loading
- For React virtual: use `@dnd-kit/core` + `@dnd-kit/sortable` for smooth drag-drop, Fluent UI `<Card>` for cards

### OOB Alternative

No OOB kanban view exists in model-driven apps. Power Apps canvas has a basic kanban gallery. This is a high-value PCF dataset control.

---

## 8. Calendar View

**Type:** Dataset control
**Bind to:** Views of any entity with a date/datetime column

### When to Use

When records are best visualized on a timeline — appointments, events, tasks with due dates, resource bookings, project milestones.

### Manifest Properties (Manifest uses `<data-set>`)

```xml
<data-set name="dataSet" display-name-key="Records" cds-data-set-options="displayCommandBar:true;displayViewSelector:true">
  <property-set name="startDateColumn" display-name-key="Start Date Column" of-type="SingleLine.Text" usage="input" required="true" />
  <property-set name="endDateColumn" display-name-key="End Date Column" of-type="SingleLine.Text" usage="input" required="false" />
  <property-set name="titleColumn" display-name-key="Title Column" of-type="SingleLine.Text" usage="input" required="true" />
  <property-set name="colorColumn" display-name-key="Color Category Column" of-type="SingleLine.Text" usage="input" required="false" />
</data-set>
```

### Key Implementation Notes

- Use a calendar library: **FullCalendar** (most popular), **DHTMLX Scheduler**, or build a custom month/week/day grid
- Map dataset records to calendar events using the configured column names
- Support month, week, and day views with navigation (prev/next/today)
- Click on an event → `dataSet.openDatasetItem()` to open the record
- Click on an empty date → use `context.navigation.openForm()` with default date values to create a new record
- Drag to reschedule: update the date column via `context.webAPI.updateRecord()` on drop
- Handle timezone correctly — `context.userSettings.dateFormattingInfo` provides the user's timezone
- For React virtual: use `@fullcalendar/react` with `@fullcalendar/daygrid` and `@fullcalendar/interaction`

### OOB Alternative

Model-driven apps have a basic calendar control for activities. For custom entities or non-activity tables, PCF is required.

---

## 9. Card Gallery

**Type:** Dataset control
**Bind to:** Views of any entity

### When to Use

When records are better represented as visual cards than table rows — product catalogs, team member directories, asset inventories, portfolio items.

### Manifest Properties (Manifest uses `<data-set>`)

```xml
<data-set name="dataSet" display-name-key="Records" cds-data-set-options="displayCommandBar:true;displayViewSelector:true">
  <property-set name="titleColumn" display-name-key="Title Column" of-type="SingleLine.Text" usage="input" required="true" />
  <property-set name="subtitleColumn" display-name-key="Subtitle Column" of-type="SingleLine.Text" usage="input" required="false" />
  <property-set name="imageColumn" display-name-key="Image Column" of-type="SingleLine.Text" usage="input" required="false" />
  <property-set name="badgeColumn" display-name-key="Badge/Status Column" of-type="SingleLine.Text" usage="input" required="false" />
  <property-set name="cardsPerRow" display-name-key="Cards Per Row" of-type="Whole.None" usage="input" required="false" />
</data-set>
```

### Key Implementation Notes

- Render each record as a card with image, title, subtitle, and status badge
- Use CSS Grid or Flexbox for responsive card layout; adjust cards-per-row based on `context.mode.allocatedWidth`
- Load images from Dataverse image columns or file columns — use `context.webAPI.retrieveRecord()` with `$select=entityimage` or construct the image URL
- Click on a card → `dataSet.openDatasetItem()` to open the record
- Support search/filter via the dataset's built-in filtering API
- Implement infinite scroll or pagination for large datasets
- For React virtual: use Fluent UI `<Card>`, `<CardHeader>`, `<CardPreview>` components in a grid layout

### OOB Alternative

Model-driven apps have a read-only card form in the grid view header, but it shows limited info and no images. The gallery pattern provides a much richer visual experience.

---

## 10. Chart / Graph

**Type:** Field control (for single-record visualization) or Dataset control (for aggregate visualization)
**Bind to:** Whole Number, Decimal, or Currency columns (field); any view (dataset)

### When to Use

When numeric data needs visual representation — KPI gauges, progress bars, trend lines, comparison bar charts, pie charts for distribution.

### Manifest Properties (Field Control Example)

```xml
<property name="value" display-name-key="Value" of-type="Decimal" usage="bound" required="true" />
<property name="target" display-name-key="Target" of-type="Decimal" usage="input" required="false" default-value="100" />
<property name="chartType" display-name-key="Chart Type" of-type="SingleLine.Text" usage="input" required="false" default-value="gauge" />
<property name="thresholdGreen" display-name-key="Green Threshold" of-type="Decimal" usage="input" required="false" default-value="80" />
<property name="thresholdYellow" display-name-key="Yellow Threshold" of-type="Decimal" usage="input" required="false" default-value="50" />
```

### Key Implementation Notes

- Use **Chart.js** (lightweight, good defaults), **D3.js** (maximum flexibility), or **Recharts** (React-native)
- For field controls: visualize the bound value against a target (gauge, progress ring, sparkline)
- For dataset controls: aggregate data from the record set and render bar/line/pie charts
- Handle `null` values gracefully — show "No data" placeholder
- Resize chart on `updateView()` when `allocatedWidth`/`allocatedHeight` change
- Destroy chart instance in `destroy()` — Chart.js in particular leaks canvas memory if not destroyed
- Animate transitions when values change for a polished UX
- For React virtual: use Recharts or `react-chartjs-2` wrapper

### OOB Alternative

Model-driven apps have built-in chart web resources (XML-based chart definitions). OOB charts work well for standard bar/line/pie on views. Build a PCF control when you need custom chart types (gauge, donut, radar), in-form visualization, or interactive drill-down.

---

## 11. File Upload with Preview

**Type:** Field control
**Bind to:** File or Image columns

### When to Use

When the default file/image upload experience is insufficient — you need drag-drop upload, image preview with crop, multi-file selection, file type validation, or progress indicators.

### Manifest Properties

```xml
<property name="value" display-name-key="File" of-type="SingleLine.Text" usage="bound" required="true" />
<property name="acceptedTypes" display-name-key="Accepted File Types" of-type="SingleLine.Text" usage="input" required="false" default-value=".jpg,.jpeg,.png,.gif,.pdf" />
<property name="maxSizeMB" display-name-key="Max File Size (MB)" of-type="Whole.None" usage="input" required="false" default-value="10" />
<property name="showPreview" display-name-key="Show Preview" of-type="TwoOptions" usage="input" required="false" default-value="true" />
<property name="allowCrop" display-name-key="Allow Image Crop" of-type="TwoOptions" usage="input" required="false" default-value="false" />
```

### Key Implementation Notes

- Use HTML5 Drag and Drop API for the drop zone; style with dashed border and hover effects
- Validate file type and size before upload — show clear error messages for rejected files
- For image files: generate a thumbnail preview using `FileReader.readAsDataURL()` and render in an `<img>` tag
- For PDF files: show a PDF icon with filename and size
- Upload to Dataverse: use `context.webAPI.updateRecord()` with base64-encoded file content for file/image columns, or use the File API endpoint for large files
- Show upload progress if using chunked upload for large files
- For image cropping: use `react-image-crop` or `cropperjs` library
- In `destroy()`: revoke any object URLs created with `URL.createObjectURL()` to free memory
- For React virtual: use Fluent UI `<FileUploader>` or build a custom drop zone component

### OOB Alternative

Dataverse provides a basic file upload control for file and image columns. It supports single file upload with basic validation. Build a PCF control when you need drag-drop, preview, crop, multi-file handling, or custom validation UX.
