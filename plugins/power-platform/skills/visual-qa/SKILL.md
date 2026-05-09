---
name: visual-qa
description: >
  AI-powered visual QA testing that walks through an app in the browser, records every action
  with annotated captions (what was done, what should happen), captures screenshots/GIFs, and
  sends the evidence to Gemini for automated review. Catches UX misalignments, broken flows,
  missing states, and edge cases that traditional tests miss. Can use Agent Teams for parallel
  test coverage. Triggers on: "visual test", "visual qa", "test the app", "qa review",
  "check the ui", "record a test", "walk through the app", "e2e test", "end to end test",
  "catch edge cases", "gemini review", "screen test", "ux test", "visual regression".
license: MIT
compatibility: "Claude Code with Claude in Chrome MCP, Gemini API for review"
metadata:
  author: custom
  version: "1.0.0"
  platform: "Any web application"
  requires: "Claude in Chrome extension, Gemini API key"
---

# Visual QA — AI-Powered Visual Testing Skill

You perform visual quality assurance by walking through a web app in the browser,
recording every action with structured captions, and sending the evidence to Gemini
for automated review. You catch what traditional unit/integration tests miss:
misaligned layouts, confusing UX, broken visual states, and edge cases.

## CRITICAL RULES

1. **Take a screenshot BEFORE and AFTER every action.** This creates the visual evidence chain.
2. **Log every action with the structured caption format.** Every click, type, scroll, and
   wait must have an ACTION, INTENT, and EXPECT block. Read `resources/caption-format.md`.
3. **Never skip the edge case checklist.** After the happy path, run through edge cases.
   Read `resources/edge-cases.md`.
4. **The GIF recording must be started BEFORE the first action** and stopped AFTER the last.
5. **Gemini reviews the FULL evidence** — screenshots + captions + GIF. Not just one piece.

## How It Works

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────────┐
│ 1. Plan the │───▶│ 2. Walk the  │───▶│ 3. Collect   │───▶│ 4. Send to   │
│    test run  │    │    app       │    │    evidence  │    │    Gemini     │
└─────────────┘    └──────────────┘    └─────────────┘    └──────────────┘
  What to test       Click, type,       Screenshots,        AI reviews
  and expect         scroll, wait       GIF, captions       actual vs expected
```

## Workflow

### Phase 1 — Plan the Test Run

Before touching the browser, define the test plan:

1. **What app?** Get the URL from the user
2. **What flows?** List the user journeys to test (e.g., "create a record, edit it, delete it")
3. **What to check?** Define expected visual states for each step

Write the test plan as a caption script. Read `resources/caption-format.md` for the format.

### Phase 2 — Execute the Test Run

Use Claude in Chrome tools to walk through the app:

```
1. Navigate to the app URL (mcp__claude-in-chrome__navigate)
2. Start GIF recording (mcp__claude-in-chrome__gif_creator: start_recording)
3. Take initial screenshot (mcp__claude-in-chrome__computer: screenshot)
4. For each test step:
   a. Log the caption (ACTION, INTENT, EXPECT)
   b. Take a "before" screenshot
   c. Perform the action (click, type, scroll)
   d. Wait for the page to settle
   e. Take an "after" screenshot
   f. Note any discrepancies from expected behavior
5. Stop GIF recording (mcp__claude-in-chrome__gif_creator: stop_recording)
6. Export GIF (mcp__claude-in-chrome__gif_creator: export)
```

### Phase 3 — Edge Case Testing

After the happy path, run through the edge case checklist in `resources/edge-cases.md`.
For each applicable edge case:
- Attempt the action
- Screenshot the result
- Log whether it passed or failed

### Phase 4 — Compile Evidence

Gather all evidence into a structured report:
- The caption script (expected behavior)
- Screenshots at each step (actual behavior)
- The GIF recording (full flow)
- Edge case results

### Phase 5 — Gemini Review (Optional)

If the user has a Gemini API key, send the evidence for AI review.
Read `resources/gemini-review.md` for the integration approach.

Gemini analyzes:
- Visual alignment (are elements properly positioned?)
- Content accuracy (do labels/values match expectations?)
- State consistency (do UI states match the action taken?)
- Accessibility issues (contrast, text size, touch targets)
- Missing feedback (loading states, error messages, confirmations)

### Phase 6 — Report

Present findings in this format:

```
## Visual QA Report — [App Name]
Date: [date]
Flows Tested: [count]
Edge Cases Checked: [count]

### Results Summary
PASS: [count]    FAIL: [count]    PARTIAL: [count]

### Findings

FINDING #1 [SEVERITY: Critical]
STEP: [which step in the flow]
EXPECTED: [what should have happened]
ACTUAL: [what actually happened]
SCREENSHOT: [reference to screenshot]
RECOMMENDATION: [how to fix]
```

## Agent Team Mode (Optional)

For large apps, spawn a team for parallel test coverage:

| Role | Agent Name | Tests |
|---|---|---|
| Happy Path Tester | `happy-path` | Core user flows, CRUD operations |
| Edge Case Hunter | `edge-hunter` | Empty states, long text, permissions, error handling |
| Visual Inspector | `visual-inspector` | Layout, alignment, responsive, accessibility |

Each agent walks the app independently and produces their own findings.
The Lead merges results into a single report.

Read `resources/team-testing.md` for agent team test orchestration.

## Without Claude in Chrome

If the Chrome extension isn't available, the skill can still generate:
- A structured test plan with the caption format
- An edge case checklist customized to the app
- A manual testing script the user can follow

The user would then record their own screen and send the video + captions to Gemini.
