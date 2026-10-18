# Autonomous repo review — 2026-09-28

A scheduled multi-panel repository review ran on branch `claude/awesome-wright-jh8fgh`.

**Structure.** Panel 1 = a deterministic baseline (the repo's own gates/lint, so findings are
reproducible, not speculative) **plus** six independent expert-review agents (Sonnet tier — the
"lighter model for categorization" per the routine's model-assignment directive) across
non-overlapping, risk-sampled slices: tribunal/guard hooks, dashboard servers, generators,
the `/repo-review` engine scripts, the newest v0.32x code (routine-reserve etc.), and CI
workflows. The orchestrator (Opus) served as Panel 2 (priority validation, impact/effort) and
Panel 3 (tie-breaking). Confirmed, low-risk fixes that touch **only root `scripts/`** (no plugin,
no substrate) were applied and validated directly; everything that touches tribunal substrate,
needs a design decision, rests on documented behavior, or would trigger the plugin
version-bump + `generate-copilot-plugin.py` regen cascade is recorded below as **design-input**.

**No P0 surfaced.** The deterministic floor is fully green (JSON 186 files, shell syntax 327
scripts, ruff, prettier, and macOS/BSD portability — no real `grep -P`/`sed -i`/`declare -A`).
The tribunal core (`thing-orchestrator.sh`, `thing-decision.py`, `thing-decide.py`,
`thing-seat.sh`, `thing-concerns.py`) is confirmed extremely hardened — fail-closed discipline
intact under manual trace, and 20K-token adversarial ReDoS inputs to `classify()` completed
in <200ms with no catastrophic backtracking. This is a heavily-and-frequently-reviewed tree;
most auto-fixable low-hanging fruit was already picked in prior runs.

---

## Implemented in the accompanying PR (confirmed, validated — no decision needed)

Every fix was reproduced before and after the change. **Scope discipline:** all four are in root
`scripts/` files (not inside any plugin), so there is **no plugin version bump and no
generated-file churn** — `index.html` output is byte-identical on Linux, and every relevant
`--check`/gate is green. No doc-count corrections were generated this run (deliberately — the
version-bump-for-counts churn is the standing open question #6 below, and
`check-marketplace-claims.py` self-heals the gated counts post-merge).

### P1

| ID | Fix | File | Validation |
|---|---|---|---|
| **C-2** | `sync-plugin-versions.py` wrote `marketplace.json` via `write_text()` (default `newline=None`), which on **Windows** translates every `\n`→`\r\n` — rewriting all ~252 KB of the catalog and violating the module's **own documented byte-stability invariant** (lines 23-29), then failing the whole-tree `prettier --check .` required gate (which the repo documents as blocking *every subsequent PR* until fixed on `main`). Changed to `write_bytes(...encode("utf-8"))`, matching the LF-preserving precedent already in `generate-dashboards.py:17222` / `generate-copilot-plugin.py:874`. | `scripts/sync-plugin-versions.py` | Gate 226 `--self-test` (11 finding classes) + `--check` + `--must-fail` teeth all green; `ruff` clean; Linux output byte-identical (`--check` in-sync). |
| **C-1** | `inventory-sweep.py`'s pre-exec secret-name scrub — which drops secret-shaped env-var **names** before running each repo-tree script's `--must-fail` at `audit-gates.sh` T0 with the contributor's ambient env — missed common real credential names: `AWS_ACCESS_KEY_ID` (ends `_ID`, so `_KEY$` never matched), `DATABASE_URL`, and `*_WEBHOOK` (including this repo's own documented `RAVENCLAUDE_NOTIFY_WEBHOOK`). Broadened the regex (unanchored `KEY` subsumes `_KEY$`/`API_KEY`; added `WEBHOOK`/`DATABASE_URL`/`CONNECTION_STRING`) — every added token is credential-shaped and NAME-only, so `PATH`/`HOME`/`LANG`/etc. still never match (child-script behavior unperturbed, the reason `cwd`/`HOME` are deliberately left untouched). | `scripts/inventory-sweep.py` | Direct regex test: catches all named-missed secrets **and** false-scrubs zero of a 14-var system-var control set; `ruff` clean. **Honest limit:** the full `inventory-sweep.py --check` was **not** re-run in-session (it exceeds 180s — see design-input #10); the change is monotonic and isolated (it can only remove *more* credential-shaped names from child envs, never alter census/schema/covers output), so Gates 237/239 are unaffected. |
| **B-2** | `check-dashboard-server-parity.py`'s `unguarded_get_handlers` dispatch regex required `self.path` **immediately** followed by `.startswith(...)`/`==`, so it never saw `/__reserve`'s real dispatch form `self.path.split("?", 1)[0] == "/__reserve"` — meaning `_handle_reserve` rode the static path, escaping the MH-33 "every `/__` GET handler calls `_local_request_ok()`" coverage assertion in **both** server copies. Widened the regex with an optional `.split(...)[0]` clause. | `scripts/check-dashboard-server-parity.py` | `/__reserve` now appears in the checked dispatch set (was absent); gate green on the in-sync tree; **all four Gate 32 must-fail teeth still catch their mutations** (`/__saga` stripped, `_read_mimir` body mutated, `_reclaim_port` body mutated, CSRF `args.port`). **Not a live vuln** — `_handle_reserve` already calls the guard; this closes the gate blind-spot so a future regression is caught. |

### P2

| ID | Fix | File | Validation |
|---|---|---|---|
| **C-3** | `generate-index-dashboard.py` wrote `index.html` via `write_text()` — the same CRLF-on-Windows risk as C-2; the sibling dashboard generators already fixed it. Changed to `write_bytes(...encode("utf-8"))`. Lower severity than C-2 because the primary regen path is `regenerate-artifacts.yml` on `ubuntu-latest`, but `audit-gates.sh` also invokes it in write-mode locally. | `scripts/generate-index-dashboard.py` | `--check` reports `index.html` up to date (byte-identical on Linux); `ruff` clean. |

---

## Design-input — needs your decision (NOT auto-applied)

Each item was confirmed by a panel but deliberately **not** force-applied by this unattended
session, for the stated reason. Tagged `[SUBSTRATE]` = editing the Thing's own
`plugins/ravenclaude-core/hooks/` or `.../scripts/` is tribunal-blocked in an unattended
session (apply from a session with maintainer authority). Tagged `[CASCADE]` = a fix inside
`ravenclaude-core` would trigger the plugin version bump + `generate-copilot-plugin.py`
whole-agent-tree regen — held to avoid unreviewed generated churn in an unattended PR.

### 1. (P1) `[SUBSTRATE]` `guard-destructive.sh` curl→interpreter hard-deny is not segment-scoped
- **Where:** `plugins/ravenclaude-core/hooks/guard-destructive.sh:1864,1870`.
- **Defect (verified live):** the `curl|wget`-piped-to-interpreter hard-deny patterns are not scoped
  to a single command segment (unlike the rest of the file, which splits on `;`/`&`/newline). A
  two-line `curl -s URL > /tmp/f.json` followed by an **unrelated** `cat /tmp/f.json | python3 -m
  json.tool` is denied outright (exit 2) — a very common "fetch then process" shape, with no
  ask/override path. Fails **safe** (over-deny, never under-allow), so low security risk but real
  usability friction.
- **Why held:** substrate. Also, the tribunal-catalog twin (`sce.curl-pipe-shell`) was already
  segment-scoped in v0.244.0 — this is the `guard-destructive.sh` layer that wasn't given the same
  treatment.
- **Recommendation:** apply the same `[^|&;]`-style single-segment scoping the file's sibling
  detectors already use, so `|` into an interpreter within one segment still denies but a later,
  separate command's pipe does not.

### 2. (P1) `[SUBSTRATE]` `log-probe.sh` records a data value that looks like an HTTP status
- **Where:** `plugins/ravenclaude-core/hooks/log-probe.sh:134,183`.
- **Defect (verified live):** the "is this an HTTP probe" gate (added to fix the `wc -l`/`ls`
  false-positive class in v0.273.0) confirms an HTTP tool was invoked but never confirms the matched
  3-digit number is actually a status code. `curl -s .../inventory/42 | jq .remaining` returning the
  legitimate data value `404` is recorded as `verdict=negative/label=http-404`, which can spuriously
  deny a new-source-module creation via `guard-premise.sh` (recoverable via the existing `control.md`
  escape) **or**, more concerningly, falsely *clear* a genuine unresolved negative when a data value
  happens to be 2xx/3xx.
- **Why held:** substrate; and this is a residual of a known, carefully-tuned class (the v0.273.0
  milestone documents how narrow the fix had to be to avoid over-matching).
- **Recommendation:** additionally require the 3-digit token to be in a status-code *position* (e.g.
  the HTTP client's own `-w "%{http_code}"` output, or a status line), not merely any 3-digit run in
  the combined output. Re-run the v0.273.0 dry-run corpus before landing.

### 3. (P1) `context-usage-meter.py` — a Grok config window overrides the Claude Code model-aware window
- **Where:** `plugins/ravenclaude-core/scripts/context-usage-meter.py` (`window_from_grok_config()`
  consulted before the `source=="claude-code"` model-aware path). `[SUBSTRATE]` too.
- **Defect (verified live):** on a dual-host machine, a `~/.grok/config.toml` `context_window=128000`
  makes `measure()` return `window=128000`/`window_source=explicit` for a `claude-sonnet-5` session
  whose real window is 1,000,000 — defeating the v0.319.0 model-aware fix and potentially
  suppressing the conserve-tokens / handoff-nudge triggers in either direction.
- **Why held:** the resolution ranking (`signals.json → owner knob → Grok config → model-aware
  catalog → hardcoded default`) is **documented and intentional** in the v0.319.0 milestone. Whether a
  Grok config window *should* apply to a Claude Code session is a cross-host **precedence decision**,
  not an obvious bug — reordering documented behavior in an unattended session would be wrong.
- **Recommendation:** decide the precedence. The most defensible fix is to gate the Grok-config path
  to Grok sessions (rank it below the Claude Code model-aware resolution when `source=="claude-code"`),
  so each host's window comes from its own source.

### 4. (P1) `[repo-review engine, CASCADE + gated]` cost-affecting caps aren't bounded against the hard cap
- **Where:** `plugins/ravenclaude-core/skills/repo-review/scripts/block_planner.py` (`--safe-ceiling`)
  and `estimate_cost.py:~225` (`verify_cap`/`fix_cap`/`overhead`).
- **Defect (verified live):** v0.321.1 clamped `agent_budget` to `WORKFLOW_AGENT_CALL_HARD_CAP`
  (1000), but the *other* cost-affecting knobs aren't clamped. `--safe-ceiling 5000` on a 40-batch
  `ultra` plan reports `needs_blocks:false` while the single invocation would cost 40×30=1200
  `agent()` calls (20% over the real cap); `--verify-cap 2000 --fix-cap 0 --overhead 0` yields
  `total_agents:2000` with `agent_budget_clamped:false`. Both require **non-default misuse** of
  advanced tuning flags (Panel-2 downgrade from the agent's P0 → P1: the repo's P0 definition is
  "catastrophic on *realistic* input"; the default path is already safe). Negative caps additionally
  break the "finalize block is always most-constrained" invariant, silently under-provisioning
  review-only blocks.
- **Why held:** these are gated engine scripts (Gate 258 self-tests + Gate 260 structural checks with
  must-fail teeth); a fix must land a coherent clamp-or-refuse policy **and** fixtures while keeping
  those gates green, and a fix inside `ravenclaude-core` triggers the version-bump/regen cascade — too
  much to do blindly unattended, but genuinely high-value given the tool exists precisely to prevent
  the documented 98.7M-token overrun.
- **Recommendation:** clamp every cost-affecting param (or refuse the run) against
  `WORKFLOW_AGENT_CALL_HARD_CAP`, set an explicit `*_clamped`/warning field, reject negative caps, and
  add a must-fail fixture per param. Do it as one coherent change with the gates re-run green.

### 5. (P1) `[KNOWN — still open]` `check-workflow-hygiene.py` Rule 1 checks the `permissions:` key, not its value
- **Where:** `.github/scripts/check-workflow-hygiene.py:69` (invoked by
  `github-protocol-workflow-hygiene.yml`). Re-confirmed still-open this run.
- Same finding and recommendation as **2026-09-23 design-input #1** (job-count-aware value inspection
  + a broad-permissions must-fail fixture; decide the single-job carve-out policy first). Not
  re-derived here — see that doc.

### 6. (P2) `[SUBSTRATE]` `guard-memory-compaction.sh` integer-division truncation
- **Where:** `plugins/ravenclaude-core/hooks/guard-memory-compaction.sh:268`.
- **Defect (verified by arithmetic):** the shrink-percent uses integer division, so `old=10000`,
  `new=8410` computes `_pct=15` and a **15.9%** shrink passes the default `<=15%` check — the guard is
  slightly more permissive than documented.
- **Recommendation:** compare `(old-new)*100` vs `threshold*old` (integer cross-multiply) to avoid the
  truncation, or round up. Substrate — maintainer authority.

### 7. (P2) `[SUBSTRATE]` `routine-reserve.py` has no type-guard on the `routines` shape
- **Where:** `plugins/ravenclaude-core/scripts/routine-reserve.py:940` (`hook_warn()` / `_print_status()`).
- **Defect (verified live):** a malformed `reserve.json` (`routines` as a dict, not a list of dicts)
  raises an uncaught `AttributeError`. The wrapping `routine-reserve-hook.sh` masks it (stderr→/dev/null,
  exit 0) so the hook contract holds, but the advisory warning then **silently never fires** with zero
  diagnostic. Untested by Gate 291's fixtures (which always hand-shape `routines` correctly).
- **Recommendation:** add the same defensive `isinstance` guard the rest of the file uses; substrate —
  maintainer authority.

### 8. (P2) `[CASCADE]` `fix_summary.py` doesn't check the git subprocess returncode
- **Where:** `plugins/ravenclaude-core/skills/repo-review/scripts/fix_summary.py:198`
  (`write_patch_and_stat`).
- **Defect:** a bad `--repo-root` silently writes empty `fixes.patch`/`fixes.stat`, indistinguishable
  from "no changes made" even when the accompanying `summary.md` reports applied fixes.
- **Why held:** clean isolated robustness fix, but inside `ravenclaude-core` (cascade) and gated by 258.
- **Recommendation:** check `returncode` and raise/warn on a failed git call; add a fixture. Bundle with
  #4 (same engine, same cascade/gate).

### 9. (P2) `[CASCADE]` `coordinator-lock.sh` `_write_lease()` is not atomic
- **Where:** `plugins/ravenclaude-core/bin/coordinator-lock.sh:83`.
- **Defect (verified):** `cat > file` instead of the repo's temp-file+rename idiom; 4 concurrent writers
  produced 1/298 torn (invalid-JSON) reads. A torn read during `heartbeat()` can persist blanked fields
  (lost `current_pr`/`acquired_at`). The `mkdir`-based mutual exclusion itself **is** atomic (correctly
  proven by the script's own `--disable-atomic-step` control) — only the lease *write* isn't.
- **Why held:** the coordinator is opt-in (`source_control_coordinator: off` default), so real-world
  likelihood is low today; the fix is inside `ravenclaude-core` (cascade).
- **Recommendation:** write to a temp file then `mv` (atomic rename), matching `stall_watch.py`.

### 10. (P2/P3) `inventory-sweep.py` `_script_callgraph` is quadratic — and it explains the ci-preflight timeout
- **Where:** `scripts/inventory-sweep.py:300` (`_script_callgraph`), root file.
- **Defect (measured):** O(scripts × haystack_files) ≈ 400 × 226 (~4.5 MB combined) substring search
  with no index, re-run on every PR at the default tier. `ci-preflight.py`'s `hotspot:6b`
  (`inventory-sweep.py --check`) **timed out after 180s** this run (soft-skip UNAVAILABLE) — this
  quadratic (plus per-script `--must-fail` subprocess launches) is the likely contributor.
- **Why held:** a perf refactor (e.g. one Aho-Corasick pass over script names) touches a script gated
  by Gates 237/239 and used by the census; needs care to prove output-equivalence.
- **Recommendation:** build one combined search structure once; assert byte-identical census output
  before/after.

### 11. (P2) `artifact-budgets.seed.json` ratchet is stale on `main` after a `[skip ci]` self-heal
- **Where:** `scripts/artifact-budgets.seed.json` (`measured_against` = `4f3ced1`, merge-base now
  `121432c`).
- **Defect (verified):** commit `121432c` ("chore(artifacts): self-heal generated artifacts (#1261)
  `[skip ci]`") regenerated artifacts without re-stamping the seed, and because it was `[skip ci]` the
  ratchet-freshness gate never fired — so the stored budget claim differs from a fresh re-measurement.
  `ci-preflight.py hotspot:1-ratchet-merge-base` FAILs on it. (The `inventory-coverage-ratchet.json`
  and `model-tier-ratchet.json` files share the stale SHA but their *claims* still match `origin/main`
  — benign.)
- **Why held:** re-stamping a ratchet is a **deliberate maintainer operation** per repo doctrine (said
  out loud, not silent) — doing it in an unattended review PR could mask a real regression.
- **Recommendation:** `python3 scripts/check-ratchet-freshness.py --stamp` as a conscious action, then
  confirm the re-measured budget matches the intended artifact sizes from #1261.

### 12. (P3) `[SUBSTRATE]` `_emit-event.sh` no-jq fallback doesn't escape the full C0 range
- **Where:** `plugins/ravenclaude-core/hooks/_emit-event.sh:197`.
- **Defect:** the hand-rolled JSON-escape fallback (used when `jq` is absent) doesn't escape the full
  C0 control-byte range, so a rare control byte in a denied command could produce invalid JSONL that
  Heimdall/Víðarr silently drop. Low likelihood (jq usually present; control byte in a command rare).
- **Recommendation:** escape `\u0000`–`\u001f` in the fallback; substrate — maintainer authority.

### 13. (P3) `[CASCADE]` `repo_map.py` batch-id tie-break is lexicographic
- **Where:** `plugins/ravenclaude-core/skills/repo-review/scripts/repo_map.py:247`.
- **Defect:** the risk-sort tie-break compares zero-padded id strings (`"b100" < "b23"`), inverting
  order among risk-tied batches once a scan exceeds 99 batches. Near-nil impact (ties are
  risk-equivalent by definition).
- **Recommendation:** natural/int sort on the batch-id number; bundle with #4/#8 (same engine).

---

## Standing items from 2026-09-23 — confirmed still open

Not re-derived here; see [`2026-09-23-repo-review.md`](2026-09-23-repo-review.md) for full writeups.

- **#2** (P1) the 29 remaining **routed-shape** anti-pattern hooks scan disk not the proposed edit +
  the systemic `check-pretooluse-payload-scan.py` regression gate + `_edit-subject.sh` shared helper
  (must land together).
- **#3** (P2) `check-verdict-default-nonpermissive.py` `FALLIBLE` regex misses bare commands (latent).
- **#4** (P2) `check-model-tier-fit.py` `_IMPL_DESC` lacks `re.IGNORECASE` (may be deliberate; 5 agents
  need per-agent tiering first).
- **#5** (P2/P3) three substrate hooks (`enforce-layout.sh` unreachable jq-warn, `guard-web-access.sh`
  IPv6-literal host parse, `guard-premise.sh` no `command -v python3` guard).
- **#6** convention question — version bumps for README/CLAUDE.md count corrections. This run added no
  count fixes, so the question is unchanged; a one-line addition to the CHANGELOG convention in
  `AGENTS.md` would settle it.

---

## Panel artifacts

Per-agent raw findings, the deterministic baseline, and the standing-items cross-reference are in
the session run directory `.ravenclaude/runs/repo-review-2026-09-28/`
(`findings-raw.md`, `deterministic-baseline.md`, `standing-items.md`) — local-tier, gitignored, not
committed.
