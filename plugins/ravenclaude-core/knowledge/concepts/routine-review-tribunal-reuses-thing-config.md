---
id: routine-review-tribunal-reuses-thing-config
title: "The routine-review tribunal borrows its panel, not just its shape"
category: "Inventory — measured mechanisms"
kind: ravenclaude-built
entry_class: inventory
order: 934
summary: "routine-review-tribunal.py imports thing-decision.py and calls its resolve_panel_config directly, so the model-diversity guarantee is inherited, not re-implemented."
last_verified: 2026-09-11
covers:
  - plugins/ravenclaude-core/scripts/routine-review-tribunal.py
  - plugins/ravenclaude-core/skills/routine-review-tribunal/SKILL.md
covers_digest: "sha256:7174ddecf3992c016f267169ec6104dc664e994b48d36f39eeeceb97f12484c5"
nuance: "resolve_panels() does an importlib load of thing-decision.py and calls its resolve_panel_config — it is not a hand-copied seat/model table, so the Thing's >=2-distinct-model diversity rule applies here for free and cannot silently drift from it."
nuance_evidence:
  measured: 2026-09-11
  control: "ran `routine-review-tribunal.py --root . panels`; the returned seat->model mapping (Mimir: a code-reviewer-shaped seat, Forseti/Thor: security-reviewer/architect-shaped) matched the built-in defaults thing-decision.resolve_panel_config resolves for those same seat names, not a separately hardcoded pair"
  falsifier: "a future edit that hardcodes a model/agent string in routine-review-tribunal.py instead of calling resolve_panel_config would let the two panels drift apart with no test catching it"
  probe: "plugins/ravenclaude-core/scripts/routine-review-tribunal.py"
nuance_source: "plugins/ravenclaude-core/scripts/routine-review-tribunal.py:106-150"
verify:
  tier: "none"
  rationale: "The reuse is a 5-line source fact (one module importing another's function) already read in the panels subcommand's own output; the --self-test suite covers the deterministic tally() logic downstream of resolution, not this import fact, and a dedicated static-AST check would be redundant with reading resolve_panels() directly."
sources:
  - label: written + verified this session, alongside the routine-review-tribunal build
    url: https://github.com/mcorbett51090/RavenClaude/pull/1161
---

## What a reader would have assumed instead

That a new tribunal-shaped script would need its own model/agent config — either a duplicated seat table or a fresh entry in `.ravenclaude/thing.yaml` — since it reviews a different payload (a diff, not a command or a question) from the Thing or decision-review.

## The discriminator

control: ran `routine-review-tribunal.py --root . panels`; the returned seat->model mapping matched thing-decision's own built-in defaults for the same seat names, not a separately hardcoded pair.

Measured 2026-09-11: `resolve_panels()` loads `thing-decision.py` via `importlib.util.spec_from_file_location` and calls `resolve_panel_config(root, posture)` on it directly — the exact function the live command-review tribunal and decision-review already use. There is no second, parallel model table to keep in sync.

## Why it matters

If `.ravenclaude/comfort-posture.yaml` or `.ravenclaude/thing.yaml` ever repoints a seat to a different model (e.g. to raise Forseti's reasoning effort), the routine-review tribunal picks that up automatically on its next `panels` call — the same way the Thing and decision-review would. A script that had instead hardcoded `"agent": "security-reviewer", "model": "claude-opus-4-8"` would silently keep reviewing routine diffs with a stale seat long after the rest of the marketplace moved on.

Falsifier: a future edit to `routine-review-tribunal.py` that hardcodes a seat's model/agent instead of calling `resolve_panel_config`.
