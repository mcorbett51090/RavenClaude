# ai-coding-model-guidance — best-practice docs

Named, citable rules for the `ai-coding-model-guidance` plugin's model-selection
strategists. Each file is **one rule**, grounded in the plugin's single dated
knowledge bank ([`../knowledge/cross-tool-model-lineup-2026.md`](../knowledge/cross-tool-model-lineup-2026.md)).

**CI gate reminder:** this plugin is under `check-lineup-citations.py`. Do NOT
add specific volatile numbers (prices, context-window sizes, benchmark scores)
without a `(verify-at-use — YYYY-MM)` marker. Rules here cover
**selection methodology** — how to choose, how to evaluate, how to avoid
lock-in — not current specific numbers.

---

## Index

_20 rules._

| Doc | Status | Use when |
|---|---|---|
| [`traverse-the-tree-before-naming-a-sku.md`](./traverse-the-tree-before-naming-a-sku.md) | Absolute rule | Every model recommendation — before naming any SKU |
| [`right-size-not-top-of-range.md`](./right-size-not-top-of-range.md) | Pattern | Developer asks "which model?" without evidence the frontier tier is needed |
| [`scope-availability-surface-plan-date.md`](./scope-availability-surface-plan-date.md) | Absolute rule | Any claim about model availability in Copilot, Codex, or Grok |
| [`volatile-numbers-carry-a-marker.md`](./volatile-numbers-carry-a-marker.md) | Absolute rule | Any price, context-window size, or benchmark score is about to be quoted |
| [`closed-world-verified-lineup-only.md`](./closed-world-verified-lineup-only.md) | Absolute rule | Any model id is about to be named — especially version-pattern ids |
| [`reasoning-level-before-model-upgrade.md`](./reasoning-level-before-model-upgrade.md) | Pattern | Developer says Codex output quality is insufficient on the current model |
| [`flag-retirements-first.md`](./flag-retirements-first.md) | Absolute rule | A developer mentions a model id — check retirements before answering |
| [`seam-to-claude-for-claude-questions.md`](./seam-to-claude-for-claude-questions.md) | Absolute rule | Any question involving Claude models or the Anthropic API |
| [`avoid-vendor-lock-in-through-methodology.md`](./avoid-vendor-lock-in-through-methodology.md) | Pattern | Every recommendation — teach the methodology, not just the current SKU |
| [`org-model-rules-escalate-to-security.md`](./org-model-rules-escalate-to-security.md) | Absolute rule | Developer asks about org model policies, API-key governance, or compliance |
| [`scope-task-before-agent-run.md`](./scope-task-before-agent-run.md) | Absolute rule | Before recommending or starting any autonomous AI coding agent run |
| [`cross-ecosystem-compare-by-tier-not-name.md`](./cross-ecosystem-compare-by-tier-not-name.md) | Pattern | Developer asks to compare Copilot, Codex, and Grok by model quality |
| [`context-window-estimate-before-long-run.md`](./context-window-estimate-before-long-run.md) | Primary diagnostic | Task is High or Very High context demand — long run, multi-file, full repo |
| [`surface-coupling-is-a-first-class-selection-criterion.md`](./surface-coupling-is-a-first-class-selection-criterion.md) | Pattern | Any cross-ecosystem comparison or recommendation |
| [`sweep-lineup-before-quoting-availability.md`](./sweep-lineup-before-quoting-availability.md) | Absolute rule | Knowledge bank is more than 4 weeks old or a discrepancy is reported |
| [`high-blast-tasks-require-human-gate.md`](./high-blast-tasks-require-human-gate.md) | Absolute rule | Agentic task involves DB writes, deploys, secret rotation, or force-push |
| [`narrate-the-tier-selection-not-just-the-sku.md`](./narrate-the-tier-selection-not-just-the-sku.md) | Pattern | Every model recommendation — the traversal is the deliverable |
| [`prompt-scope-before-model-upgrade.md`](./prompt-scope-before-model-upgrade.md) | Pattern | Developer reports insufficient model output quality |
| [`document-model-choice-in-project-adr.md`](./document-model-choice-in-project-adr.md) | Pattern | Any model choice that will persist in team config, CI, or org policy |
| [`free-tier-model-access-is-a-subset-not-the-full-picker.md`](./free-tier-model-access-is-a-subset-not-the-full-picker.md) | Absolute rule | Developer's Copilot plan is Free or unknown |

---

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — plugin team constitution and house opinions
- [`../knowledge/ai-coding-decision-trees.md`](../knowledge/ai-coding-decision-trees.md) — the vendor-neutral selection tree these rules operationalize
- [`../../../docs/best-practices/README.md`](../../../docs/best-practices/README.md) — marketplace-wide best-practice docs
