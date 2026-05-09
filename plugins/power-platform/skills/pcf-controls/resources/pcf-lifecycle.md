# PCF Control Lifecycle and Architecture

## Control Lifecycle

Every PCF control follows a strict lifecycle managed by the platform host. Understanding this lifecycle is essential for building controls that initialize cleanly, update efficiently, report values correctly, and clean up resources.

```
┌──────────┐     ┌──────────────┐     ┌──────────────┐     ┌───────────┐
│  init()  │ ──► │ updateView() │ ──► │ getOutputs() │ ──► │ destroy() │
└──────────┘     └──────┬───────┘     └──────────────┘     └───────────┘
                        │       ▲            ▲
                        │       │            │
                        ▼       │            │
                   (re-render)  │   notifyOutputChanged()
                        │       │            │
                        └───────┘            │
                   (platform triggers        │
                    on data/size change)      │
```

### `init(context, notifyOutputChanged, state, container)`

Called **once** when the control is first loaded onto the form. This is where you:

- Store references to `context`, `notifyOutputChanged`, and `container`
- Set up initial DOM structure (standard controls) or initialize state (React virtual controls)
- Register event listeners
- Load external resources or configuration
- Restore previous state from `state` parameter (if the platform provides saved state)

**Parameters:**
- `context: ComponentFramework.Context<IInputs>` — The full context object with parameters, mode, navigation, webAPI, resources
- `notifyOutputChanged: () => void` — Call this function when your control's output value has changed; triggers the platform to call `getOutputs()`
- `state: ComponentFramework.Dictionary` — Saved state from a previous session (if any), for restoring control state across navigations
- `container: HTMLDivElement` — The DOM container element the control should render into (standard controls only; React virtual controls do not receive this)

### `updateView(context)`

Called by the platform **every time** the control needs to re-render. This includes:

- After `init()` completes (initial render)
- When bound parameter values change (user edits another field, record is refreshed)
- When the container is resized (`context.mode.allocatedHeight`/`allocatedWidth` change)
- When the dataset refreshes (dataset controls)
- When the platform triggers a re-render for any reason

**For standard controls:** Update the DOM inside `container` with the new data from `context.parameters`.

**For React virtual controls:** Return a `React.ReactElement` representing the control's UI. The platform manages the React tree — you do not call `ReactDOM.render()`.

**Key rule:** `updateView` must be **idempotent** and **fast**. Do not start async operations here without guarding against stale renders. Do not make webAPI calls on every `updateView` — cache results and refresh only when necessary.

### `getOutputs()`

Called by the platform **after** you call `notifyOutputChanged()`. Return an object matching the `IOutputs` interface with the current output values of your control.

**Key rules:**
- Only return properties that have changed (partial returns are fine)
- Return `undefined` for a property to clear it
- This is synchronous — do not perform async work here
- The platform uses these values to update the bound column(s) on the form

### `destroy()`

Called **once** when the control is removed from the DOM (navigating away, form closes, control is hidden by business rule). This is where you:

- Remove event listeners
- Cancel pending async operations (timers, fetch calls, subscriptions)
- Release external resources (maps, editors, chart instances)
- Clean up any global state

If you skip cleanup in `destroy()`, you risk memory leaks and zombie event handlers.

---

## StandardControl Interface

Standard controls manipulate the DOM directly via the `container` element provided in `init()`.

```typescript
import { IInputs, IOutputs } from "./generated/ManifestTypes";

export class MyFieldControl
  implements ComponentFramework.StandardControl<IInputs, IOutputs>
{
  private _notifyOutputChanged: () => void;
  private _container: HTMLDivElement;
  private _value: number | null;
  private _inputElement: HTMLInputElement;

  public init(
    context: ComponentFramework.Context<IInputs>,
    notifyOutputChanged: () => void,
    state: ComponentFramework.Dictionary,
    container: HTMLDivElement
  ): void {
    this._notifyOutputChanged = notifyOutputChanged;
    this._container = container;

    // Build DOM
    this._inputElement = document.createElement("input");
    this._inputElement.type = "range";
    this._inputElement.min = "0";
    this._inputElement.max = "100";
    this._inputElement.addEventListener("input", this._onInputChange.bind(this));
    this._container.appendChild(this._inputElement);

    // Read initial value
    this._value = context.parameters.value.raw;
    if (this._value !== null) {
      this._inputElement.value = this._value.toString();
    }
  }

  public updateView(context: ComponentFramework.Context<IInputs>): void {
    // Update DOM when platform provides new value
    const newValue = context.parameters.value.raw;
    if (newValue !== this._value) {
      this._value = newValue;
      this._inputElement.value = (newValue ?? 0).toString();
    }

    // Handle disabled/read-only state
    this._inputElement.disabled = context.mode.isControlDisabled;
  }

  public getOutputs(): IOutputs {
    return {
      value: this._value ?? undefined,
    };
  }

  public destroy(): void {
    this._inputElement.removeEventListener("input", this._onInputChange);
  }

  private _onInputChange(event: Event): void {
    const target = event.target as HTMLInputElement;
    this._value = parseInt(target.value, 10);
    this._notifyOutputChanged();
  }
}
```

---

## React Virtual Control Interface

React virtual controls return React elements from `updateView()`. The platform manages the React rendering tree. You do **not** receive a `container` in `init()`, and you do **not** call `ReactDOM.render()`.

**Key differences from standard controls:**
- `init()` has no `container` parameter — skip DOM manipulation entirely
- `updateView()` returns a `React.ReactElement` instead of void
- The platform provides React and ReactDOM — do not install or bundle your own
- Use Fluent UI React components (`@fluentui/react-components`) for consistent styling
- Use `--framework react` when scaffolding with `pac pcf init`

```typescript
import * as React from "react";
import { IInputs, IOutputs } from "./generated/ManifestTypes";
import { Slider, Label, makeStyles } from "@fluentui/react-components";

const useStyles = makeStyles({
  root: {
    display: "flex",
    flexDirection: "column",
    gap: "4px",
    padding: "4px",
  },
});

interface SliderControlProps {
  value: number | null;
  min: number;
  max: number;
  step: number;
  disabled: boolean;
  onChange: (value: number) => void;
}

const SliderControlComponent: React.FC<SliderControlProps> = ({
  value,
  min,
  max,
  step,
  disabled,
  onChange,
}) => {
  const styles = useStyles();

  return (
    <div className={styles.root}>
      <Label>{`Value: ${value ?? "—"}`}</Label>
      <Slider
        value={value ?? min}
        min={min}
        max={max}
        step={step}
        disabled={disabled}
        onChange={(_ev, data) => onChange(data.value)}
      />
    </div>
  );
};

export class SliderControl
  implements ComponentFramework.ReactControl<IInputs, IOutputs>
{
  private _notifyOutputChanged: () => void;
  private _currentValue: number | null;

  public init(
    context: ComponentFramework.Context<IInputs>,
    notifyOutputChanged: () => void,
    state: ComponentFramework.Dictionary
  ): void {
    this._notifyOutputChanged = notifyOutputChanged;
    this._currentValue = context.parameters.value.raw;
  }

  public updateView(
    context: ComponentFramework.Context<IInputs>
  ): React.ReactElement {
    return React.createElement(SliderControlComponent, {
      value: context.parameters.value.raw,
      min: context.parameters.minValue?.raw ?? 0,
      max: context.parameters.maxValue?.raw ?? 100,
      step: context.parameters.step?.raw ?? 1,
      disabled: context.mode.isControlDisabled,
      onChange: this._handleChange.bind(this),
    });
  }

  public getOutputs(): IOutputs {
    return {
      value: this._currentValue ?? undefined,
    };
  }

  public destroy(): void {
    // React cleanup is handled by the platform
  }

  private _handleChange(value: number): void {
    this._currentValue = value;
    this._notifyOutputChanged();
  }
}
```

---

## Context Object Deep Dive

The `context` object is the primary interface between your control and the platform. It is passed to both `init()` and `updateView()`.

### `context.parameters`

Contains the values of all properties declared in the manifest. Each parameter has:

- `.raw` — The raw typed value (number, string, boolean, Date, etc.). `null` if empty.
- `.formatted` — The display-formatted string (e.g., currency formatting, date formatting).
- `.type` — The metadata type string.
- `.error` — Whether the value has a validation error.
- `.security` — Security-related metadata (can the user read/update this field).
- `.attributes` — Column metadata (logical name, display name, type, min/max, precision).

```typescript
// Reading a bound parameter
const score = context.parameters.score.raw; // number | null
const formatted = context.parameters.score.formatted; // "1,250"
const isSecured = context.parameters.score.security?.readable; // boolean
```

### `context.mode`

Information about the control's rendering context:

- `isControlDisabled: boolean` — Whether the control should be read-only
- `isVisible: boolean` — Whether the control is visible
- `label: string` — The field label
- `allocatedHeight: number` — Available height in pixels (-1 if unconstrained)
- `allocatedWidth: number` — Available width in pixels (-1 if unconstrained)
- `setControlState(state: Dictionary): boolean` — Save state for later restoration
- `setFullScreen(fullscreen: boolean): void` — Request fullscreen mode
- `trackContainerResize(track: boolean): void` — Opt in to resize notifications

```typescript
// Respond to container resizing
public init(context, notifyOutputChanged, state, container) {
  context.mode.trackContainerResize(true);
}

public updateView(context) {
  const width = context.mode.allocatedWidth;
  const height = context.mode.allocatedHeight;
  // Adjust layout based on available space
}
```

### `context.navigation`

Navigate to forms, URLs, or dialogs:

- `openForm(options): Promise<OpenFormSuccessResponse>` — Open an entity form
- `openUrl(url, options): void` — Open a URL in a new window
- `openAlertDialog(options): Promise<void>` — Show an alert dialog
- `openConfirmDialog(options): Promise<ConfirmDialogResponse>` — Show a confirm dialog
- `openErrorDialog(options): Promise<void>` — Show an error dialog

```typescript
// Open a related record
await context.navigation.openForm({
  entityName: "account",
  entityId: accountId,
  openInNewWindow: false,
});

// Confirm before deletion
const result = await context.navigation.openConfirmDialog({
  title: "Confirm Delete",
  text: "Are you sure you want to delete this item?",
});
if (result.confirmed) {
  // proceed
}
```

### `context.webAPI`

CRUD operations against Dataverse from within the control:

- `createRecord(entityType, data): Promise<EntityReference>` — Create a record
- `retrieveRecord(entityType, id, options): Promise<Entity>` — Get a single record
- `retrieveMultipleRecords(entityType, options, maxPageSize): Promise<RetrieveMultipleResponse>` — Query records
- `updateRecord(entityType, id, data): Promise<EntityReference>` — Update a record
- `deleteRecord(entityType, id): Promise<EntityReference>` — Delete a record

```typescript
// Query related records
const result = await context.webAPI.retrieveMultipleRecords(
  "pic_gamescore",
  "?$filter=_pic_player_value eq '" + playerId + "'&$orderby=pic_score desc&$top=10"
);
for (const record of result.entities) {
  console.log(record.pic_score, record.pic_dateplayed);
}
```

### `context.resources`

Access localized strings and images defined in the manifest:

- `getString(key): string` — Get a localized string from the .resx file
- `getResource(key, successCallback, failureCallback): void` — Get a resource file (image, etc.)

```typescript
const label = context.resources.getString("MyControl_Label");
```

---

## Dataset Controls

Dataset controls bind to a view or subgrid and receive a full record set via `context.parameters.dataSet`.

### Dataset API Surface

```typescript
const dataSet = context.parameters.dataSet;

// Records
const recordIds = dataSet.sortedRecordIds; // string[] — ordered record IDs
const record = dataSet.records[recordId]; // DataSetRecord
const value = record.getValue("pic_name"); // raw value
const formatted = record.getFormattedValue("pic_name"); // display string
const recordRef = record.getNamedReference(); // EntityReference

// Columns
const columns = dataSet.columns; // Column[] — visible columns with metadata
// Each column has: name, displayName, dataType, order, visualSizeFactor, isHidden, isPrimary

// Sorting
dataSet.sorting; // SortStatus[] — current sort columns and directions

// Filtering
dataSet.filtering; // FilterExpression — current filter
dataSet.filtering.setFilter({
  conditions: [
    {
      attributeName: "pic_score",
      conditionOperator: 2, // GreaterThan
      value: "100",
    },
  ],
  filterOperator: 0, // And
});

// Paging
dataSet.paging.pageSize; // number
dataSet.paging.hasNextPage; // boolean
dataSet.paging.hasPreviousPage; // boolean
dataSet.paging.loadNextPage(); // fetch next page
dataSet.paging.loadPreviousPage(); // fetch previous page
dataSet.paging.setPageSize(50); // change page size

// Loading state
dataSet.loading; // boolean — true while data is being fetched
dataSet.error; // boolean — true if data fetch failed
dataSet.errorMessage; // string — error description

// Refresh
dataSet.refresh(); // re-fetch data from server

// Open a record
dataSet.openDatasetItem(record.getNamedReference()); // navigate to record form
```

### Complete Dataset Control Example

```typescript
import { IInputs, IOutputs } from "./generated/ManifestTypes";

export class RecordListControl
  implements ComponentFramework.StandardControl<IInputs, IOutputs>
{
  private _container: HTMLDivElement;
  private _notifyOutputChanged: () => void;

  public init(
    context: ComponentFramework.Context<IInputs>,
    notifyOutputChanged: () => void,
    state: ComponentFramework.Dictionary,
    container: HTMLDivElement
  ): void {
    this._container = container;
    this._notifyOutputChanged = notifyOutputChanged;
    context.mode.trackContainerResize(true);
  }

  public updateView(context: ComponentFramework.Context<IInputs>): void {
    const dataSet = context.parameters.dataSet;

    // Wait for data to load
    if (dataSet.loading) {
      this._container.innerHTML = "<div>Loading...</div>";
      return;
    }

    if (dataSet.error) {
      this._container.innerHTML = `<div class="error">${dataSet.errorMessage}</div>`;
      return;
    }

    // Build a table
    const table = document.createElement("table");
    table.style.width = "100%";
    table.style.borderCollapse = "collapse";

    // Header row
    const thead = document.createElement("thead");
    const headerRow = document.createElement("tr");
    const visibleColumns = dataSet.columns
      .filter((col) => !col.isHidden)
      .sort((a, b) => a.order - b.order);

    for (const col of visibleColumns) {
      const th = document.createElement("th");
      th.textContent = col.displayName;
      th.style.padding = "8px";
      th.style.borderBottom = "2px solid #ddd";
      th.style.textAlign = "left";
      th.style.cursor = "pointer";
      th.addEventListener("click", () => {
        // Toggle sort on click
        const currentSort = dataSet.sorting.find((s) => s.name === col.name);
        const newDirection = currentSort?.sortDirection === 0 ? 1 : 0;
        dataSet.sorting = [{ name: col.name, sortDirection: newDirection }];
        dataSet.refresh();
      });
      headerRow.appendChild(th);
    }
    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Data rows
    const tbody = document.createElement("tbody");
    for (const recordId of dataSet.sortedRecordIds) {
      const record = dataSet.records[recordId];
      const tr = document.createElement("tr");
      tr.style.cursor = "pointer";
      tr.addEventListener("click", () => {
        dataSet.openDatasetItem(record.getNamedReference());
      });

      for (const col of visibleColumns) {
        const td = document.createElement("td");
        td.textContent = record.getFormattedValue(col.name) || "";
        td.style.padding = "8px";
        td.style.borderBottom = "1px solid #eee";
        tr.appendChild(td);
      }
      tbody.appendChild(tr);
    }
    table.appendChild(tbody);

    // Paging controls
    const pagingDiv = document.createElement("div");
    pagingDiv.style.display = "flex";
    pagingDiv.style.justifyContent = "space-between";
    pagingDiv.style.padding = "8px";

    if (dataSet.paging.hasPreviousPage) {
      const prevBtn = document.createElement("button");
      prevBtn.textContent = "Previous";
      prevBtn.addEventListener("click", () => dataSet.paging.loadPreviousPage());
      pagingDiv.appendChild(prevBtn);
    }

    if (dataSet.paging.hasNextPage) {
      const nextBtn = document.createElement("button");
      nextBtn.textContent = "Next";
      nextBtn.addEventListener("click", () => dataSet.paging.loadNextPage());
      pagingDiv.appendChild(nextBtn);
    }

    // Render
    this._container.innerHTML = "";
    this._container.appendChild(table);
    this._container.appendChild(pagingDiv);
  }

  public getOutputs(): IOutputs {
    return {};
  }

  public destroy(): void {
    this._container.innerHTML = "";
  }
}
```

---

## Scaffolding Commands

### Field Control (Standard)

```bash
pac pcf init --namespace MyCompany.Controls --name MySlider --template field
cd MySlider
npm install
npm run build
npm start watch
```

### Field Control (React Virtual)

```bash
pac pcf init --namespace MyCompany.Controls --name MyReactSlider --template field --framework react
cd MyReactSlider
npm install
npm install @fluentui/react-components
npm run build
npm start watch
```

### Dataset Control (Standard)

```bash
pac pcf init --namespace MyCompany.Controls --name MyGrid --template dataset
cd MyGrid
npm install
npm run build
npm start watch
```

### Dataset Control (React Virtual)

```bash
pac pcf init --namespace MyCompany.Controls --name MyReactGrid --template dataset --framework react
cd MyReactGrid
npm install
npm install @fluentui/react-components
npm run build
npm start watch
```

---

## Building and Debugging

### Test Harness (`npm start watch`)

The test harness launches a local web server with a sandboxed environment:

- Configure input parameters via the property pane on the right
- For dataset controls, load CSV test data or configure mock columns
- Hot reload on file save — no manual refresh needed
- Browser DevTools work normally (breakpoints, console, network)
- `context.webAPI` calls are mocked — they return empty results by default

### Development Push (`pac pcf push`)

For rapid iteration on a connected dev environment:

```bash
pac pcf push --publisher-prefix pic
```

This pushes the compiled control directly to the connected environment without solution packaging. The control appears in the customization UI and can be added to forms.

**Limitations of `pac pcf push`:**
- Only works for development — not suitable for ALM/deployment pipelines
- Creates an unmanaged web resource — must be cleaned up before solution packaging
- Requires an active `pac auth` connection

### Production Build (Solution Packaging)

```bash
# From a separate solution directory
pac solution init --publisher-name PIC --publisher-prefix pic --outputDirectory MySolution
cd MySolution
pac solution add-reference --path ../MyControl

# Build the solution zip
msbuild /t:build /restore

# Import to environment
pac solution import --path bin/Debug/MySolution.zip
```

### Debugging Tips

1. **Use `console.log` liberally in development** — The test harness and browser DevTools capture all console output.
2. **Check `context.parameters.X.error`** — If a parameter has a validation error, the control should show an error state.
3. **Watch for `updateView` storms** — If your control calls `notifyOutputChanged()` inside `updateView()`, you create an infinite loop. Always guard with a value comparison.
4. **Dataset loading state** — Always check `dataSet.loading` before accessing `sortedRecordIds`. Accessing records while loading produces stale or empty data.
5. **Fullscreen mode** — Use `context.mode.setFullScreen(true)` for controls that need more space (maps, charts, rich editors). The platform will re-render with full viewport dimensions.
