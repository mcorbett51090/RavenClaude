# Accuracy & Learning Gap-Closure Plan — "assumption-as-fact" + "learn-from-mistake"

> **Why this exists.** In a live session the agent concluded **"the sandbox blocks the Mermaid renderer"** and baked that false-fact into chat, a commit message, a PR body, and GitHub issue #231 — from **two same-root-cause failures**, the second of which was a *self-authored test that was itself miswritten* (it passed the puppeteer config as inline JSON to `mmdc -p`, which wants a **file path**, so `--no-sandbox` was dropped and Chromium refused to launch as root). On correct invocation — the way `scripts/render-trees.py` already does it — the renderer **worked** (Chromium cached, no network). **A single mis-configured route was treated as a capability verdict.** The user asked for two mechanisms: (1) *learn from each mistake*, (2) *don't treat an assumption as fact without testing it*. This plan, produced by a five-seat research panel grounded in the repo's actual machinery, closes the residual gap that `docs/accuracy-safeguards-build-plan-2026-05-29.md` deferred.
>
> **Status:** plan. Builds on the existing honesty stack — does **not** reinvent it.

---

## 1. Root cause — why the existing machinery didn't fire

The repo already has a dense honesty stack. The incident slipped through every layer for a *specific, mappable* reason:

| Mechanism (real) | Should have caught | Why it didn't |
|---|---|---|
| **Capability Grounding Protocol** §"try ≥2 routes / read the error before re-routing" (`ravenclaude-core/CLAUDE.md`) | Exactly this: a route failed → don't conclude the capability is absent. | **Behavioral only — no event sees model prose.** The agent skipped step 0 (diagnose the *actual* error) and never suspected its own test was the failing variable. |
| **Claim Grounding & Source Honesty, Rule 1** ("cite the this-session check or mark `[unverified]`") | The "sandbox blocks the renderer" claim entering durable artifacts un-verified. | Same behavioral ceiling — **and the agent *believed* it had verified** (it ran a test). Rule 1 guards against *absence* of grounding; here the grounding was **counterfeit** (a buggy negative test mistaken for evidence). |
| **`claim-grounding-lint.sh`** (PostToolUse Edit/Write/MultiEdit) | An absolute capability claim in a durable file. | **Four fatal scope-misses:** scans only `knowledge/`+`docs/` `.md` (not commit/PR/issue text); phrase set lacks `blocks`/`can't run`/`not supported`; opt-in; advisory. The false-fact landed in exactly the surfaces it can't see. |
| **`xc.unverified-capability-assertion`** (tribunal concern) | A seat ASKing on an unverified platform assumption. | Reviews **commands**, not chat/commit/issue text; `judgment_only`; inert unless command-review is on. |
| **`contribute-finding` / `review-staged-contributions`** (learning loop) | Capturing "we were wrong; here's the guardrail." | **Loop exists but has no mistake-shaped entry point and no trigger** — keyed on *positive* findings, manually invoked, consumer→marketplace oriented. |
| **`scenario-retrieval` + `check-runtime-state.md`** | A prior: "the renderer worked before — check before claiming blocked." | Scenarios are `power-platform`-only today; nothing captured the renderer-works fact; retrieval fires on plugin-domain questions, **not at the negative-assertion moment**. |

**The single deepest root cause:** *no mechanism distinguishes "the route (or my test of it) failed" from "the capability is absent" — and the one protocol that says exactly this is behavioral-only, while the one enforced surface (the lint) is blind to both the phrasing ("blocks") and the surfaces (commit/PR/issue) where the false-fact landed.* The buggy self-test is the accelerant: it **manufactured false positive evidence of a negative**, defeating Rule 1 (which assumes danger = *missing* grounding, not *fake* grounding).

---

## 2. Mechanism #2 — "test before asserting" (anti-assumption)

### 2a. The behavioral rule (the only lever for the chat surface) — **sharpen, don't add ceremony**
Add one tight CGP sub-clause in `ravenclaude-core/CLAUDE.md` (mirrored one-liner in root `AGENTS.md` for cross-tool reach), under the existing "read the error before you re-route" clause:

> **A failed attempt is evidence about the attempt.** Before asserting — in chat **or any durable artifact (commit message, PR/issue body, knowledge/doc file)** — that something is *blocked / can't / not supported / unavailable / doesn't work*, you must have run the **known-good / sanctioned invocation** this session and seen it fail. A failed attempt is first evidence about **that attempt** — the command, its flags, your test harness — not the capability. Before "blocked" leaves you: (1) confirm you invoked it the way the repo's own working code does (find the canonical invocation — e.g. `scripts/render-trees.py` — and match it); a self-authored probe that fails is evidence the *probe* is wrong until proven otherwise; (2) if a known-good path exists, run it **once**; (3) name the specific mechanical cause (exit code + stderr, not the headline). Absent that positive check, the claim is `[unverified]` — never a committed fact.

The cheap cognitive counter-pattern it encodes: *"My test failed. Is the test the variable? Run the path I know works (or the repo's own script) before I write that it can't."* This forces the known-good run **before** the assertion enters a durable artifact, so there's nothing written down to defend yet — neutralizing both single-failure generalization and sunk-cost. (This incident even had a free disconfirming witness — the user's *"it's worked before"* — that the rule makes the default first move, not a prompt.)

### 2b. The enforceable surfaces — **be honest about what a hook can/can't do**
| Surface | Mechanism | Enforceable? |
|---|---|---|
| `knowledge/`+`docs/` `.md` | **Extend `claim-grounding-lint.sh`** phrase-set with a *negative-capability* family (`is blocked`, `blocks the`, `refuses to`, `not supported`, `unsupported`, `unavailable`, `won't run`, `can't run`, `fails in the sandbox`, `the sandbox (blocks\|prevents)`); keep every existing FP guard. | Advisory, opt-in (closes phrase-miss only) |
| **Commit message** | New `grounding-artifact-lint.sh` wired as a git **`commit-msg`** hook (the message *is* a file = `$1`) — same regex; warn if a negative-capability phrase has no inline `[unverified]`/citation. | Advisory (first surface that sees commit text) |
| **PR / issue body** | A **pre-push** check over new commit messages + (where reachable) the PR body. *Honest caveat:* bodies posted via `gh`/MCP may never hit the working tree — then this surface is **behavioral-only** (the §2a rule). | Partial / behavioral |
| **Chat answer** | **Nothing** — no hook reads model prose. §2a rule + a `Stop`-hook salience nudge (`grounding-stop-nudge.sh`: if a session-produced artifact carries a negative-capability claim without a citation, emit one Stop-time reminder). | Behavioral + advisory nudge |

**Enforceable = advisory phrase-detection on durable surfaces. Irreducibly behavioral = the chat assertion, the *decision* to run the known-good path, and telling a buggy test from a real failure.** Every new hook header must state what it *cannot* see (the existing lint's HONEST-SCOPE discipline). **False-positive budget:** "blocks"/"not supported" appear in legitimate guardrail prose all over this repo — so advisory-only by default, reuse all suppressions, and **corpus-grep + tune before shipping**; if it can't hit **< ~1 nag / legit doc-session**, narrow the phrase set rather than ship noise.

---

## 3. Mechanism #1 — "learn from each mistake" (the loop that *closes*)

A logged lesson nobody reads is theater. The loop must (a) **trigger on the correction moment**, (b) **store durably**, and (c) **change future behavior**.

**3a. Trigger — on correction, not on memory.** The detectable signal is *agent asserted a capability fact → user contradicted → re-verification reversed the agent.* Bolt a `/postmortem` (alias `/mistake`) skill onto CGP's existing "verify before you yield" clause: *when a user correction reverses a consequential claim you already wrote into a durable artifact, run `/postmortem` before moving on.*

**3b. Store — two tiers, reusing existing substrate (no new top-level dirs).**
- **Tier 1 — Sága mistake ledger:** one JSONL line to `.ravenclaude/runs/mistakes/ledger.jsonl` (sibling of the decision-review substrate) — `{kind, claim, surfaces, root_cause, correct_fact, guardrail, session_id, ts}`. Additive, fail-safe, queryable.
- **Tier 2 — distil into the existing staging loop:** `/postmortem` also emits a `type: lesson` staging submission (pre-filled from the ledger) into `docs/staging/incoming/`, draining through the **already-built** `review-staged-contributions` skill into `docs/memory-bank/lessons-learned.md`. No new review machinery — its `What we tried / Why it failed / What works` fields *are* the postmortem shape.

**3c. Close the loop — each mistake routes to ONE behavior-changing output:**
1. **Regex/phrase edit** — if the false-fact used a phrasing the lint *should* catch, propose the exact addition to the grounding lints. (This case → add `blocks the`, `refuses to launch`, `fails in the sandbox`.) Tightest loop: a mistake literally edits the enforced surface.
2. **A scenario prior injected at the assertion moment** — promote the corrected fact to a `scenario` ("the Mermaid renderer via `render-trees.py` works offline with cached Chromium; a bare `mmdc -p '<inline-json>'` drops `--no-sandbox` and fails — that failure is the *test*, not the capability"), and extend `scenario-retrieval` to fire **before a negative capability assertion**, not only on plugin-domain questions. (Requires enabling the scenarios bank for `ravenclaude-core` — already a planned v0.2.0 step.)
3. **A CLAUDE.md rule sharpening** — only when a *missing rule* is revealed (as here: §2a). Used sparingly (no-sprawl).

**The closure that makes it impossible to miss:** extend the SessionStart banner (`capability-orientation.sh`) with a **"recent lessons (count)"** line read from the ledger — derived counts only, never raw content (its injection-safety contract). Mistake → ledger → (lint edit | scenario | rule) → surfaced at next session-start **and** at the assertion moment via scenario-retrieval.

---

## 4. Phased plan

| Phase | Deliverables | Advisory/Blocking | Exit criteria |
|---|---|---|---|
| **P1 — rule + cheapest enforceable wins** | CGP §2a sub-clause + `AGENTS.md` mirror; extend `claim-grounding-lint.sh` phrase-set (+ corpus-grep tune + new `audit-gates.sh` fixture pair); `/postmortem` skill writing Tier-1 ledger + Tier-2 staging, hooked to the "verify before yield" clause. | Advisory | Lint nags on negative-capability phrasing in a fixture, silent on the FP corpus (< ~1 nag/session); `/postmortem` yields a valid ledger line + drainable staging file. |
| **P2 — artifact surfaces + loop closure** | `grounding-artifact-lint.sh` as `commit-msg` hook + pre-push; `grounding-stop-nudge.sh` in the Stop lane; enable `ravenclaude-core` scenarios + extend `scenario-retrieval` to the negative-assertion moment; SessionStart "recent lessons (count)" banner line. | Advisory (opt-in blocking) | A committed negative-capability claim w/o citation nags; a captured mistake surfaces as a count next session; a fixture question "is the renderer blocked?" surfaces the renderer-works scenario with an `[unverified]` preamble. |
| **P3 — calibration + optional teeth** | Mistake-lessons on the dashboard's Urðr/lineage column (read-only, existing endpoint pattern); review FP/usage telemetry; per-surface advisory→blocking decision; *optionally* a `judgment_only` tribunal concern for commit/issue commands — **only if telemetry proves the advisory layer insufficient (don't build speculatively).** | Mixed | Lessons visible in dashboard; a documented graduation decision per surface; no new blocking gate without telemetry. |

---

## 5. Top risks
1. **False-positive fatigue** (highest) — "blocks"/"not supported" are common legitimate prose. Advisory-only default; reuse suppressions; mandatory corpus-grep tune; **narrow rather than ship noise** (a channel the agent learns to ignore is worse than the gap).
2. **Ceremony that gets ignored** — `/postmortem` must fire on the correction moment (bolted to the CGP clause), auto-emit both ledger + staging (zero manual formatting), or it won't run just-after-being-wrong.
3. **Enforcing the unenforceable** — the hooks nag on *durable phrasing*, blind to chat and to mis-grounded-but-correctly-phrased claims. Keep every hook's HONEST-SCOPE header; never overstate coverage.
4. **The irreducibly-behavioral residue is the real root cause** — suspecting your own test and running the known-good path is a reasoning move no hook catches. §2a *shifts the odds* (sharper rule + session-start salience + scenario prior at the assertion moment + advisory nags); it does **not** guarantee closure. Claiming otherwise would be the very over-claim we're fixing.
5. **Scenario-bank scope creep** — keep the negative-assertion trigger narrow; the existing `review-staged-contributions` gate guards promotion.

---

## 6. Open questions
1. Phrase-set precision vs recall on *this* corpus — tunable to < ~1 FP/session, or drop from the lint and leave to the rule + commit-msg surface?
2. Can the pre-push lint reliably see PR/issue **bodies** built via `gh`/MCP before posting? If not, concede that surface is behavioral-only.
3. `/postmortem` auto-fire vs prompt ("this looks correctable — run /postmortem?") — where's the line between capture-everything and capture-fatigue?
4. Of the three loop-closure outputs, which should `/postmortem` default to — and should the regex-edit one *always* require maintainer review (it edits an enforced surface)?
5. Cross-tool reach: capture half ports via staging files; do the SessionStart banner + scenario-retrieval-at-assertion survive for Cursor/Codex reading only `AGENTS.md`, or does the *injection* half degrade to Claude-Code-only?

---

## Appendix — provenance
- Five-seat research panel (Opus) grounded in `ravenclaude-core/CLAUDE.md` (CGP + Claim-Grounding), `AGENTS.md` (Accuracy discipline), `hooks/claim-grounding-lint.sh` + `hooks.json`, `skills/{contribute-finding,review-staged-contributions,scenario-retrieval}`, `best-practices/check-runtime-state.md`, and the prior `docs/accuracy-safeguards-build-plan-2026-05-29.md` (this plan closes its deferred Open Q #3 + the commit/PR/issue surfaces it never scoped).
- **Worked example used throughout:** the Mermaid-renderer false-"blocked" incident in this session — including its own resolution (the renderer works; the real bug was invalid Mermaid in 4 trees, diagnosed by testing each block individually rather than assuming).
- This is a plan, not an implementation. No hook, rule, or skill has been changed by this document.
