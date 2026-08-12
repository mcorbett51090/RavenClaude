# Changelog — memory-engineering

All notable changes to this plugin are documented here. Versioning is semver; bump on every user-visible change (AGENTS.md).

## [0.1.0] — 2026-08-06

Initial release. Advisory only — no surface in this plugin reads or mutates a real memory store.

- **3 agents** — [`memory-architect-lead`](agents/memory-architect-lead.md), [`memory-retention-and-erasure-engineer`](agents/memory-retention-and-erasure-engineer.md), [`memory-eval-cost-analyst`](agents/memory-eval-cost-analyst.md), each carrying the full scenario-authoring schema and an explicit `tools:` allowlist.
- **6 skills + 6 commands** — `choose-memory-paradigm`, `map-memory-surface`, `design-forgetting-policy`, `budget-memory-costs`, [`memory-poisoning-review`](skills/memory-poisoning-review/SKILL.md), `build-memory-eval`. `cost-per-correct` is shared between `budget-memory-costs` (cost) and `build-memory-eval` (accuracy) and is owned by neither.
- **5-file knowledge bank** — paradigms (with the corrections block and a consolidated provenance table), the shipped memory surfaces dated `2026-08-06`, unit economics, security & privacy (OWASP ASI06, cited from [`ai-red-teaming`](../ai-red-teaming/knowledge/ai-attack-taxonomy-decision-tree.md) rather than re-derived), and Mermaid decision trees. Every file carries a `**Last verified:**` line the marketplace freshness sweep can read.
- **[`scripts/memory_engineering_calc.py`](scripts/memory_engineering_calc.py)** — stdlib calculator, 4 modes: `cost-per-correct` (the spine), `amortize`, `store-growth`, `cache-economics`. **Zero baked-in vendor constants** — every priced input is supplied by the user, `--baseline` is required with no default, and volatile published figures live in [`knowledge/memory-surfaces-2026.md`](knowledge/memory-surfaces-2026.md) where the staleness sweep can see them. Decision-support, not professional advice.
- **8 best-practice rules · 4 templates · 3 scenarios · 1 advisory hook** — the hook is advisory and flags two things in generated deliverables: an unsourced benchmark number, and a metric cited with no baseline. It blocks nothing unless `MEMORY_ENGINEERING_STRICT=1` is set.
- **Memory security ships as a skill, not a fourth agent.** ASI06 review is [`memory-poisoning-review`](skills/memory-poisoning-review/SKILL.md), invoked by `ravenclaude-core/security-reviewer` through an inline prior; the house rule's grip is strictest on review roles, which never fork. Its discoverability is mechanically checked, not asserted.
- **Requires `ravenclaude-core@>=0.238.0`** — deliberately a precise floor rather than the boilerplate one most manifests copy. This plugin's constitution links the **Memory Engineering Protocol**, which first ships in core `0.238.0`; on an older core that link and the inherited floor do not exist.

### Migration

New plugin, opt-in — nothing breaks on `/plugin marketplace update`. Installing it requires `ravenclaude-core` at `0.238.0` or later, which ships in the same release.
