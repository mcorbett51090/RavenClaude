# Business Process Flow (BPF) Client API

JavaScript API for interacting with Business Process Flows in model-driven app forms.
Covers configuration limits, stage navigation, events, and common patterns.

## BPF Configuration Limits

- Max **10 activated BPFs** per table
- Max **30 stages** per BPF
- One BPF can span **up to 5 different tables**
- Each BPF creation creates a **new tracking table** with the same name as the BPF
- BPFs must be added to the model-driven app via app designer > Automation

## BPF Components

- **Stages** — milestones with data steps
- **Conditions** — branching logic
- **Data Steps** — fields required at each stage, can be marked mandatory
- Can call: Classic workflows, Custom Actions, Power Automate flows

## formContext.data.process API

### Get/Set Active Process

```javascript
// Get the active BPF
var activeProcess = formContext.data.process.getActiveProcess();
console.log("Process ID: " + activeProcess.getId());
console.log("Process Name: " + activeProcess.getName());

// Switch to a different BPF
formContext.data.process.setActiveProcess("PROCESS-GUID-HERE", function onSuccess() {
    console.log("BPF switched successfully");
}, function onError(error) {
    console.log("Error: " + error.message);
});
```

### Get/Set Active Stage

```javascript
// Get current stage
var activeStage = formContext.data.process.getActiveStage();
console.log("Stage ID: " + activeStage.getId());
console.log("Stage Name: " + activeStage.getName());

// Set active stage (jump to specific stage)
formContext.data.process.setActiveStage("STAGE-GUID-HERE", function onSuccess() {
    console.log("Stage set successfully");
}, function onError(error) {
    console.log("Error: " + error.message);
});
```

### Navigate Stages

```javascript
// Move to next stage
formContext.data.process.moveNext(function onSuccess() {
    console.log("Moved to next stage");
}, function onError(error) {
    console.log("Cannot advance: " + error.message);
});

// Move to previous stage
formContext.data.process.movePrevious(function onSuccess() {
    console.log("Moved to previous stage");
}, function onError(error) {
    console.log("Error: " + error.message);
});
```

### Get All Stages

```javascript
// Get all stages in active process
var stages = formContext.data.process.getActiveProcess().getStages();
stages.forEach(function(stage) {
    console.log("Stage: " + stage.getName() + " | Status: " + stage.getStatus());
    // Get data steps in this stage
    var steps = stage.getSteps();
    steps.forEach(function(step) {
        console.log("  Step: " + step.getName() + " | Required: " + step.isRequired());
    });
});
```

### Process Status

```javascript
// Get process status ("active" or "finished")
var status = formContext.data.process.getStatus();

// Set process status
formContext.data.process.setStatus("finished", function onSuccess() {
    console.log("Process completed");
}, function onError(error) {
    console.log("Error: " + error.message);
});
```

## BPF Events

| Event | When Fired | Handler Registration |
|---|---|---|
| OnProcessStatusChange | Process completes, reactivates, or changes status | formContext.data.process.addOnProcessStatusChange(handler) |
| OnStageChange | User advances or goes back to a different stage | formContext.data.process.addOnStageChange(handler) |
| OnStageSelected | User clicks on a stage in the BPF bar | formContext.data.process.addOnStageSelected(handler) |

```javascript
// Register BPF event handlers (typically in form OnLoad)
function onLoad(executionContext) {
    var formContext = executionContext.getFormContext();
    formContext.data.process.addOnStageChange(onStageChange);
    formContext.data.process.addOnProcessStatusChange(onProcessStatusChange);
}

function onStageChange(executionContext) {
    var formContext = executionContext.getFormContext();
    var stage = formContext.data.process.getActiveStage();
    console.log("Now at stage: " + stage.getName());
    // Example: unlock fields specific to this stage
    // Example: show/hide tabs based on current stage
}

function onProcessStatusChange(executionContext) {
    var formContext = executionContext.getFormContext();
    var status = formContext.data.process.getStatus();
    if (status === "finished") {
        // Lock all fields, show completion notification
        formContext.ui.setFormNotification("Process complete!", "INFO", "bpf-done");
    }
}
```

## Common Patterns

### Switch BPF from Command Bar

```javascript
// Command bar handler receives primaryControl (not executionContext)
function switchToApprovalProcess(primaryControl) {
    var formContext = primaryControl;
    formContext.data.process.setActiveProcess("APPROVAL-BPF-GUID",
        function() { formContext.data.refresh(); },
        function(err) {
            Xrm.Navigation.openAlertDialog({ text: "Cannot switch: " + err.message });
        }
    );
}
```

### Stage-Based Field Visibility

```javascript
function adjustFieldsForStage(executionContext) {
    var formContext = executionContext.getFormContext();
    var stage = formContext.data.process.getActiveStage();
    var stageName = stage.getName();

    // Show resolution fields only in "Resolution" stage
    var showResolution = (stageName === "Resolution");
    formContext.getControl("new_resolution").setVisible(showResolution);
    formContext.getControl("new_rootcause").setVisible(showResolution);
}
```

## BPF Security

- Security roles can restrict which BPFs a user sees
- System Administrator and System Customizer see all BPFs by default
- Users need minimum read-level privileges on the **Process** table

## Command Bar Button + BPF: Switch Process

A common pattern is a command bar button that switches between BPFs. The handler receives `primaryControl` (the form context directly), not `executionContext`:

```javascript
function switchBPF(primaryControl, targetProcessId) {
    var formContext = primaryControl;
    formContext.data.process.setActiveProcess(targetProcessId,
        function() { formContext.data.refresh(); },
        function(err) { console.log(err.message); }
    );
}
```
