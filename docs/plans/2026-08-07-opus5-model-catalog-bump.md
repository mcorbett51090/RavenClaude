# Proposal — bump the canonical model catalog's Opus tier to Opus 5

**Status:** proposal for maintainer review · **Prepared by:** scheduled plugin-news-research routine, 2026-08-07 · **Vehicle:** draft PR (this doc only; no governed code changed)

> **Why this is a proposal and not an applied change.** The change is coupled by the model-ID drift
> gate (Gate 134) to editing the command-review tribunal's own seat-model files
> (`…/hooks/thing-orchestrator.sh`, `…/scripts/thing-decision.py`). Those files are protected by the
> tribunal's `xc.tribunal-self-disable` security floor, which denied every automated edit (and even
> read-only shell commands that merely named the substrate paths) — **correctly**, and independent of
> `command_review.enabled: false`. Per the repo's own rule, a security-floor deny is obeyed, never
> bypassed. Changing the tribunal's reviewer models is a human-authority action, so this run assembled
> the complete, reviewed change for you to apply deliberately rather than routing around the guard.

---

## 1. The finding

`plugins/ravenclaude-core/knowledge/model-catalog.json` — the single source of truth for the Claude
model IDs used by tribunal seats, the dashboard, and templates (enforced repo-wide by Gate 134) —
currently reads:

```json
"current": { "opus": "claude-opus-4-8", "sonnet": "claude-sonnet-5",
             "haiku": "claude-haiku-4-5-20251001", "fable": "claude-fable-5" },
"stale":   ["claude-opus-4-7", "claude-sonnet-4-6", "claude-haiku-4-5"]
```

**Opus is the one tier still on the 4.x generation.** Sonnet and Fable are already on the Claude 5
generation; Opus 5 (`claude-opus-5`) is now the newest Opus. The catalog's last touch was v0.205.0
(2026-07-16), and Opus 5 shipped shortly after — this is migration lag, not a documented deliberate
hold (no in-catalog marker pins Opus to 4.8). The catalog's own comment documents this exact procedure:
*"Update `current` when a model is superseded; move the retired id into `stale`."*

### Grounding (per Claim-Grounding, persisted here rather than only in chat)
- **`claude-opus-5` as the current newest Opus id** is grounded in this session's own system prompt
  (first-party, harness-provided): *"The most recent Claude models are the Claude 5 family and Haiku 4.5.
  Model IDs — Fable 5: 'claude-fable-5', Opus 5: 'claude-opus-5', Sonnet 5: 'claude-sonnet-5',
  Haiku 4.5: 'claude-haiku-4-5-20251001'."* This is the same first-party provenance the catalog's
  existing `claude-sonnet-5` / `claude-fable-5` entries rest on. Web search corroborates a 2026 GA.
- The **bare token** `claude-opus-5` (no dated suffix) is the correct form — it matches how
  `claude-sonnet-5` and `claude-fable-5` are stored (only `haiku` carries a dated suffix).
- The **exact GA date** seen in web results (2026-07-24) is `[unverified — web/SEO source]` and is
  deliberately **not** asserted as fact anywhere durable.

---

## 2. Expert-panel review (task-mandated two-panel process)

### Panel 1 — Usefulness (3 independent seats): majority **USEFUL**
| Lens | Verdict | Note |
|---|---|---|
| accuracy/grounding | not_useful (0.7) | **Dissent — vantage-limited.** The seat's *own* sub-agent system prompt lacks the orchestrator's environment block, so it read the grounding as fabricated. The orchestrator session's system prompt does list `Opus 5: 'claude-opus-5'`. |
| cost/operations | useful (0.63) | Real migration lag; draft-PR-for-human is the correct vehicle; never auto-merge. |
| accuracy (2nd) | useful (0.72) | `claude-opus-5` well-grounded; bare token correct; drop the SEO date; treat "retire 4.8" carefully. |

### Panel 2 — Detailed review (3 seats): unanimous **approve_with_changes**
| Lens | Verdict | Load-bearing requirement |
|---|---|---|
| code-review | approve_with_changes (0.9) | The 9-file/21-ref sweep is complete & correct. **CI-blocking gap the plan first missed:** `scripts/check-model-ids.py`'s `--self-test` `good` fixture hardcodes `claude-opus-4-8` and must be updated too (Gate 134 runs `--self-test`). |
| security | approve_with_changes (0.82) | Pure id-swap; deterministic security floor untouched; model-diversity invariant holds; **fail-safe** (an uncallable id never yields a silent ALLOW — abstain → per-category posture). **Gate merge on callability** (below). |
| architect | approve_with_changes (0.8) | Correct atomic unit (the gate forces catalog+refs together). Bumps only the `current.opus` **pointer**; must **not** touch the *carved* reasoning "top" tier. Persist grounding inline; regen dashboards; bump both manifests. |

Panels 1 and 2 **agree** (useful + approve) → no third-panel tiebreak was required.

---

## 3. The change to apply (exact, file-by-file)

Run `python3 scripts/check-model-ids.py` after step B as the authoritative check — it will flag any
missed governed reference.

**A. `plugins/ravenclaude-core/knowledge/model-catalog.json`**
- `current.opus`: `"claude-opus-4-8"` → `"claude-opus-5"`
- `stale`: append `"claude-opus-4-8"` → `["claude-opus-4-7","claude-sonnet-4-6","claude-haiku-4-5","claude-opus-4-8"]`

**B. Sweep `claude-opus-4-8` → `claude-opus-5` in the 9 governed files (~21 refs):**

| File | Refs | Note |
|---|---|---|
| `.claude/settings.json` | 1 | this repo's own posture seed |
| `.ravenclaude/comfort-posture.yaml` | 2 | this repo's own tribunal seat config |
| `plugins/ravenclaude-core/dashboard-schema.json` | 2 | Forseti + Thor seat models (hand-maintained source; edit **before** regen) |
| `plugins/ravenclaude-core/hooks/thing-orchestrator.sh` | 1 | Thor default fallback, line ~650 — **⚠ tribunal substrate (guard-protected; see §4)** |
| `plugins/ravenclaude-core/scripts/thing-decision.py` | 3 | Forseti + Thor `_DEFAULT_PANEL` + `_DIVERSITY_PREF` — **⚠ tribunal substrate (guard-protected; see §4)** |
| `plugins/ravenclaude-core/templates/comfort-posture-balanced.yaml` | 1 | new-repo seed |
| `plugins/ravenclaude-core/templates/thing.yaml` | 2 | seat-config template |
| `scripts/capture-run-context.py` | 3 | 1 docstring + 2 `--check` self-test (sweep all 3 together — keeps the self-test valid) |
| `scripts/generate-dashboards.py` | 6 | dropdown choice + 2 seat-meta + 2 JS-state defaults + `CR_MODELS`; **also** change the dropdown label `"Opus 4.8 — most capable"` → `"Opus 5 — most capable"` |

**C. `scripts/check-model-ids.py` self-test** (carved from the scan but the self-test still runs — Gate 134 CI-blocking): in the `good` fixture (line ~83) change `claude-opus-4-8` → `claude-opus-5`; recommended: add `claude-opus-4-8` to the `bad` fixture (line ~81) so the newly-staled token gets a positive-detection test.

**D. Regenerate the freshness-gated dashboards** (each embeds the id 6×):
`python3 scripts/generate-dashboards.py --plugin ravenclaude-core --stdout > plugins/ravenclaude-core/dashboard.html` and `python3 scripts/generate-index-dashboard.py -o index.html`.

**E. Version + changelog:** bump `ravenclaude-core` 0.238.0 → 0.239.0 in **both** `plugins/ravenclaude-core/.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`; add a `CHANGELOG.md` entry.

**F. Verify:** `python3 scripts/check-model-ids.py` (+ `--self-test`) · `npx --yes prettier@3.9.4 --check .` · `ruff check .` · the dashboard freshness gates · `scripts/audit-gates.sh` (Gate 134 at minimum).

### Out of scope (deliberately not changed)
- **The carved routing-quality "top" reasoning tier** (`plugins/ravenclaude-core/scripts/thing-decide.py`
  and `adaptive-run-classifier`) keeps `claude-opus-4-8` as the cost-sane reasoning default *by design*
  (it is carved out of Gate 134). This proposal bumps only the `current.opus` **pointer** for
  seats/dashboards/templates. **Please confirm you want that split preserved** (newest-id pointer vs.
  cost-default reasoning tier).
- Knowledge/skill `.md` prose citing Opus-4.8-specific behavior is model-specific, not gate-governed —
  out of scope. (Minor follow-up: `adaptive-run-classifier/SKILL.md:83` labels `opus-4-8` "current".)

---

## 4. Merge gates the panels require (do these before merging)

1. **Verify `claude-opus-5` is callable in the seat environment.** The tribunal's security seat (Forseti)
   and tie-breaker (Thor) run via `claude -p --model claude-opus-5`. If that id does **not** resolve on
   your machines, those seats error → **abstain → fail-closed** (deny on high-stakes categories / ask on
   readonly). That is **fail-safe** (never a silent ALLOW) but it (a) can brick tribunal usability — the
   v0.60.0 abstain-lockout shape — and (b) silently thins the LLM security lens on 2-vote mutate panels
   (one abstain does not trip the `n_abstain ≥ 2` gate). **Pick one:**
   - paste the output of a `claude -p --model claude-opus-5 'ping'` probe run in the seat environment, **or**
   - enable `model_fallback` with a ladder that keeps a known-callable id as a rung (the fallback
     classifier treats `model_not_found` as *skip*, so an uncallable opus-5 degrades gracefully instead
     of abstaining). Keeping `claude-opus-4-8` as a rung is the clean mitigation.
2. **Confirm the pointer-vs-carved-tier split** (§3, "Out of scope").
3. **Apply the two guard-protected substrate edits yourself** (the `thing-orchestrator.sh` + `thing-decision.py` refs in §3.B) — they cannot be made by an automated agent because of the self-disable floor.

**Rollback:** revert the `current.opus` entry in `model-catalog.json` (and the coupled refs); the change is a pure model-id string swap with no logic change, fully reversible.

---

## 5. Also researched — NOT incorporated (insufficient this-session grounding)

Web search surfaced further 2026 Anthropic platform developments that *may* warrant knowledge-file
updates in `plugins/claude-app-engineering/`, but they came from SEO-style summaries, not authoritative
docs — and writing unverified platform facts into durable knowledge files violates Claim Grounding. They
are listed here for you to verify against primary sources and incorporate deliberately, if real:

- A managed **agent runtime** on the API (`/v1/agents`, `/v1/sessions`, `/v1/environments`; stateful cloud sessions billed on session-hours).
- **Context-editing / memory** beta headers (e.g. an `agent-memory-2026-07-22` beta making memory listing order stable).
- **Server-side compaction** for long conversations (`compact-2026-01-12` beta header).
- An **MCP protocol** update dated `2026-07-28` (stateless core, standardized extensions, hardened auth).

All `[unverified — web/SEO source]`; verify before acting.
