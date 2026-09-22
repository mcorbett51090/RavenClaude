# Repository review — 2026-09-22

Autonomous, multi-panel review of the RavenClaude marketplace. Scope: the full
working tree (**184 plugins**, ~10k files, the `scripts/` gate suite, CI workflows,
boundary docs), with a focused correctness pass over the logic-heavy code most
likely to harbour an un-gated defect.

Method mirrors the requested three-panel structure. Ground truth for repo health
is the repo's own gate corpus (the highest-signal detector in a repo this
self-validating), not an LLM opinion — so the panels ran _on top of_ the real
gates rather than instead of them. Every conclusion is grounded in a this-session
check, cited inline.

> **Provenance note.** This sweep was first executed against a checkout that was
> ~3 weeks / 146 commits behind `origin/main`. On discovering the staleness
> (`git merge-base` showed the local base was an ancestor of the real main tip
> `76925beb`, #1235 — itself a "three tooling fixes from the 2026-09-22
> three-panel review" commit), the work was **reset onto the real `origin/main`
> and every finding re-verified there** before anything was committed. The two
> code findings below were confirmed still-present on real main; the count fix's
> value was recomputed for the real plugin count (183, not the 181 the stale tree
> implied). This is the checkout-freshness discipline the repo's own `AGENTS.md`
> mandates — a fix already merged upstream can otherwise look "not done" locally.

## Headline

**The repository is in excellent health.** Every surface gate and the whole-repo
meta-test pass on the real-main tree:

| Check | Result (this session, on `origin/main`) |
|---|---|
| `python3 -m json.tool` on all manifests + `.repo-layout.json` | ✅ valid |
| `bash -n plugins/*/hooks/*.sh scripts/*.sh` + hook executability | ✅ clean |
| `scripts/sync-plugin-versions.py --check` (184 manifests) | ✅ in sync |
| `scripts/check-frontmatter.py` (600+ agents/skills) | ✅ OK |
| `scripts/concepts.py --check` (97 concepts) | ✅ 0 covers drift, 0 calendar warnings |
| `ruff check` (changed files) | ✅ clean |
| `npx prettier@3.9.4 --check .` (whole tree) | ✅ exit 0 |
| `scripts/audit-gates.sh` (per-gate teeth meta-test) | ✅ exit 0 |
| broken-link scan across boundary docs | ✅ 0 broken |

**No P0 or P1 issues.** Three genuine issues were found and **fixed in the
accompanying PR** (1× P2 correctness, 1× P3 correctness, 1× P3 doc drift). Two
items are judgment calls left for review — see the companion decision doc,
[`docs/2026-09-22-repo-review-design-questions.md`](../2026-09-22-repo-review-design-questions.md).

## Panel 1 — expert scan & categorization

Highest-signal detectors first (the gate corpus, all green), then a targeted
correctness review of the logic-heavy Python, then a gate-invisible drift sweep
(stale counts, dead references, broken links).

The correctness review was dispatched to two independent expert-reviewer panels
over the two highest-risk code clusters, each held to a strict bar (report only a
concrete input→wrong-output/crash with a file:line; verify by reading; prefer
fewer, high-confidence findings):

- **Cluster A — core runtime scripts** (`precompact-digest.py`,
  `thing-denial-kb.py`, `stall_watch.py`, `reset-plugin-cache.py`,
  `sanitize-webfetch-body.py`): **no confirmed P0–P2**. Verified by compile-check,
  the shipped `--self-test`, and behavioral probing of the security-sensitive
  sanitizer (nested-decoy, unterminated-block, and legit-fence inputs all strip
  correctly and never fail open). One P3 trade-off surfaced for visibility
  (sanitizer over-stripping) — routed to the decision doc, not fixed.
- **Cluster B — repo-review + refine-to-rubric pipeline** (`review_cache.py`,
  `findings_merge.py`, `check-dom-budget.py`, `converge.py`, `loop.py`): **two
  confirmed findings** (F-1, F-2 below), each reproduced against the real code.

| # | Finding | Pri |
|---|---|---|
| F-1 | `converge.py` maps a wrong-typed judge field (a list where a dict/null is expected → `AttributeError`) to exit 1 ("continue"), not the intended exit 2 ("contract error"), so a malformed verdict is silently misread. | **P2** |
| F-2 | `review_cache.py batch-status` doesn't catch the `_validate_rel_path` `ValueError` its `lookup`/`store` siblings do → uncaught traceback (exit 1) on a `..`/absolute path instead of the contract error (exit 2). | **P3** |
| F-3 | `marketplace.json` headline description says "180 domain plugins"; the tree has 184 plugins, exactly one of which (`ravenclaude-core`) is non-domain → **183** domain plugins. No gate validates this integer. | **P3** |

## Panel 2 — analysis (priority validation, impact & effort)

- **F-1 (P2, confirmed).** _Impact:_ the refine-to-rubric convergence loop is a
  gate/shell caller of `converge.py`; exit 1 is its documented "keep iterating"
  signal (`converge.py:33-35`). A judge that emits a schema-permitted-but-wrong-
  typed `hard_gates`/`scores` (a list) turns a contract error into a false
  "continue" — the loop proceeds on a verdict it should have rejected. The
  existing `or {}`/`or []` null-guards were written for exactly this "weird judge
  output" class but only cover `null`, not a wrong container type. _Effort:_ one
  token (add `AttributeError` to the existing `except` tuple). _Kept P2:_ it
  silently mis-routes control flow; not P1 because it needs a malformed judge
  payload to trigger.
- **F-2 (P3, confirmed).** _Impact:_ robustness/consistency only — the `--files`
  list is pipeline-enumerated and won't contain `..` in normal operation, and the
  crash is order-dependent (a hostile path only reaches `_validate_rel_path`
  before a cache miss short-circuits the loop). But a crash-with-traceback vs. a
  clean exit-2 is a real behavior gap vs. the sibling branches. _Effort:_ 8 lines,
  mirrors the existing pattern.
- **F-3 (P3, confirmed).** _Impact:_ cosmetic/marketing accuracy of the catalog
  description; no functional effect. _Effort:_ one integer. This is the **third**
  recurrence of un-gated count drift in this field (144 fixed 2026-08-31 → 180
  set when the total was ~180 → now stale at 180 while the real count is 183) —
  see the decision doc for a proposed gate.

## Panel 3 — tie-breaking

No priority was ambiguous enough to need a tie-breaker. The one candidate for
disagreement — whether the sanitizer over-stripping (Cluster A's P3) is a "bug"
or a "documented trade-off" — was resolved as **neither a P-graded bug nor an
autonomous fix**: it is a deliberate, documented security-over-availability
posture (`prefer the floor / accept over-stripping`, stated in the file's own
comments and in force across patterns 1–5), so changing it is a design decision,
not a defect fix. Routed to the decision doc.

## Implementation (this PR)

Sorted P0 → P3; all three confirmed findings needed no design input and are
fixed:

| Pri | Fix | File(s) | Verified on real main |
|---|---|---|---|
| P2 | Add `AttributeError` to `converge.py`'s contract-error guard (F-1). | `plugins/ravenclaude-core/skills/refine-to-rubric/scripts/converge.py` | Reproduced: wrong-typed `hard_gates` → exit **2** (was exit 1); well-formed dict input still → exit 1. |
| P3 | Wrap `batch-status`'s `batch_status(...)` in the same `try/except ValueError → exit 2` as `lookup`/`store` (F-2). | `plugins/ravenclaude-core/skills/repo-review/scripts/review_cache.py` | Reproduced: `--files ../../etc/passwd` → clean `error:` + exit **2** (was traceback exit 1); `self-test` still passes. |
| P3 | Correct the catalog description count 180 → 183 domain plugins (F-3). | `.claude-plugin/marketplace.json` | 184 plugins; exactly `ravenclaude-core` lacks `requires.plugins` → 183 domain (script-counted). |

Version discipline: `ravenclaude-core` bumped `0.324.7 → 0.324.8`, catalog version
re-derived via `sync-plugin-versions.py`, Copilot package regenerated, CHANGELOG
top entry added, and the two concept `covers_digest`s cosmetically restamped (the
edits are orthogonal to both concepts' claims, so `last_verified` was **not**
advanced — no false freshness bought). All post-change gates re-run green.

## Items NOT changed (verified intentional)

- The sanitizer over-stripping trade-off (`sanitize-webfetch-body.py:119`) — a
  deliberate, documented security posture. See the decision doc.
