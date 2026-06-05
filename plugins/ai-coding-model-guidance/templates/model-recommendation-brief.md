> **Use for:** a structured, shareable model-recommendation brief a developer or team lead can attach to a ticket, ADR, or Slack thread. Fill in each `[placeholder]` based on the strategist agent's output. All capability claims must include a retrieval date or a `[verify-at-use]` marker before sharing.

---

# Model Recommendation Brief

**Prepared by:** [agent name — e.g. codex-model-strategist]
**Date:** [YYYY-MM-DD]
**Task reference:** [ticket / PR / description]

---

## Task summary

| Attribute | Value |
|---|---|
| Use-case type | [inline completion / supervised chat / autonomous run] |
| IDE / surface | [VS Code / JetBrains / terminal / GitHub.com / other] |
| Estimated context demand | [Low / Medium / High / Very High] |
| Blast radius | [Low / Medium / High] |
| Org / team context | [individual / small team / enterprise org with policy] |

---

## Recommended model tier

**Primary recommendation:** [ecosystem] — [Fast inline / Balanced default / Raised reasoning / Frontier]

**Reason:** [1-3 sentences grounded in the task attributes above — not just "it's the best model"]

**Fallback:** [ecosystem / tier — if primary is unavailable or if condition X applies]

---

## Availability verification

> All entries below are volatile and must be re-verified before using in a production workflow.

| Claim | Value | Source | Retrieval date | Verify-at-use? |
|---|---|---|---|---|
| Recommended model id | [model id or "see lineup"] | [primary source URL] | [YYYY-MM-DD] | Yes |
| Plan / surface gate | [plan name + surface] | [Copilot / Codex / Grok docs] | [YYYY-MM-DD] | Yes |
| Context window | [size or "not quoted — verify"] | [primary source URL] | [YYYY-MM-DD] | Yes |

---

## Model rules / org policy check

- Org policy reviewed: [yes / no / not applicable]
- Model rules block: [none found / [model] blocked — see finding]
- Escalation to security-reviewer: [yes / no]

---

## Reasoning-level setting (Codex only)

- Reasoning dial available: [yes / no]
- Recommended level: [low / medium / high / max — or "not applicable"]
- Tried lower level first: [yes / no / not applicable]

---

## Open questions

- [ ] [Any unresolved question about availability, org policy, or task scope]
- [ ] [Any verify-at-use item that must be confirmed before the run]

---

## Alternatives considered

| Option | Ruled out because |
|---|---|
| [ecosystem / tier] | [specific reason] |
| [ecosystem / tier] | [specific reason] |
