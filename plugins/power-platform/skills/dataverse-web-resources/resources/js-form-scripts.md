# JavaScript Form Scripts

JavaScript web resources extend model-driven app forms with custom logic for
validation, auto-population, visibility control, and business rule enforcement.

## The Namespace Pattern

**Always** wrap functions in a namespace to avoid global scope pollution:

```javascript
// cnt_/js/projectform.js
var Contoso = Contoso || {};
Contoso.ProjectForm = {

    onLoad: function(executionContext) {
        var formContext = executionContext.getFormContext();
        // Form load logic
    },

    onSave: function(executionContext) {
        var formContext = executionContext.getFormContext();
        // Save validation logic
    },

    onBudgetChange: function(executionContext) {
        var formContext = executionContext.getFormContext();
        // Field change logic
    }
};
```

## Event Types

### OnLoad — Fires when the form opens

```javascript
onLoad: function(executionContext) {
    var formContext = executionContext.getFormContext();

    // Check form type (1=Create, 2=Update, 3=ReadOnly, 4=Disabled, 6=BulkEdit)
    var formType = formContext.ui.getFormType();

    if (formType === 1) {
        // Create mode — set defaults
        formContext.getAttribute("cnt_status").setValue(892100000);
    }

    // Hide a section based on a condition
    var tab = formContext.ui.tabs.get("details");
    if (tab) {
        var section = tab.sections.get("admin_section");
        if (section) section.setVisible(false);
    }
}
```

### OnSave — Fires before save completes

```javascript
onSave: function(executionContext) {
    var formContext = executionContext.getFormContext();

    var budget = formContext.getAttribute("cnt_budget").getValue();
    if (budget > 1000000) {
        // Prevent save with validation message
        executionContext.getEventArgs().preventDefault();
        formContext.ui.setFormNotification(
            "Budget exceeds $1M — requires VP approval.",
            "ERROR",
            "budgetValidation"
        );
        return;
    }

    // Clear any previous notification
    formContext.ui.clearFormNotification("budgetValidation");
}
```

### OnChange — Fires when a field value changes

```javascript
onBudgetChange: function(executionContext) {
    var formContext = executionContext.getFormContext();

    var budget = formContext.getAttribute("cnt_budget").getValue();

    // Auto-set priority based on budget
    if (budget > 500000) {
        formContext.getAttribute("cnt_priority").setValue(892100002); // High
    } else if (budget > 100000) {
        formContext.getAttribute("cnt_priority").setValue(892100001); // Medium
    } else {
        formContext.getAttribute("cnt_priority").setValue(892100000); // Low
    }
}
```

## formContext API Reference

### Getting/Setting Field Values

```javascript
// Get a field value
var name = formContext.getAttribute("cnt_projectname").getValue();

// Set a field value
formContext.getAttribute("cnt_status").setValue(892100001);

// Get lookup value (returns array of objects)
var lookup = formContext.getAttribute("cnt_accountid").getValue();
if (lookup && lookup.length > 0) {
    var accountId = lookup[0].id;
    var accountName = lookup[0].name;
}

// Set lookup value
formContext.getAttribute("cnt_accountid").setValue([{
    id: "{account-guid}",
    name: "Contoso Ltd",
    entityType: "account"
}]);

// Get option set value (numeric)
var priority = formContext.getAttribute("cnt_priority").getValue(); // e.g., 892100001

// Get option set text
var priorityText = formContext.getAttribute("cnt_priority").getText(); // e.g., "Medium"
```

### Control Visibility and State

```javascript
// Show/hide a field
formContext.getControl("cnt_budget").setVisible(true);
formContext.getControl("cnt_budget").setVisible(false);

// Enable/disable a field
formContext.getControl("cnt_budget").setDisabled(true);
formContext.getControl("cnt_budget").setDisabled(false);

// Set field as required
formContext.getAttribute("cnt_budget").setRequiredLevel("required");  // "required", "recommended", "none"

// Set field notification (validation message)
formContext.getControl("cnt_budget").setNotification("Budget must be positive", "budgetError");
formContext.getControl("cnt_budget").clearNotification("budgetError");
```

### Form-Level Operations

```javascript
// Form notification (top banner)
formContext.ui.setFormNotification("Record saved successfully", "INFO", "saveSuccess");
formContext.ui.clearFormNotification("saveSuccess");

// Refresh the form
formContext.data.refresh(false); // false = don't save before refresh

// Save the form
formContext.data.entity.save(); // or save("saveandclose"), save("saveandnew")

// Get record ID
var recordId = formContext.data.entity.getId();

// Get entity name
var entityName = formContext.data.entity.getEntityName();
```

### Tab and Section Control

```javascript
// Show/hide a tab
formContext.ui.tabs.get("details").setVisible(false);

// Expand/collapse a tab
formContext.ui.tabs.get("details").setDisplayState("expanded"); // or "collapsed"

// Show/hide a section within a tab
formContext.ui.tabs.get("general").sections.get("admin_section").setVisible(false);
```

## Ribbon/Command Bar Handlers

```javascript
Contoso.RibbonCommands = {
    // Enable rule — determines if button is enabled
    isApproveEnabled: function(primaryControl) {
        var formContext = primaryControl;
        var status = formContext.getAttribute("cnt_status").getValue();
        return status === 892100000; // Only enable for "Pending" status
    },

    // Command handler — executes when button is clicked
    approveRecord: function(primaryControl) {
        var formContext = primaryControl;
        formContext.getAttribute("cnt_status").setValue(892100001); // "Approved"
        formContext.data.entity.save();
    }
};
```

## Async Operations (Web API calls from forms)

```javascript
onLoad: async function(executionContext) {
    var formContext = executionContext.getFormContext();

    try {
        // Fetch related data using Xrm.WebApi
        var result = await Xrm.WebApi.retrieveMultipleRecords(
            "cnt_task",
            "?$filter=_cnt_projectid_value eq " + formContext.data.entity.getId().replace(/[{}]/g, "") +
            "&$select=cnt_taskname,cnt_status"
        );

        console.log("Found " + result.entities.length + " related tasks");
    } catch (error) {
        console.error("Error fetching tasks:", error.message);
    }
}
```

## Best Practices

1. **Always use namespaces** — never pollute global scope
2. **Always check for null** before accessing field values
3. **Use constants** for option set values (not magic numbers)
4. **Handle all form types** — Create, Update, ReadOnly behave differently
5. **Test with form type checks** — `formContext.ui.getFormType()`
6. **Use async/await** for Web API calls, with try/catch error handling
7. **Clear notifications** when conditions are resolved
8. **Minimize OnLoad logic** — heavy scripts delay form rendering
9. **Use `passExecutionContext: true`** when registering handlers
10. **Log with `console.log`** during development, remove for production

## Advanced Form Control

Beyond basic show/hide of tabs and sections, these patterns handle complex, multi-condition
form layout changes driven by field values.

### Cascading Visibility Based on Multiple Fields

```javascript
Contoso.FormControl = {

    /**
     * Call from OnLoad and from OnChange of both cnt_category and cnt_priority.
     * Evaluates multiple fields together to determine form layout.
     */
    updateFormLayout: function(executionContext) {
        var formContext = executionContext.getFormContext();

        var category = formContext.getAttribute("cnt_category").getValue();
        var priority = formContext.getAttribute("cnt_priority").getValue();
        var formType = formContext.ui.getFormType();

        // --- Tab visibility ---
        var financialTab = formContext.ui.tabs.get("tab_financial");
        var technicalTab = formContext.ui.tabs.get("tab_technical");

        if (financialTab) {
            // Show financial tab only for "Capital" category
            financialTab.setVisible(category === 892100002);
        }
        if (technicalTab) {
            // Show technical tab for "IT" or "Engineering" categories
            technicalTab.setVisible(category === 892100003 || category === 892100004);
        }

        // --- Section visibility within a tab ---
        var generalTab = formContext.ui.tabs.get("tab_general");
        if (generalTab) {
            var approvalSection = generalTab.sections.get("section_approval");
            var escalationSection = generalTab.sections.get("section_escalation");

            if (approvalSection) {
                // Show approval section for High priority on existing records
                approvalSection.setVisible(priority === 892100002 && formType === 2);
            }
            if (escalationSection) {
                // Show escalation section only for Critical priority
                escalationSection.setVisible(priority === 892100003);
            }
        }

        // --- Dynamic field requirements based on section visibility ---
        if (priority === 892100002 || priority === 892100003) {
            formContext.getAttribute("cnt_approver").setRequiredLevel("required");
            formContext.getAttribute("cnt_justification").setRequiredLevel("required");
        } else {
            formContext.getAttribute("cnt_approver").setRequiredLevel("none");
            formContext.getAttribute("cnt_justification").setRequiredLevel("none");
        }
    },

    /**
     * Iterate all sections in a tab and hide those matching a pattern.
     * Useful for role-based or license-based section visibility.
     */
    hideAdminSections: function(executionContext) {
        var formContext = executionContext.getFormContext();
        var userRoles = Xrm.Utility.getGlobalContext().userSettings.securityRoles;
        var isAdmin = false; // Determine based on role GUIDs

        formContext.ui.tabs.forEach(function(tab) {
            tab.sections.forEach(function(section) {
                var sectionName = section.getName();
                if (sectionName && sectionName.indexOf("admin_") === 0) {
                    section.setVisible(isAdmin);
                }
            });
        });
    }
};
```

### Programmatic Tab Focus and Expansion

```javascript
/**
 * Expand a specific tab and scroll to it after a field change.
 */
focusOnTab: function(executionContext, tabName) {
    var formContext = executionContext.getFormContext();
    var tab = formContext.ui.tabs.get(tabName);
    if (tab) {
        tab.setVisible(true);
        tab.setDisplayState("expanded");
        tab.setFocus();
    }
}
```

## Notification API

Model-driven apps have two notification levels: form-level banners (top of form) and
field-level messages (below a specific control).

### Form-Level Notifications

```javascript
Contoso.Notifications = {

    /**
     * Form notifications appear as a colored banner at the top of the form.
     * Types: "ERROR" (red), "WARNING" (yellow), "INFO" (blue)
     * Each notification needs a unique ID for later clearing.
     */
    showFormNotifications: function(executionContext) {
        var formContext = executionContext.getFormContext();

        // Error — blocks save if used with preventDefault()
        formContext.ui.setFormNotification(
            "This record has validation errors. Please review before saving.",
            "ERROR",
            "validationError"
        );

        // Warning — informational, does not block save
        formContext.ui.setFormNotification(
            "This record is past its due date.",
            "WARNING",
            "overdueWarning"
        );

        // Info — neutral informational message
        formContext.ui.setFormNotification(
            "This record was last modified by an automated process.",
            "INFO",
            "autoModifiedInfo"
        );
    },

    /**
     * Clear notifications individually by ID or check before adding.
     */
    clearSpecificNotification: function(formContext) {
        formContext.ui.clearFormNotification("overdueWarning");
    },

    /**
     * Timed notification — show for 5 seconds then clear.
     */
    showTimedNotification: function(formContext, message, notificationId) {
        formContext.ui.setFormNotification(message, "INFO", notificationId);
        setTimeout(function() {
            formContext.ui.clearFormNotification(notificationId);
        }, 5000);
    }
};
```

### Field-Level Notifications

```javascript
Contoso.FieldNotifications = {

    /**
     * Field-level notifications appear directly below the control.
     * Useful for inline validation messages.
     */
    validateEmail: function(executionContext) {
        var formContext = executionContext.getFormContext();
        var emailControl = formContext.getControl("cnt_email");
        var emailValue = formContext.getAttribute("cnt_email").getValue();

        if (emailValue && emailValue.indexOf("@") === -1) {
            // Show error below the email field
            emailControl.setNotification("Please enter a valid email address.", "emailFormat");
        } else {
            // Clear the error when valid
            emailControl.clearNotification("emailFormat");
        }
    },

    /**
     * Validate multiple fields and show individual messages.
     */
    validateAllFields: function(executionContext) {
        var formContext = executionContext.getFormContext();
        var isValid = true;

        // Validate budget
        var budget = formContext.getAttribute("cnt_budget").getValue();
        if (budget !== null && budget < 0) {
            formContext.getControl("cnt_budget").setNotification(
                "Budget cannot be negative.", "budgetNegative"
            );
            isValid = false;
        } else {
            formContext.getControl("cnt_budget").clearNotification("budgetNegative");
        }

        // Validate end date is after start date
        var startDate = formContext.getAttribute("cnt_startdate").getValue();
        var endDate = formContext.getAttribute("cnt_enddate").getValue();
        if (startDate && endDate && endDate <= startDate) {
            formContext.getControl("cnt_enddate").setNotification(
                "End date must be after start date.", "dateRange"
            );
            isValid = false;
        } else {
            formContext.getControl("cnt_enddate").clearNotification("dateRange");
        }

        return isValid;
    }
};
```

## Business Rule Equivalent via JS

Business rules (no-code, configured in the Maker Portal) handle simple show/hide, required
levels, and field defaults. JavaScript is the better choice when:

### When to Use JS Instead of Business Rules

| Scenario | Why JS is Better |
|---|---|
| Cross-entity lookups | Business rules cannot query related entities |
| Async validation (API calls) | Business rules are synchronous only |
| External API calls | Business rules have no HTTP capability |
| Complex conditional chains | Business rules become unreadable with 5+ conditions |
| Regex validation | Business rules have no pattern matching |
| Date arithmetic beyond simple compare | Business rules lack date functions |
| Role-based visibility | Business rules cannot check user security roles |
| Dynamic option filtering | Business rules cannot filter option set choices |

### Cross-Entity Lookup Example

```javascript
/**
 * When the account lookup changes, fetch the account's credit limit
 * and set a warning if the current project budget exceeds it.
 * Business rules cannot do this — they only see current entity fields.
 */
Contoso.BusinessLogic = {

    onAccountChange: async function(executionContext) {
        var formContext = executionContext.getFormContext();
        var accountLookup = formContext.getAttribute("cnt_accountid").getValue();

        if (!accountLookup || accountLookup.length === 0) {
            formContext.ui.clearFormNotification("creditWarning");
            return;
        }

        var accountId = accountLookup[0].id.replace(/[{}]/g, "");

        try {
            var account = await Xrm.WebApi.retrieveRecord(
                "account", accountId, "?$select=creditlimit"
            );

            var budget = formContext.getAttribute("cnt_budget").getValue();
            if (account.creditlimit && budget > account.creditlimit) {
                formContext.ui.setFormNotification(
                    "Budget ($" + budget + ") exceeds account credit limit ($" +
                    account.creditlimit + ").",
                    "WARNING",
                    "creditWarning"
                );
            } else {
                formContext.ui.clearFormNotification("creditWarning");
            }
        } catch (error) {
            console.error("Failed to fetch account credit limit:", error.message);
        }
    }
};
```

### Async Validation on Save Example

```javascript
/**
 * Validate that no duplicate project name exists before saving.
 * Business rules cannot perform this kind of uniqueness check.
 */
onSaveValidation: async function(executionContext) {
    var formContext = executionContext.getFormContext();
    var projectName = formContext.getAttribute("cnt_name").getValue();
    var recordId = formContext.data.entity.getId().replace(/[{}]/g, "");

    if (!projectName) return;

    // Prevent save until async validation completes
    executionContext.getEventArgs().preventDefault();

    try {
        var filter = "?$filter=cnt_name eq '" + projectName.replace(/'/g, "''") + "'";
        if (recordId) {
            filter += " and cnt_projectid ne '" + recordId + "'";
        }
        filter += "&$select=cnt_projectid&$top=1";

        var result = await Xrm.WebApi.retrieveMultipleRecords("cnt_project", filter);

        if (result.entities.length > 0) {
            formContext.ui.setFormNotification(
                "A project with this name already exists. Please use a unique name.",
                "ERROR",
                "duplicateName"
            );
            // Do NOT allow save — preventDefault already called
        } else {
            formContext.ui.clearFormNotification("duplicateName");
            // Validation passed — trigger save programmatically
            formContext.data.entity.save();
        }
    } catch (error) {
        console.error("Duplicate check failed:", error.message);
        // Allow save if check fails (fail-open) or block (fail-closed)
        formContext.data.entity.save();
    }
}
```

## Loading PCF Controls

PCF (PowerApps Component Framework) controls can be bound to form fields and interacted
with through the form scripting API. While direct programmatic manipulation of PCF internals
is limited from form scripts, you can interact with the control through standard APIs.

### Interacting with Controls Hosting PCFs

```javascript
Contoso.PCFInteraction = {

    /**
     * Get the control and check its type.
     * PCF controls are accessed through the same getControl() API.
     */
    interactWithPCF: function(executionContext) {
        var formContext = executionContext.getFormContext();

        // Get the control (works the same whether standard or PCF)
        var control = formContext.getControl("cnt_rating");

        if (control) {
            // Standard operations still work on PCF-bound fields
            control.setVisible(true);
            control.setDisabled(false);

            // The underlying attribute is still accessible
            var ratingValue = formContext.getAttribute("cnt_rating").getValue();
            console.log("Current rating:", ratingValue);
        }
    },

    /**
     * Set a value on the attribute bound to a PCF control.
     * The PCF control will re-render to reflect the new value.
     */
    resetRating: function(executionContext) {
        var formContext = executionContext.getFormContext();
        formContext.getAttribute("cnt_rating").setValue(0);
        // PCF control auto-updates via its updateView lifecycle
    },

    /**
     * Use addOnChange on the attribute to react when the user interacts
     * with the PCF control (e.g., clicks a star in a star rating).
     */
    onLoadSetupPCFListeners: function(executionContext) {
        var formContext = executionContext.getFormContext();

        formContext.getAttribute("cnt_rating").addOnChange(function() {
            var newRating = formContext.getAttribute("cnt_rating").getValue();
            console.log("User changed rating to:", newRating);

            // Update related fields based on PCF interaction
            if (newRating >= 4) {
                formContext.getAttribute("cnt_satisfaction").setValue(892100002); // High
            } else if (newRating >= 2) {
                formContext.getAttribute("cnt_satisfaction").setValue(892100001); // Medium
            } else {
                formContext.getAttribute("cnt_satisfaction").setValue(892100000); // Low
            }
        });
    }
};
```

### Control Notification with PCF Controls

```javascript
/**
 * addNotification on a control shows a clickable notification icon.
 * This works on both standard and PCF controls.
 * Note: This is different from setNotification (validation message).
 */
addControlNotification: function(executionContext) {
    var formContext = executionContext.getFormContext();
    var control = formContext.getControl("cnt_accountid");

    control.addNotification({
        messages: ["This account has overdue invoices."],
        notificationLevel: "RECOMMENDATION",  // "ERROR" or "RECOMMENDATION"
        uniqueId: "overdueInvoice",
        actions: [{
            message: "View Invoices",
            actions: [function() {
                // Navigate to the invoices view
                Xrm.Navigation.navigateTo({
                    pageType: "entitylist",
                    entityName: "invoice",
                    viewId: "invoice-view-guid"
                });
            }]
        }]
    });
}
```

## Refreshing Subgrids

After creating, updating, or deleting related records (via `Xrm.WebApi` or `openForm`),
the subgrid on the parent form does not auto-refresh. You must refresh it programmatically.

### Basic Subgrid Refresh

```javascript
Contoso.SubgridOps = {

    /**
     * Refresh a subgrid after creating a related record.
     * The control name matches the subgrid name on the form designer.
     */
    createAndRefresh: async function(executionContext) {
        var formContext = executionContext.getFormContext();
        var parentId = formContext.data.entity.getId().replace(/[{}]/g, "");

        try {
            await Xrm.WebApi.createRecord("cnt_task", {
                "cnt_name": "New Task",
                "cnt_status": 892100000,
                "cnt_ProjectId@odata.bind": "/cnt_projects(" + parentId + ")"
            });

            // Refresh the subgrid to show the new record
            var subgrid = formContext.getControl("tasks_subgrid");
            if (subgrid) {
                subgrid.refresh();
            }
        } catch (error) {
            console.error("Failed to create task:", error.message);
        }
    },

    /**
     * Refresh subgrid after openForm returns (record created/updated in modal).
     */
    openAndRefresh: function(executionContext) {
        var formContext = executionContext.getFormContext();
        var parentId = formContext.data.entity.getId();
        var parentName = formContext.getAttribute("cnt_name").getValue();

        Xrm.Navigation.openForm({
            entityName: "cnt_task",
            createFromEntity: {
                entityType: "cnt_project",
                id: parentId,
                name: parentName
            }
        }).then(function(result) {
            if (result && result.savedEntityReference) {
                // Record was saved — refresh the subgrid
                var subgrid = formContext.getControl("tasks_subgrid");
                if (subgrid) {
                    subgrid.refresh();
                }
            }
        });
    },

    /**
     * Refresh multiple subgrids at once (e.g., after a bulk operation).
     */
    refreshAllSubgrids: function(formContext) {
        var subgridNames = ["tasks_subgrid", "notes_subgrid", "attachments_subgrid"];

        subgridNames.forEach(function(name) {
            var subgrid = formContext.getControl(name);
            if (subgrid) {
                subgrid.refresh();
            }
        });
    },

    /**
     * Get the row count from a subgrid (useful for conditional logic).
     */
    getSubgridCount: function(formContext, subgridName) {
        var subgrid = formContext.getControl(subgridName);
        if (subgrid) {
            var rowCount = subgrid.getGrid().getTotalRecordCount();
            return rowCount;
        }
        return 0;
    },

    /**
     * Get selected rows from an editable subgrid.
     */
    getSelectedSubgridRows: function(formContext, subgridName) {
        var subgrid = formContext.getControl(subgridName);
        if (!subgrid) return [];

        var selectedRows = subgrid.getGrid().getSelectedRows();
        var records = [];

        selectedRows.forEach(function(row) {
            records.push({
                id: row.getData().getEntity().getId(),
                name: row.getData().getEntity().getPrimaryAttributeValue()
            });
        });

        return records;
    }
};
```

## Static Parameters for Form Event Handlers

```javascript
// Handlers can receive additional string parameters beyond executionContext.
// Configure these in Maker Portal when registering the event handler.
// Parameters are comma-separated strings passed after executionContext.
function onLoadWithParams(executionContext, configParam1, configParam2) {
    var formContext = executionContext.getFormContext();
    // configParam1 and configParam2 are strings configured in the handler registration
    console.log("Config: " + configParam1 + ", " + configParam2);
}
```
This is useful for reusable scripts where you want to parameterize behavior without hardcoding values.

## Additional Client API Methods

### Form Type Detection

```javascript
// formContext.ui.getFormType() returns:
// 0 = Undefined, 1 = Create, 2 = Update, 3 = Read Only, 4 = Disabled, 6 = Bulk Edit
var formType = formContext.ui.getFormType();
if (formType === 1) {
    // Creating a new record — set defaults
} else if (formType === 2) {
    // Updating existing record
}
```

### Submit Mode Control

```javascript
// Control whether a field's value is submitted on save
// "always" — always submit (use when setting values on disabled fields)
// "never" — never submit
// "dirty" — only submit if changed (default)
formContext.getAttribute("fieldname").setSubmitMode("always");
```
IMPORTANT: When programmatically setting values on read-only/disabled fields, you MUST call `setSubmitMode("always")` or the value won't be saved.

### Field Validation

```javascript
// Mark field as invalid (prevents save)
formContext.getControl("fieldname").setIsValid(false, "Value must be between 1 and 100");

// Mark field as valid again (call when user corrects)
formContext.getControl("fieldname").setIsValid(true);

// Check if field is valid
var isValid = formContext.getAttribute("fieldname").isValid();
```

## Table Column Dependencies

When JavaScript references specific columns, add them to the **Table Column Dependencies** list in the form designer. This prevents columns from being accidentally removed from the form, which would break your scripts silently.

## RESX Web Resources for Localization

```javascript
// Extract localized strings from RESX web resources
// RESX filename must include LCID: e.g., "prefix_/strings/Labels.1033.resx"
var localizedText = Xrm.Utility.getResourceString("prefix_/strings/Labels", "ErrorMessage_Required");
formContext.getControl("fieldname").setNotification(localizedText, "validation-error");
```

## BehaviorInBulkEditForm

By default, event handlers are NOT called in bulk edit mode. To enable an OnLoad handler in bulk edit:
- Modify FormXml and set `BehaviorInBulkEditForm="Enabled"` on the relevant event element
- Currently only supported for OnLoad events

## Complete Form Events Reference

| Component | Event | Handler Type |
|---|---|---|
| Column | OnChange | UI (Maker Portal) |
| Control | OnOutputChange | Code (FormXml) |
| Form | OnLoad, OnSave | UI (Maker Portal) |
| Form data | OnLoad | UI (Maker Portal) |
| Grid/Subgrid | OnChange, OnLoad, OnRecordSelect, OnSave | Code (FormXml) |
| IFrame | OnReadyStateComplete | Code (FormXml) |
| Lookup | OnLookupTagClick, PreSearch | Code (FormXml) |
| Process (BPF) | OnProcessStatusChange, OnStageChange, OnStageSelected | Code (formContext.data.process) |
| Tab | TabStateChange | UI (Maker Portal) |
