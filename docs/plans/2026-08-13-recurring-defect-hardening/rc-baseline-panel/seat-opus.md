# RC-BASELINE-VOTE — seat-opus

**Vote: (b) — keep RC_BASELINE hand-maintained as a golden test oracle.** Confidence 0.73.

## The crux, resolved from code: is (a)'s independence real or a tautology?

**It is REAL, not a tautology — but that finding does not carry the vote, because independence is
necessary-not-sufficient for (a) to be the right call.** I disagree with Plan B's route to keep-golden
(it called (a) a tautology); I reach keep-golden by granting (a)'s independence and voting (b) anyway
on the merits.

**What the render count actually reflects (post-processing, not raw dirs).**
`check-plugin-detail-render.mjs:128-138` computes `nine` by parsing the **committed `index.html`'s
serialized arrays** — the eager `__RC_DATA__` blob (`erc.agents`, `erc.skills_index`, `erc.hooks_index`,
`erc.rules_index`) and the lazy detail island (`irc.scripts_index`, `irc.scenarios_index`,
`irc.templates_index`, `irc.best_practices_index`), plus `treeCount()` from the `#dt-store` HTML. That is
the artifact **after** both the generator's scan **and** the eager/island split (the H4 hydration hazard the
gate's own header, lines 2-19, exists to catch). So a card can be lost in two distinct places: (A) the
generator's scan drops it, or (B) the islanding/serialization split drops it from the eager blob or island.

**Why an independent FS scanner is genuinely a second path.** For the H4 case (B) — an island bug drops
`scripts_index` for `ravenclaude-core` → `irc.scripts_index` is `undefined` → render `tools=0` — a
separately-authored scanner reading `plugins/ravenclaude-core/scripts/*.py` from disk yields 19, and
`0 !== 19` → RED. Two different substrates (committed HTML vs. filesystem source) reached by two different
code paths; the regression makes them diverge. That is real independence. Plan B's tautology objection only
holds for the *import-`_scan_skills`-directly* implementation — which Plan A already forbade by requiring a
separately-authored scanner. So the tautology charge misfires against the actual (a) proposal.

## Why (b) anyway — per-scenario coverage, grounded

Granting full independence, (a) still buys almost nothing here and costs real teeth:

- **H4 islanding catch (the gate's actual job): (a) == (b).** Island drops `scripts_index` → render `tools=0`;
  independent FS scan says 19 → RED; frozen baseline says 19 → RED. Both catch it identically. (a) adds
  **zero** coverage on the hazard Gate 141 exists for.
- **Consistent source deletion: (a) is BLIND, (b) catches.** Delete `skills/foo/` and regenerate → render
  `skills=52` AND independent FS scan of `skills/*/` = 52 → `52===52` GREEN, the vanished skill unnoticed.
  Frozen baseline `53 !== 52` → RED, forcing "did you mean to delete foo?" For a *"zero content loss"* oracle
  that is exactly the class of silent disappearance worth catching.
- **Intent-confirmation checkpoint: (b) has it, (a) sheds it.** A legit 54th skill forces a conscious 53→54
  bump under (b); (a) absorbs it silently. `_scan_agents` (line 548) and `_scan_skills` (677-689) mostly
  emit one card per dir, so for those sections an independent raw scan and the generator share a definition —
  the checkpoint is the only thing distinguishing them.
- **New definition-drift footgun: (a) introduces it, and Plan A already tripped it.** `_scan_scripts`
  (line 644) globs **all** `*.py` with no `_`-exclusion; `ravenclaude-core/scripts/` has 19 `.py`, one
  `_`-prefixed, so render `tools=19`. Plan A's own independent-scanner spec ("`scripts/*.py` minus
  `_`-prefixed helpers") computes **18** → a **false RED on a clean tree**. The scanner must mirror the
  generator's counting definition exactly while diverging in code path — a live, demonstrated fragility.
- **Manual-bump cost of (b): negligible for this artifact.** RC_BASELINE is one object in one file, ~4
  historical bumps each with a provenance comment. It was **not** the ~180-mirror Copilot-freshness cascade
  that motivated count-SSOT — the prose-count drop (settled) already closes that. Self-maintaining solves a
  problem that barely exists here.

**Category point:** RC_BASELINE is a *test oracle / golden fixture* (the same shape as this repo's SVG /
box-packer / screen-flow byte-diff goldens), not consumer-facing duplicated data that must track reality.
Deriving a golden from the thing under test is a category error — `assert add(2,2)==4` must not compute the
4 from the adder. The count-SSOT thesis ("derive, don't duplicate") governs the data mirrors; it does not
govern the assertion.

**Optional sweetener (Plan B):** a non-blocking advisory printing when
`actual_skill_count`/`actual_agent_count(ravenclaude-core)` (already computed in Python, an independent
language from the Node gate) disagree with the baseline's `skills`/`agents` — recovers most of (a)'s
"don't-notice-by-eye" benefit for 2 of 9 keys without touching the gate's teeth. Nice-to-have, not
load-bearing; keeps (b) strictly better than (c)'s untouched status quo and records the deliberate
"golden, do not compute" decision so a future session doesn't re-open this fork into a tautology.
