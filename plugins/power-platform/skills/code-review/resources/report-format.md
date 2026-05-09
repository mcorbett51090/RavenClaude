# Report Format

The code review produces a structured report. Follow this format exactly.

---

## Report Template

```markdown
# Code Review Report — [Project Name]

**Date:** [YYYY-MM-DD]
**Scope:** [e.g., "src/ directory — React/TypeScript frontend"]
**Files Scanned:** [count]
**Total Findings:** [count] (X critical, Y warning, Z prune, W info)

---

## Summary

[2-3 sentence executive summary. What's the overall health of the codebase?
What's the single biggest risk? What's the single best thing about it?]

### Scorecard

| Category | Score | Notes |
|---|---|---|
| Wiring (end-to-end) | [A-F] | [one line] |
| Error Handling | [A-F] | [one line] |
| Completeness | [A-F] | [one line] |
| Dead Code | [A-F] | [one line] |
| Bloat | [A-F] | [one line] |
| Hardcoding | [A-F] | [one line] |
| Security | [A-F] | [one line] |

**Overall Grade: [A-F]**

---

## CRITICAL — Must Fix

### CR-001: [Short descriptive title]
**File:** `path/to/file.ts:42`
**Pass:** [Which audit pass found this: Wiring/Error Handling/etc.]
**Problem:** [What's wrong. Be specific — include the actual code if short.]
**Impact:** [What breaks because of this. User-visible consequence.]
**Fix:** [Exactly what to do. Include code if helpful.]

### CR-002: ...

---

## WARNING — Should Fix

### WR-001: [Short descriptive title]
**File:** `path/to/file.ts:78`
**Pass:** [Which audit pass]
**Problem:** [What's wrong]
**Impact:** [Why it matters]
**Fix:** [What to do]

### WR-002: ...

---

## PRUNE — Consider Removing

### PR-001: [Short descriptive title]
**File:** `path/to/file.ts:15-30`
**What:** [What can be removed]
**Why:** [Why it's safe to remove — zero references, never called, etc.]
**Lines saved:** [approximate count]

### PR-002: ...

---

## INFO — Minor Observations

- **IN-001:** [One-liner observation] (`file.ts:10`)
- **IN-002:** ...

---

## Pruning Plan

### Safe to Delete

| # | File / Range | Lines | Description |
|---|---|---|---|
| 1 | `src/utils/old.ts` (entire) | 45 | Zero imports anywhere |
| 2 | `src/types/legacy.ts:10-25` | 15 | Dead interface |

### Should Inline

| # | File:Function | Called From | Recommendation |
|---|---|---|---|
| 1 | `src/utils/format.ts:formatDate()` | 1 site | Body is a one-liner, inline it |

### Should Split

| # | File | Lines | Recommendation |
|---|---|---|---|
| 1 | `src/stores/big-store.ts` | 350 | Split persistence logic into own module |

### Dependencies to Remove

| Package | Reason |
|---|---|
| `unused-lib` | Zero imports in src/ |

### Estimated Impact

- **Lines removable:** ~[N]
- **Files removable:** [N]
- **Dependencies removable:** [N]
- **Est. bundle reduction:** ~[N] KB

---

## Action Items (Priority Order)

1. [ ] [Most critical fix first]
2. [ ] [Second most critical]
3. [ ] ...
```

---

## Grading Scale

| Grade | Meaning |
|---|---|
| A | Excellent — no significant issues |
| B | Good — minor issues, nothing critical |
| C | Acceptable — some warnings, no criticals |
| D | Needs Work — has critical issues or many warnings |
| F | Failing — multiple critical issues, broken functionality |

---

## Finding ID Convention

- `CR-NNN` — Critical findings
- `WR-NNN` — Warning findings
- `PR-NNN` — Prune findings
- `IN-NNN` — Info findings

Number sequentially within each category. This makes it easy to reference
specific findings in follow-up conversations: "Fix CR-003 and PR-001."
