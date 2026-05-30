---
name: copilot-agent-eval-harness
description: "Build the golden-prompt regression set + pre-publish evaluation gate for a Microsoft 365 Copilot agent — author representative + adversarial prompts, check grounding accuracy and citation correctness, stress the declarative-agent hard limits (50/25/4096/45s, no-loop), and gate publish on the results. Use before declaring any declarative or custom-engine agent done, and on every manifest/grounding change."
---

# Copilot agent eval harness

Cross-agent playbook (used by `declarative-agent-engineer`, `api-plugin-engineer`, `graph-connector-engineer`, `agents-sdk-engineer`). House rule: **no agent ships without a golden-prompt regression set** — schema-valid ≠ behaviorally correct.

## 1. Author the golden-prompt set
- **Representative** prompts covering each in-scope task + each grounding source.
- **Boundary** prompts (just inside / just outside scope).
- **Adversarial** prompts: prompt-injection over ingested content (→ flag to `ravenclaude-core/security-reviewer`), out-of-scope coercion, requests that should be refused, ACL-bypass attempts (a low-privilege identity probing for content it shouldn't see).

## 2. Score each run
| Dimension | Check |
|---|---|
| Grounding accuracy | did it use the right source + return correct facts? |
| Citation correctness | are citations present, correct, and clickable (labels working)? |
| Refusal | did it decline what it should? |
| ACL trimming | does a low-privilege test identity get correctly trimmed results? |
| Tone/scope | on-brand, in-scope? |

## 3. Stress the hard limits (declarative agents)
Prompts that push toward 50 grounding items / 25 response items / ~4,096 tokens / 45 s — confirm graceful behavior at the ceiling, and that nothing needs a **loop** (a loop = wrong platform → `agents-sdk-engineer`).

## 4. Gate publish
Run the set on every manifest/grounding/auth change. A regression = no publish. Pair with manifest schema + **RAI** validation. Keep the set in source control next to the agent project.

## Anti-patterns
- "It worked once" instead of a versioned set; no adversarial/ACL prompts; no citation check; gating only on schema validity; not re-running on grounding changes.
