# Repo-review — 2026-09-22 (autonomous multi-panel sweep)

**Run:** scheduled routine, no human present. Findings categorized P0–P3, validated by a
second panel, and tie-broken where severity was ambiguous. This document is the
**design-input / decisions** deliverable (task step 6); the safe, in-scope fixes ship in the
accompanying PR.

## TL;DR

The repository is **healthy**. **No P0 (critical) and no P1 (high) findings.** The reviewed
security-critical surfaces — the command/decision tribunal, the destructive-command and
premise guards, the dashboard server's CSRF/host/path-traversal defenses, the pre-compaction
egress floor, the atomic posture-apply — are all sound. Bash-3.2 / BSD-tool portability
discipline is thoroughly applied across shipped code. Structural health (184 manifests,
version-sync, layout allow-list, hook executability, shell syntax) is clean.

The residue is **5 P2 (medium) and 6 P3 (low)** findings. **Every P2 sits in
`plugins/ravenclaude-core/{hooks,scripts}/`, which the tribunal self-tamper floor
(`xc.tribunal-self-disable`) protects from writes category-independently** — confirmed this
session (a fix attempt on `stall_watch.py` was DENIED, Sága-logged). So the P2s are correctly
**human/maintainer work**, applied from a session with substrate access or via the dashboard,
not autonomously by a routine. This is the intended safety boundary, not an obstacle.

## Scope (stated explicitly)

Reviewed the repo's **code** surfaces: root `scripts/`, `plugins/ravenclaude-core/{hooks,scripts}/`,
`.github/workflows/`, and the repo-review skill scripts — ~398 files across 32 risk-ranked
batches. **Out of scope** (deliberately, for an autonomous run): the 7,681 markdown files and
the agent/skill/knowledge content of all 184 plugins — a "comprehensive" content review of
those is neither feasible nor high-value here, and would dilute signal. A full whole-repo
`/repo-review` sweep would be ~362 agent dispatches (the v0.321.1 record shows a comparable
run burned ~98.7M tokens); the `Workflow` tool was also unavailable (no opt-in this session).
So the pipeline (Panel 1 review → Panel 2 validate → Panel 3 tie-break → fix) was driven via
direct subagent dispatch over the highest-risk slice, exactly as the skill was proven.

## Method

- **Panel 1 (expert review):** 3 parallel reviewers — security (guards/tribunal),
  CI/CD Actions security (all 17 workflows), core Python correctness — plus a deterministic
  health/portability sweep (Seat D). Raw findings: `.ravenclaude/runs/repo-review-2026-09-22/findings/`.
- **Panel 2 (validation):** priorities re-checked against a deterministic severity→priority
  map (blocking→P0, major→P1, minor→P2, nit→P3); one Seat-C note **refuted** (see below).
- **Panel 3 (tie-break):** ambiguous severities verified against the actual code paths. The
  guard-premise finding was re-graded twice (P2→P3→P2) by reading the code to the final exit —
  a worked example of observation-vs-inference (Python `sys.exit(0)` was not the final decision;
  the shell wrapper re-decides and `exit 2`s).

---

## P2 — medium (all require maintainer action; all substrate-locked from autonomous edit)

### P2-1 · `guard-destructive.sh:351` (+379/405/420) — dangerous target matched over the whole command, not scoped to the subcommand
- **Impact:** false-positive **denials** on legitimate chained commands. `rm -rf ./build && cat /etc/os-release` is denied as recursive-rm-of-dangerous-target because the `/etc/os-release` token elsewhere in the command satisfies the whole-command target regex, even though `rm` targets `./build`. Same shape for `chmod -R 755 dir && echo 777`.
- **Direction:** over-block, **not** an under-block — no security hole. But per this repo's own doctrine, over-blocking drives guard-disablement, which is a real cost.
- **Precedent:** this is the exact unscoped-token class the repo already fixed for git-push-delete (`_is_dangerous_git_push_delete`, CLAUDE.md v0.242.0/v0.244.0).
- **Recommendation:** scope each helper's dangerous-target/mode test to the segment containing its own verb — split the normalized command on `;`/`&`/`|` (mirroring `_is_dangerous_git_push_delete`), then require verb + recursive-flag + dangerous-target to co-occur **within one segment**.
- **Question for you:** this is security-guard matching logic — a fix **must** ship with a must-fail teeth test proving it still denies a real `rm -rf /etc` / `chmod -R 000 /`. Want this scoped as its own small PR with the teeth test? (It cannot be edited from a routine — substrate-locked.)
- Effort: **medium**. Confidence: 0.72.

### P2-2 · `stall_watch.py:383` — `count_compact_boundaries()` unbounded full-file read defeats the module's own `TAIL_BYTES` discipline
- **Impact:** a 6-hour stall on the observed 85 MB transcript ≈ 72 ticks × full 85 MB read ≈ **~6 GB read every 5 minutes**, to recount a value that changes rarely. Bounded to stalled sessions, but it is the exact I/O pattern the module's docstring warns against.
- **Recommendation:** bound the read the way `last_progress_age_min` does (a tail read suffices for the recency window), **or** cache the count on the episode and recompute only when the transcript mtime/size changed. Prefer the cache — a tail bound could undercount boundaries on a huge transcript, so confirm the caller's semantics first.
- Effort: **low-medium**. Confidence: 0.75.

### P2-3 · `stall_watch.py:347` / `:387` — unguarded `os.path.getsize`/`open` aborts the whole general-stall pass on a transcript-vanish race
- **Impact:** if one session's transcript is rotated/removed between `find_transcript()` and the `getsize`/`open`, the `OSError` aborts `evaluate()` before it reaches **other** sessions — so a genuinely stalled, alert-worthy session in the same tick gets no finding. **Fails toward silence**, against the module's own never-fail-silent design.
- **Recommendation:** wrap the `getsize`/`open` in each helper (or the two call sites) in `try/except OSError` that appends a note and `continue`s to the next session — matching the per-session error discipline used everywhere else in the file. (This is the fix I attempted and was correctly DENIED by the tribunal substrate floor.)
- Effort: **low**. Confidence: 0.70. *(Clearest, safest of the P2s — a maintainer with substrate access should just apply it.)*

### P2-4 · `guard-premise.sh:527` — marketplace-relative recorder path → spurious BLIND **deny** in consumer repos
- **Impact:** the recorder-existence check uses `os.path.join(proj, "plugins", "ravenclaude-core", "hooks", "log-probe.sh")` — a path that exists in *this* marketplace but **not** in a consumer repo (consumers install to `~/.claude/plugins/cache/…`). A consumer whose **first session action is a Write** creating a new source file (`.py`/`.sh`/`.ts`/…), before any Bash has dropped the session beacon, is **denied** (`permissionDecision: deny`, exit 2, `guard-premise.sh:711`) with "the premise recorder is not installed."
- **Corroboration:** this very session runs with the recorder unwired (persistent "I AM BLIND" notices) — the BLIND state is reachable in practice.
- **Trigger is narrow:** requires no prior Bash this session (any earlier Bash drops the beacon and the branch isn't reached). But when it fires it hard-blocks legitimate work with a confusing message.
- **Recommendation:** detect the recorder host-agnostically — resolve via `CLAUDE_PLUGIN_ROOT` / the cache path, or key blindness on whether the recorder has **ever** dropped a beacon in any prior run dir — rather than a project-relative path that is structurally wrong outside this repo.
- **Question for you:** is the Write-side BLIND policy intended to fail **closed** for consumers at all? (The Bash-side sibling `cause-gate` deliberately fails **open** on blindness — this asymmetry may be intentional, but the marketplace-relative path makes it mis-fire regardless.)
- Effort: **low-medium**. Confidence: 0.60 (validity confirmed; frequency depends on the first-Write case).

### P2-5 · `route-decision-review.sh:173` — perl-absent fallback discards the always-present `tr` sanitization
- **Impact:** under `set -o pipefail`, the `|| printf original` fallback returns the **raw** engine reasoning when `perl` is absent (perl is not POSIX-guaranteed; minimal containers may lack it), so embedded newlines / U+2028 / U+2029 pass unsanitized into the `permissionDecisionReason` — defeating the line-break-stripping half of the JudgeDeceiver injection hardener. Defense-in-depth degradation, not a full bypass (other layers remain).
- **Recommendation:** keep `tr` unconditional and make only `perl` optional: `printf reasoning | tr -d … | { perl -pe … 2>/dev/null || cat; }`.
- Effort: **low** (one-line). Confidence: 0.50. *(Low-confidence, narrow-trigger, but a trivially correct hardening.)*

---

## P3 — low

| # | Finding | Location | Note |
|---|---|---|---|
| P3-1 | Sága audit JSON persists the raw reviewed command **unscrubbed** (secret-at-rest in a local gitignored forensic log), unlike `_emit_hook_event` / guard-destructive stderr | `thing-orchestrator.sh:180` | **Decision needed:** is raw retention deliberate forensic fidelity? If not, call `_scrub_reason` on the command before serialization. Substrate. |
| P3-2 | `_read_norns()` sort key `p.stat().st_mtime` is an unguarded stat race that can 500 `/__norns` | `serve-dashboards.py:675` | Reuse `_handle_runs()`'s `_safe_mtime` (returns 0.0 on OSError). **Blocked from autofix:** the plugin copy is substrate and Gate 32 requires byte-identical parity, so one copy can't be fixed alone. |
| P3-3 | Observability endpoints `read_text()` local files with no size cap | `serve-dashboards.py:2107` (+ `_read_nidhoggr`, `_read_norns`) | Add a `stat().st_size` cap mirroring `_MIMIR_JSONL_READ_CAP`/`_POSTURE_MAX_BYTES`. Local-only (127.0.0.1 + CSRF). Same dual-copy parity block as P3-2. |
| P3-4 | `declare -A _MOCK` (bash 4.0+) in a **test** file — aborts on stock macOS bash 3.2 | `hooks/tests/test-gate120-model-fallback.sh:36` | Sole live-code associative-array use; all shipped code is 3.2-clean. Rewrite with the repo's 3.2-safe idiom or add a `bash>=4` skip-guard. CI (Linux) and the macOS gate's shell-glob scope don't surface it. |
| P3-5 | `validate-schemas.yml:60` bare `pip install` vs the repo-mandated `python3 -m pip` | `.github/workflows/validate-schemas.yml` | **FIXED in this PR** — aligns a required check with the documented standard. |
| P3-6 | `golden-set-inject-light.yml:39` grants unused `actions: read` | `.github/workflows/golden-set-inject-light.yml` | **FIXED in this PR** — least-privilege; verified `gh api rulesets` needs only `contents: read`, `upload-artifact`/`checkout` need no `actions` grant. |

## Refuted by Panel 2 (recorded so it isn't re-raised)

- **`audit-gates.sh:264–272` "stale comment" (Seat C out-of-scope note):** NOT a defect. The
  comment deliberately distinguishes *(a)* the exit a tool's own check returns from *(b)* the exit
  the `--must-fail` run returns, and states *(b)* is 0 for both tools. The note conflated (a) and
  (b) — the exact confusion the comment itself warns against. Gate 226 correctly uses `-eq 2` for
  (a). No change.

## What shipped in the accompanying PR (autonomously fixed — non-substrate, low-risk)

1. `validate-schemas.yml` — `pip install` → `python3 -m pip install` (P3-5).
2. `golden-set-inject-light.yml` — dropped unused `actions: read` (P3-6).

Both YAML-validated and prettier-clean. Everything else above is substrate-locked and/or needs
a design decision, so it is routed here rather than changed by the routine.

## Suggested next actions (for a maintainer session with substrate access)

1. **P2-3** (stall_watch TOCTOU guard) — apply as-is; smallest, safest, clearest win.
2. **P2-2** (stall_watch bounded/cached count) — apply with a caller-semantics check.
3. **P2-1** (guard-destructive segment-scoping) — its **own** PR with a must-fail teeth test.
4. **P2-4 / P2-5** (guard-premise recorder path; route-decision-review perl fallback) — both small.
5. **P3-1** — decide raw-vs-scrubbed Sága retention, then act.
6. **P3-2/P3-3** — fix both `serve-dashboards.py` copies together (Gate 32 parity).
