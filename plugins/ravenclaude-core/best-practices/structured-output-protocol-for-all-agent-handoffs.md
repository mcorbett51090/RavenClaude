# Use the Structured Output Protocol for every agent-to-agent handoff

**Status:** Absolute rule
**Domain:** Agent design / Multi-agent / Handoff quality
**Applies to:** `ravenclaude-core`

---

## Why this exists

An agent that returns a Markdown narrative and nothing else leaves the Team Lead — and any downstream automation — in the position of parsing prose to extract structured data: status, confidence, what was done, what needs to happen next. Prose is for humans; the Team Lead needs machine-parseable handoffs to route reliably. The `---RESULT_START--- ... ---RESULT_END---` delimited JSON block alongside the Markdown narrative is the dual-output format that provides both: the human-readable reasoning is preserved, and the structured payload is extractable without NLP. Every specialist agent in ravenclaude-core declares this format in its output contract; every domain plugin inherits it.

## How to apply

Agents must end every substantive deliverable with the Structured Output Protocol block:

```markdown
[Human-readable Markdown report here]

---RESULT_START---
{
  "status": "complete",
  "summary": "one-sentence outcome",
  "deliverables": ["file-created.md", "updated-schema.json"],
  "handoff_recommendation": {
    "to_specialist": "tester-qa",
    "reason": "implementation complete; needs test coverage before review"
  },
  "confidence": 0.85,
  "risks_or_open_questions": [
    "auth module assumes env var OAUTH_SECRET is set"
  ],
  "next_actions": [
    {
      "item": "run tester-qa against the new auth module",
      "owner": "Team Lead",
      "date": "2026-06-06",
      "expected_movement": "green test suite"
    }
  ]
}
---RESULT_END---
```

**Status values:**
- `complete` — all success criteria met; handoff recommended.
- `partial` — some criteria met; `risks_or_open_questions` explains what is missing.
- `blocked` — work cannot proceed; `next_actions` lists the recovery path (applies the mandatory CGP phrasing).

**Confidence float guidance:**
- `0.9+` — verified against this-session evidence.
- `0.7–0.9` — based on strong domain knowledge; specific claims may be `[unverified — training knowledge]`.
- `< 0.7` — significant uncertainty; the Team Lead should validate before acting on the result.

**Do:**
- Include the block on every handoff-bearing report; exempt only informational chatter ("file read," "test ran").
- Populate `handoff_recommendation` with the next specialist's exact agent name (from the roster) and a one-sentence reason.
- Set `status: blocked` and populate `next_actions` with the mandatory CGP phrasing when the work genuinely cannot proceed.

**Don't:**
- Emit the JSON block without the preceding Markdown narrative — the dual-output format requires both.
- Use `status: complete` when work is partial; a partially-done `complete` misleads the Team Lead's routing.
- Put sensitive data (secrets, PII, credentials) in the structured block — it travels through agent handoffs.

## Edge cases / when the rule does NOT apply

- Quick informational responses in a multi-turn conversation ("what does this function do?") that do not involve delegation or handoff are exempt from the protocol block.
- The Team Lead's own response to the user (the synthesized final output) may omit the JSON block when the user is the audience — the block is for agent-to-agent routing, not for user consumption.

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — "Structured Output Protocol (Active — required for handoffs)" section.
- [`./focused-task-delegation-beats-full-context-dumps.md`](./focused-task-delegation-beats-full-context-dumps.md) — the task brief that produces the input the SOP block responds to.

## Provenance

Distilled from `plugins/ravenclaude-core/CLAUDE.md` §"Structured Output Protocol (Active — required for handoffs)" and the per-agent output contract sections. All 14 specialist agents in `agents/` declare this format.

---

_Last reviewed: 2026-06-05 by `claude`_
