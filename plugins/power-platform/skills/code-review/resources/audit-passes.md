# Audit Passes — Detailed Checklists

Each pass has specific grep patterns and manual checks. Run them systematically.

---

## Pass 1: WIRING — Is everything connected end-to-end?

The #1 cause of "it looks done but doesn't work" bugs. Every function needs a caller,
every event needs a handler, every UI element needs behavior behind it.

### Automated Checks

```
# Find all exported functions/constants across the project
grep -r "export (async )?function \w+" --include="*.ts" --include="*.tsx"
grep -r "export const \w+" --include="*.ts" --include="*.tsx"

# For each export, verify it's imported somewhere
# If an export has zero imports outside its own file → FINDING
```

### Manual Checks

- [ ] **Service → Store:** Every service function (API call) is called from a store action or component
- [ ] **Store → UI:** Every store action is triggered by a UI event (button click, form submit, lifecycle)
- [ ] **UI → Handler:** Every button/link/form has an onClick/onSubmit/onChange handler
- [ ] **Event → Effect:** Every event handler actually does something (not empty or just logging)
- [ ] **Async → Await:** Every async function's promise is awaited or handled (no fire-and-forget without reason)
- [ ] **Callback → Registration:** Every callback/handler function is registered with its event source
- [ ] **Route → Page:** Every route in the router maps to an actual page component
- [ ] **Type → Usage:** Every interface/type defined is used somewhere (not just declared)

### What to grep for

```bash
# Functions defined but potentially unused
# Pattern: export function X — then check if X appears in any import statement
grep "export function (\w+)" src/ -r -o  # get all exported function names
# Then for each: grep "import.*{.*$name" src/ -r  # check for imports

# Store actions defined but unused
grep "^\s+\w+:" src/stores/ -r  # action names in store
# Then check each is called via useStore(s => s.actionName) or store.actionName

# Event handlers that do nothing
grep "onClick=\{[^}]*\}" src/ -r  # find onClick handlers
# Check the handler function body isn't empty
```

---

## Pass 2: ERROR HANDLING — Can failures be seen and debugged?

Silent failures are worse than crashes. At least a crash tells you something broke.

### Automated Checks

```bash
# Empty catch blocks (the worst offender)
# Pattern: catch { } or catch (e) { } with nothing inside
grep -A2 "catch" src/ -r --include="*.ts" --include="*.tsx"

# Catch blocks that only return null/undefined/empty
grep -A3 "catch" src/ -r --include="*.ts" --include="*.tsx"
# Look for: catch { return null } or catch { return [] }

# Promises without .catch() or try/catch
grep "\.then(" src/ -r --include="*.ts" --include="*.tsx"
# Check if there's a .catch() following
```

### Manual Checks

- [ ] **API calls:** Every fetch/axios call has error handling that surfaces to the user
- [ ] **Form submissions:** Validation errors are shown, not just logged
- [ ] **File operations:** Missing file / permission errors are handled
- [ ] **Parse operations:** JSON.parse, parseInt, etc. have fallbacks
- [ ] **User feedback:** Errors produce visible feedback (toast, alert, error state), not just console.log
- [ ] **Error boundaries:** React apps have ErrorBoundary components around major sections
- [ ] **Loading states:** Async operations show loading indicators
- [ ] **Retry logic:** Transient failures (network, 429s) have retry or clear messaging

### Severity guide

| Pattern | Severity |
|---|---|
| Empty catch block | CRITICAL |
| Catch returns null with no logging | CRITICAL |
| Catch logs but no user feedback | WARNING |
| Missing error boundary | WARNING |
| No loading state for async op | WARNING |
| Console.error without user feedback | INFO |

---

## Pass 3: COMPLETENESS — Are features fully implemented?

Half-built features are tech debt that confuses users and future developers.

### Automated Checks

```bash
# TODO/FIXME/HACK/XXX comments
grep -rn "TODO\|FIXME\|HACK\|XXX\|TEMP\|PLACEHOLDER" src/

# Stub functions (empty or just throwing)
grep -A5 "function \w+" src/ -r  # look for single-line bodies like "return" or "throw"

# Commented-out code blocks (not comments about code, but actual code that's commented out)
grep -n "^\s*//\s*(import|const|let|var|function|class|if|for|while|return|export)" src/ -r

# Console.log debugging left in
grep -rn "console\.log" src/ --include="*.ts" --include="*.tsx"
```

### Manual Checks

- [ ] **Every UI element does something:** Buttons click, forms submit, links navigate
- [ ] **Every power-up/feature in the game works:** Test each one actually affects gameplay
- [ ] **Every config option is respected:** Difficulty settings, theme selections, etc.
- [ ] **Data flows round-trip:** Create → Read → Update → Delete all work
- [ ] **Edge cases handled:** Empty states, long text, zero values, null/undefined
- [ ] **Validation exists:** Required fields enforced, types checked, ranges bounded
- [ ] **Feature flags:** Any feature behind a flag/config actually has a code path

### Red flags

- Function body is `{ return; }` or `{ /* TODO */ }`
- Component renders `{null}` or `{undefined}` conditionally without a fallback
- Switch statement with `default: break;` that silently drops cases
- Interface with 10+ fields where only 3 are ever set

---

## Pass 4: DEAD CODE — What can be deleted right now?

Dead code misleads developers, increases bundle size, and complicates refactoring.

### Automated Checks

```bash
# Unused imports (TypeScript compiler catches these, but double-check)
npx tsc --noEmit --noUnusedLocals --noUnusedParameters 2>&1

# Files that are never imported
# List all .ts/.tsx files, then check each is imported or is an entry point
find src/ -name "*.ts" -o -name "*.tsx" | while read f; do
  basename=$(basename "$f" | sed 's/\..*//')
  grep -r "$basename" src/ --include="*.ts" --include="*.tsx" -l | grep -v "$f" | head -1
done

# Unused npm dependencies
npx depcheck 2>&1

# Unreachable code after return/throw/break
grep -B1 -A1 "return\|throw\|break" src/ -r --include="*.ts" --include="*.tsx"
```

### Manual Checks

- [ ] **Exported but never imported:** Function/type/constant defined and exported but zero import sites
- [ ] **Imported but never used:** Import statement exists but the imported name isn't referenced
- [ ] **Old migration/setup scripts:** One-time scripts that already ran and aren't needed anymore
- [ ] **Commented-out code:** Not comments about code, but actual code lines that are commented out
- [ ] **Duplicate type definitions:** Same shape defined in multiple places
- [ ] **Console.log debugging:** Leftover debug logging from development
- [ ] **Test data / seed helpers:** Development-only code shipped to production

---

## Pass 5: BLOAT — What's too big, too complex, or redundant?

Big files hide bugs. Complex functions resist understanding. Redundant logic means
double the maintenance for the same result.

### Thresholds

| Metric | Threshold | Action |
|---|---|---|
| File length | > 300 lines | Consider splitting by responsibility |
| Function length | > 50 lines | Extract helpers or simplify |
| Component length | > 200 lines | Extract sub-components |
| Nesting depth | > 4 levels | Flatten with early returns or extract |
| Parameter count | > 5 params | Use an options object |
| Import count | > 15 imports | File is doing too much |
| Switch cases | > 8 cases | Consider a lookup table/map |
| Ternary chains | > 2 nested | Use if/else or a function |

### Checks

- [ ] **God files:** Files doing 3+ unrelated things (split by responsibility)
- [ ] **Copy-paste logic:** Near-identical code blocks in multiple files (extract shared utility)
- [ ] **Wrapper-only components:** Components that just pass all props through to a child
- [ ] **Over-abstraction:** Helpers/utilities called exactly once (inline them)
- [ ] **Config objects for constants:** Complex config structure for values that never change
- [ ] **Unnecessary state:** State that could be derived from other state (compute instead of store)
- [ ] **Redundant null checks:** Checking for null on values that can't be null

### Pruning decision

Ask for each candidate: "If I delete this, what breaks?"
- If nothing breaks → **safe to delete**
- If tests break → **the code is used, keep it**
- If only other dead code breaks → **delete both**

---

## Pass 6: HARDCODING — What should be configurable but isn't?

Hardcoded values that differ across environments or might need changing are tech debt.

### Checks

```bash
# Hardcoded URLs
grep -rn "https://\|http://" src/ --include="*.ts" --include="*.tsx"

# Hardcoded API keys / secrets (CRITICAL security issue)
grep -rn "api[_-]?key\|secret\|password\|token" src/ -i --include="*.ts" --include="*.tsx"

# Magic numbers (numbers without explanation)
grep -rn "[^0-9][0-9]{3,}[^0-9]" src/ --include="*.ts" --include="*.tsx"
# Check if they're option set values, port numbers, etc. that should be constants

# Hardcoded timeouts/intervals
grep -rn "setTimeout\|setInterval" src/ --include="*.ts" --include="*.tsx"
# Check if the duration is a magic number
```

### Manual Checks

- [ ] **Environment URLs:** API endpoints, org URLs, etc. should come from config/env vars
- [ ] **Option set values:** Numeric codes (689020000, etc.) should be named constants
- [ ] **Feature flags:** Boolean toggles should be config, not code
- [ ] **Timeouts/durations:** Game speeds, animation durations, polling intervals should be constants
- [ ] **Display strings:** User-facing text should be in a central location or i18n system

---

## Pass 7: SECURITY — Any obvious vulnerabilities?

Not a full pentest — just the low-hanging fruit that causes real breaches.

### Checks

```bash
# eval() usage
grep -rn "eval(" src/ --include="*.ts" --include="*.tsx"

# innerHTML/dangerouslySetInnerHTML
grep -rn "innerHTML\|dangerouslySetInnerHTML" src/ --include="*.ts" --include="*.tsx"

# SQL/OData injection (string interpolation in queries)
grep -rn "filter=.*\$\{" src/ --include="*.ts" --include="*.tsx"
grep -rn "filter=.*'\s*\+" src/ --include="*.ts" --include="*.tsx"

# Secrets in code
grep -rn "Bearer \|Authorization:" src/ --include="*.ts" --include="*.tsx"
```

### Manual Checks

- [ ] **Input sanitization:** User input is sanitized before display or query
- [ ] **Authentication checks:** Protected operations verify the user is authenticated
- [ ] **Authorization checks:** Users can only access their own data
- [ ] **CORS configuration:** API allows only expected origins
- [ ] **Sensitive data exposure:** Passwords, tokens, keys not logged or displayed
- [ ] **Dependency vulnerabilities:** `npm audit` shows no critical/high vulnerabilities
