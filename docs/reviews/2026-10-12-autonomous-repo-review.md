# Autonomous whole-repo review — 2026-10-12

> Scheduled autonomous review of the RavenClaude marketplace. Three-panel method
> (expert review → validation → tie-break), confirmed findings categorized P0–P3,
> mechanical non-design fixes applied, design-input items surfaced here for a human
> decision. Branch: `claude/awesome-wright-fcug5o`.

## 1. Executive summary

**Verdict: the repository is in excellent objective health.** A full pass over the
automated gate harness and a focused expert review of the highest-risk hand-written
surface found **no P0/P1/P2 issues** and **one benign, CONFIRMED P3** correctness
inconsistency whose *fix direction* is a design decision (so it is surfaced here, not
auto-applied). No autonomous code fix was warranted; the one candidate fix that surfaced
early was a **false positive** and was correctly reverted before any commit (see §3).

Scope reviewed: 184 plugins, 10,861 tracked files. Review date 2026-10-12. Reviewer:
autonomous scheduled session (Opus 4.8) with delegated expert sub-panels.

| Priority | Count | Auto-fixed | Surfaced for decision |
|---|---|---|---|
| P0 (critical) | 0 | — | — |
| P1 (high) | 0 | — | — |
| P2 (medium) | 0 | — | — |
| P3 (low) | 5 | 0 | 5 |
| Observations (not defects) | 3 | — | 3 |

The five P3s are: one correctness inconsistency whose *fix direction* is a design call
(§5.1), and four low-severity hardening items in the per-tool-call hook scripts (§5.2).
**None met the bar for safe autonomous modification** (CONFIRMED + small + a single
verified-correct implementation + fully validatable), so all are surfaced with
ready-to-apply fixes rather than auto-applied — see §7 for why that bar matters for
security-critical guardrail code in an unattended run.

## 2. Method (the three panels)

- **Panel 1 — expert review.** Two complementary sources ran in parallel:
  1. *The codified gate harness* — this repo encodes its engineering standards as ~700
     CI gates, so the harness itself is the most reliable "expert." Every objective
     validator was run (see §4); all green.
  2. *Focused expert sub-panels* on the highest-risk, recently-churned, hand-written
     code the gates do **not** fully cover — the Spectate per-tool-call hook scripts
     (security), the host-hook generators / committed-artifact checkers (correctness),
     and a broad tech-debt inventory. Dimensions covered: correctness, security,
     resource/leak, error-handling, determinism, dead-code/tech-debt, CI/Actions.
- **Panel 2 — validation.** Each candidate finding was re-verified against the source
  (observation vs. inference separated per the repo's own accuracy discipline) before
  being accepted. This caught and rejected the prettier false positive (§3) and
  confirmed the P3 (§5.1) against the live manifest + code.
- **Panel 3 — tie-break.** The only ambiguity that surfaced is the *fix direction* of
  the P3 — a design-intent question, not a severity question. Because the two candidate
  fixes produce opposite consumer behavior and regenerate a consumer-facing committed
  artifact, it is deferred to a human rather than auto-resolved (matches the repo rule:
  high-blast / design-intent decisions defer to the maintainer).

## 3. The prettier "finding" that was a false positive (recorded for transparency)

An initial whole-tree `prettier --check` (using the host's local prettier **3.8.1**)
flagged two committed files as mis-formatted:
`plugins/web-commerce/templates/shared/commerce-types.ts` and
`scripts/check-committed-routes.mjs`. That *looked* like a repo-wide CI blocker.

**It was not a real issue.** CI pins **prettier@3.9.4** (`scripts/ci-preflight.py:289`,
and the project testing instructions). Re-checking the *original committed* files with
the pinned `prettier@3.9.4` returns **exit 0 — clean**. The drift was an artifact of the
local 3.8.1 vs. CI 3.9.4 version gap; applying the 3.8.1 "fix" would have *introduced* a
regression that fails CI's 3.9.4 gate. The change was reverted before any commit, and a
full-tree `prettier@3.9.4 --check .` confirms the whole repository is clean.

*Lesson (already documented in CLAUDE.md): always verify prettier with the pinned
`prettier@3.9.4`, never the host's ambient version.*

## 4. Objective gate harness — all green

Run this session, all passing:

- JSON validity: `marketplace.json`, `.repo-layout.json`, all 184 `plugin.json` (186 files).
- Shell: `bash -n` over all hooks + scripts; all plugin hooks executable.
- `prettier@3.9.4 --check .` (whole tree) — clean.
- `ruff check .` — clean.
- `scripts/ci-preflight.py` — **19/19 PASS** (ratchet merge-base; inventory
  staleness/schema/census/sweep/evidence/inception; dashboard/index/concepts-doc
  freshness; Copilot-package freshness; Codex-agents projection).
- `scripts/check-frontmatter.py` — clean (every agent has schema, `tools`, `model`,
  description ≤ 300 chars).
- `scripts/check-model-tier-fit.py` — clean. `scripts/check-model-tier-ratchet.py` —
  clean. `scripts/check-nested-dispatch.py` — clean (no shipped agent can dispatch).
- `scripts/check-gate-registration.py` — clean.

## 5. Findings

### 5.1 [P3] Codex hook generator does not honor `_SKIP` on the SessionStart lane — NEEDS DESIGN INPUT

- **Where:** `scripts/generate-codex-hooks.py` — `_derive_sessionstart()` (lines
  300–322), the `_SKIP` map (lines 124–184, entry at 180–183), and the skip-accounting
  loop (lines 420–423).
- **What (CONFIRMED, verified against source + the live `hooks.json`):**
  `routine-reserve-hook.sh` is listed in Codex's `_SKIP` map with a documented rationale
  — *"claude.ai Routines + Claude Code statusline data only; nothing to reserve or warn
  about on Codex."* But it is also registered in the canonical
  `plugins/ravenclaude-core/hooks/hooks.json` SessionStart block
  (matcher `startup|resume|clear|fork`), and `_derive_sessionstart()` wires **every**
  script in that block unconditionally, never consulting `_SKIP`. So the generated Codex
  config *includes* a SessionStart `routine-reserve-hook.sh`, contradicting the `_SKIP`
  intent. Because the script then appears in `wired_names`, the skip-accounting loop
  never records it as skipped, so `--check` reports it as accounted-for — the mismatch is
  **invisible to the gate** (silently-wrong output, not a "freshness fails forever"
  failure).
- **Asymmetry that makes it a bug, not a choice:** the three sibling generators
  (`generate-cursor-hooks.py`, `generate-gemini-hooks.py`, `generate-copilot-hooks.py`)
  route SessionStart through a `project()` path that *does* check `_SKIP`, so they
  correctly exclude `routine-reserve-hook.sh` on all lanes. Codex is the lone outlier.
- **Impact (low / benign):** the hook is fail-safe ("absent posture key → off"), so a
  stock Codex install no-ops. A Codex user who set `routine_reserve` would get the
  pointless claude.ai/statusline network work the skip reason explicitly warns against,
  plus an extra hook entry requiring a Codex hash re-trust.
- **Why this is deferred, not auto-fixed:** the two candidate fixes have **opposite**
  consumer behavior, and `_derive_sessionstart`'s own docstring ("every SessionStart
  hook … read directly off hooks.json's own SessionStart block") can be read as a
  *deliberate* decision to wire the whole manifest block regardless of `_SKIP`. Choosing
  requires knowing the authoritative intent, and the change regenerates a consumer-facing
  committed artifact (Codex config) that forces a hash re-trust. That is a design
  decision.
- **Decision needed — pick one:**
  - **Option A (recommended): honor `_SKIP` in `_derive_sessionstart`.** Make it skip
    scripts in `_SKIP` (and record them in the returned skipped-list so `--check` can see
    the resolution). Result: Codex matches the documented intent **and** the three
    sibling generators. This treats the `_SKIP` entry + sibling behavior as authoritative.
  - **Option B: accept the SessionStart wiring as intended.** Remove
    `routine-reserve-hook.sh` from Codex's `_SKIP` and correct the reason text to say it
    *is* wired on SessionStart. This treats the "wire every SessionStart hook" docstring
    as authoritative.
  - Either way, make `--check` able to *see* the resolution so the skip map cannot
    silently shadow a wired hook again, and regenerate + re-verify the committed Codex
    artifact and its gate/test (`test-gate155-codex-hook-env.sh` and the Codex projection
    freshness check) before merge.
  - *Recommendation: Option A* — the `_SKIP` entry states a concrete technical rationale
    and all three siblings already behave that way; Codex is the inconsistent one.

### 5.2 Security + correctness review of the per-tool-call hook scripts

Files read in full: `spectate-emit.sh`, `copilot-hook-adapter.sh`,
`cursor-hook-adapter.sh`, `guard-destructive.sh` (all 1959 lines), `guard-web-access.sh`,
`enforce-layout.sh`, `route-decision-review.sh`, and the sourced helpers `_emit-event.sh`,
`_scrub.sh`, `_portable.sh`.

**Bottom line: no P0/P1/P2.** The high-blast-radius matching logic is genuinely
well-defended — the catastrophe floor (`guard-destructive.sh`) uses pure `[[ =~ ]]` string
scanning (no `eval`/execution of the command), fails **closed** on preprocessor failure,
and its force-push / curl-pipe-shell / merge-bypass regex family is heavily patched with no
traced slip-through. `guard-web-access.sh`'s SH-F2 host-parse ordering was traced against
`@`/`#`/`?`/backslash confusion URLs and resolves correctly. `route-decision-review.sh`
fails safe to "ask the human" on every error path and its JudgeDeceiver reasoning-sanitizer
is sound. Four low-severity hardening items follow, each with the reviewer's honest
reachability caveat — **all surfaced, none auto-applied**:

**[P3 — arguably P2; see tie-break] `cursor-hook-adapter.sh:248` — a JSON-shaped deny is
dropped when `jq` is absent but `python3` is present (fail-open in a deny path).**
CONFIRMED by trace, narrow config. Shell-pretool honors `exit 2` unconditionally
(line 247), but the `hookSpecificOutput.permissionDecision=="deny"` path is gated on
`command -v jq` (line 248), while `_claude_stdin` falls back to `python3` when jq is absent
— so with jq absent / python3 present, a guard that denies via JSON-at-exit-0 (the
command-review tribunal / `thing-orchestrator`) fails **open** on Cursor. The deterministic
catastrophe floor (`guard-destructive.sh`, `exit 2`) is **unaffected**. Copilot's adapter
sidesteps this by requiring jq up front (line 73).
- *Fix:* detect the JSON deny with a jq-free fallback (e.g. grep for
  `"permissionDecision":"deny"`) before `exit 0`, mirroring the no-jq fallbacks used
  elsewhere.
- *Verify first (why this was not auto-applied):* the reviewer **did not trace into**
  `thing-orchestrator.sh` / `thing-decide.py`, so the **exact** emitted deny-JSON shape
  (spacing, nesting) the fallback must match is unverified. A security fallback that
  silently fails to match the real shape is worse than the documented gap — confirm the
  literal shape before writing the grep, then validate with
  `test-gate159-cursor-hook-adapter.sh`.
- *Panel-3 severity tie-break:* a security control failing **open** argues P2; the narrow
  trigger (Cursor host **and** jq-absent/python3-present **and** tribunal opt-in) and the
  unaffected catastrophe floor argue P3. Recorded as P3 pending the maintainer's severity
  call — this is the one item worth confirming the priority of.

**[P3] `spectate-emit.sh:44,57` — a large PostToolUse payload can `E2BIG` the python exec
and silently drop the Spectate event.** PLAUSIBLE (mechanism reasoned from Linux
`MAX_ARG_STRLEN` ≈ 128 KiB, **not executed**). Line 44 exports the payload as the env var
`SPECTATE_PAYLOAD`; line 57 execs python with it in the environment. A payload carrying a
large `tool_response` (big Read/Bash output) exceeds the single-env-var cap → `execve`
fails `E2BIG` → `|| exit 0` (+ `trap 'exit 0' EXIT`) swallows it → event dropped. Fails
safe (Spectate is observe-only, never blocks) so this is a completeness gap, not a safety
defect — but the dropped events are precisely the high-output calls.
- *Fix:* feed the payload on **stdin** rather than the environment — exactly what
  `guard-destructive.sh:288-293` already does to dodge this same `E2BIG` (its SH-F3 note).
  Validate with `test-spectate-emit.sh`.

**[P3] `copilot-hook-adapter.sh:81,83,208` — `sid` used unsanitized in a filesystem path
and exported as `CLAUDE_SESSION_ID`.** PLAUSIBLE, low reachability. `sid` is read from
`.sessionId` via jq with no sanitization (line 81); under `RAVENCLAUDE_DIAGNOSE=1` it builds
`…/.ravenclaude/runs/${sid:-unknown}` and `mkdir -p`s it (line 208), so a `sid` of `../../…`
would escape `runs/`. Low reachability because `sessionId` is **host-generated, not
model/tool-arg controllable** (not reachable via prompt injection), and every downstream
consumer re-sanitizes via `_ee_sanitize_session`. Defense-in-depth gap, not a demonstrated
exploit.
- *Fix:* run `sid` through the existing `_ee_sanitize_session` before line 83 and the diag
  path (the helper already strips the charset, caps length, rejects `.`/`..`).

**[P3] `guard-destructive.sh` — unquoted `for word in $seg` / `for w in $text` (e.g. lines
386, 460, 1059, 1222, 1331, 1466, 1548, 1796) enables pathname expansion during command
scanning.** PLAUSIBLE, **no traceable bypass** — the reviewer could not turn it into an
exploit (the dangerous anchors `git`/`merge`/`-X`/`DELETE`/`--admin`/`checkout` contain no
glob metacharacters, and a glob-mangled branch token fails `_is_safe_ref_token` → forced to
the ambiguous-sentinel → treated as dangerous). Code-smell / hardening only.
- *Fix (optional, low value):* `set -f` around the scanning section, or quote the loop
  subjects. **Caution:** this is the 1959-line catastrophe floor; any change here warrants
  its own focused PR with the full `test-guard-destructive-*` suite, not a drive-by edit —
  which is why it was not auto-applied for a non-exploitable smell.

_Out-of-target-set note from the reviewer: it did not trace `thing-orchestrator.sh` /
`thing-decide.py`; the Cursor fail-open item assumes the tribunal emits JSON-at-exit-0
denies, which its documented design states but which was not source-traced this pass._

## 6. Observations (not defects — context for the maintainer)

1. **Shell strict-mode is uneven, but this is largely by design — do NOT bulk-"fix" it.**
   155 `.sh` files lack `set -euo pipefail`. A blind sweep adding it would be a
   **regression**: many RavenClaude hooks are deliberately *fail-open* (e.g.
   `precompact-digest.sh`, `ask-on-ambiguity.sh` carry comments saying the omission is
   intentional) — adding `set -e` would make a safety hook fail *closed* and block tool
   calls. 86 of the 155 are test scripts. If the maintainer wants a consistency pass, it
   must be done per-file with the fail-open intent preserved, and would be a large diff
   warranting its own PR — not an autonomous change.
2. **Model-tier roster is heavily frontier-weighted.** `check-model-tier-ratchet.py`
   reports 434/623 agents (69.66%) on `opus`/frontier vs. 1 on `haiku` and 188 on
   `sonnet`. The ratchet gate *accepts* this (it only prevents *raising* the share), but
   the model-tier-delegation doctrine prefers "the cheapest tier the job survives,"
   reserving frontier for design/adjudication/merge-gates. A roster where ~70% sit on
   frontier is worth a deliberate cost review — a judgment call for the maintainer, not a
   gate failure. (No action taken; flagged for awareness.)
3. **Pre-existing uncommitted drift in `.claude/settings.json` (working tree only).**
   When this session's container started, `.claude/settings.json` already carried an
   uncommitted change (SessionStart bootstrap / posture drift): it empties the permission
   `allow` list (removing six Gmail read permissions) and adds
   `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH: "1"`, plus re-encodes some comment unicode. This
   was **not** authored by this review and is **not** included in this branch — it mutates
   the permission allow-list, a security-sensitive config change that is a human decision.
   Surfaced here so the maintainer can decide whether that drift should be committed,
   reverted, or is an expected artifact of the bootstrap hook.

## 7. Implemented fixes — and the bar for autonomous change

**None applied.** No finding cleared the bar for a safe autonomous fix in this unattended
run. The bar: **CONFIRMED (not PLAUSIBLE) + small/local + low regression risk + a single
verified-correct implementation + fully validatable with the repo's own gate tests.**

Why each finding fell short of it:

- **§5.1 (Codex `_SKIP`)** — the *fix direction* is a design-intent call (two candidate
  fixes, opposite consumer behavior) and it regenerates a consumer-facing committed
  artifact. Design input required.
- **§5.2 security items** — these are **security-critical guardrail hooks** in the
  flagship `ravenclaude-core` plugin; any edit forces a plugin version bump (triggering
  the repo's plan-mode-default for manifest changes) + a Copilot-package regeneration, and
  this repo's own governance routes security decisions to the human. Beyond that: three of
  the four are PLAUSIBLE / non-exploitable (so a fix would add guardrail code against an
  untraced path — against the proportionality discipline), and the one CONFIRMED item (the
  Cursor deny fail-open) depends on an **unverified** deny-JSON shape, so a fix could be
  silently wrong. Applying any of these unattended would be worse engineering than
  surfacing them with exact, ready-to-apply patches — which is what §5.2 does.
- **§3 (prettier)** — a false positive; the "fix" was reverted before any commit.
- **§6 observations** — by-design (strict-mode), a cost-posture judgment (model tiers), or
  a human config decision (settings.json drift). Not defects.

This is the honest outcome of a comprehensive review of a mature, heavily-gated
repository: **it is clean.** This report **is** the deliverable — the full categorized
review record plus five ready-to-apply recommendations and three open decisions for the
maintainer. Nothing here blocks a merge or a consumer `/plugin marketplace update` today.
