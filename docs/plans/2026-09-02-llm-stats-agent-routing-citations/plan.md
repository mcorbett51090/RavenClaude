# Fill-in-the-numbers plan: cite llm-stats.com in `agent-routing-matrix.json`

**Status:** ready to execute once a free API key exists (see `docs/research/2026-09-02-llm-stats-api-verification.md`
for the verified endpoint facts + the WebFetch-fabrication correction this plan is built on top of).
**Blocked on:** a human signing up at `https://llm-stats.com/developer` for a bearer token — not done here.
**Why this is a plan doc and not a half-edited JSON file:** `agent-routing-matrix.json` is gated by
Gate 255, which validates every citation is real (check E verifies a `framework-rule` quote exists
verbatim in its source; check B bans unlisted vendor-fact literals). Landing placeholder numbers into
that file — even clearly marked `<TODO>` — risks either failing the schema/gate or, worse, surviving a
careless future edit as if it were real data. This plan carries the exact diff shape; a future session
(or this one, once a key exists) fills in real numbers and applies it directly.

## Step 0 — get data

```bash
export LLM_STATS_KEY="<paste the bearer token from https://llm-stats.com/developer>"
curl -s -H "Authorization: Bearer $LLM_STATS_KEY" https://api.zeroeval.com/stats/v1/models > /tmp/llm-stats-models.json
curl -s -H "Authorization: Bearer $LLM_STATS_KEY" https://api.zeroeval.com/stats/v1/scores > /tmp/llm-stats-scores.json
```
Extract, for the models this matrix actually names by *tier* (never a raw SKU — see the ban-list note
below): the `claude` fast/balanced/top tier, the `codex` fast/balanced/top tier, and the `grok`
fast/balanced/top tier, per `plugins/ravenclaude-core/knowledge/substrate-tier-map.json` (retrieved
2026-08-14 — re-check it hasn't drifted before pulling numbers). Record: SWE-Bench Verified score,
Coding Arena rank/score, and $/M input-token price for each. Note the retrieval date.

## Step 1 — add the source entry

Append to `sources[]` in `plugins/ravenclaude-core/knowledge/agent-routing-matrix.json` (after `"copilot-chat-c8"`):

```json
{
  "id": "llm-stats",
  "note": "llm-stats.com data API (api.zeroeval.com/stats/v1/*), retrieved <FILL IN DATE> -- SWE-Bench Verified, Coding Arena, and $/M-token pricing for the model tiers named in substrate-tier-map.json. API verified live 2026-09-02 (see docs/research/2026-09-02-llm-stats-api-verification.md); requires a free bearer-token signup. Live/self-reported split is not disclosed by the vendor -- treat scores as vendor-published, not independently re-run."
}
```

⛔ **Do not put a raw SKU or model display name in this file** — Gate 255 check B derives its ban-list
from `model-catalog.json` + `substrate-tier-map.json`'s own leaf values and will fail the build on one.
Every citation below refers to a **tier** (`fast`/`balanced`/`top`) or a **host**, never the literal id.

## Step 2 — the cells worth strengthening, and why these three (not all of them)

Not every cell benefits equally. These three are where the current `rationale` is doing real work with
no comparative evidence behind it — exactly where a real number replaces editorial judgment with
`capability-fact`/`cost-heuristic` grounding the file's own taxonomy already has room for:

### 2a. `coding-implementation` → `agent` × `reversible` (3-way rank with no differentiator today)

Current: claude-code(1, framework-rule) > codex-cli(2, framework-rule) > grok-build-cli(3,
capability-fact) — grok's `rationale` already says "a reasonable third option," which is exactly the
editorial-judgment-dressed-as-capability-fact shape worth firming up.

Diff shape (only the `rationale` + `sources` change; `rank`/`basis`/`agent`/`model_ref` untouched —
a numeric score does not change WHICH agent is ranked first unless the data says so, and if it does,
that's a `rank` change to make deliberately, not accidentally, in a follow-up review):

```json
{
  "interaction_mode": "agent",
  "blast_radius": "reversible",
  "agent": "grok-build-cli",
  "model_ref": { "host": "grok", "tier": "balanced" },
  "rank": 3,
  "basis": "capability-fact",
  "rationale": "Grok Build CLI's balanced tier already carries the architect perspective (SSOT, smallest surface) with high effort -- a reasonable third option for a reversible autonomous run, resolved entirely through the tier map with no independent effort field on this recommendation. Per llm-stats.com (retrieved <DATE>), <grok balanced tier> scores <SWE-BENCH SCORE> on SWE-Bench Verified vs <claude balanced tier>'s <SCORE> and <codex balanced tier>'s <SCORE>, consistent with its rank-3 placement here.",
  "sources": ["substrate", "cheap-lane", "llm-stats"]
}
```

If the real numbers instead show grok's balanced tier *beating* one of the higher-ranked agents on
SWE-Bench Verified, **do not silently reorder** — that's a real disagreement between this file's
framework-rule-derived ranking and an empirical benchmark, and belongs in a `## Correction` note (this
file's own established convention — see `agent-routing-matrix.md`'s "A correction inherited from this
build's own review process" section) rather than a quiet edit, since it would mean either the benchmark
doesn't measure what this cell cares about (autonomous multi-file reversible work vs. a benchmark's
narrower task shape) or the framework-rule ranking needs revisiting.

### 2b. `coding-debugging-design` → `agent` × `reversible` (only one agent listed today)

Current: only `claude-code` (rank1, `cost-heuristic`) — no comparison offered at all, because the file
had nothing to compare against for this genuinely-hard-tail cell.

Diff shape (an ADDITION, rank2+, not a replacement):

```json
{
  "interaction_mode": "agent",
  "blast_radius": "reversible",
  "agent": "codex-cli",
  "model_ref": { "host": "codex", "tier": "top" },
  "rank": 2,
  "basis": "capability-fact",
  "rationale": "Per llm-stats.com (retrieved <DATE>), <codex top tier> scores <SCORE> on SWE-Bench Verified vs <claude top tier>'s <SCORE> -- close enough to name as a second option for a confirmed-hard bug session, gated by the same PR review since the run stays reversible.",
  "sources": ["cost-tree", "mode-tree", "llm-stats"]
}
```

Only add this if the real gap is small enough to be a genuine "second option" — if claude's top tier
leads by a wide margin, the honest move is to NOT add a rank-2 entry here at all (a manufactured
alternative is worse than none; the file's own design note on `editorial-judgment` being "the weakest
basis, used sparingly" applies in reverse to a fabricated near-tie).

### 2c. Pricing → one `cost-heuristic` cell, `data-analysis` → `agent` × `reversible`

Current rationale argues for frontier tier on reconciliation strength alone, with no cost figure to
weigh against it — exactly the gap `cost-heuristic` exists to fill with a real number instead of
"the premium is worth it" asserted on faith.

```json
{
  "rationale": "An unsupervised multi-step analysis that must reconcile genuinely conflicting sources or an ambiguous methodology before reporting a conclusion is the hard tail: the frontier tier's reconciliation strength justifies its premium here, same logic as research-deep's agent/reversible cell. Per llm-stats.com (retrieved <DATE>), <claude top tier> prices at $<PRICE>/M input tokens vs <claude balanced tier>'s $<PRICE>/M -- a <RATIO>x premium, small relative to the cost of a wrong reconciliation on a report a human will act on.",
  "sources": ["cost-tree", "llm-stats"]
}
```

## Step 3 — mechanical follow-through (per this repo's own `AGENTS.md` convention)

1. Bump `plugins/ravenclaude-core/.claude-plugin/plugin.json` `version` (patch — additive citations,
   no behavior/schema change), then `python3 scripts/sync-plugin-versions.py` to derive the catalog
   entry (never hand-edit `marketplace.json`'s version).
2. `python3 plugins/ravenclaude-core/scripts/check-agent-routing-matrix.py` — must pass (Gate 255).
3. `python3 -m json.tool plugins/ravenclaude-core/knowledge/agent-routing-matrix.json > /dev/null`.
4. Add one `agent-routing-matrix.md` prose line noting the llm-stats citation under "Composition with
   existing mechanisms," and a one-line `CLAUDE.md` milestone entry per this repo's own convention (a
   dated append, not an edit to prior entries).
5. Branch `feat/ravenclaude-core-agent-routing-matrix-llm-stats-cites`, PR per `AGENTS.md` (this is a
   `plugins/` change — PR required, not straight-to-main).
6. Re-run `scripts/audit-gates.sh` before pushing.

## Non-goals (deliberately out of scope)

- **No numeric confidence field.** Gate 255 check C bans this permanently; a benchmark score lives in
  `rationale` prose, never a new schema field.
- **No live API call from inside the matrix file or a gate.** The citation is a dated, retrieved-once
  fact like every other `sources[]` entry (`copilot-chat-c8` is the precedent) — not a live-refetch
  mechanism. If drift becomes a problem, that's the existing weekly researcher sweep's job
  (`staleness_tier: Tier-4`), not a new gate.
- **No reordering of `rank` without a real, disclosed number** — see 2a above.
