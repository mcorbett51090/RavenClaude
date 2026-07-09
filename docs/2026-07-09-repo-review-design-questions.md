# Repo review — decisions needed (2026-07-09)

Autonomous 3-panel repo review (expert finders → analysis/validation → tie-break),
run over the executable-code surface (~190 Python files, 179 shell scripts). The
repo passed every mechanical CI gate going in (JSON, shell `-n`, python compile,
ruff, prettier, no version drift, frontmatter), so the panels hunted for what the
gates can't catch. **23 findings survived validation: 1 P0, 2 P1, 6 P2, 14 P3;
0 rejected.** 21 were mechanical and are implemented in the accompanying PR. This
doc holds the **3 findings that need a decision from Matt** before they can land.

## What was implemented in the PR (no decision needed)

| Pri | Fix | File(s) |
|---|---|---|
| **P0** | **Guard bypass** — `git -p …` / `git -P …` (the real short globals `--paginate`/`--no-pager`, absent from the strip's curated allow-list) let any git subcommand dodge **every** git deny (force-push, `reset --hard`, `branch -D`, `clean -f`). Strip is now tolerant of any dash-prefixed global while still consuming separate-token values (`-c key=val`). Empirically reproduced + regression fixtures added. | `hooks/guard-destructive.sh`, `scripts/audit-gates.sh` |
| P1 | Stream classifier's suggestion/auto-switch surfaced a raw registry **key** into the always-injected SessionStart banner with no slug/frame-break validation — a repo-planted `registry.json` key could inject out-of-frame instructions into trusted context. Now validated (`_SLUG_OK` + membership) exactly like the active pointer. | `scripts/capability-orientation.py` |
| P1 | Consolidation silently rolled up entities from **different fiscal periods** when the group config omitted `fiscal_period` (the period guard was skipped, and a mixed-period roll-up still balances to 0.00). Now fails closed: derive the period from the first entity and assert every entity matches. | `plugins/finance/scripts/consolidate.py` |
| P2 | Tribunal self-disable could be evaded by a >4 KiB `MultiEdit` to `comfort-posture.yaml` that pushes the disabling text past the `\A`-anchored 4000-char `screen_always` window. `_posture_write_disables` now **reconstructs** the post-edit document (on-disk file + edits) and screens it; unreconstructable → DENY. | `scripts/thing-decision.py` |
| P2 | `guard-web-access.sh` + `mark-web-domain-seen.sh` built `runs/$sess/…` paths from an **unsanitized** session id, skipping the PR #363 `.`/`..` traversal hardening — a write primitive (`mkdir`/`touch`) outside the sandbox. Factored `_ee_sanitize_session()` into `_emit-event.sh`; both hooks route through it. | `hooks/_emit-event.sh`, `hooks/guard-web-access.sh`, `hooks/mark-web-domain-seen.sh` |
| P2 | NetSuite connector staged the TB from a **second, independent** SuiteQL pull while the watermark hash was computed from the first — so the pinned `source_tb_sha256` described data that was never staged (silently defeats drift detection). Now one pull backs both. | `plugins/finance/scripts/connectors/netsuite_connect.py` |
| P2 | Dataverse `query_solution_flows` had no `@odata.nextLink` pagination — >5000-flow environments silently dropped flows (verify even returned OK). Now follows nextLink to exhaustion via the same guarded opener. | `plugins/power-platform/skills/managed-solution-import/managed_import.py` |
| P3 | 11 lower-risk robustness fixes: `stream-ops.py` event `stream_id` desync; `oauth_client.py` (TransportTimeout classification, M2M 429/5xx backoff parity, corrupted-store diagnostics); `consolidate.py`/`remeasure.py` KeyError→BLOCKED; `statement_engine.py`/`recon_match.py` bare-`assert`→`SystemExit` (survives `-O`) + prior-TB balance check; `generate-bi-report.py` + `thing-golden-eval.py` KeyError guards; `worktree-new/clean.sh` `.`/`..` slug reject; `pbir-layout-engine/lint.py` + `pbir-ref-integrity/check_refs.py` `abspath`→`realpath` symlink escape; `declarative-visualization/lint.py` Vega `signals[].on[].update` expression coverage. | (see PR diff) |

---

## Decision 1 (the big one) — `check-hook-stdin-fallback.py` is case-sensitive, so 45 advisory hooks are silently inert

**Finding (P2, verified this session).** `scripts/check-hook-stdin-fallback.py:29` compiles
`_ARG_PATH` **without `re.IGNORECASE`** and only lists lowercase `file|path|target`, so it
matches `file="${1:-}"` but not `FILE="${1:-}"`. **45 shipped advisory anti-pattern hooks**
use the uppercase `FILE="${1:-}"` idiom and **all 45 lack a `tool_input.file_path` stdin
fallback** — verified this session (`grep` count = 45; 45/45 inert). Because `$CLAUDE_TOOL_FILE_PATH`
is not a real Claude Code hook variable, these hooks receive an empty path under Claude Code and
**silently no-op** — none of their advertised secret/CORS/auth/SQL/IAM file checks ever inspect a
written file. The gate whose sole job is to catch exactly this class **passes today** because of
the case blind spot.

- **Impact:** advisory only (these hooks print to stderr, never block), so no gate breaks and no
  security floor is bypassed — but every one of those domain plugins' in-editor anti-pattern
  assistance is inert.
- **The checker fix is one line** (`re.IGNORECASE`). **But applying it turns CI red** until all 45
  hooks get the stdin-JSON fallback — and fixing 45 hooks means, per the repo's "bump semver on
  every user-visible change" rule, **45 `plugin.json` bumps + 45 matching `marketplace.json`
  bumps** (CI hard-fails on version drift). That is a **~135-file, 45-plugin consumer-facing
  release** — every one of those plugins ships an update on the next `/plugin marketplace update`.

**Why this wasn't auto-applied:** it is the exact high-blast release the repo's own discipline
routes to a human — and a direct parallel to the prior review's "Decision 1" (the 66-domain-hook
version, documented on 2026-07-08 and then implemented in #580). Applying only the checker fix
would break the build; applying the full remediation unattended is a 45-plugin release event.

**Recommendation.** Approve the full remediation as its own dedicated PR: add `re.IGNORECASE`
(+ allow leading `local`/`declare`/`readonly` prefixes) to the checker, add the stdin-JSON
`.tool_input.file_path` fallback to all 45 hooks (the same block already proven in
`guard-destructive.sh` / the core file hooks), and bump the 45 plugins together. It's mechanical
and identical per hook — it just needs the "ship 45 plugin updates at once" go-ahead.

**The 45 affected plugins:** run
`grep -lE 'FILE="\$\{1:-\}"' plugins/*/hooks/*.sh` for the current list (all under
`plugins/*/hooks/flag-*-antipatterns.sh` / `check-*-anti-patterns.sh`).

---

## Decision 2 — `statement_engine.py`: wire `cf_category`/`noncash`, or drop them?

**Finding (P2, `needs_design`).** `load_mapping()` parses `cf_category` (operating/investing/
financing) and `noncash` from the COA CSV, `author-coa-mapping/SKILL.md` documents both as
meaningful controller-set fields, and `netsuite_coa_draft.py` even auto-generates `cf_category` —
but `build_cashflow_draft()` **never reads either**. It derives the op/inv/fin split purely from
current-vs-non-current BS-section deltas, so tagging an account `noncash=true` or
`cf_category='investing'` produces a **byte-identical** cash-flow draft. The documented knob
silently does nothing. (Impact is bounded: the CF is loudly labeled `unaudited_draft` /
not-GAAP-derivable-from-a-TB.)

**The decision (genuinely two-way):**
- **(a) Wire them in** — add non-cash IS items back to operating; let `cf_category` override a
  line's bucket. Makes the documented contract real, but adds a code path to a draft the module
  already disclaims as non-authoritative.
- **(b) Remove them** — delete the columns from `load_mapping`, the SKILL doc, and
  `netsuite_coa_draft` so the contract matches actual behavior. Simpler; concedes the fields were
  aspirational.

**Recommendation:** lean **(b) remove** unless you intend the CF draft to become a real
controller-facing artifact — the fields imply a precision the draft explicitly disclaims. Your
call on the product direction.

---

## Decision 3 — `refine-to-rubric/evaluate.py`: support judge-graded hard gates, or reject them?

**Finding (P3, `needs_design`).** A rubric dimension that combines `hard_gate=true` with a
judge-only (empty `objective_signal`) is parsed but **never enforced** — `evaluate.py` routes an
empty-signal dim to `judge_dims` and never writes `hard_gates[did]`, so `converge.terminate`
never blocks on it. **No shipped rubric hits this** (the library convention keeps judge dims
`hard_gate=no`, and the design treats judge hard-gates as a category error), so it's a latent
validation gap reachable only by a future custom rubric, not a live defect.

**The decision:**
- **(a) Support judge hard-gates** — plumb a `hard_gates` dict out of `judge_fn`. Larger, and it
  contradicts the design's "objective gates are deterministic" invariant.
- **(b) Reject/warn at authoring** — have `derive_rubric.py` reject or warn on a row that combines
  `hard_gate=true` with an empty `objective_signal`, so the unsupported shape can't silently go
  unenforced.

**Recommendation:** **(b)** — it matches the design's stated intent (judge scorecards are never
objective tripwires) and is the smaller change. A one-line reject in the rubric parser closes the
gap without touching the convergence engine. Approve and it can ship in a follow-up.

---

_Generated by the autonomous 3-panel repo-review routine, 2026-07-09. The mechanical fixes are in
the accompanying PR; these three await Matt's call._
