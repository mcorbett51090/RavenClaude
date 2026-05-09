# Edge Case Checklist

After the happy path passes, systematically test these edge cases.
Not every case applies to every app — skip items marked N/A but document why.

## Input Edge Cases

### Text Fields
- [ ] **Empty submission** — Submit the form with required fields blank. Expect validation errors.
- [ ] **Maximum length** — Paste text at the field's MaxLength limit. Does it truncate or error?
- [ ] **One character over max** — Paste MaxLength + 1 characters. Does it prevent or silently truncate?
- [ ] **Special characters** — Enter `<script>alert('xss')</script>` in a text field. Should be escaped.
- [ ] **Unicode/emoji** — Enter text with emojis, CJK characters, RTL text. Does it display correctly?
- [ ] **Leading/trailing spaces** — Enter "  Name  " with spaces. Does the app trim them?
- [ ] **Only spaces** — Enter just spaces in a required field. Should it fail validation.
- [ ] **HTML in text** — Enter `<b>bold</b>` — should render as literal text, not HTML.
- [ ] **Very long single word** — Enter a 200-character word with no spaces. Does the layout break?

### Number Fields
- [ ] **Zero** — Enter 0 in a number field. Is it treated as empty or as a valid value?
- [ ] **Negative numbers** — Enter -1. Is it allowed? Should it be?
- [ ] **Decimal in integer field** — Enter 3.5 in an integer field. Does it round, truncate, or error?
- [ ] **Very large number** — Enter 999,999,999,999. Does it exceed MaxValue?
- [ ] **Non-numeric input** — Type "abc" in a number field. Should be prevented or show error.

### Date Fields
- [ ] **Past date** — Enter a date from 1900. Is it valid?
- [ ] **Far future date** — Enter a date in 2099. Is it valid?
- [ ] **February 29** — Enter Feb 29 on a leap year and a non-leap year.
- [ ] **Date format** — Does the date picker respect the user's locale format?

### Lookup Fields
- [ ] **Search with no results** — Search for "zzzznonexistent" in a lookup. Expect "No records found."
- [ ] **Cleared lookup** — Clear a required lookup field. Expect validation error on save.
- [ ] **Deactivated referenced record** — What happens when the looked-up record is inactive?

### Choice Fields
- [ ] **No selection** — Leave a required choice field unset. Expect validation error.
- [ ] **Rapid selection changes** — Quickly toggle between options. Does the last selection stick?

## State Edge Cases

### Empty States
- [ ] **Empty view** — Navigate to a view with 0 records. Is there a friendly empty message?
- [ ] **Empty subgrid** — View a form where the related records subgrid has 0 items.
- [ ] **Empty dashboard** — View a dashboard with no data. Do charts show "No data" gracefully?
- [ ] **New form with defaults** — Open a new record form. Are default values populated?

### Loading States
- [ ] **Slow network simulation** — Is there a loading indicator when data takes time?
- [ ] **Double-click prevention** — Click "Save" twice rapidly. Does it prevent duplicate records?
- [ ] **Navigation during save** — Click away while a save is in progress. What happens?

### Error States
- [ ] **Network error** — Disconnect network and try to save. Is there a meaningful error message?
- [ ] **Concurrent edit** — Open the same record in two tabs, edit in both, save both. Conflict handling?
- [ ] **Deleted record** — Open a record, delete it in another tab, try to save in the first tab.
- [ ] **Permission denied** — Access a record/view you don't have permission for. Friendly error?

## Layout Edge Cases

### Responsive / Window Size
- [ ] **Narrow window** — Resize browser to 800px wide. Does the form/view adapt?
- [ ] **Very wide window** — Maximize on a 4K monitor. Do fields stretch absurdly?
- [ ] **Zoom 150%** — Browser zoom to 150%. Does layout break?
- [ ] **Zoom 75%** — Browser zoom to 75%. Is text still readable?

### Visual Alignment
- [ ] **Field label alignment** — Are all labels left-aligned consistently?
- [ ] **Button alignment** — Are command bar buttons evenly spaced?
- [ ] **Column alignment in views** — Do view columns align with headers?
- [ ] **Tab overflow** — If there are many tabs, do they wrap or provide a "more" dropdown?
- [ ] **Long field values** — Does a very long text value overflow its container or truncate with ellipsis?

### Scroll Behavior
- [ ] **Long form scroll** — Scroll to bottom of a form with many fields. Does it scroll smoothly?
- [ ] **Sticky header** — Does the command bar stay visible when scrolling down?
- [ ] **Subgrid scroll** — Does a subgrid with many records have its own scrollbar?

## Navigation Edge Cases

- [ ] **Browser back button** — Click back after saving. Where does it go? Is data lost?
- [ ] **Refresh during edit** — Press F5 with unsaved changes. Is there a "discard changes" prompt?
- [ ] **Direct URL access** — Paste a record URL directly. Does it load correctly?
- [ ] **Deep link to tab** — If the app supports tab deep links, do they work?
- [ ] **Breadcrumb navigation** — Does the breadcrumb trail reflect the actual navigation path?

## Performance Edge Cases

- [ ] **Large dataset view** — Open a view with 10,000+ records. Does it paginate? How fast?
- [ ] **Many subgrid records** — Open a form where the subgrid has 500+ related records.
- [ ] **Complex form load** — A form with 10+ tabs and 50+ fields. Load time?
- [ ] **Rapid navigation** — Click through 10 records in quick succession. Any lag or crashes?

## Accessibility Edge Cases

- [ ] **Keyboard navigation** — Can you Tab through all form fields without a mouse?
- [ ] **Focus indicators** — Is the currently focused field visually obvious?
- [ ] **Screen reader labels** — Do form fields have accessible labels (check with read_page)?
- [ ] **Color contrast** — Is text readable on all backgrounds? (Check status badges, alerts)
- [ ] **Error announcement** — When validation fails, is the error communicated clearly?

## Security Edge Cases

- [ ] **URL parameter tampering** — Modify record GUIDs in the URL. Does it show "not found" or error?
- [ ] **JavaScript console access** — Can sensitive data be read from the console?
- [ ] **Form field inspection** — Are hidden fields actually hidden (not just visually hidden via CSS)?

## Documenting Edge Case Results

For each tested edge case, log:

```
EDGE_CASE: [checklist item name]
STATUS: PASS | FAIL | PARTIAL | N/A
EXPECTED: [what should happen]
ACTUAL: [what actually happened]
SCREENSHOT: [reference if captured]
SEVERITY: Critical | High | Medium | Low
NOTE: [any additional context]
```
