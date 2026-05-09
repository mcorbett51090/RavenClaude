# Caption Format Specification

Every test action must be documented with a structured caption. This creates the
"expected behavior" track that Gemini compares against the actual recording.

## Caption Structure

Each caption has a timestamp, event ID, and structured fields:

```
TIMESTAMP: [MM:SS]
EVENT: [unique_event_id]
ACTION: [What the tester did — click, type, scroll, navigate, wait]
INTENT: [Why the action was taken — the business purpose]
EXPECT_VISUAL: [What should appear on screen after this action]
EXPECT_STATE: [What UI state change should occur]
EXPECT_FEEDBACK: [What feedback the user should receive — toast, animation, sound]
EXPECT_DATA: [What data should appear or change — field values, list items]
```

## Field Definitions

### ACTION (Required)
The literal action taken. Be specific about targets:
- "Click the 'Save' button in the top-right command bar"
- "Type 'Contoso Project Alpha' into the 'Project Name' field"
- "Scroll down to the 'Team' tab"
- "Wait 2 seconds for page load"

### INTENT (Required)
The business reason for the action:
- "Create a new project record"
- "Verify the lookup resolves to the correct account"
- "Check that the subgrid loads related employees"

### EXPECT_VISUAL (Required)
What the screen should look like AFTER the action:
- "The form saves and the command bar shows 'Deactivate' instead of 'Save'"
- "A green success toast appears at the top of the screen"
- "The 'Budget' field displays '$50,000.00' with currency formatting"
- "The subgrid shows 3 employee records in a table"

### EXPECT_STATE (Optional)
UI state changes:
- "Form transitions from 'New' to 'Saved' mode"
- "The 'Required' asterisk disappears from 'Project Name'"
- "The record status changes from 'Active' to 'Inactive'"
- "The 'Delete' button becomes enabled"

### EXPECT_FEEDBACK (Optional)
User feedback mechanisms:
- "A confirmation dialog appears asking 'Are you sure?'"
- "A loading spinner appears for 1-3 seconds"
- "A validation error appears under the 'Email' field: 'Invalid email format'"
- "A notification banner says 'Record saved successfully'"

### EXPECT_DATA (Optional)
Data-level assertions:
- "The 'Created On' field populates with today's date"
- "The 'Owner' field shows the current user's name"
- "The view refreshes and shows the new record at the top"
- "The calculated 'Total' field shows the sum of line items"

## Example: Complete Test Script

```
TIMESTAMP: 00:00
EVENT: NAVIGATE_TO_APP
ACTION: Navigate to https://org.crm.dynamics.com/main.aspx?appid={guid}
INTENT: Open the HR Manager app
EXPECT_VISUAL: The app loads with the sitemap showing 'Human Resources' area
EXPECT_STATE: Default view 'Active Projects' is displayed
EXPECT_DATA: The view shows existing project records (if any)

TIMESTAMP: 00:05
EVENT: CLICK_NEW
ACTION: Click the '+New' button in the command bar
INTENT: Start creating a new project record
EXPECT_VISUAL: A blank 'Project Main Form' opens
EXPECT_STATE: Form is in 'New Record' mode, 'Save' button is enabled
EXPECT_FEEDBACK: No loading delay — form should appear within 1 second

TIMESTAMP: 00:08
EVENT: FILL_NAME
ACTION: Type 'Alpha Initiative' into the 'Project Name' field
INTENT: Set the primary name for the project
EXPECT_VISUAL: Text appears in the field as typed
EXPECT_STATE: The form title updates to show 'Alpha Initiative' (or remains 'New Project')

TIMESTAMP: 00:12
EVENT: SET_PRIORITY
ACTION: Click the 'Priority' dropdown and select 'High'
INTENT: Set the project priority
EXPECT_VISUAL: Dropdown opens showing Low/Medium/High/Critical, 'High' is highlighted after click
EXPECT_STATE: Field shows 'High' after selection, dropdown closes

TIMESTAMP: 00:16
EVENT: SAVE_RECORD
ACTION: Click the 'Save' button in the command bar (or press Ctrl+S)
INTENT: Persist the new project record to Dataverse
EXPECT_VISUAL: The command bar changes (Save becomes grayed, Deactivate appears)
EXPECT_STATE: Form transitions from 'New' to 'Saved' mode
EXPECT_FEEDBACK: Success notification or no error messages
EXPECT_DATA: 'Created On' and 'Owner' fields auto-populate
```

## Rules

1. **One caption per action.** Don't bundle multiple actions into one caption.
2. **EXPECT_VISUAL is always required.** Every action should have a visible result.
3. **Be specific about locations.** "Top-right" not "somewhere on the page."
4. **Include negative expectations.** "No error message should appear" is valid.
5. **Timestamps are relative** to the start of recording, not wall clock time.
6. **Event IDs must be unique** within a test run and descriptive (SAVE_RECORD not STEP_4).
