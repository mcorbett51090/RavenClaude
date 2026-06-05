# Build a golden-prompt regression set before declaring a declarative agent done

**Status:** Absolute rule
**Domain:** Declarative agent testing
**Applies to:** `microsoft-365-copilot`

---

## Why this exists

A declarative agent that passes schema validation and RAI review is not a tested agent — it is a structurally-valid one. Schema correctness tells you nothing about behavioral correctness: whether the agent stays in scope, whether the grounding source returns relevant results, whether the instruction budget is sufficient for the intended personas, or whether an off-topic prompt causes it to hallucinate beyond its capabilities. The golden-prompt regression set is the minimal behavioral safety net: a set of representative prompts (happy path, edge case, adversarial) whose expected behavior is asserted after every instruction or capability change.

## How to apply

Minimum viable regression set for a declarative agent (20 prompts):

| Category | Count | What to test |
|---|---|---|
| Happy path | 8 | Core use cases; assert the agent uses the expected grounding source |
| Scope boundary | 4 | Prompts at the edge of scope; assert the agent does not over-answer |
| Out-of-scope | 4 | Prompts clearly outside the agent's purpose; assert graceful decline |
| Adversarial | 4 | Prompt injection attempts ("ignore previous instructions"), PII extraction, jailbreak attempts; assert refusal |

Store the regression set in the Agents Toolkit project under `evals/golden-prompts.json`:

```json
[
  {
    "prompt": "What is the refund policy for orders under 30 days?",
    "expected_behavior": "Answers from the returns-policy connector; cites the source",
    "should_use_grounding": true
  },
  {
    "prompt": "What is the weather in Seattle today?",
    "expected_behavior": "Declines; explains the agent is scoped to order support",
    "should_use_grounding": false
  }
]
```

**Do:**
- Run the regression set against every version of the agent manifest before publishing — use the Agents Toolkit Playground for interactive review.
- Add a regression prompt for every incident where the agent produced an unexpected response in production.
- Include at least one prompt that tests the 45-second timeout boundary (a complex multi-source query) to verify it completes within the wall.

**Don't:**
- Declare an agent "working" based on a single happy-path demo — demos selectively avoid failure modes.
- Ship an agent to production before at least one human reviewer has run all adversarial prompts manually.
- Merge instruction changes without re-running the full regression set — instruction changes have non-local effects on the agent's behavior.

## Edge cases / when the rule does NOT apply

A prototype or internal pilot deployed to fewer than 10 named testers with explicit "this is not tested" labeling may ship without a full regression set. Label it clearly; add the set before wider rollout.

## See also

- [`../agents/declarative-agent-engineer.md`](../agents/declarative-agent-engineer.md) — owns manifest authoring and the instruction budget that the regression set validates
- [`./da-pass-rai-validation-design-the-prompt-for-it.md`](./da-pass-rai-validation-design-the-prompt-for-it.md) — the structural gate this regression set complements

## Provenance

Codifies CLAUDE.md house opinion #15 ("no DA without a golden-prompt regression set") and the `copilot-agent-eval-harness` skill; standard responsible-AI agent evaluation practice.

---

_Last reviewed: 2026-06-05 by `claude`_
