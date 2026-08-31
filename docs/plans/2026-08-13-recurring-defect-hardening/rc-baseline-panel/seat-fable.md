# RC_BASELINE panel — seat: fable

**Vote: (a)** — de-hardcode via an independent filesystem scanner — **confidence 0.72**, with two binding conditions (below).

## The crux, resolved from the real code

### What the gate actually reads (render side)

`scripts/check-plugin-detail-render.mjs` never touches the filesystem's plugin dirs. It regex-extracts and JSON-parses the **committed `index.html`'s emitted output**:

- the eager `window.__RC_DATA__` blob (`check-plugin-detail-render.mjs:97-107`),
- the detail island `<script type="application/json" id="plugin-detail-payload">` (`:72-87`),
- and, for `trees`, a literal DOM-pattern count of `class="dt-item" data-plugin="…"` occurrences (`treeCount()`, `:113-119`).

The nine counts (`:128-138`) are `(erc.skills_index||[]).length`, `(irc.scripts_index||[]).length`, etc. — **post-processed emitted data as it survived generation, islanding, serialization, and commit**. This is genuinely the render side of a two-sided comparison.

### The generator can silently drop cards (this is what makes independence real)

`scripts/generate-index-dashboard.py` has multiple silent-skip paths on the emit side:

- `_scan_skills` (`:677-680`): a `skills/<x>/` dir **without `SKILL.md` is silently `continue`d** — no error, one fewer entry.
- `_scan_hooks` (`:702-705`): a corrupt `hooks/hooks.json` → **`return []`** — the whole hooks section vanishes with zero error.
- `scan_repo` (`:746-747`): a marketplace entry whose dir is missing is silently skipped.

So the emitted count is NOT structurally identical to a raw-FS count; the generator (plus the P2 islanding split — the H4 hazard the gate's own header documents) can lose content on the way to `index.html`. A **separately-authored** FS scanner (Plan A's `count-core-sections.py`, reusing `check-marketplace-claims.py`'s `actual_skill_count`/`actual_agent_count`/`actual_core_hook_count` — Python, different traversal, no import of `scan_repo`) therefore disagrees with the render whenever a card drops in the render pipeline: **render == independent_fs is a genuine two-path cross-check for the gate's stated purpose.** The tautology only arises if the expectation were computed by importing the generator's own `_scan_*` functions — which Plan A's Phase 0 explicitly forbids and fixtures against.

### The honest residual — where (a) IS correlated

The independence is real for **render-side** regressions but **definition-correlated** for **source-shape** regressions. `actual_skill_count` (`check-marketplace-claims.py:138-150`) counts "dirs carrying SKILL.md" — the *same semantic rule* as `_scan_skills`. Delete a skill's `SKILL.md` from disk and BOTH paths count 52 → gate green → card gone. `actual_core_hook_count` (`:186-193`) even shares the fail-open shape: corrupt hooks.json → `return 0` on the Python side and `return []` on the generator side → 0 == 0 → green. RC_BASELINE-as-golden (b) catches exactly this class; (a) does not.

### Why (a) still wins

1. **The gate's documented purpose is the render class.** Its own header (`:2-14`) defines it as the H4 "zero content loss" oracle for the render/hydration split. Against that purpose, (a) is fully independent — proven so by the generator's silent-skip paths above.
2. **The class (a) loses is the class the PR diff already shows.** A deleted `SKILL.md` or corrupted `hooks.json` is *literally the diff under review* (and hooks.json corruption is caught by other manifest gates). A render drop is invisible in any source diff — that is the class needing an oracle.
3. **(b)'s "checkpoint" value has degenerated into ritual.** The bump-provenance comments in the file itself (`52 -> 53`, `30 -> 31`, `:56-63`) show the golden is bumped reactively every time it goes red on an intended change. A hand-bumped oracle whose standard response to red is "make the number match" is an automation-shaped chore, not a second opinion — and this fork exists precisely because manual count maintenance is the recurring defect. (c) merely preserves that chore.
4. **Layering still holds.** Gate 97 (committed-vs-regenerated freshness) plus (a)'s render-vs-independent-FS plus the gate's number-free invariants (island completeness `:194-199`, key-presence sentinel `:174-190`, `counts === island length` `:204-213`, `nonEmpty === 9` `:145-146` — all untouched by this fork) cover staleness, render loss, and hydration loss respectively.

## Binding conditions on the (a) vote

1. The expectation module must **not import** `generate-index-dashboard.py` / `generate-dashboards.py` scan functions — separately authored, per Plan A Phase 0.
2. Both must-fail fixtures land with it: (i) mutate the render without the FS → red; (ii) mutate the FS without regenerating → red. Fixture (ii) is the standing proof the oracle never became the generator's echo.

Named residual accepted: correlated counting-definition drift (shared "dir-with-SKILL.md" rule; shared fail-open on corrupt hooks.json) — Low probability, visible in source diffs, and worth naming in Gate 141's header rather than pretending the golden covered it well.
