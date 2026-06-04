# Cross-plugin references — soft, optional, never a hard dependency

**Status:** Absolute rule — a cross-plugin reference must degrade gracefully; a plugin that breaks (or misleads) when a referenced sister plugin is absent is a bug.

**Domain:** Cross-domain / Plugin mechanics.

**Applies to:** every plugin in this marketplace (`ravenclaude-core`, `power-platform`, `regulatory-compliance`, `finance`, and any future plugin) that references another plugin's agents, skills, or knowledge.

---

## Why this exists

The marketplace's plugins are installed **à la carte** — a consumer may install `power-platform` without `regulatory-compliance`, or `regulatory-compliance` without `finance`. Real value lives in the **seams** (Power Platform *builds* the compliance solution whose *substance* the regulatory plugin owns; regulatory work *pairs* with finance's audit/controls assurance), so plugins legitimately want to point at each other. But Claude Code has **no plugin-dependency mechanism** — there is no `requires:` that installs a sister plugin, and nothing guarantees a referenced plugin is present at runtime. A reference authored as if the other plugin is always there produces two failure modes: a **dead link** (the file isn't on disk) and, worse, a **silent competence gap** (the agent assumes a capability it doesn't have and answers from outside its lane). This rule makes every cross-plugin reference **soft** — additive when the sister is present, harmless and honest when it isn't.

## How to apply

A cross-plugin reference must satisfy **all three** of:

1. **Self-contained first.** The file/agent stands on its own. The cross-reference *adds* a routing hint or composition opportunity; it is never load-bearing for the file's own correctness. If removing every cross-plugin reference would leave the file broken or useless, the boundary is wrong.
2. **Conditioned on presence.** Phrase the reference as *"if `<plugin>` is installed alongside, route X there"* — explicitly stating both branches. Name what the sister owns and what *this* file does when it's absent (typically: flag the gap as `[needs SME / human sign-off]`, never paper over it).
3. **No hard `requires`.** Never add a manifest dependency on another plugin, and never write an agent that *cannot function* without a sister plugin. The reference is a pointer, not an import.

**The canonical phrasing block** (copy, adapt the names):

```markdown
**If `<sister-plugin>` IS installed:** route <kind-of-question> to its <agent/knowledge-file>
(<what it owns>); this plugin <what it does with that input>.

**If `<sister-plugin>` is NOT installed:** this plugin still <does its own job> — but
<every fact the sister would have owned> must be supplied/signed-off by a human <SME role>,
and is treated as `[needs sign-off]` until confirmed. No regulatory/domain truth is inferred
from this side.

**No hard dependency exists in either direction** — neither plugin `requires` the other;
this is a soft, install-time-optional bridge per
[`docs/best-practices/cross-plugin-references.md`](../../docs/best-practices/cross-plugin-references.md).
```

**Do:**
- Put the seam in a dedicated section (`## The seam to <plugin>` or a "Cross-references (graceful degradation)" block) so it's visible and auditable.
- State the **division of competence** as a small table — "what the question is about → which plugin owns it."
- Use **repo-relative links** (`../../../docs/...`) so they survive renames; a broken relative link is at least visible in review, unlike an assumed-present capability.
- Reference **stable surfaces** of the sister plugin (a named knowledge file, a named agent), not transient internals.

**Don't:**
- Don't write "see the `finance` plugin's controller" as if it's guaranteed present, with no "if installed" qualifier.
- Don't let an agent's *core* answer depend on a sister plugin's file being readable.
- Don't add a `requires`/dependency field to `plugin.json` pointing at another plugin — it isn't honored and implies a guarantee that doesn't exist.
- Don't infer the sister domain's *substance* from this side to fill the gap (a Power Platform agent guessing a Basel ratio; a regulatory agent guessing a DAX fix). Flag it for sign-off instead.

## Edge cases / when the rule does NOT apply

- **Intra-plugin references** (one file in a plugin pointing at another file in the *same* plugin) are not cross-plugin — they ship together, so a normal link is fine and this rule doesn't apply.
- **`ravenclaude-core` is the one near-universal base.** Most plugins are authored assuming `ravenclaude-core` is present (it carries the shared constitution, grounding protocol, collaboration rules). Referencing *up* into `ravenclaude-core` may assume presence — but still prefer the conditional phrasing where a graceful fallback is cheap, and never assume *sibling* (non-core) plugins.
- **Inline duplication for a single fact** is acceptable: if a sister plugin owns a body of knowledge but this plugin needs one small derived fact in isolation, it's fine to inline that fact (with a marker) rather than create a hard cross-reference — the §5-style inline fallback some plugins already use.

## See also

- [`pr-vs-direct-push.md`](./pr-vs-direct-push.md) — whether the change opens a PR (plugin content) or commits direct (docs).
- [`plugin-versioning.md`](./plugin-versioning.md) — both plugins on either side of a new bridge bump their version mirrors.
- [`lessons-vs-best-practices.md`](./lessons-vs-best-practices.md) — why this is a rule (always-applies) not a lesson (story).
- Worked examples in the tree: the `regulatory-compliance` ↔ `power-platform` bridge ([`plugins/power-platform/knowledge/regtech-compliance-solutions.md`](../../plugins/power-platform/knowledge/regtech-compliance-solutions.md) §6) and the `regulatory-compliance` ↔ `finance` bridge (the audit/controls/SOC cross-references in both plugins' CLAUDE.md sister-plugin notes).

## Provenance

Written 2026-06-04 while building the `regulatory-compliance` plugin's two outward bridges — to `power-platform` (Power Platform builds the RegTech solution whose substance the regulatory plugin owns) and to `finance` (regulatory work pairs with `audit-prep-specialist`'s controls/SOC assurance). Both bridges needed the same discipline — additive when the sister is installed, honest about the gap when it isn't, never a hard dependency — so the discipline was lifted into this named rule rather than re-derived per bridge. Codifies the pattern the `regulatory-compliance` and `finance` CLAUDE.md "Sister plugins (when installed alongside)" notes already used informally.

---

_Last reviewed: 2026-06-04 by `mcorbett51090`_
