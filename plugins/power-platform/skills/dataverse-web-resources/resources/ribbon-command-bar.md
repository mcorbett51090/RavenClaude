# Ribbon and Command Bar Customization

Model-driven apps support three approaches to command bar customization: Modern Command Bar
with Power Fx (no-code, Maker Portal only), Modern Command Bar with JavaScript handlers,
and Classic RibbonDiffXml (XML-based, API-automatable). Each approach has different
capabilities and trade-offs.

## Modern Command Bar (Power Fx)

The simplest approach, configured entirely in the Maker Portal. No API automation available.

### How It Works

1. Open the form or view in the Maker Portal designer.
2. Click **Command bar** in the top menu to open the command designer.
3. Add buttons, set **Visibility** rules with Power Fx expressions.
4. Set **OnSelect** actions (also Power Fx).

### Power Fx Visibility Rules

```
// Show button only when status is "Draft"
Self.Selected.Item.Status = 'Status (Project)'.Draft

// Show button only for specific security role
"System Administrator" in User().Roles.Name

// Show on create form only
Self.Selected.State = FormMode.New

// Compound conditions
Self.Selected.Item.Priority = 'Priority (Project)'.High And
    Self.Selected.Item.Status <> 'Status (Project)'.Closed
```

### Power Fx OnSelect Actions

```
// Navigate to a URL
Launch("https://contoso.com/reports/" & Self.Selected.Item.ProjectId)

// Patch a field
Patch(Projects, Self.Selected.Item, { Status: 'Status (Project)'.Approved });
Notify("Record approved!", NotificationType.Success)

// Open a screen (Canvas app context)
Navigate(ApprovalScreen, ScreenTransition.Cover)
```

### Limitations

- Cannot call JavaScript functions directly.
- Limited to Power Fx expression capabilities.
- Not automatable via API (must use Maker Portal).
- Best for simple show/hide logic and field updates.

## Modern Command Bar (JavaScript)

Combines the modern command designer with JavaScript handlers for complex logic.

### Setup in Maker Portal

1. Open the command designer for the form/view.
2. Add a new button.
3. Set **Action** to "Run JavaScript".
4. Select the JS web resource and specify the function name.
5. Choose parameters to pass: `PrimaryControl`, `SelectedItems`, `SelectedControl`.

### JavaScript Handler Functions

```javascript
var Contoso = Contoso || {};
Contoso.CommandBar = {

    // Handler for a form command bar button
    // PrimaryControl = formContext
    onApproveClick: function(primaryControl) {
        var formContext = primaryControl;
        var status = formContext.getAttribute("cnt_status").getValue();

        if (status !== 892100000) {
            Xrm.Navigation.openAlertDialog({
                text: "Only Draft records can be approved.",
                title: "Cannot Approve"
            });
            return;
        }

        Xrm.Navigation.openConfirmDialog({
            text: "Approve this record?",
            title: "Confirm Approval",
            confirmButtonLabel: "Approve"
        }).then(function(result) {
            if (result.confirmed) {
                formContext.getAttribute("cnt_status").setValue(892100001);
                formContext.data.entity.save();
            }
        });
    },

    // Handler for a grid/view command bar button
    // SelectedItems = array of selected records
    onBulkApproveClick: function(selectedItems) {
        if (!selectedItems || selectedItems.length === 0) {
            Xrm.Navigation.openAlertDialog({ text: "Select at least one record." });
            return;
        }

        var promises = selectedItems.map(function(item) {
            return Xrm.WebApi.updateRecord("cnt_project", item.Id, {
                "cnt_status": 892100001
            });
        });

        Promise.all(promises).then(function() {
            Xrm.Navigation.openAlertDialog({
                text: "Approved " + selectedItems.length + " records."
            });
        }).catch(function(error) {
            Xrm.Navigation.openAlertDialog({
                text: "Error: " + error.message,
                title: "Approval Failed"
            });
        });
    }
};
```

### Visibility Rules (JS-Based)

In the modern command designer, visibility rules can reference JavaScript functions that
return `true` or `false`:

```javascript
Contoso.CommandBar.Rules = {

    // Enable rule — return true to show/enable the button
    isRecordDraft: function(primaryControl) {
        var formContext = primaryControl;
        var status = formContext.getAttribute("cnt_status").getValue();
        return status === 892100000; // Draft
    },

    // Show only if user has admin role
    isUserAdmin: function(primaryControl) {
        var roles = Xrm.Utility.getGlobalContext().userSettings.securityRoles;
        // Check for specific role GUID
        return roles.some(function(role) {
            return role.toLowerCase() === "admin-role-guid-here";
        });
    },

    // Show only when at least one record is selected (grid context)
    hasSelectedRecords: function(selectedItems) {
        return selectedItems && selectedItems.length > 0;
    }
};
```

## Classic RibbonDiffXml

The XML-based approach to ribbon customization. This is the **only method that can be fully
automated via the API**, as it is stored as part of the entity metadata.

### Structure Overview

RibbonDiffXml is an XML fragment included in the entity's `RibbonDiffXml` property. It
contains:

- `<CustomActions>` — Add new buttons or groups to the ribbon.
- `<HideActions>` — Hide out-of-the-box buttons.
- `<CommandDefinitions>` — Define what happens when a button is clicked.
- `<RuleDefinitions>` — Define enable/display rules for buttons.
- `<Templates>` — Optional: custom layout templates.
- `<LocLabels>` — Localized labels.

### Adding a Custom Button

```xml
<RibbonDiffXml>
  <CustomActions>
    <!-- Add a button to the form command bar -->
    <CustomAction Id="cnt.project.form.ApproveButton"
                  Location="Mscrm.Form.cnt_project.MainTab.Actions.Controls._children"
                  Sequence="60">
      <CommandUIDefinition>
        <Button Id="cnt.project.form.ApproveButton.Button"
                LabelText="$LocLabels:cnt.approve.label"
                ToolTipTitle="$LocLabels:cnt.approve.tooltip.title"
                ToolTipDescription="$LocLabels:cnt.approve.tooltip.desc"
                Image32by32="$webresource:cnt_/images/approve32.png"
                Image16by16="$webresource:cnt_/images/approve16.png"
                Command="cnt.project.ApproveCommand"
                Sequence="60"
                TemplateAlias="o1" />
      </CommandUIDefinition>
    </CustomAction>

    <!-- Add a button to the grid (view) command bar -->
    <CustomAction Id="cnt.project.grid.BulkApproveButton"
                  Location="Mscrm.HomepageGrid.cnt_project.MainTab.Actions.Controls._children"
                  Sequence="70">
      <CommandUIDefinition>
        <Button Id="cnt.project.grid.BulkApproveButton.Button"
                LabelText="Bulk Approve"
                Image32by32="$webresource:cnt_/images/bulkapprove32.png"
                Command="cnt.project.BulkApproveCommand"
                Sequence="70"
                TemplateAlias="o1" />
      </CommandUIDefinition>
    </CustomAction>
  </CustomActions>

  <HideActions>
    <!-- Hide the out-of-the-box Deactivate button -->
    <HideCustomAction Location="Mscrm.Form.cnt_project.MainTab.Actions.Controls"
                      HideActionId="cnt.HideDeactivate"
                      Id="Mscrm.Form.Deactivate" />
  </HideActions>

  <CommandDefinitions>
    <!-- Form button command — calls JS function -->
    <CommandDefinition Id="cnt.project.ApproveCommand">
      <EnableRules>
        <EnableRule Id="cnt.project.ApproveCommand.EnableRule" />
      </EnableRules>
      <DisplayRules>
        <DisplayRule Id="cnt.project.ApproveCommand.DisplayRule" />
      </DisplayRules>
      <Actions>
        <JavaScriptFunction FunctionName="Contoso.CommandBar.onApproveClick"
                            Library="$webresource:cnt_/js/commandbar.js">
          <CrmParameter Value="PrimaryControl" />
        </JavaScriptFunction>
      </Actions>
    </CommandDefinition>

    <!-- Grid button command — passes selected items -->
    <CommandDefinition Id="cnt.project.BulkApproveCommand">
      <EnableRules>
        <EnableRule Id="cnt.project.BulkApproveCommand.EnableRule" />
      </EnableRules>
      <DisplayRules />
      <Actions>
        <JavaScriptFunction FunctionName="Contoso.CommandBar.onBulkApproveClick"
                            Library="$webresource:cnt_/js/commandbar.js">
          <CrmParameter Value="SelectedControlSelectedItemReferences" />
        </JavaScriptFunction>
      </Actions>
    </CommandDefinition>
  </CommandDefinitions>

  <RuleDefinitions>
    <TabDisplayRules />
    <DisplayRules>
      <!-- Show button only for Update form type -->
      <DisplayRule Id="cnt.project.ApproveCommand.DisplayRule">
        <FormStateRule State="Existing" />
      </DisplayRule>
    </DisplayRules>
    <EnableRules>
      <!-- Enable based on JS function return value -->
      <EnableRule Id="cnt.project.ApproveCommand.EnableRule">
        <CustomRule FunctionName="Contoso.CommandBar.Rules.isRecordDraft"
                    Library="$webresource:cnt_/js/commandbar.js"
                    Default="false">
          <CrmParameter Value="PrimaryControl" />
        </CustomRule>
      </EnableRule>
      <!-- Enable only when records are selected (grid context) -->
      <EnableRule Id="cnt.project.BulkApproveCommand.EnableRule">
        <SelectionCountRule AppliesTo="SelectedCount" Minimum="1" />
      </EnableRule>
    </EnableRules>
  </RuleDefinitions>

  <LocLabels>
    <LocLabel Id="cnt.approve.label">
      <Titles><Title languagecode="1033" description="Approve" /></Titles>
    </LocLabel>
    <LocLabel Id="cnt.approve.tooltip.title">
      <Titles><Title languagecode="1033" description="Approve Record" /></Titles>
    </LocLabel>
    <LocLabel Id="cnt.approve.tooltip.desc">
      <Titles><Title languagecode="1033" description="Mark this record as approved." /></Titles>
    </LocLabel>
  </LocLabels>
</RibbonDiffXml>
```

### Common Location IDs

| Location | Placement |
|---|---|
| `Mscrm.Form.{entity}.MainTab.Actions.Controls._children` | Form command bar — Actions group |
| `Mscrm.Form.{entity}.MainTab.Save.Controls._children` | Form command bar — Save group |
| `Mscrm.HomepageGrid.{entity}.MainTab.Actions.Controls._children` | Grid/view command bar — Actions group |
| `Mscrm.SubGrid.{entity}.MainTab.Actions.Controls._children` | Subgrid command bar |

### Common CrmParameter Values

| Value | Context | Description |
|---|---|---|
| `PrimaryControl` | Form | The formContext object |
| `SelectedControl` | Grid/Subgrid | The grid control |
| `SelectedControlSelectedItemReferences` | Grid | Array of selected record references |
| `SelectedControlSelectedItemIds` | Grid | Array of selected record GUIDs |
| `SelectedControlSelectedItemCount` | Grid | Count of selected items |
| `PrimaryEntityTypeName` | Any | Logical name of the entity |
| `FirstPrimaryItemId` | Form | GUID of the current record |

### Enable Rules and Display Rules

```xml
<!-- Display only on existing records (not create form) -->
<DisplayRule Id="cnt.ExistingRecordOnly">
  <FormStateRule State="Existing" />
</DisplayRule>

<!-- Display only on create form -->
<DisplayRule Id="cnt.CreateFormOnly">
  <FormStateRule State="Create" />
</DisplayRule>

<!-- Enable based on field value via JS -->
<EnableRule Id="cnt.FieldValueCheck">
  <CustomRule FunctionName="Contoso.Rules.checkFieldValue"
              Library="$webresource:cnt_/js/rules.js"
              Default="false">
    <CrmParameter Value="PrimaryControl" />
  </CustomRule>
</EnableRule>

<!-- Enable only when exactly 1 record is selected -->
<EnableRule Id="cnt.SingleSelection">
  <SelectionCountRule AppliesTo="SelectedCount" Minimum="1" Maximum="1" />
</EnableRule>

<!-- Enable only for specific entity privilege -->
<EnableRule Id="cnt.HasWritePrivilege">
  <EntityPrivilegeRule EntityName="cnt_project" PrivilegeType="Write" />
</EnableRule>

<!-- Display for specific security role -->
<DisplayRule Id="cnt.AdminOnly">
  <EntityPrivilegeRule EntityName="cnt_project" PrivilegeType="Delete" />
</DisplayRule>
```

### Deploying RibbonDiffXml via API

RibbonDiffXml is stored as part of the entity metadata. To update it via the API:

```powershell
# Step 1: Get the current entity metadata including RibbonDiffXml
$token = az account get-access-token --resource "https://org.crm6.dynamics.com/" `
    --tenant "your-tenant-id" --query accessToken -o tsv

$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type"  = "application/json; charset=utf-8"
    "OData-Version" = "4.0"
    "MSCRM.SolutionUniqueName" = "MySolution"
}

# Step 2: Retrieve entity metadata ID
$entityLogicalName = "cnt_project"
$entityMeta = Invoke-RestMethod `
    -Uri "https://org.crm6.dynamics.com/api/data/v9.2/EntityDefinitions(LogicalName='$entityLogicalName')?`$select=MetadataId" `
    -Method GET -Headers $headers

$entityMetaId = $entityMeta.MetadataId

# Step 3: Update the RibbonDiffXml (include it in entity metadata update)
# Note: You must include the COMPLETE RibbonDiffXml, not just a diff
$ribbonXml = @"
<RibbonDiffXml>
  <CustomActions>
    <!-- your custom actions here -->
  </CustomActions>
  <CommandDefinitions>
    <!-- your commands here -->
  </CommandDefinitions>
  <RuleDefinitions>
    <TabDisplayRules />
    <DisplayRules />
    <EnableRules />
  </RuleDefinitions>
  <LocLabels />
</RibbonDiffXml>
"@

# Step 4: Use the RetrieveEntityRibbon / UpdateEntityRibbon approach
# The ribbon is updated via entity metadata PATCH with the RibbonDiffXml property
$body = @{
    "RibbonDiffXml" = $ribbonXml
} | ConvertTo-Json -Depth 5

Invoke-RestMethod `
    -Uri "https://org.crm6.dynamics.com/api/data/v9.2/EntityDefinitions($entityMetaId)" `
    -Method PATCH -Headers $headers -Body $body

# Step 5: Publish the entity to apply ribbon changes
$publishBody = @{
    "ParameterXml" = "<importexportxml><entities><entity>$entityLogicalName</entity></entities></importexportxml>"
} | ConvertTo-Json

Invoke-RestMethod `
    -Uri "https://org.crm6.dynamics.com/api/data/v9.2/PublishXml" `
    -Method POST -Headers $headers -Body $publishBody
```

## Button to Modal Dialog Pattern

A common pattern: command bar button opens a JavaScript handler that displays a web
resource as a centered modal dialog.

### JS Web Resource (cnt_/js/commandbar.js)

```javascript
var Contoso = Contoso || {};
Contoso.CommandBar = {

    openTemplateWizard: function(primaryControl) {
        var formContext = primaryControl;
        var entityName = formContext.data.entity.getEntityName();
        var recordId = formContext.data.entity.getId().replace(/[{}]/g, "");

        Xrm.Navigation.navigateTo(
            {
                pageType: "webresource",
                webresourceName: "cnt_/html/templatewizard.html",
                data: encodeURIComponent(JSON.stringify({
                    entityName: entityName,
                    recordId: recordId
                }))
            },
            {
                target: 2,
                position: 1,
                width: { value: 70, unit: "%" },
                height: { value: 60, unit: "%" },
                title: "New from Template"
            }
        ).then(function(returnValue) {
            if (returnValue && returnValue.created) {
                formContext.data.refresh(false);
            }
        });
    }
};
```

### HTML Web Resource (cnt_/html/templatewizard.html)

```html
<!DOCTYPE html>
<html>
<head>
    <title>Template Wizard</title>
    <style>
        body { font-family: "Segoe UI", sans-serif; margin: 20px; }
        .template-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
        .template-card { border: 1px solid #ccc; padding: 16px; border-radius: 8px; cursor: pointer; }
        .template-card:hover { border-color: #0078d4; background: #f0f8ff; }
        .btn-primary { background: #0078d4; color: #fff; border: none; padding: 10px 24px;
                       border-radius: 4px; cursor: pointer; font-size: 14px; }
        .btn-secondary { background: #f3f2f1; border: 1px solid #ccc; padding: 10px 24px;
                         border-radius: 4px; cursor: pointer; font-size: 14px; }
    </style>
</head>
<body>
    <h2>Select a Template</h2>
    <div class="template-grid" id="templates"></div>
    <div style="margin-top: 20px; text-align: right;">
        <button class="btn-secondary" onclick="cancel()">Cancel</button>
        <button class="btn-primary" onclick="apply()" id="applyBtn" disabled>Apply Template</button>
    </div>

    <script>
        var selectedTemplate = null;
        var context = {};

        // Parse incoming data
        var dataParam = new URLSearchParams(window.location.search).get("Data");
        if (dataParam) {
            context = JSON.parse(decodeURIComponent(dataParam));
        }

        // Load templates (could also fetch from Dataverse via Xrm.WebApi)
        var templates = [
            { id: "basic", name: "Basic Project", description: "Standard project setup" },
            { id: "agile", name: "Agile Sprint", description: "Sprint-based project" },
            { id: "waterfall", name: "Waterfall", description: "Phase-gated project" }
        ];

        var grid = document.getElementById("templates");
        templates.forEach(function(t) {
            var card = document.createElement("div");
            card.className = "template-card";
            card.innerHTML = "<h3>" + t.name + "</h3><p>" + t.description + "</p>";
            card.onclick = function() {
                document.querySelectorAll(".template-card").forEach(function(c) {
                    c.style.borderColor = "#ccc";
                    c.style.background = "";
                });
                card.style.borderColor = "#0078d4";
                card.style.background = "#f0f8ff";
                selectedTemplate = t.id;
                document.getElementById("applyBtn").disabled = false;
            };
            grid.appendChild(card);
        });

        function apply() {
            window.parent.Xrm.Navigation.closeDialog({
                created: true,
                templateId: selectedTemplate
            });
        }

        function cancel() {
            window.parent.Xrm.Navigation.closeDialog(null);
        }
    </script>
</body>
</html>
```

## Button to Side Pane Pattern

A command bar button opens a persistent side pane with a web resource.

```javascript
Contoso.CommandBar.openDashboardPane = function(primaryControl) {
    var formContext = primaryControl;

    // Check if pane already exists
    try {
        var existing = Xrm.App.sidePanes.getPane("dashboardPane");
        if (existing) {
            existing.focus();
            return;
        }
    } catch(e) {
        // Pane doesn't exist, create it
    }

    Xrm.App.sidePanes.createPane({
        paneId: "dashboardPane",
        title: "Dashboard",
        imageSrc: "WebResources/cnt_/images/dashboard_icon.svg",
        canClose: true,
        width: 450
    }).then(function(pane) {
        pane.navigate({
            pageType: "webresource",
            webresourceName: "cnt_/html/dashboard.html",
            data: encodeURIComponent(JSON.stringify({
                recordId: formContext.data.entity.getId().replace(/[{}]/g, ""),
                entityName: formContext.data.entity.getEntityName()
            }))
        });
    });
};
```

## Common Scenarios

### "New from Template" Button

Opens a dialog where the user selects a template, then creates a new record with
pre-populated fields based on the template. See the Button to Modal Dialog pattern above.

### "Run Wizard" Button

Opens a multi-step wizard in a modal dialog. Each step collects data, the final step
creates or updates records via `Xrm.WebApi`. Returns a result to the parent form.

### "Open Dashboard" Button

Opens a side pane with an HTML dashboard showing charts, KPIs, or aggregated data for
the current record's context. Persists while the user navigates between records.

### "Export Custom Report" Button

Opens a dialog showing export options, calls a custom API or Azure Function to generate
the report, then triggers a download or opens the report in a new window.

```javascript
Contoso.CommandBar.exportReport = function(primaryControl) {
    var formContext = primaryControl;
    var recordId = formContext.data.entity.getId().replace(/[{}]/g, "");

    Xrm.Navigation.navigateTo(
        {
            pageType: "webresource",
            webresourceName: "cnt_/html/exportoptions.html",
            data: encodeURIComponent(JSON.stringify({ recordId: recordId }))
        },
        {
            target: 2,
            position: 1,
            width: { value: 500, unit: "px" },
            height: { value: 400, unit: "px" },
            title: "Export Report"
        }
    ).then(function(returnValue) {
        if (returnValue && returnValue.downloadUrl) {
            window.open(returnValue.downloadUrl, "_blank");
        }
    });
};
```

## Registering JS Web Resource as Command Handler

For the JavaScript to work as a command handler, the web resource must be:

1. **Created** in Dataverse with the correct name (e.g., `cnt_/js/commandbar.js`).
2. **Published** so it is available to the runtime.
3. **Referenced** in the RibbonDiffXml via the `Library` attribute:
   ```xml
   <JavaScriptFunction FunctionName="Contoso.CommandBar.onApproveClick"
                       Library="$webresource:cnt_/js/commandbar.js">
   ```
4. The function must be accessible via the namespace path specified in `FunctionName`.
5. Parameters are passed via `<CrmParameter>` child elements.

For the modern command designer approach, the web resource is selected via the UI and
the function name is specified in a text field.
