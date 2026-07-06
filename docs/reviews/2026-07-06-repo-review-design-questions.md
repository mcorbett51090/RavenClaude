# Repo review 2026-07-06 — design questions (needs human input)

Companion to PR #563 (the mechanical P1–P3 fixes). This doc holds the issues the
three-panel review confirmed as **real** but that require a **design decision**,
not a mechanical fix — plus the one candidate the review **rejected**, recorded so
it isn't re-surfaced next run.

## Panel process (for provenance)

- **Panel 1 (find)** — 10 parallel expert finders over scripts, the ravenclaude-core
  engine/hooks, CI, manifests, and plugin validator hooks. 23 candidates.
- **Panel 2 (validate)** — confirmed/rejected each against the P0–P3 rubric, added
  impact + effort. Rejected 1 (below). Re-graded several security findings.
- **Panel 3 (tie-break)** — 3 independent seats adjudicated the 4 contested-priority
  findings for calibration. Consensus: guard-destructive cmd-subst = **P1** (not the
  P0 one panel proposed), banner injection = **P1**, web-access flow-style = **P2**,
  guard-destructive no-jq = **P2**.

---

## OPEN — needs a decision

### D1 (P1) — PreToolUse "anti-pattern smell" hooks are dead on new-file writes

**What.** A class of vertical advisory hooks are registered `PreToolUse` on
`Edit|Write|MultiEdit` but read the target file **from disk** via
`$CLAUDE_TOOL_FILE_PATH`. At PreToolUse time the tool has not run yet, so:

- a **new file** created by `Write` does not exist on disk → the `[[ ! -f "$file" ]]`
  guard exits 0 and nothing is ever inspected (the common "write new code" path);
- an **Edit** reads the **old** pre-edit content → a smell newly *introduced* by the
  edit is invisible.

Net: these content validators are effectively dead on the exact path they exist to
guard. By contrast `finance` and `power-platform` wire the equivalent hooks as
`PostToolUse`, where the new content is on disk — proving this is a fixable wiring
inconsistency, not a platform limit.

**Affected (PreToolUse + read-from-disk), confirmed by Panel 1 + spot-checked by Panel 2:**

| Plugin | Hook | Line |
|---|---|---|
| applied-statistics | `hooks/flag-statistical-smells.sh` | 28 |
| geospatial-engineering | `hooks/flag-geo-smells.sh` | 31 |
| email-engineering | `hooks/flag-email-smells.sh` | 23 |
| api-engineering | `hooks/check-api-anti-patterns.sh` | 24 |
| auth-identity | `hooks/check-auth-identity-anti-patterns.sh` | 13 |
| data-platform | `hooks/flag-data-platform-smells.sh` | 29 |
| database-engineering | `hooks/check-database-engineering-anti-patterns.sh` | 9 |
| cloud-native-kubernetes | `hooks/check-cloud-native-kubernetes-anti-patterns.sh` | 9 |
| optometry-eyecare-practice | `hooks/check-eyecare-billing-smells.sh` | 9 |

(Working precedent to copy: `plugins/finance/hooks.json` and
`plugins/power-platform/hooks.json` register their content hooks as `PostToolUse`.)

**Why it's a design call (the tradeoff).** The two fixes are not equivalent:

- **Option A — re-register `PreToolUse` → `PostToolUse`.** Simplest; matches the
  working precedent; the hook sees the real post-write content. **Cost:** PostToolUse
  **cannot block** — it can only log/advise. Several of these hooks support a
  `*_STRICT=1` mode that *blocks* via exit 2 (e.g.
  `flag-statistical-smells.sh:107-111`). Moving to PostToolUse **silently drops the
  strict-blocking capability** for those consumers.
- **Option B — keep `PreToolUse`, stop reading disk.** Parse the *pending* content
  from the PreToolUse stdin JSON (`tool_input.content` for Write,
  `tool_input.new_string` for Edit) and lint that. **Cost:** more code per hook, a
  MultiEdit shape to handle, and each hook diverges from the simple `grep $file`
  form; needs a shared helper to stay maintainable across ~9 plugins.

Either way it touches ~9 plugins + a version bump each, so it wants a single
consistent decision before the sweep.

**Recommendation.** **Option B behind a shared helper** — keep the blocking
capability (which is the whole point of `*_STRICT`) and actually inspect the content
being written. Concretely: add a small `_read_pending_content.sh` helper in
ravenclaude-core that emits the pending text from the stdin JSON (Write/Edit/MultiEdit),
source it in each hook, and grep that instead of `$file`. If the appetite is only for
advisory (non-blocking) smells, **Option A** is far cheaper and is a legitimate call —
but it should be made explicitly, knowing STRICT blocking goes away.

**Questions for you:**

1. Do any consumers rely on `*_STRICT=1` **blocking** for these vertical smell hooks?
   If yes → Option B. If "advisory is fine" → Option A is much cheaper.
2. Sweep all ~9 in one PR, or start with a 1-plugin reference implementation
   (say `applied-statistics`) and template the rest?

---

## REJECTED — recorded so it isn't re-surfaced

### R1 — `route-decision-review.sh` high-blast heuristic "not enforced"

Panel 1 flagged that `route-decision-review.sh` computes an `hb` (high-blast)
heuristic (lines 99–100, commented "belt + suspenders") but never uses it to
independently refuse to auto-resolve — so a binding verdict could, in theory,
auto-resolve a high-blast question.

**Panel 2 traced the full path and rejected it:** `route-decision-review.sh:107`
threads `hb` into the engine as `high_blast`; `thing-decide.py:520-523` computes
`effective_high_blast = high_blast or _screen_high_blast(question, context)` and
forces `verdict = "defer"` whenever it is true, which makes `binding` false
(`binding = mode == "binding" and verdict in {"yes","no"}`). So the shell's
`if binding==true` auto-resolve branch **can never fire on a high-blast question**
today — the invariant holds by composition through the engine, not a redundant shell
gate. The finding describes a scenario the current code structurally prevents.

It remains a legitimate *defense-in-depth* suggestion (short-circuit on the shell's
own `hb` to survive a future regression in `thing-decide.py`), but that is hardening
for a hypothetical, not a present bug — so it was not implemented. Noting here so a
future review doesn't re-raise it as new.

---

## Everything else

The other 21 confirmed findings were mechanical and are implemented in PR #563
(2 P1, 7 P2, 12 P3), each backed by a bidirectional gate fixture where it guards
behavior. `audit-gates.sh`: 502 pass, 0 fail, 2 skip (offline-only).
