# Structured Output Skill (New)

**Purpose**: Enforce the Structured Output Protocol across all agents and tasks for reliable, parseable, high-quality deliverables and handoffs.

## When to Use
- For any handoff note to the Team Lead.
- For summaries, plans, reviews, research findings, code proposals, or any structured deliverable.
- At the conclusion of focused tasks.
- Whenever the Team Lead or a specialist needs machine-readable + human-readable output.

## How to Apply (Core Pattern)
1. **Define success criteria** and output shape upfront in the prompt/task.
2. **Instruct the model** to think step-by-step first (reasoning visible to humans).
3. **Then emit** the structured payload using the exact delimiter format:

```
---RESULT_START---
{
  "status": "complete" | "partial" | "blocked",
  "summary": "Concise one-sentence outcome",
  "deliverables": ["list", "of", "key", "items"],
  "structured_data": { ... any JSON schema ... },
  "handoff_recommendation": {
    "to_specialist": "Architect | Coder | Reviewer | ...",
    "reason": "Why this specialist next",
    "context_summary": "Brief relevant context for handoff"
  },
  "confidence": 0.0-1.0,
  "risks_or_open_questions": [...],
  "next_actions": [...]
}
---RESULT_END---
```

4. For non-JSON narrative work (e.g., full design spec), still include a final delimited structured summary block as above.

## Example Invocation (for Team Lead or skills)
"Delegate this as a Focused Task to the Coder. Use the Structured Output Skill. Require the Coder to return reasoning + the exact ---RESULT_START--- block with status, summary, code_changes summary, and handoff if needed."

## Benefits
- Dramatically reduces parsing errors and miscommunication in multi-agent flows.
- Enables reliable downstream processing (e.g., auto-extract for PR descriptions, checks, or further orchestration).
- Produces consistently "ideal" outputs that are both human-friendly and automation-ready.
- Complements the existing Researcher and Grounding Protocol.

## Integration Notes
- Reference this skill in the main CLAUDE.md and in individual agent definitions.
- Combine with Focused Task Execution and Run Artifacts standards.
- The Researcher should also return findings in this structured format.