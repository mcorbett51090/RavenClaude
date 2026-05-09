# Agent Team Testing Mode

For large apps, spawn a team of testing agents that cover different aspects in parallel.

## Team Composition

| Role | Agent Name | Focus Area |
|---|---|---|
| Happy Path Tester | `happy-path` | Core user flows — CRUD, navigation, key business processes |
| Edge Case Hunter | `edge-hunter` | Empty states, bad input, boundary conditions, error handling |
| Visual Inspector | `visual-inspector` | Layout, alignment, responsive behavior, accessibility |

## Spawn Prompts

### Happy Path Tester

```
You are the Happy Path Tester. Your job is to walk through the core user flows
of the application and verify that the primary use cases work correctly.

Load the visual-qa skill and use the caption format from resources/caption-format.md.

Your test plan:
1. Navigate to the app
2. Create a new record (fill all fields, save)
3. Find the record in the default view
4. Open and edit the record (change 2-3 fields, save)
5. Test navigation (all sitemap items, all form tabs)
6. Test subgrids (view related records, add a related record)
7. Test views (switch between views, use Quick Find search)
8. Deactivate/reactivate the record
9. Delete the record (if applicable)

For each step: screenshot before, perform action, screenshot after, log caption.

At the end, compile your findings and broadcast them to the team.
Specifically flag any step where the actual behavior didn't match expectations.
```

### Edge Case Hunter

```
You are the Edge Case Hunter. Your job is to break the application by testing
boundary conditions, error states, and unusual inputs.

Load the visual-qa skill and use the edge case checklist from resources/edge-cases.md.

Go through the FULL checklist. For each applicable item:
1. Navigate to the relevant screen
2. Attempt the edge case action
3. Screenshot the result
4. Log whether it PASSED (handled gracefully) or FAILED (broke, confusing, or missing feedback)

Priority order:
1. Input edge cases (empty, max length, special chars)
2. State edge cases (empty states, loading, errors)
3. Security edge cases (URL tampering, permissions)
4. Navigation edge cases (back button, refresh, deep links)

At the end, compile your findings and broadcast them to the team.
Focus on FAIL and PARTIAL results — those are the actionable findings.
```

### Visual Inspector

```
You are the Visual Inspector. Your job is to examine the visual quality of every
screen in the application without performing functional actions.

Load the visual-qa skill for reference.

Your inspection plan:
1. Navigate to each screen/view in the app
2. For each screen, check:
   - Element alignment (fields, labels, buttons aligned in grid)
   - Text overflow (any truncated or overflowing text)
   - Spacing consistency (even margins/padding throughout)
   - Color consistency (matching theme, accessible contrast)
   - Icon quality (no broken images, correct icons)
   - Empty space (is layout efficient or wastefully spaced)
   - Font consistency (same font family/sizes for same-level elements)
3. Resize the browser to 1024px width and re-check each screen
4. Zoom to 150% and re-check the current screen

Use the accessibility tree (read_page with filter: "all") to verify:
- All interactive elements have accessible labels
- Tab order is logical
- Focus indicators are visible

At the end, compile your findings and broadcast them to the team.
Include specific pixel coordinates or element references for each issue.
```

## Lead Coordination

The Lead agent should:

1. **Spawn all three agents** with the app URL and any login context
2. **Monitor progress** — check in every 2-3 minutes
3. **Unblock agents** if they get stuck (e.g., auth issues, navigation confusion)
4. **Merge findings** from all three agents into a single Visual QA Report
5. **Deduplicate** — if multiple agents found the same issue, consolidate
6. **Prioritize** — rank all findings by severity
7. **Optionally send to Gemini** for a final cross-check of the merged report

## Merge Template

```markdown
## Visual QA Report — [App Name]
Date: [date]
Test Duration: [time]
Agents: Happy Path Tester, Edge Case Hunter, Visual Inspector

### Summary
| Category | Tested | Pass | Fail | Partial |
|---|---|---|---|---|
| Happy Path Steps | [n] | [n] | [n] | [n] |
| Edge Cases | [n] | [n] | [n] | [n] |
| Visual Checks | [n] | [n] | [n] | [n] |
| **Total** | **[n]** | **[n]** | **[n]** | **[n]** |

### Critical Findings (Must Fix)
[findings with severity Critical or High]

### Medium Findings (Should Fix)
[findings with severity Medium]

### Low Findings (Nice to Fix)
[findings with severity Low]

### Top 5 Priority Fixes
1. [most impactful fix]
2. ...
```
