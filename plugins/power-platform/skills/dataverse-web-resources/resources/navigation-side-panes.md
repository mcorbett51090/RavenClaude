# Navigation, Side Panes, and Dialogs

Model-driven apps provide several APIs for programmatic navigation: opening side panes,
inline dialogs, web resources in new windows, entity forms, and system alert/confirm dialogs.
These are all accessed through the `Xrm.App` and `Xrm.Navigation` namespaces.

## Xrm.App.sidePanes.createPane()

Opens a web resource, custom page, or entity form in a collapsible side panel that persists
alongside the main form. Ideal for contextual tools (AI chat, help, related record preview)
that users interact with without leaving the current record.

### Pane Properties

| Property | Type | Description |
|---|---|---|
| `paneId` | string | Unique identifier for the pane. If a pane with this ID exists, it is focused instead of creating a new one. |
| `title` | string | Title displayed at the top of the pane. |
| `imageSrc` | string | URL to an icon image shown in the pane selector rail (32x32 recommended). Can be a web resource URL. |
| `canClose` | boolean | Whether the user can close the pane via the X button. Default: `true`. |
| `width` | number | Width of the pane in pixels. Default: `300`. Recommended range: 300-600. |
| `hidden` | boolean | Whether the pane starts hidden (just icon in rail). Default: `false`. |
| `alwaysRender` | boolean | Whether the pane content renders even when collapsed. Default: `false`. |
| `badge` | number | Badge count shown on the pane icon (for notifications). |

### Opening a Web Resource in a Side Pane

```javascript
var MyApp = MyApp || {};
MyApp.SidePanes = {

    openHelpPane: function(primaryControl) {
        var formContext = primaryControl;
        var recordId = formContext.data.entity.getId().replace(/[{}]/g, "");
        var entityName = formContext.data.entity.getEntityName();

        Xrm.App.sidePanes.createPane({
            paneId: "helpPane",
            title: "Contextual Help",
            imageSrc: "WebResources/cnt_/images/help_icon.svg",
            canClose: true,
            width: 400
        }).then(function(pane) {
            pane.navigate({
                pageType: "webresource",
                webresourceName: "cnt_/html/helpviewer.html",
                data: encodeURIComponent(JSON.stringify({
                    entityName: entityName,
                    recordId: recordId
                }))
            });
        });
    }
};
```

### Opening a Custom Page in a Side Pane

```javascript
openCustomPagePane: function(primaryControl) {
    Xrm.App.sidePanes.createPane({
        paneId: "wizardPane",
        title: "Record Wizard",
        imageSrc: "WebResources/cnt_/images/wizard_icon.svg",
        canClose: true,
        width: 500
    }).then(function(pane) {
        pane.navigate({
            pageType: "custom",
            name: "cnt_wizardpage_a1b2c",  // Custom page logical name
            recordId: "some-guid-here"      // Optional: pass record context
        });
    });
}
```

### Opening an Entity Form in a Side Pane

```javascript
openRelatedRecordPane: function(primaryControl) {
    var formContext = primaryControl;
    var lookup = formContext.getAttribute("cnt_parentaccountid").getValue();
    if (!lookup || lookup.length === 0) return;

    Xrm.App.sidePanes.createPane({
        paneId: "relatedAccountPane",
        title: "Parent Account",
        canClose: true,
        width: 500
    }).then(function(pane) {
        pane.navigate({
            pageType: "entityrecord",
            entityName: "account",
            entityId: lookup[0].id.replace(/[{}]/g, "")
        });
    });
}
```

### Managing Existing Panes

```javascript
// Get an existing pane by ID
var pane = Xrm.App.sidePanes.getPane("helpPane");

// Close a pane
Xrm.App.sidePanes.getPane("helpPane").close();

// Update badge count (e.g., for unread notifications)
Xrm.App.sidePanes.getPane("chatPane").badge = 3;

// Check if a pane already exists before creating
var existingPane = Xrm.App.sidePanes.getPane("helpPane");
if (existingPane) {
    existingPane.focus();
} else {
    // Create new pane...
}
```

## Xrm.Navigation.navigateTo()

Opens content as an inline dialog (modal or modeless) that floats over the current form.
Use for wizard flows, confirmation screens, or focused data entry that should not navigate
away from the current context.

### Modal Dialog with Web Resource

```javascript
MyApp.Dialogs = {

    openWizardDialog: function(primaryControl) {
        var formContext = primaryControl;
        var recordId = formContext.data.entity.getId().replace(/[{}]/g, "");

        Xrm.Navigation.navigateTo(
            {
                pageType: "webresource",
                webresourceName: "cnt_/html/wizard.html",
                data: encodeURIComponent(JSON.stringify({
                    recordId: recordId,
                    mode: "create"
                }))
            },
            {
                target: 2,           // 2 = inline dialog (1 = new window)
                position: 1,         // 1 = center (2 = side)
                width: { value: 70, unit: "%" },
                height: { value: 60, unit: "%" },
                title: "Setup Wizard"
            }
        ).then(function(returnValue) {
            // Dialog closed — returnValue contains data passed back
            console.log("Wizard completed:", returnValue);
            formContext.data.refresh(false);
        }).catch(function(error) {
            console.error("Dialog error:", error.message);
        });
    }
};
```

### Modeless Dialog (Side Position)

```javascript
openSideDialog: function(primaryControl) {
    Xrm.Navigation.navigateTo(
        {
            pageType: "webresource",
            webresourceName: "cnt_/html/chatpanel.html"
        },
        {
            target: 2,
            position: 2,        // 2 = side (slides in from the right)
            width: { value: 400, unit: "px" },
            height: { value: 100, unit: "%" }
        }
    );
}
```

### Dialog with Custom Page Content

```javascript
openCustomPageDialog: function(primaryControl) {
    Xrm.Navigation.navigateTo(
        {
            pageType: "custom",
            name: "cnt_approvalpage_c3d4e"
        },
        {
            target: 2,
            position: 1,
            width: { value: 600, unit: "px" },
            height: { value: 400, unit: "px" },
            title: "Approval Form"
        }
    ).then(function(returnValue) {
        if (returnValue && returnValue.approved) {
            // Handle approval
        }
    });
}
```

### Returning Data from a Dialog

Inside the web resource opened as a dialog, use `Xrm.Navigation.closeDialog()` to pass
data back to the caller:

```javascript
// Inside the dialog web resource (cnt_/html/wizard.html)
function completeWizard() {
    var returnData = {
        selectedOption: "optionA",
        quantity: 5,
        notes: "User completed wizard"
    };
    // Close and return data to the .then() handler in the parent
    window.parent.Xrm.Navigation.closeDialog(returnData);
}

function cancelWizard() {
    window.parent.Xrm.Navigation.closeDialog(null);
}
```

## Xrm.Navigation.openWebResource()

Opens a web resource in a new browser window or a dialog. Simpler than `navigateTo()` but
less control over dialog positioning.

```javascript
MyApp.Navigation = {

    openReportWindow: function(primaryControl) {
        var formContext = primaryControl;
        var recordId = formContext.data.entity.getId().replace(/[{}]/g, "");

        Xrm.Navigation.openWebResource(
            "cnt_/html/reportviewer.html",    // Web resource name
            {
                openInNewWindow: true,         // true = new window, false = dialog
                width: 1024,
                height: 768
            },
            encodeURIComponent(JSON.stringify({ recordId: recordId }))  // Data parameter
        );
    },

    openReportDialog: function(primaryControl) {
        Xrm.Navigation.openWebResource(
            "cnt_/html/reportviewer.html",
            {
                openInNewWindow: false,
                width: 800,
                height: 600
            }
        );
    }
};
```

## Xrm.Navigation.openForm()

Opens an entity form programmatically. Use for creating related records, opening specific
forms, or pre-populating fields.

### Open Existing Record

```javascript
openAccountForm: function(accountId) {
    Xrm.Navigation.openForm({
        entityName: "account",
        entityId: accountId.replace(/[{}]/g, "")
    });
}
```

### Create New Record with Pre-populated Fields

```javascript
createRelatedTask: function(primaryControl) {
    var formContext = primaryControl;
    var recordId = formContext.data.entity.getId();
    var recordName = formContext.getAttribute("cnt_name").getValue();

    Xrm.Navigation.openForm({
        entityName: "cnt_task",
        createFromEntity: {                    // Pre-set parent lookup
            entityType: formContext.data.entity.getEntityName(),
            id: recordId,
            name: recordName
        },
        formId: "specific-form-guid-here",     // Optional: open specific form
        cmdbar: true,                          // Show command bar
        navbar: "off"                          // "on", "off", or "entity"
    }).then(function(result) {
        if (result && result.savedEntityReference) {
            var newId = result.savedEntityReference[0].id;
            console.log("Created task:", newId);
            // Refresh a subgrid to show the new record
            formContext.getControl("tasks_subgrid").refresh();
        }
    });
}
```

### Open Form with Parameters (Pre-fill Fields)

```javascript
createPrepopulatedRecord: function(primaryControl) {
    var formContext = primaryControl;

    var params = {};
    params["cnt_name"] = "Auto-generated from " + formContext.getAttribute("cnt_name").getValue();
    params["cnt_priority"] = 892100002;  // High
    params["cnt_parentid"] = formContext.data.entity.getId().replace(/[{}]/g, "");
    params["cnt_parentidname"] = formContext.getAttribute("cnt_name").getValue();
    params["cnt_parentidtype"] = formContext.data.entity.getEntityName();

    Xrm.Navigation.openForm({
        entityName: "cnt_childrecord",
        useQuickCreateForm: false
    }, params);
}
```

### Open Quick Create Form

```javascript
openQuickCreate: function(primaryControl) {
    Xrm.Navigation.openForm({
        entityName: "cnt_task",
        useQuickCreateForm: true
    }).then(function(result) {
        if (result && result.savedEntityReference) {
            console.log("Quick created:", result.savedEntityReference[0].id);
        }
    });
}
```

## Xrm.Navigation.openAlertDialog() / openConfirmDialog()

Simple system dialogs for alerts and confirmations. No custom content, just text and buttons.

### Alert Dialog

```javascript
showAlert: function(message) {
    Xrm.Navigation.openAlertDialog(
        {
            text: message,
            title: "Information",
            confirmButtonLabel: "OK"
        },
        {
            width: 400,
            height: 200
        }
    ).then(function() {
        console.log("User acknowledged alert");
    });
}
```

### Confirm Dialog

```javascript
confirmAction: function(primaryControl) {
    var formContext = primaryControl;

    Xrm.Navigation.openConfirmDialog(
        {
            text: "Are you sure you want to approve this record? This action cannot be undone.",
            title: "Confirm Approval",
            confirmButtonLabel: "Approve",
            cancelButtonLabel: "Cancel"
        },
        {
            width: 450,
            height: 220
        }
    ).then(function(result) {
        if (result.confirmed) {
            formContext.getAttribute("cnt_status").setValue(892100001); // Approved
            formContext.data.entity.save();
        }
    });
}
```

## Use Cases and Integration Patterns

### AI Chat Panel

A persistent side pane that hosts a web resource containing a chat interface for
AI-assisted data entry or record analysis.

```javascript
MyApp.AI = {
    openChatPanel: function(primaryControl) {
        var formContext = primaryControl;
        var entityName = formContext.data.entity.getEntityName();
        var recordId = formContext.data.entity.getId().replace(/[{}]/g, "");

        Xrm.App.sidePanes.createPane({
            paneId: "aiChatPane",
            title: "AI Assistant",
            imageSrc: "WebResources/cnt_/images/ai_chat_icon.svg",
            canClose: true,
            width: 420,
            badge: 0
        }).then(function(pane) {
            pane.navigate({
                pageType: "webresource",
                webresourceName: "cnt_/html/aichat.html",
                data: encodeURIComponent(JSON.stringify({
                    entityName: entityName,
                    recordId: recordId,
                    userName: Xrm.Utility.getGlobalContext().userSettings.userName
                }))
            });
        });
    }
};
```

### Wizard Flow in Modal Dialog

A multi-step wizard for complex record creation, opened from a command bar button.

```javascript
MyApp.Wizards = {
    openSetupWizard: function(primaryControl) {
        Xrm.Navigation.navigateTo(
            {
                pageType: "webresource",
                webresourceName: "cnt_/html/setupwizard.html"
            },
            {
                target: 2,
                position: 1,
                width: { value: 80, unit: "%" },
                height: { value: 70, unit: "%" },
                title: "Setup Wizard"
            }
        ).then(function(returnValue) {
            if (returnValue && returnValue.completed) {
                primaryControl.data.refresh(false);
            }
        });
    }
};
```

### Related Record Preview

A side pane that shows a read-only preview of a related record (e.g., parent account
details) without navigating away from the current form.

```javascript
MyApp.Preview = {
    previewParentAccount: function(primaryControl) {
        var formContext = primaryControl;
        var accountLookup = formContext.getAttribute("cnt_accountid").getValue();
        if (!accountLookup || accountLookup.length === 0) {
            Xrm.Navigation.openAlertDialog({
                text: "No parent account is set on this record.",
                title: "No Account"
            });
            return;
        }

        Xrm.App.sidePanes.createPane({
            paneId: "accountPreview",
            title: accountLookup[0].name,
            canClose: true,
            width: 500
        }).then(function(pane) {
            pane.navigate({
                pageType: "entityrecord",
                entityName: "account",
                entityId: accountLookup[0].id.replace(/[{}]/g, "")
            });
        });
    }
};
```

### Command Bar Button Integration Pattern

The standard integration pattern: a command bar button triggers a JavaScript handler that
opens a side pane or dialog.

1. **Create the JS web resource** with the handler function.
2. **Create the HTML web resource** (the content shown in the pane/dialog).
3. **Add a command bar button** (via RibbonDiffXml or modern command bar) that calls the handler.
4. The handler uses `Xrm.App.sidePanes.createPane()` or `Xrm.Navigation.navigateTo()`.

```
[Command Bar Button] --click--> [JS Handler] --calls--> [createPane / navigateTo]
                                                              |
                                                              v
                                                     [Web Resource / Custom Page]
```

## Passing Data Between Parent Form and Pane/Dialog Content

### Parent to Child (Outbound Data)

Data is passed via the `data` parameter as a URL-encoded JSON string:

```javascript
// Parent (JS handler)
pane.navigate({
    pageType: "webresource",
    webresourceName: "cnt_/html/viewer.html",
    data: encodeURIComponent(JSON.stringify({ recordId: "abc", mode: "edit" }))
});
```

```javascript
// Child (inside the web resource HTML)
var dataParam = new URLSearchParams(window.location.search).get("Data")
    || new URLSearchParams(window.location.search).get("data");
if (dataParam) {
    var context = JSON.parse(decodeURIComponent(dataParam));
    console.log(context.recordId, context.mode);
}
```

### Child to Parent (Return Data)

For dialogs opened via `navigateTo()`, the child calls `closeDialog()`:

```javascript
// Child closes and returns data
window.parent.Xrm.Navigation.closeDialog({ status: "completed", newRecordId: "xyz" });
```

For side panes, use `window.parent.postMessage()` for cross-frame communication:

```javascript
// Child sends message to parent frame
window.parent.postMessage({ type: "PANE_ACTION", payload: { action: "refresh" } }, "*");

// Parent listens (set up in OnLoad)
window.addEventListener("message", function(event) {
    if (event.data && event.data.type === "PANE_ACTION") {
        formContext.data.refresh(false);
    }
});
```

## Code App as Pane Content

Power Apps Code Apps (React/TypeScript) can be loaded as custom pages within side panes
and dialogs. However, note:

- Code Apps run as **custom pages**, not web resources. Use `pageType: "custom"` in navigation.
- The Code App must be registered as a custom page in the solution.
- Side pane width may constrain the Code App layout; design responsive components.
- If Code App hosting is not available, use an **HTML web resource** with embedded
  React (bundled via webpack/vite) as an alternative.

```javascript
// Open Code App custom page in side pane
Xrm.App.sidePanes.createPane({
    paneId: "codeAppPane",
    title: "Analytics Dashboard",
    width: 500
}).then(function(pane) {
    pane.navigate({
        pageType: "custom",
        name: "cnt_analyticsdashboard_a1b2c"
    });
});
```

## Error Handling

Always wrap navigation calls in error handling:

```javascript
Xrm.App.sidePanes.createPane({
    paneId: "myPane",
    title: "My Pane",
    width: 400
}).then(function(pane) {
    pane.navigate({
        pageType: "webresource",
        webresourceName: "cnt_/html/mypane.html"
    });
}).catch(function(error) {
    console.error("Failed to create side pane:", error.message);
    Xrm.Navigation.openAlertDialog({
        text: "Could not open the panel. Please try again.",
        title: "Error"
    });
});
```
