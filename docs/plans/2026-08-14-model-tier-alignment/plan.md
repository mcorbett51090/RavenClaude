# FORGE plan — `model-tier-alignment` (G6 synthesis, authoritative)

**Slug:** `model-tier-alignment` · **Depth:** quick · **Date:** 2026-08-14 · **Owner:** Matt
**Worktree:** `/Users/matthewcorbett/RavenClaude/.claude/worktrees/forge-model-tier-alignment`
**Branch:** `forge/model-tier-alignment`
**This document supersedes** `plan-A.md` and `plan-B.md`. Tiebreaks are **bound, not re-litigated**. Quick depth has no G4a/G4b/G5.

**Live versions (re-read 2026-08-14 before writing):**
`plugins/ravenclaude-core/.claude-plugin/plugin.json` **0.255.0** · marketplace mirror **0.255.0** → bump **0.256.0**.
`plugins/ai-coding-model-guidance/.claude-plugin/plugin.json` **0.3.13** · marketplace mirror **0.3.13** → bump **0.3.14**.

**Success signal (G0, amended):** every consumption site that maps `fast`/`balanced`/`top` (or `haiku`/`sonnet`/`opus`) to a SKU names a verified, dated Grok + Codex/API + Copilot + Claude id, and the three Grok rungs are **three different SKUs**.

---

## 0. Conflict verdicts (orchestrator-bound)

| ID | Fork (gap-delta) | Verdict | Encoded as |
|---:|---|---|---|
| **V1** | Runtime maps: A comment-only Claude dicts vs B host-keyed resolver | **B.** `resolveTier(host, tier)` with default `host=claude`. G0 named all consumption sites; comment-only fails that. Default protects `claude -p`. | §3, P1, P3 |
| **V2** | New gate 134b vs reuse 45+134 | **A.** No new gate number. Optional self-test lives **in the shared module**, not `audit-gates.sh`. | §3, P1, DoD |
| **V3** | FORGE A==B after Grok collapse | **Overturned 2026-08-14.** Distinct SKUs: haiku=`grok-build-0.1`, sonnet=`grok-4.5`, opus=`grok-4.6`. If a host cannot dispatch the fast SKU, fail closed — do not map two Claude rungs onto one Grok id. | P4 |
| **V4** | Thing seats | **Both.** Stay Claude. Do not flip Forseti/Thor/Mímir/Heimdall to Grok. | P5 |
| **V5** | Copilot `balanced` dual cell vs pin | **B.** Sonnet 5 **primary**; `Auto` footnote only. | §2 |
| **V6** | Copilot `top` / Claude-host catalog | **Claim 13 + A.** Copilot `top` = **Opus 5**. Claude-host catalog stays `claude-opus-4-8`. No Opus-5 catalog bump. | §2, P5 |
| **V7** | Versions | **Live+1** (pins matched live): core **0.255.0→0.256.0**, guidance **0.3.13→0.3.14**, marketplace lockstep. | P7 |
| **V8** | SSOT shape | **Union.** One shared `substrate-tier-map` module (B) **+** adapter SKILL table **+** lineup knowledge file. **No** third rewrite of the frozen 2026-06-03 plan (annotate only). | §3, P1–P2, P6 |

Shared (not a fork): G0 surfaces; ChatGPT column = OpenAI API/Codex only; Grok `fast`+`balanced`→`grok-4.5`, `top`→`grok-4.6`; no third Grok CLI SKU; no consumer ChatGPT picker; pro = `reasoning.mode` not a slug; Codex = Luna/Terra/Sol; dual plugin + marketplace bumps.

---

## 1. G1 claims — every row settled or marked

No G1 row carried an `[unverified]` token. Settling-gates G2/G6 close here. Vendor strings still carry `[verify-at-use]` until P0 restamps.

| id | Settlement | Marker |
|---:|---|---|
| 1 | Grok Build CLI this host lists only `grok-4.6` (default) and `grok-4.5`. Adapter CLI column uses only those two. | **settled** (G0 + this-session `grok models`; P0 re-runs) |
| 2 | xAI API also lists `grok-4.3`, `grok-4.20-*`, `grok-build-0.1`. Those stay **lineup API/historical** rows, never CLI adapter SKUs. | **settled** (docs.x.ai 2026-08-14; P0 re-verify) |
| 3 | Owner: `fast`+`balanced`→`grok-4.5`; `top`→`grok-4.6`. No third CLI SKU. | **settled** (G0 ruling 3) |
| 4 | Codex/API three-rung = `gpt-5.6-luna` / `gpt-5.6-terra` / `gpt-5.6-sol`. Alias `gpt-5.6` → Sol. | **settled** (G1 probe; `[verify-at-use]` at P0) |
| 5 | No `*-pro` slug; pro is `reasoning.mode: "pro"` on Sol. | **settled** |
| 6 | Copilot GA includes Haiku 4.5, Sonnet 5, Opus 4.8 **and Opus 5**, plus Luna/Terra/Sol, Grok 4.5, Auto. | **settled** (G1; P0 re-fetch) |
| 7 | Copilot retirement 2026-09-01: Opus 4.5/4.6, Sonnet 4.5/4.6 → Opus 5 / Sonnet 5. Live adapter `top` = Opus 4.6 is already retiring. | **settled** |
| 8 | Claude-host catalog = `claude-haiku-4-5-20251001` / `claude-sonnet-5` / `claude-opus-4-8` / `claude-fable-5`. | **settled** (live `model-catalog.json` this session) |
| 9 | Adapter table has no Grok column; Codex still GPT-5.5 + GPT-5.5-Pro; Copilot `top` still Opus 4.6. **This is the defect.** | **settled** (as defect; P2 fixes) |
| 10 | Runtime `TIER_*` / `tier_model` dicts are Claude-only and host-blind. **This is the defect V1 fixes.** | **settled** (as defect; P3 fixes) |
| 11 | FORGE `--models` are Claude aliases with no host resolver. | **settled** (as defect; P4 fixes) |
| 12 | Thing seat defaults are Claude SKUs by design. | **settled** (V4; P5 empty-diff) |
| 13 | Copilot `top` = Claude Opus 5 (not 4.8 / 4.6). | **settled (G3b)** |
| 14 | Copilot `fast` = Haiku 4.5; `balanced` = **Sonnet 5 primary** (V5), Auto footnote. | **settled (G3b + V5)** |
| 15 | Codex column = Luna / Terra / Sol; not GPT-5.5 reasoning-level-on-one-SKU. | **settled (G3b)** |
| 16 | Thing seats stay Claude even on a Grok host. Host-aware seat map is a different design. | **settled (G3b + V4)** |
| 17 | `docs/plans/2026-06-03-adaptive-run-classifier/plan.md` is a frozen design record. Annotate; do not rewrite. | **settled** (G0 + P6) |

### 1.1 G3b settlement (inferences 13–16)

G1 already marked 13–16 `settled` from the 2026-08-14 probe-run. **G3b is closed for planning.** Implement still re-fetches in P0 (pages move). Do not re-open the inferences.

| Claim | Probe (P0, ≤300s, no creds) | `expected_if_true` | If false at implement |
|---|---|---|---|
| **13** | Fetch https://docs.github.com/en/copilot/reference/ai-models/supported-models | Claude Opus 5 listed as current; Opus 4.6 in 2026-09-01 retirement table | Ship last observed name + `[verify-at-use]`; do not invent |
| **14** | Same page | Sonnet 5 and Haiku 4.5 listed | Same |
| **15** | Fetch https://developers.openai.com/api/docs/guides/latest-model | `gpt-5.6-luna` / `terra` / `sol`; no `*-pro` slug | Same |
| **16** | Repo read: `thing-decide.py` seat dispatch + `.ravenclaude/comfort-posture.yaml` `panel:` | Seats invoke `claude -p` with Claude ids | **Stop and ask.** Do not silently overwrite |

If 16 is already host-switched in the tree, that is a plan-break, not a silent edit.

---

## 2. Target mapping (write this; do not invent off it)

Every cell `[verify-at-use — 2026-08-14]` until P0 restamps. Prices/context stay in the lineup, never here. Claude column **bytes** = `model-catalog.json` `current` (claim 8).

| Tier / alias | Claude (host catalog) | Grok Build CLI | Codex / OpenAI API | Copilot |
|---|---|---|---|---|
| `fast` / `haiku` | `claude-haiku-4-5-20251001` | **`grok-build-0.1`** | `gpt-5.6-luna` | Claude Haiku 4.5 (footnote: Luna / MAI-Code-1.1-Flash) |
| `balanced` / `sonnet` | `claude-sonnet-5` | **`grok-4.5`** | `gpt-5.6-terra` | **Claude Sonnet 5** (footnote: `Auto` when no tier label) |
| `top` / `opus` | `claude-opus-4-8` (catalog; **not** Opus 5) | **`grok-4.6`** | `gpt-5.6-sol` — pro = `reasoning.mode:"pro"` on Sol, **no** `*-pro` slug | **Claude Opus 5** |

**Owner amendment 2026-08-14 (overturns G0 ruling 3 / V3 collapse):** three **distinct** Grok SKUs so FORGE `B ≠ A` is a different model, not a waiver. Source: [xAI models](https://docs.x.ai/developers/models) 2026-08-14 — `grok-build-0.1` is the cheapest text SKU ($1/$2, 256k); `grok-4.5` is the prior flagship still listed; `grok-4.6` is current flagship. `grok models` in Grok Build CLI still only lists 4.5/4.6 — if `grok-build-0.1` is not dispatchable on that host, **fail closed** (do not silently collapse fast→4.5). `fable` is not in G0 — pass-through. Tribunal seats are **not** the Grok column.

---

## 3. Alternatives

| Alt | Approach | Trade-off | Verdict |
|---|---|---|---|
| **A — Host-keyed shared map (chosen)** | `substrate-tier-map.json` + `resolveTier(host,tier)` default `claude`; SKILL table + lineup stay the human/vendor surfaces | Correct at every consumption site; needs host arg/env + Gate 52 lockstep | **Select.** G0 + V1 |
| **B — Doc-only cascade (plan A chosen)** | Refresh SKILL + lineup; runtime dicts stay Claude values with four-column comments | Cheap; **fails FM-1** — Grok `/forge` and any non-Claude caller still see Claude ids | **Reject.** Comment-only fails G0 “all consumption sites” |
| **C — Per-file host tables** | Copy four columns into each JS/py consumer | No shared module; evaluate-dispatch / rc-deep-research / thing-decide drift | **Reject.** Historical failure mode of the Claude-only dicts |
| **D — Flip Thing seats to Grok** | Host-switch tribunal panel models | Breaks Claude-hosted `claude -p` tribunal (claim 16) | **Reject** (V4) |

Not in play: Claude-host `opus` → `claude-opus-5` (separate `docs/plans/2026-08-07-opus5-model-catalog-bump.md`). New Gate 134b. Third Grok CLI SKU. Consumer ChatGPT picker. Frozen-plan body rewrite.

### 3.1 SSOT — three surfaces, one machine map

| Surface | Path | Owns | Does not own |
|---|---|---|---|
| **Machine map** | `plugins/ravenclaude-core/knowledge/substrate-tier-map.json` + thin loaders | `host × {fast,balanced,top}` → SKU; Grok three-SKU uniqueness invariant | Prices; seats; Gate 134 Claude catalog |
| **Adapter table** | `plugins/ravenclaude-core/skills/adaptive-run-classifier/SKILL.md` § Substrate tier table | Human four-column table; must **mirror** the JSON | Vendor prices/retirements |
| **Vendor facts** | `plugins/ai-coding-model-guidance/knowledge/cross-tool-model-lineup-2026.md` | Dated names, prices, retirements, API/historical Grok rows | Claude-host catalog; Thing seats |
| **Claude-host catalog** (untouched) | `plugins/ravenclaude-core/knowledge/model-catalog.json` | Governed `claude-*` (Gate 134) | Grok / Codex / Copilot |

`agent-dispatch-evaluator/SKILL.md` keeps “Do NOT re-author the table here.” Re-date the pointer only.

**Loader shape (V1 + V2):**

```json
{
  "schema_version": 1,
  "retrieved": "2026-08-14",
  "hosts": {
    "claude":  {"fast": "claude-haiku-4-5-20251001", "balanced": "claude-sonnet-5", "top": "claude-opus-4-8"},
    "grok":    {"fast": "grok-build-0.1", "balanced": "grok-4.5", "top": "grok-4.6"},
    "codex":   {"fast": "gpt-5.6-luna", "balanced": "gpt-5.6-terra", "top": "gpt-5.6-sol"},
    "copilot": {"fast": "Claude Haiku 4.5", "balanced": "Claude Sonnet 5", "top": "Claude Opus 5"}
  },
  "notes": {
    "grok_distinct": "fast=grok-build-0.1 balanced=grok-4.5 top=grok-4.6",
    "codex_pro_mode": "reasoning.mode pro on sol — not a separate slug",
    "copilot_balanced": "Sonnet 5 primary; Auto footnote",
    "seats": "Thing seats stay Claude; not this map"
  }
}
```

- **Python:** `plugins/ravenclaude-core/scripts/load-substrate-tier-map.py` — `resolve_tier(host, tier, default_host="claude")`. `--self-test` asserts four hosts × three tiers, Grok `fast==balanced==grok-4.5`, `top==grok-4.6`, no `*-pro` slug, seats absent.
- **JS:** sibling `plugins/ravenclaude-core/scripts/substrate-tier-map.js` kept **byte-lockstep** with the JSON in the same PR (workflow scripts have **no module resolution**). Exports `resolveTier(host, tier)` — missing/blank host → `claude`.
- **Callers** that cannot `require()` (evaluate-dispatch reference + rc-deep-research copy-paste fence) **inline the generated `resolveTier` + map** behind the existing fence. Values generated from the JSON; do not hand-author a third table.
- **Host detection:** explicit arg > `RAVENCLAUDE_HOST` > FORGE-known CLI host > **`claude`**. Do **not** extend `scripts/rc-artifacts.py` `detect_host()` (no Grok signal today; a wrong stamp is worse than `unknown`).
- **No new `── Gate N:` header** in `scripts/audit-gates.sh`. Self-test is a module flag, invoked as a P1/P7 acceptance command.

---

## 4. Consumption inventory (P0 discipline, already named)

| Path | Kind | Today host-aware? | Action |
|---|---|---|---|
| `skills/adaptive-run-classifier/SKILL.md` § Substrate tier table | adapter / knowledge | n (3 cols, no Grok) | P2 — four columns; mirror JSON |
| `skills/agent-dispatch-evaluator/SKILL.md` pointer | knowledge | n/a | P2 — re-date only |
| `skills/agent-dispatch-evaluator/reference/evaluate-dispatch.js` `TIER_MODEL` | adapter | n | P3 — `resolveTier` |
| `skills/rc-deep-research/rc-deep-research.js` `TIER_MODEL` + `DISPATCH_TIER_MODEL` | adapter | n | P3 — lockstep copy fence |
| `scripts/thing-decide.py` `_evaluator_shadow` `tier_model` | adapter (shadow) | n | P3 — `resolve_tier`; default `claude` |
| `commands/forge.md` + `skills/forge-pipeline/SKILL.md` `--models` | alias resolve | n | P4 — host column; Grok `B ≠ A` is three SKUs |
| `.ravenclaude/comfort-posture.yaml` `panel.*.model` | seat | n (Claude by design) | P5 — **do not edit SKUs** |
| `templates/thing.yaml` + `templates/comfort-posture-balanced.yaml` | seat template | n | P5 — optional one-line comment |
| `scripts/generate-dashboards.py` `CR_MODELS` | seat / dashboard | n | P5 — **do not edit** |
| `knowledge/model-catalog.json` | Claude catalog | n/a | **untouched** |
| `plugins/ai-coding-model-guidance/knowledge/cross-tool-model-lineup-2026.md` | vendor facts | n/a | P2 |
| `plugins/ai-coding-model-guidance/agents/{grok,codex}-model-strategist.md` + plugin `CLAUDE.md` | strategist defaults | n/a | P2 (A named; B silent — adopt A) |
| `docs/plans/2026-06-03-adaptive-run-classifier/plan.md` | frozen design | n/a | P6 — banner only |
| Gate 52 GOOD fixture `DISPATCH_TIER_MODEL` | fixture | n | P7 — lockstep if shape changes |
| Gate 121 seat-diversity fixtures | fixture / seat | n | P7 — **do not** feed Grok SKUs into Claude seat diversity |
| `eval-adaptive-classifier` fixtures | fixture | maybe | P7 — only if they assert SKU strings |

P0 greps `TIER_TO_SKU|TIER_MODEL|DISPATCH_TIER_MODEL|tier_model|GPT-5.5|Opus 4.6` and diffs against this table. New hits get classified; no product edit until the grep is clean or added here.

---

## 5. Phases + reconciled DAG

```
                    P0 preflight + G3b re-fetch + inventory grep
                                    │
                                    ▼
                    P1 machine map + resolveTier + module --self-test
                    /        |         \              \
                   /         |          \              \
         P2 knowledge    P3 runtimes    P5 seats      P6 frozen banner
         (lineup +       (lockstep      (no-flip)     (annotate only)
          adapter table   evaluate-dispatch
          + strategists)  ↔ rc-deep-research
                 \        ↔ thing-decide)
                  \              │
                   \             ▼
                    \        P4 FORGE aliases (needs P1 resolver; not all of P3)
                     \           /
                      \         /
                       ▼       ▼
                    P7 fixtures/gates (52 / 91 / 121 / 134 / 45) → versions + DoD
```

| | Detail |
|---|---|
| **Blocks** | 0 → 1. 1 → {2, 3, 4, 5, 6}. 3 → 7 (fixture lockstep). {2, 3, 4, 5, 6} → 7 versions. |
| **Parallel after P1** | **P2 ∥ P3 ∥ P5 ∥ P6.** P4 after P1 (resolver), **not** after full P3. |
| **Serial lock** | `evaluate-dispatch.js` ↔ `rc-deep-research.js` copy fence ↔ Gate 52 fixture — one PR slice. |
| **Critical path** | **0 → 1 → 3 → 7** (probes → map → host-switch runtimes → ship). |
| **Do not serialize** | Seats (5) and frozen banner (6) do not wait on the table. Version bumps only at P7. |
| **Not a fake dep** | P0 inventory grep is a pre-build gate, not a product file. Formal `inventory.md` in the run dir is optional. |

### P0 — Preflight (no product edits)

`depends_on_claims: [1, 2, 3, 4, 5, 6, 7, 8, 13, 14, 15, 16]`

1. `git -C .claude/worktrees/forge-model-tier-alignment branch --show-current` → `forge/model-tier-alignment`. Empty = detached HEAD → stop.
2. Re-run `grok models`. Allowed CLI ids = exactly `grok-4.6`, `grok-4.5`. Any other selectable CLI id → stop and amend G0.
3. Execute G3b URL probes 13–15. Stamp retrieval date. If falsified → last observed + `[verify-at-use]`, do not invent.
4. Confirm Claude catalog still claim 8. Do not migrate Opus 5.
5. Confirm probe 16 (`claude -p` + Claude seat ids). If false → stop.
6. Inventory grep vs §4. Classify extras.

**Acceptance:** worktree on reserved branch; probe stamps in the run dir; no product file touched.

### P1 — Shared `substrate-tier-map` + `resolveTier`

`depends_on_claims: [1, 3, 4, 5, 8, 13, 14, 15, 16]` · **Blocked by:** P0.

Add the JSON + Python loader + JS sibling (§3.1). Default host = `claude`. Seats not in this file.

**Pre-build:** `python3 -m json.tool` on the map. Layout: `plugins/*/knowledge/**` and `plugins/*/scripts/**` already allow both paths — **no `.repo-layout.json` glob**.

**Acceptance:**
- [ ] `--self-test` (py + js) PASS: 4 hosts × 3 tiers; Grok three SKUs are pairwise distinct; no `gpt-*-pro`; `resolveTier("grok","top")=="grok-4.6"` and never `claude-*`; `resolveTier(undefined,"top")=="claude-opus-4-8"`.
- [ ] No new `── Gate N:` in `audit-gates.sh`.

### P2 — Knowledge + strategists

`depends_on_claims: [2, 6, 7, 9, 13, 14, 15]` · **Blocked by:** P1 (table mirrors JSON). **Parallel with:** P3, P5, P6.

1. Adapter SKILL table: four host columns from §2; Grok three-SKU uniqueness one-liner; seats-are-not-this-column sentence; `last_reviewed` → 2026-08-14.
2. Dispatch-evaluator skill: re-date pointer (`2026-05-31` → `2026-08-14`); **zero** SKU rows of its own.
3. Lineup: `Last reviewed:` → 2026-08-14. Grok 4.6 = CLI/API flagship (`top`); 4.5 = selectable cheaper rung (`fast`+`balanced`); 4.3 / 4.1 Fast / 4.20 / `grok-build-0.1` = API or historical with `[verify-at-use]`. Codex three-rung Luna/Terra/Sol; GPT-5.5 / GPT-5.5-Pro = prior-generation (keep rows, mark superseded). Copilot: Opus 5 current Claude top; 2026-09-01 retirement table. Mermaid leaves that still say “GPT-5.5-Pro” / “Grok 4.3” as the *live* balanced/top default: retarget or class-label + table pointer. Every `$` / context row keeps date, link, or `verify` (Gate 45).
4. Strategists (A; B silent — adopt A):
   - `agents/grok-model-strategist.md` — default balanced = Grok 4.5; top = Grok 4.6; closed-world must not treat 4.5/4.6 as fictional. `description` ≤ 300 chars.
   - `agents/codex-model-strategist.md` — fast = Luna; balanced = Terra; top = Sol.
   - Plugin `CLAUDE.md` roster one-liners that still say “Grok 4.3 flagship” / “GPT-5.5-Pro”.

**Acceptance:**
- [ ] `python3 scripts/check-lineup-citations.py` exit 0.
- [ ] `python3 scripts/check-frontmatter.py` exit 0.
- [ ] Four-column adapter table; Grok `fast==balanced==grok-4.5`; `top==grok-4.6`.
- [ ] Grep live adapter/lineup *current* cells for `GPT-5.5-Pro`, Copilot `Opus 4.6` as `top`, third Grok CLI adapter SKU → 0 (historical/superseded rows OK).

### P3 — Runtime adapters (host switch, default Claude)

`depends_on_claims: [8, 10, 12, 16]` · **Blocked by:** P1. **Parallel with:** P2, P5, P6. **Serial with its own copy fence.**

1. `evaluate-dispatch.js` — `TIER_MODEL` → `resolveTier(host, tier)` (inlined generated map).
2. `rc-deep-research.js` — both `TIER_MODEL` and `DISPATCH_TIER_MODEL` + re-copy fence.
3. `thing-decide.py` `tier_model` — load JSON via the py helper; **default host=`claude`** (tribunal is `claude -p`). Do **not** change seat default models.

**Acceptance:**
- [ ] `resolveTier('claude','top')` → `claude-opus-4-8`.
- [ ] `resolveTier('grok','fast')` → `grok-4.5` (same as balanced).
- [ ] `resolveTier('codex','top')` → `gpt-5.6-sol`.
- [ ] Default/missing host never returns a non-Claude SKU.
- [ ] Comfort-posture seat model literals unchanged.
- [ ] Disabled dispatch path still byte-identical floor (Gate 52).

### P4 — FORGE `--models` host-aware aliases (three distinct Grok SKUs)

`depends_on_claims: [1, 3, 11]` · **Blocked by:** P1 (not full P3).

In `commands/forge.md` + `skills/forge-pipeline/SKILL.md`:

1. Aliases: `haiku`=`fast`, `sonnet`=`balanced`, `opus`=`top`; raw SKUs pass through.
2. Resolve each alias through `resolveTier(thisHost, alias)`. Host = the CLI `/forge` is running inside (orchestrator-known) or `RAVENCLAUDE_HOST`. Default `claude`.
3. **After resolve, if `A == B`:** **fail closed** (V3 amended). That means the map is wrong. Do not invent a SKU and do not waive divergence.
4. Spec pairs: Claude `A=opus,B=sonnet` → `claude-opus-4-8` vs `claude-sonnet-5`. Grok `A=opus,B=sonnet` → `grok-4.6` vs `grok-4.5`. Grok `A=sonnet,B=haiku` → `grok-4.5` vs `grok-build-0.1`.
5. `fable` unresolved / pass-through.
6. If this host’s `grok models` omits `grok-build-0.1`, say so in the run log and pin `A=grok-4.6,B=grok-4.5` for the two panels — do **not** rewrite the adapter map to collapse tiers.

**Acceptance:**
- [ ] Skill + command state the alias map, host default, and Grok three-SKU uniqueness.
- [ ] No `resolve-tier.py` as a new user-facing CLI; no new gate.
- [ ] A dry read of the skill pins `A=grok-4.6,B=grok-4.5` when only those two are CLI-selectable, while the map still names `grok-build-0.1` as `fast`.

### P5 — Thing seats: address claim 16; do not flip

`depends_on_claims: [12, 16]` · **Blocked by:** P0 probe 16. **Parallel with:** P1–P4.

**In-scope:** P2 already carries “seats are not the Grok column.” Optional one-line comment above `command_review.panel` in `templates/thing.yaml` and `templates/comfort-posture-balanced.yaml`.

**Do not edit SKU literals in:** `.ravenclaude/comfort-posture.yaml` `panel.*.model`; `scripts/generate-dashboards.py` `CR_MODELS`; `thing-decide.py` seat dispatch model; `model-catalog.json`; tribunal disposition logic.

**Acceptance:** `git diff` on seat-SKU literals is empty. No dashboard regen.

### P6 — Frozen-plan banner only

`depends_on_claims: [17]` · **Parallel with:** P1–P5.

Insert **only** this banner under the title of `docs/plans/2026-06-03-adaptive-run-classifier/plan.md`:

> **Frozen design record (2026-06-03).** Live adapter map: `plugins/ravenclaude-core/skills/adaptive-run-classifier/SKILL.md` § Substrate tier table and `plugins/ravenclaude-core/knowledge/substrate-tier-map.json`. Do not treat the SKUs in this file as current.

**Acceptance:** diff is the banner hunk only. No other file under that plan directory.

### P7 — Fixtures, gates, versions, DoD

`depends_on_claims: [2, 4, 6, 7]` · **Blocked by:** P2–P6.

**Fixtures / gates (B awareness — required because runtime shape changes):**
- Update Gate 52 GOOD fixture `DISPATCH_TIER_MODEL` if the object is now host-keyed; disabled floor stays byte-identical.
- Gate 91 (`test-gate91-tribunal-shadow.py`) — shadow still Claude under default host.
- Gate 121 — keep Claude seat-diversity semantics; **do not** collapse Grok `fast`+`balanced` into panel diversity.
- Gate 134 — still Claude-only on `model-catalog.json`; new multi-host ids must not appear as stray `claude-*` in governed files. Prefer shared import over new carves.
- Gate 45 — lineup citations still clean.
- `eval-adaptive-classifier` self-test only if fixtures assert SKU strings.
- Module `--self-test` (not a new gate number).

**Versions (V7, live-confirmed):**

| Plugin | Live | Bump | Why |
|---|---|---|---|
| `ravenclaude-core` | `0.255.0` | **`0.256.0`** | Map + resolver + adapter table + FORGE prose |
| `ai-coding-model-guidance` | `0.3.13` | **`0.3.14`** | Lineup + strategist defaults |

Lockstep each `plugin.json` **and** `.claude-plugin/marketplace.json`. Guidance `CHANGELOG.md` new top entry `[0.3.14] — 2026-08-14`. Do **not** create a core CHANGELOG for symmetry.

`python3 scripts/generate-copilot-plugin.py --check`; regen only if that check fails on the skill edit. No skill/agent **count** change → no `reference/regen-discipline.md` load. No `generate-dashboards.py` edit → no dashboard regen.

---

## 6. Risk matrix (from gap-delta; no G4a/G5 at quick)

| ID | Risk | Sev | Mitigation |
|---|---|---|---|
| FM-1 | Host-unaware `TIER_*` feeds Claude ids to Grok/Codex | HIGH | V1: `resolveTier`; default `claude`; acceptance never returns `claude-*` for `host=grok` |
| FM-2 | Seats flipped to Grok; Claude tribunal breaks | HIGH | V4 / P5 empty-diff on seat literals; map `notes.seats` |
| FM-3 | Copilot `Auto` as non-reproducible balanced SKU | MED | V5: Sonnet 5 primary; Auto footnote |
| FM-4 | `gpt-5.6-pro` / leftover `GPT-5.5-Pro` as live `top` | MED | P1 self-test forbids `*-pro` slugs; P2/P7 grep |
| FM-5 | New Gate 134b / Claude-only catalog scope creep | MED | V2: reuse 45+134; multi-host lives in sibling JSON; self-test in module |
| FM-6 | Gate 52 / 121 / copy-fence drift after shape change | HIGH | Serial lock P3↔P7; 121 must not ingest Grok SKUs |
| FM-7 | FORGE `A == B` after resolve | HIGH | V3 amended: fail closed. Three Grok SKUs must stay distinct |
| FM-8 | Version / marketplace drift | MED | P7 exact pins + `json.tool` + parity check |
| FM-9 | Vendor page moved since G1 (2026-08-14) | MED | P0 probes; falsify → last observed + `[verify-at-use]` |
| FM-10 | Strategist `description` > 300 chars | LOW | `check-frontmatter.py` |
| FM-11 | Workflows without host context | MED | Default `claude` + document `RAVENCLAUDE_HOST` |
| FM-12 | Someone “fixes” Claude catalog to Opus 5 while here | MED | P0/P5: catalog untouched; separate parked proposal |
| FM-13 | Layout deny on new map/loader | LOW | Paths already match `plugins/*/knowledge/**` and `plugins/*/scripts/**` — confirm, do not add a glob unless a path changes |
| FM-14 | Prettier/ruff on JS/py shape change | LOW | Whole-tree `prettier --write` then `--check`; `ruff check .` |

---

## 7. Definition of done

**G0 success signal, mechanically:**

1. Machine map exists; Grok three SKUs are pairwise distinct (`--self-test`, not a new gate).
2. Adapter SKILL table names Claude + Codex/API + Copilot + Grok for `fast`/`balanced`/`top`, dated, `[verify-at-use]`; mirrors the JSON.
3. Lineup re-dated; strategists no longer default to Grok 4.3 / GPT-5.5-Pro as *current*.
4. Runtime maps host-switch via `resolveTier`; **default host=`claude`**. `evaluate-dispatch.js`, `rc-deep-research.js`, `thing-decide.py` never send `grok-*` to `claude -p` unless host is explicitly grok.
5. FORGE `--models` aliases resolve through the host column; Grok `haiku`/`sonnet`/`opus` are three different SKUs.
6. Comfort-posture / dashboard / `thing.yaml` seat ids unchanged (claim 16 addressed, not flipped).
7. Frozen plan has a banner only.
8. **Versions:** core `0.255.0`→`0.256.0`, guidance `0.3.13`→`0.3.14`, marketplace lockstep.
9. **Layout:** no new `.repo-layout.json` glob (confirm every added path matches an existing allow). If a path is added outside `plugins/*/knowledge/**` or `plugins/*/scripts/**`, update `allowed_globs` **before** push.
10. **Gates / lint:**
    - `python3 -m json.tool` on both plugin manifests + marketplace.json + `substrate-tier-map.json`
    - Marketplace `version` == plugin `version` for both plugins
    - `python3 scripts/check-lineup-citations.py` (Gate 45) exit 0
    - `python3 scripts/check-model-ids.py` (Gate 134) exit 0
    - `python3 scripts/check-frontmatter.py` exit 0
    - Gate 52 PASS (real workflow + good/bad fixtures)
    - Gate 91 PASS (shadow still Claude at default host)
    - Gate 121 PASS (no Grok SKUs in Claude seat diversity)
    - Module `--self-test` PASS
    - `npx --yes prettier@3.9.4 --write .` then `--check .` exit 0
    - `ruff check .` exit 0
    - `scripts/audit-gates.sh` — **no new gate header**; existing gates still registered
    - `python3 scripts/generate-copilot-plugin.py --check` (regen only on fail)
11. Grep of in-scope shipped live maps: `GPT-5.5-Pro` as adapter-`top`, Copilot `Opus 4.6` as adapter-`top`, missing Grok column, third Grok CLI adapter SKU → 0.

---

## 8. Out of scope (restated so impl does not grow)

- Implementing this plan in the G6 artifact (impl is a later lane).
- Ultraplan handoff.
- Consumer ChatGPT picker column (Auto / Thinking / app display names).
- Third Grok CLI SKU (`grok-build`, `grok-4.1 Fast`, …).
- Thing tribunal disposition / vote math; host-aware seat map.
- Claude-host Opus 5 catalog bump / Gate 134 rewrite.
- New audit-gate number (including 134b).
- Rewrite of `docs/plans/2026-06-03-adaptive-run-classifier/plan.md` body.

---

## 9. Confidence

**0.86.** Truth table (SKU rows) is high-agreement and G3b-settled. Runtime host-switch is bound (V1) with a safe `claude` default. Residual: vendor pages can move between this plan and P0 (mitigated: last-observed + `[verify-at-use]`); workflow JS cannot `require()` the sibling module (mitigated: generated inline + copy fence + Gate 52).
