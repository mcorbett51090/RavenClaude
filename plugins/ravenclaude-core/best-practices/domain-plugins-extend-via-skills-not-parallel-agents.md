# Domain plugins extend core via skills and knowledge — not parallel agents

**Status:** Absolute rule
**Domain:** Agent design / Plugin architecture / Marketplace design
**Applies to:** `ravenclaude-core`

---

## Why this exists

Every time a domain plugin ships a parallel agent that duplicates a core agent role (a `domain-security-reviewer` alongside `ravenclaude-core/security-reviewer`, a `domain-architect` alongside `ravenclaude-core/architect`), two failure modes emerge. First: dispatch ambiguity — the Team Lead does not know which reviewer to spawn when a diff crosses plugin boundaries. Second: rubric drift — the domain reviewer diverges from the core rubric over time, and the same diff gets different verdicts depending on which reviewer handles it. The fix is structural: domain-specific craft belongs in skills and knowledge files that core agents invoke, not in parallel agents that replicate core roles.

## How to apply

Before proposing a new domain agent, apply the litmus test:

> *Could a competent `ravenclaude-core` agent, handed the right skill and knowledge file, produce indistinguishable output?*

If **yes** → ship a skill (with an inline prior on the relevant core agent pointing at it).

If **no** — the domain carries operational craft the core agent genuinely lacks — → ship an agent.

**The canonical carve-out (the rule's one honored exception):**

A *generalist* concern may earn its own plugin when it splits cleanly into "domain-neutral hygiene" (stays core) and "deep specialist craft" (the plugin). Project management is the worked example: lightweight RAID/status hygiene stays as `ravenclaude-core/project-manager` (unchanged for all plugins); the deep PM craft — EVM, sprint facilitation, scored risk registers — lives in the `project-management` plugin, which **extends** the core agent rather than replacing it.

**The test that keeps this honest:** *hygiene → core; running the project → the plugin.* This is a deliberate carve-out, not a precedent to fork every generalist.

**Do:**
- Ship `domain/skills/<capability>.md` + an inline prior on the core agent that reads it.
- Put domain-specific review rubrics in `domain/knowledge/<rubric>.md` and point `ravenclaude-core/security-reviewer` at it via the inline prior.
- Confirm: 5 of 5 domain plugins in the marketplace ship **no** domain-specific security reviewer. All security review escalates to `ravenclaude-core/security-reviewer`.

**Don't:**
- Ship `domain-security-reviewer.md` or `domain-architect.md` — these are the specific failure cases the rule was extracted from.
- Treat the project-management carve-out as a precedent for forking every role; earn the split by demonstrating the depth genuinely can't live in a skill file.
- Add a domain agent and then add an inline prior on the same core agent pointing at it — the inline prior is the alternative to the domain agent, not a complement to it.

## Edge cases / when the rule does NOT apply

- An agent whose entire operating domain is genuinely incompatible with any core agent role (e.g., a regulatory audit specialist with a completely different deliverable format and no core-agent analog) may justify a new agent. The rule is about **parallel-role forks**, not about genuinely new roles.

## See also

- [`./route-before-spawning.md`](./route-before-spawning.md) — the routing tree that relies on this boundary being clean to produce unambiguous dispatch.
- [`../CLAUDE.md`](../CLAUDE.md) — "Plugin Architecture: Core vs Domain Plugins" and "House rule: domain plugins extend core via skills and knowledge" sections.

## Provenance

Distilled from `plugins/ravenclaude-core/CLAUDE.md` §"House rule: domain plugins extend core via skills and knowledge, not parallel agents (added 2026-05-21)". Precedent: the `data-platform` plugin's v0.1.0 plan — two proposed parallel agents found to be skills + decision trees.

---

_Last reviewed: 2026-06-05 by `claude`_
