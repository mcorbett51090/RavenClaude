# Severity Guide

Every finding must be categorized into one of four severity levels.
Use these definitions — don't inflate or deflate severity.

---

## CRITICAL — Must Fix

The code is **broken in production** or **will break** under normal use.

Examples:
- Function defined but never called (feature doesn't work)
- API call with no error handling (app crashes on network error)
- Data never persisted (user thinks it saved but it didn't)
- Security vulnerability (injection, exposed secrets)
- Infinite loop or memory leak under normal conditions
- Race condition that corrupts data

**Rule of thumb:** Would a user file a bug report about this?

---

## WARNING — Should Fix

The code **works** but has significant quality issues that will cause problems.

Examples:
- Empty catch block (errors invisible during debugging)
- Missing loading/error states (confusing UX)
- Hardcoded values that should be configurable
- Console.log debugging left in production
- Missing input validation on user-facing forms
- Overly complex logic that's hard to maintain

**Rule of thumb:** Would a code reviewer block a PR for this?

---

## PRUNE — Consider Removing

The code is **unnecessary** — removing it makes the codebase better.

Examples:
- Exported function with zero import sites
- Commented-out code blocks
- Unused npm dependencies
- Type/interface defined but never referenced
- Wrapper function that just calls another function
- Config object for values that never change
- Duplicate logic that should be unified
- File over 300 lines that should be split

**Rule of thumb:** "If I delete this line/file, does anything break?"
If no → PRUNE it.

---

## INFO — Minor Observations

Observations that don't require action but are worth noting.

Examples:
- Inconsistent naming conventions (not causing bugs)
- Missing JSDoc on public API functions
- Test coverage gaps (if tests exist)
- Opportunity to use a newer API/pattern
- Performance optimization opportunity (not a current bottleneck)

**Rule of thumb:** "Nice to know, but I wouldn't stop my work to fix this."

---

## Severity Escalation

Some patterns automatically escalate severity:

| Pattern | Base Severity | Escalates To | When |
|---|---|---|---|
| Unused function | PRUNE | CRITICAL | If the function is the **only** implementation of a user-visible feature |
| Empty catch | WARNING | CRITICAL | If the catch is around a data persistence operation |
| Hardcoded value | WARNING | CRITICAL | If it's a secret, API key, or password |
| Console.log | WARNING | PRUNE | If it's debug noise with no diagnostic value |
| Dead import | PRUNE | INFO | If it's a type-only import (no bundle impact) |
