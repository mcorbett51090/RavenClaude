---
name: completion-contract
description: "Use whenever a bot finishes, fails, or blocks on a deliverable: end with one RESULT block, the PARENT bot SendToAgents it to CoS (priority when Matthew/blocked/failed), and writes /workspace/state/ready/<id>.json."
---
# Completion contract (replaces result-block; Matthew-approved 2026-10-13 8:02 ET)
Source pattern: RavenClaude `ravenclaude-core/skills/structured-output`, `best-practices/structured-output-protocol-for-all-agent-handoffs.md`; scored by `evals/rubric.md` §1 (@52fcb08).

## 1. RESULT block: every deliverable ends with exactly one
```
---RESULT_START---
{"id":"<bot-short>-<topic>-<YYYYMMDD-HHMM>",
 "status":"DONE|FAILED|BLOCKED|NEEDS_DECISION",
 "needs_matthew":"Y|N",
 "decision_asks":[{"ask":"...","options":["RECOMMENDED first","..."],"confidence":"1-5"}],
 "summary":"≤3 sentences",
 "deliverables":["/workspace/... file paths, PR #, URLs"],
 "handoff_recommendation":"next owner bot (name+id) or none",
 "confidence":0.0,
 "risks_or_open_questions":[],
 "next_actions":[]}
---RESULT_END---
```
- Required: status, needs_matthew, decision_asks (may be []), file paths in deliverables. All keys are present, and the block parses as JSON (`python3 -m json.tool`).
- The whole return is ≤~2k tokens. Large outputs go to files, never raw dumps. No secrets: give RavenPower vault item names only.
- In decision_asks the recommended option comes FIRST. Matthew decisions are never defaulted.

## 2. Who reports: the PARENT, never the executor
- The bot that owns the task (the parent) sends the RESULT block to CoS **7e392c00-01db-4d8b-84c4-46ba11298263** with **SendToAgent**. An executor or subagent returns its block to its parent only.
- Use **priority=true** when needs_matthew=Y OR status ∈ {BLOCKED, FAILED}. Otherwise send it as an FYI (priority=false).
- **A file on disk alone never counts as reporting.** Until SendToAgent succeeds, the task is not reported.
- This applies when work came bot-to-bot too: CoS still gets the results, decisions and failures only (no status chatter).

## 3. Ready file
Write `/workspace/state/ready/<id>.json` (the directory exists):
`{"id":..., "status":..., "needs_matthew":"Y|N", "notified_cos":true|false, "deliverables":[...], "ts":"<ISO with offset>"}`.
Set notified_cos=true only after SendToAgent succeeded. The PR ready files `<repo>-<pr>.json` for Sage keep their existing schema and add the two fields.

## 4. Plans with Matthew decisions
Any plan that contains Matthew decisions also writes `ASK-<plan-name>.md` next to the plan. It holds one section per decision: the question in plain words, the options with the recommended one first, the 1–5 confidence, and what is blocked until he answers.

## 5. Thread hygiene (item 15)
For long threads, also use the thread-hygiene skill (persist state to a file, fresh thread per task).
