# Repository review — 2026-09-18 (multi-panel bug sweep)

**Autonomous scheduled run.** Branch `claude/awesome-wright-ij27il`. Model assignment per the
task: Sonnet Panel-1 reviewers (categorization), Opus orchestrator (validation, tie-break,
implementation decisions).

## Read this first — the operational headline

1. **The repo is mechanically clean.** `scripts/ci-preflight.py` reported **19 PASS / 0 FAIL / 0
   UNAVAILABLE** on the tree at the start of this run (JSON validity, shell syntax, prettier, ruff,
   ratchet/merge-base, inventory census/sweep/schema, dashboard/index/concepts freshness, Copilot
   package, Codex projection). Every finding below is a **latent** defect a currently-green gate does
   not assert against — none is a red gate.
2. **This run's only autonomously-applied fixes are the Q4 doc-accuracy corrections** (the
   `exit 1`-to-block / PostToolUse-can't-block defect class flagged as the open **Q4** in
   [`docs/2026-09-15-repo-review-design-questions.md`](2026-09-15-repo-review-design-questions.md)).
   These are doc-only, non-substrate, zero-behaviour-change. Details under "Fixed in this PR".
3. **Everything else this run's panels surfaced is guardrail *substrate*** (`plugins/ravenclaude-core/{hooks,scripts}/`)
   and is **staged, not applied** — the same load-bearing constraint every prior run recorded: an
   unattended agent must not self-patch the guardrail code that governs it (high blast radius; it runs
   on every session and every consumer). These are for a human, or a session with the Thing off, to
   apply. See "Staged substrate findings (this run)".
4. **The prior backlog is still open.** The 2026-09-14 run's N-01..N-20 and the 2026-09-11 batch
   (including the **P0 tribunal-self-disable bypass, D1**) remain unapplied. This run independently
   re-confirmed **N-01** is still present on `main` (see below, with the control probe). Nothing here
   supersedes those docs.

## Method (panels + model assignment)

- **Panel 1 (scan, Sonnet — the lighter tier per the model-assignment rule):** four parallel
  reviewers over disjoint high-risk code slices — (A) root `scripts/*.sh`; (B) `ravenclaude-core/hooks/*.sh`
  (widest blast radius — runs every session); (C) root `scripts/*.py` CI/gate scripts; (D)
  `ravenclaude-core/scripts/*.py` engine (tribunal/ledger/dashboard). Each required a **concrete
  failing scenario** per finding.
- **Panel 2 (validation, Opus — this orchestrator):** re-verified every finding it could reach
  against the live code (read the actual functions, read `hooks.json` for hook-event wiring,
  cross-checked the repo's own canonical exit-code semantics in
  [`docs/best-practices/hook-authoring.md`](best-practices/hook-authoring.md)). No finding was
  actioned on a panel's say-so alone.
- **Panel 3 (tie-break):** convened for priority disagreements. The only genuine one was the Q4
  `regulatory-compliance` instance — resolved **P2** (it is a documented SAR/STR *compliance control*
  that promised enforcement it did not deliver), consistent with the 2026-09-15 recommendation.

> **Coverage gap, stated honestly:** Panel 1-C (root `scripts/*.py`) hit its turn limit before
> delivering a report. That slice (~129 Python files) was therefore not fully reviewed this run; it
> overlaps heavily with prior sweeps (2026-09-11/14), so no *known* coverage was lost, but treat root
> `scripts/*.py` as under-covered by *this* run specifically.

## Fixed in this PR (non-substrate, doc-accuracy — the open Q4 defect class)

The `exit 1`-to-block defect class: docs telling a maintainer to flip a hook's `exit 0` to `exit 1`
to make it block. Claude Code's PreToolUse contract blocks **only on exit 2** (`exit 1` is a
non-blocking error silently swallowed); on **PostToolUse** *no* exit code can block, because the
write already happened (canonical statement: `docs/best-practices/hook-authoring.md:22`). The
2026-09-15 PR fixed this class in five hooks (finance/web-design/power-platform) and left the
remaining named instances as **Q4**. This PR closes those.

| ID | Priority | File | Fix |
|---|---|---|---|
| Q4-A | **P2** | `plugins/regulatory-compliance/README.md`, `.../skills/sar-narrative-drafting/SKILL.md` | Both told the user to flip `exit 0` → `exit 1` to block the confidential-PII-scrub hook (a PreToolUse hook — exit 2 blocks). Corrected to `exit 2` with the non-blocking-exit-1 note. The hook itself and `CLAUDE.md` §7 were already correct; only these two docs had drifted. **P2** because it is a stated SAR/STR compliance control. |
| Q4-B | **P3** | `plugins/data-platform/CLAUDE.md` §7 | Said "flip `exit 0` to `exit 1` to enforce"; the hook is PreToolUse and its real switch is `DATA_PLATFORM_STRICT=1` (→ exit 2). Doc now points at the env var + correct exit-code semantics. |
| Q4-C | **P3** | `plugins/edtech-partner-success/CLAUDE.md` §7 + `hooks/flag-psm-anti-patterns.sh` (header comment + runtime banner) | Doc *and* the hook's own comment/banner claimed `exit 2` = BLOCK, but the hook is **PostToolUse** — it runs after the write and cannot block at all. Corrected to state PostToolUse semantics honestly (exit 2 only surfaces stderr to the agent; blocking would require re-wiring to PreToolUse). Comment/stderr-text only — **no** control-flow or exit-code change. |

Each touched plugin's semver was bumped (regulatory-compliance 0.12.6, data-platform 0.33.4,
edtech-partner-success 0.12.10), the catalog re-derived via `scripts/sync-plugin-versions.py`, each
CHANGELOG's top entry added, and the generated inventory/dashboards/index regenerated.

## Staged substrate findings (this run) — NOT applied (guardrail self-patch constraint)

New this run relative to the 2026-09-14 N-list. Line numbers are reviewer-reported and approximate —
confirm at the file before applying. Priorities are Panel-2 verdicts.

| ID | Priority | File:line | One-line | Provenance |
|---|---|---|---|---|
| S-01 | **P2** | `plugins/ravenclaude-core/hooks/guard-foreground-suite.sh:170` | The `--check` bypass is a **substring** match (`case "$_seg" in *--check*)`), but `audit-gates.sh` accepts only an exact `--check <N>` token — so `bash scripts/audit-gates.sh --checkpoint…` is waved through as a "scoped single-gate run" while `audit-gates.sh` doesn't recognize the flag and runs the full ~900-gate suite: the exact 10-minute session-wedge this guard exists to prevent. **Fix:** anchor on `(^\|[[:space:]])--check([[:space:]]+[0-9]+)?([[:space:]]\|$)`. | Reviewer-reported, verified by reviewer against `audit-gates.sh:549` flag parsing; not independently re-opened by the orchestrator. |
| S-02 | **P2/P3** | `plugins/ravenclaude-core/hooks/sanitize-webfetch-output.sh:9-11`, `sanitize-mcp-output.sh:9-11` | If `python3` or the sibling `.py` sanitizer is absent, the wrapper exits 0 with the **unsanitized** WebFetch/MCP body and **no `_emit_hook_event`** — a silent, untelemetered fail-open of an anti-injection layer, unlike every other guard in the plugin (Heimdall/Víðarr show a clean perimeter while the defense is off). **Fix:** emit a `warn` hook-event on the sanitizer-unavailable path. **Open q:** confirm the `.py` sanitizers don't themselves emit telemetry first (Python side out of this panel's scope). | Reviewer-reported (medium confidence). |
| S-03 | **P3** | `plugins/ravenclaude-core/hooks/guard-recursive-spawn.sh:114` | `echo "$match" \| grep -qiE …` under `set -o pipefail`: `grep -q` closes the pipe on first match → producer SIGPIPE → pipeline returns 141, flipping the `if`'s truth value. Advisory PostToolUse hook (blast radius = a wrong stderr warning), needs an implausibly long single line to manifest. **Fix:** capture-then-grep (the idiom the repo's own tests already document). | Reviewer-reported (low confidence / narrow trigger). |
| S-04 | **P3** | `plugins/ravenclaude-core/scripts/serve-dashboards.py:2673-2721` | TOCTOU PID-reuse in port reclaim: `_is_our_dashboard(pid)` checked via `ps`/`lsof`, then `os.kill(pid, SIGTERM)` afterward — a recycled PID in the window kills the wrong process. Local-only. **Fix:** re-verify immediately before the kill, or document the residual risk. | Reviewer-reported. |
| S-05 | **P3** | `plugins/ravenclaude-core/scripts/prompt-optimizer-format.py:598…722` | Self-test uses hardcoded `/tmp/pof-selftest-N` paths (not `tempfile.mkdtemp()`) — a symlink pre-plant by a co-resident local user is theoretically possible; only reachable via manual `--self-test`, exploitability unconfirmed. **Fix:** `tempfile.mkdtemp()`. | Reviewer-reported (unconfirmed). |

**Positive assurance (worth recording):** the security reviewer's read of the tribunal/ledger/dashboard
core found **no P0–P2 defects** — `thing-decision.py`/`thing-decide.py` resolve every
error/timeout/injection/abstention path to deny/ask/defer (never allow); `always_screen` self-disable +
hard-rule screens can't be routed around by miscategorization; model-diversity enforcement holds;
`serve-dashboards.py` `/__save`/`/__read` allow-list the path *and* re-verify containment via
`.resolve().relative_to(PROJECT_ROOT)`, use `hmac.compare_digest` for CSRF; `precompact-digest.py`
egress is fail-closed. Root `scripts/*.sh` came back clean (3 low-confidence P3 hypotheses only, none
independently reproduced).

## Prior backlog still open (re-confirmed / unchanged)

- **N-01 (`hooks/_scrub.sh:51-52`) — orchestrator-confirmed still present this session, with a
  control probe.** GitHub token prefixes `gho_`/`ghs_`/`ghu_`/`ghr_` are absent from `_secret_patterns`
  (only `ghp_`/`github_pat_`). Control run this session: positive control
  `grep -nE "gh[a-z_]*_\[|github_pat" _scrub.sh` → lines 51-52 present (probe works); discriminating
  probe `grep -nE "gh[osru]_" _scrub.sh` → **no match** (the four prefixes are genuinely absent — this
  would have matched if the claim were false). Consequence: a denied command carrying such a token
  leaks it verbatim into `hook-events.jsonl` + stderr; this session's own `GITHUB_TOKEN` is a `ghu_`
  token. The fix (`ghp_…` → `gh[oprsu]_[A-Za-z0-9]{30,}`) is unarguably safe — widening a redaction
  only ever redacts *more*. **Lowest-risk substrate patch to apply first.**
- **The full 2026-09-14 N-02..N-20** (guard-destructive false-positive deny scoping, serve-dashboards
  crash paths, delegate fail-open, conserve-tokens / context-usage-meter / stall_watch defects) —
  see [`docs/repo-review-2026-09-14-findings.md`](repo-review-2026-09-14-findings.md). Paste-ready fixes there.
- **The 2026-09-11 batch, including the P0 D1 tribunal-self-disable `curl -o`/`wget -O` bypass** —
  see [`docs/repo-review-2026-09-11-findings.md`](repo-review-2026-09-11-findings.md). **D1 remains the
  single highest-priority item in the repo.**

## Design questions / decisions (need a human)

1. **The standing structural question (raised every run since 2026-09-11): an unattended agent cannot
   fix its own guardrail code here.** Correct by design — but it means the substrate backlog (N-01,
   D1, S-01..S-05) can only be auto-*found*, never auto-*fixed*. It grows each run. **Decision needed:**
   either (a) a maintainer / Thing-off session drains it, or (b) a narrow, sanctioned
   substrate-edit path for authorized autonomous maintenance is defined. The safe-widening N-01 (and
   the false-positive-deny-scoping N-03/N-04) are the natural first batch — each mirrors a fix idiom
   the file already uses elsewhere.
2. **Q2 / Q4 remaining from 2026-09-15 are now partially closed.** Q4's named instances are fixed in
   this PR. **Q2** (a targeted "comment promises fail-closed, code is a no-op" sweep over the
   `scripts/check-*.py` gate family) is still a defensible low-effort follow-up and was **not** run
   this session (Panel 1-C's turn-limit exit). **Q1** (a shared `strict-block.sh` helper to make the
   whole anti-pattern-hook STRICT class un-driftable), **Q3** (structural placeholder detection in the
   secrets scanner), and **Q5** (wire-or-skip `prompt-optimizer-gate.sh` in the Codex projection) are
   unchanged — see the 2026-09-15 doc.
3. **C-02 from 2026-09-11 is still open** — does `--no-cross-model` apply to the `max` tier in
   `/repo-review`? SKILL.md documents the flag; the code ignores it for `max`. Recommendation there
   was a tri-state. Still yours to decide.

---

_Panel-1 reviewer finding JSON (full scenarios/observations/confidence) is in this run's task
transcripts; the minimal patch for each staged finding is in its row's "Fix:" clause._
