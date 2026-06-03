# Near-Guarantee Design — closing "assumption-as-fact" + "fail-to-learn" as far as honestly possible

> **How this was produced.** A design panel (Opus) proposed a "verification receipt" architecture; a **red-team panel** (Sonnet) attacked it and proved its "essentially guarantee" claim overpromised (it covered ~the registered-route + exact-phrase + commit-surface + agent-already-verified intersection — a small slice); **7 independent experts** then ruled the genuine conflicts. This document is the calibrated synthesis. It **supersedes the residual-risk section of `accuracy-and-learning-gap-closure-plan.md`** with a harder, and more honestly-scoped, design.
>
> **The motivating incident:** the agent concluded "the sandbox blocks the Mermaid renderer" from a buggy self-test and baked it into chat, a commit message, a **PR body, and a GitHub issue** — all false (the renderer worked). This design is judged by one question: *would it have stopped that false fact from reaching every durable surface, and captured the lesson?*

---

## 0. The honest answer to "how do you essentially guarantee it"

**You cannot guarantee the model's reasoning** — no hook reads chain-of-thought, and self-verification provably reduces-but-never-eliminates error (CoVe, self-consistency literature; a critic is itself stochastic — the incident *was* a self-authored verification that was wrong). So a guarantee can only come from **deterministic interception that doesn't depend on the model's cooperation** (AgentSpec's `trigger→check→enforce`; neurosymbolic guardrails "cannot be overridden" — retrieved 2026-06-03).

The move that earns the word "essentially" is therefore: **make the false fact unable to survive into any *durable* surface — and make the durable surfaces a near-complete set.** The incident used four surfaces — chat, commit, PR body, issue. Three of those four are interceptable by deterministic gates; only chat is not. So the honest, calibrated claim:

> **Tiered guarantee.** A false negative-capability claim is *deterministically blocked* from reaching a **commit, a push, a PR body, or an issue body** (when authored by an agent session), and *every detected* reversal is force-prompted into a captured lesson that is re-surfaced next session. **Chat is reduced-not-eliminated** (behavioral). We do not claim more — claiming the chat/reasoning surface is closed would be the exact over-claim this design exists to prevent.

What follows is engineered to that claim, with each rung labeled by what it actually earns.

---

## 1. The guarantee, tiered by what each layer earns

| Surface (the incident used ★) | Mechanism | Strength | Earns |
|---|---|---|---|
| **Commit message ★** | `grounding-receipt-gate.sh` as `commit-msg` git hook | Blocking (agent-scoped, C3) | **Near-guarantee** for registered claims; **falsifiability floor** for unregistered |
| **Push (commit range)** | same gate as `pre-push` | Blocking (agent-scoped) | same |
| **PR body ★ / issue body ★** | **`PreToolUse` hook on `mcp__github__create_pull_request` / `issue_write` / `add_issue_comment`** — scans the `body` param *before the call* (Claude Code PreToolUse: **exit 2 blocks**) | Blocking (agent path) | **Near-guarantee** for the MCP-authored path (the surface the incident actually used) |
| **`knowledge/`+`docs/` `.md`** | extend `claim-grounding-lint.sh` phrase family | Advisory→blocking on promotion (C6) | Detector now, gate later |
| **Chat answer** | sharpened CGP rule + scenario prior at the assertion moment | Behavioral only | **Reduced, not eliminated** (irreducible residual) |
| **`gh` CLI / non-agent committers** | git hook fires advisory for humans (C3) | Advisory | Norm-building, no bypass-training |

The two residuals that remain after this stack: **pure chat**, and **a determined agent calling the raw `gh` CLI / `--no-verify`** (mitigated, not closed — §5). Everything else the incident touched is a deterministic gate.

---

## 2. Mechanism #2 — "test before asserting", calibrated by the 7 rulings

### 2a. The gate is **claim-first**, the registry sets the *bar* (C1)
The gate fires on **any** negative-capability assertion (not only registered ones — that was the red-team's decisive point: ~95% of such claims have no registered route, and a registry-first gate leaves them behind a free `[unverified]`). What the registry changes is the **bar to pass**:

- **Registered capability** (has a canonical route in `.ravenclaude/capability-routes.yaml`, e.g. `mermaid-render → scripts/render-trees.py`): the claim passes only with a **`CONFIRMED_ABSENT` receipt** (§2b). *Near-guarantee* — and since the incident's route exits 0, no such receipt can exist → **blocked**.
- **Unregistered capability**: the claim passes only with a **structured-deferral receipt** — the **verbatim error**, its **classified mechanical cause** (`not-found` | `401` | `403` | `unreachable` | `unsupported` | `timeout`), and **≥2 distinct routes tried with their outputs**. This is the AGENTS.md "read the error, name the cause, try ≥2 routes" protocol, made blocking. *Falsifiability floor* — it doesn't prove the claim true, it proves it was non-trivially attempted and is auditable.

`[unverified — training knowledge]` **alone never satisfies the gate** (C1+C5); it must carry a claim-specific justification (§2d).

### 2b. The receipt cannot be laundered by a flaky route (C2)
`verify-capability.py` runs the **registered** canonical route (a buggy *self-authored* probe is not the registered route → cannot mint a valid receipt — this closes the incident's accelerant). Receipt schema:

```json
{"claim":"mermaid-render-blocked","route":"scripts/render-trees.py --self-test",
 "verdict":"CONFIRMED_ABSENT|FAILED_ONCE|PROBE_ERROR","consecutive_failures":3,
 "exit_codes":[1,1,1],"route_script_sha":"…","session_id":"…","minted_at":"…",
 "ttl_seconds":86400,"fingerprint":"sha256(route_mtime + key_env_vars)"}
```
- **`CONFIRMED_ABSENT` requires N≥3 consecutive failures** of the canonical route, all with exit codes in the route's declared *"genuine unavailability"* set. A single failure is `FAILED_ONCE` (insufficient — transients are common). A harness/probe crash is `PROBE_ERROR` and **never counts toward absence** (a buggy probe can't mint a "blocked" verdict — the incident's exact trap, now structurally impossible).
- The gate accepts a "blocked" claim **only** when `verdict==CONFIRMED_ABSENT`.

### 2c. Receipts are session-TTL'd + environment-fingerprinted (C7)
A receipt is valid only if `now − minted_at < ttl` (≈1 session / 24h, configurable) **AND** `current_fingerprint == receipt.fingerprint` (`sha256(route_script_mtime + sorted key env-vars present)`). A "blocked" receipt minted in a *broken* environment last Monday cannot bless a claim in a *working* environment today — the fingerprint mismatches → re-run forced. Stable routes (e.g., "is `gh` installed") still reuse within TTL, so slow routes aren't re-run every session needlessly.

### 2d. The `[unverified]` hatch is a justified, logged deferral — not a free suffix (C5)
For genuinely-unverifiable training-knowledge claims, `[unverified — training knowledge]` passes the gate **only if** it carries an inline, **claim-specific one-sentence justification** — *why* it can't be verified this session **and** *what route would verify it*. Each is logged to `hook-events.jsonl`; a templated/vacuous justification ("can't verify, training knowledge" pasted everywhere) is detectable as a rate and reviewable. High-blast/irreversible claims defer to a human regardless of marker. This raises the cost of the *reflexive* suffix specifically while taxing an honest one-off claim by one sentence — and it nudges the agent back to "name the cause + the verifying route," the behavior we actually want.

### 2e. Agent-scoped blocking; humans advisory (C3)
The git hook checks `CLAUDE_SESSION_ID` (+ `GIT_AUTHOR` fallback): **agent session → blocking**; human/Cursor/Codex commit → **advisory warning, exit 0**. Reason: humans legitimately cite SDK docs/changelogs (not receipts); blocking them trains `--no-verify` into a reflex, and a gate that trains its own bypass is worse than none. *(Caveat `[unverified]`: confirm `CLAUDE_SESSION_ID` is present in the hook env across commit modes before shipping.)*

### 2f. Block only where confidence is high; advisory-first elsewhere (C6)
- **Blocking from P1:** a phrase match **accompanied by a resolvable registered-route claim** (structured, low-FP — receipt lookup, not phrase fuzzing).
- **Advisory from P1:** the broader negative-capability **phrase family** (`is blocked`, `blocks the`, `refuses to`, `not supported`, `won't run`, `can't run`, `fails in the sandbox`, …) — high-variance, FP-prone. **Promote a tier to blocking only when its 30-day rolling FP rate ≤ 5% over ≥20 triggered commits.** A blocking gate with FPs trains bypass faster than an advisory one corrects.

### 2g. Make the honest path the lazy path (rung 4)
`verify-capability --claim X --route Y` runs the route, mints the receipt, **and prints the answer**: "✅ route exited 0 — your 'blocked' claim is contradicted; don't write it" or "⚠️ 3/3 failed → CONFIRMED_ABSENT receipt minted; you may assert blocked, citing it." The deny message is a **copy-paste fix** (the exact `verify-capability` command, claim/route pre-filled from the registry), not a scolding. Getting the receipt is less effort than crafting a justified `[unverified]` dodge — the gradient points at honesty.

---

## 3. Mechanism #1 — "learn from each mistake", honestly calibrated (C4)

The red-team killed the "deterministic capture" claim: Panel A's receipt-reversal signature only fires if the agent **already ran the honest verification** (got exit 0) and *then* still wrote "blocked" — which is **not** the incident's shape (the agent never ran `verify-capability`; a human corrected it in chat). So:

- **Deterministic *eligibility*, semi-deterministic *capture*.** A Stop/SessionEnd hook fires a `/postmortem` prompt when the transcript shows **(a)** a committed/posted negative-capability claim this session **with no clearing exit-0 receipt**, **AND (b)** ≥1 user turn after the claim. That conjunction is a fact about the transcript — computable with no NLU. Whether that user turn was *actually* a correction is a behavioral judgment, so the honest claim is **"deterministic eligibility + Stop-time-prompted capture," never "deterministic learning."** (The receipt-reversal arm is kept as a cheap union member for the rare verified-yet-denied case.)
- **Storage** (deterministic): `/postmortem` writes a Sága ledger line to `.ravenclaude/runs/mistakes/ledger.jsonl` (`{kind, claim, root_cause, correct_fact, guardrail_proposed, receipt_ref, session_id}`) **and** a `type: lesson` staging submission draining via the existing `review-staged-contributions` skill — no new review machinery.
- **Re-surfacing IS deterministic:** `capability-orientation.sh`'s SessionStart banner gains a **"RECENT LESSONS (N)"** line (derived counts + claim-keys only, never raw content — the existing injection-safety contract). Plus a scenario prior at the assertion moment (behavioral odds-shifter; the **gate in §2 is the deterministic backstop** if the prior doesn't fire).
- **Closing the loop onto the gate:** a lesson of kind "phrase-the-gate-should-have-caught" auto-drafts the exact phrase-family diff → routed through `review-staged-contributions` for a human to ratify (it edits an enforced surface). The mistake literally proposes its own gate-hardening.
- **Self-limit + loud failure:** the Stop-block self-limits (`max_blocks=3`, like `dod-gate.sh`) so it can never wedge a session — **but the force-allow emits an `ERROR`-level Sága event** so a silently-degraded gate is detectable (red-team Attack 10).

---

## 4. Defense-in-depth + honest residual estimate

**Independence is what makes residual math real** — N layers that all depend on the model cooperating are one layer. `[D]` = deterministic (model-independent); `[B]` = behavioral.

**Class 1 — false capability-claim reaches a durable artifact:**
`[B]` sharpened CGP rule · `[B]` scenario prior at assertion · `[D-advisory]` doc-lint phrase family · **`[D-block]` commit-msg gate** · **`[D-block]` pre-push gate** · **`[D-block]` PreToolUse MCP-body gate (PR/issue)** · `[D]` the receipt/structured-deferral the gates require.

> **Residual (honest):** for **commit + push + MCP-authored PR/issue** (the incident's persistent surfaces), residual ≈ **the gate's own defect rate + the justified-`[unverified]`-abuse rate** — both *observable* (logged), so a miss is a fixable bug, not a class of behavior. For **pure chat** and **raw-`gh`/`--no-verify`**, residual is **reduced, not eliminated** — bounded below by the model's reasoning-error rate × the fraction of assertions routed there. We put **no fabricated number** on the chat residual; a false precision there would be the very error we're closing.

**Class 2 — fail to learn from a *detected* mistake:**
`[D]` Stop eligibility-trigger (forces the prompt) · `[B]` the correction adjudication + `/postmortem` content · `[D]` ledger write · `[D]` SessionStart re-surfacing · `[D-draft]/[B-apply]` auto gate-hardening.

> **Residual (honest):** capture is **force-*prompted* deterministically** whenever a committed/posted capability-claim is followed by a user turn; whether a lesson is *well-distilled* is behavioral. Re-surfacing of whatever is captured **is** guaranteed. Mistakes of a *different shape* (a wrong financial assumption) leave no fingerprint and stay behavioral — we close **this class's** shape deterministically and say so.

---

## 5. Phased plan (every exit criterion is an `audit-gates.sh` fixture pair)

**P1 — receipt spine + the lowest-FP blocking surfaces.** `verify-capability.py` + skill + `capability-routes.yaml` (seed `mermaid-render`); receipt schema with `verdict`/`consecutive_failures`/`fingerprint`/TTL (C2,C7); `grounding-receipt-gate.sh` as **commit-msg, agent-scoped, blocking only on registered-route+receipt** (C1,C3,C6); **PreToolUse MCP-body gate** on `create_pull_request`/`issue_write`; doc-lint phrase family **advisory**; sharpened CGP rule + AGENTS.md mirror.
*Exit:* a commit/PR-body/issue-body "Mermaid is blocked" with no `CONFIRMED_ABSENT` receipt → **denied**; with a 3×-fail receipt → passes; an unregistered "API X unsupported" with a structured-deferral block → passes, without → denied; `verify-capability` on the working renderer prints "your blocked claim is contradicted." (Each with a must-fail half.)

**P2 — push surface + capture + re-surfacing.** `pre-push` gate; `learning-capture-gate.sh` Stop eligibility-trigger + self-limit + loud force-allow (C4); `/postmortem` → ledger + staging; SessionStart "RECENT LESSONS (N)"; enable `ravenclaude-core` scenarios + assertion-moment retrieval.
*Exit:* a session with a committed capability-claim + a later user turn and no postmortem → Stop **prompts**; banner shows "RECENT LESSONS (1)" leaking no raw content; structured-deferral fixtures pass/deny correctly.

**P3 — calibrate + harden the loop.** Promote a doc-lint/phrase tier advisory→blocking only against the **measured ≤5%/20-commit FP** (C6); auto-drafted gate-diff from a lesson → `review-staged-contributions`; surface the `unverified-bypass` rate + lessons on the dashboard's Urðr panel.
*Exit:* a documented per-surface graduation decision with the measured FP behind it; a "missed-phrase" lesson generates a diff that makes the previously-passing bad fixture fail (the loop hardens the gate); the bypass-rate metric renders.

---

## 6. The honesty checkpoint — the biggest way this still becomes theater

**Single biggest risk: the justified-`[unverified]` deferral degrades into templated boilerplate** (and, secondarily, structured-deferral blocks become copy-paste). The defenses are *observability, not prevention*: every `[unverified]`/structured-deferral pass is logged as a **rate**; a spike is a Níðhöggr-style debt signal; the auto gate-hardening loop turns caught-misses into new gate teeth. **But this only works if someone actually reads the rate** — so the audit itself is the load-bearing human step, and §5/P3 surfaces it on the dashboard precisely so it's hard to ignore. Second risk: a noisy gate gets disabled (false assurance > no gate) — defended by C6 (advisory-first + measured promotion) and C3 (agent-only blocking).

**The one claim this design will not make:** that chat or reasoning is guaranteed. It is not. The gates guarantee the false fact doesn't *survive* into commit/push/PR/issue; the Stop-trigger guarantees a detected reversal is *prompted* into capture; re-surfacing is guaranteed. Upstream of the first gate — the belief forming in chat — is *reduced* by a sharper rule, session-start salience, and an assertion-moment prior, and **honestly, that is reduction, not a guarantee.** Saying otherwise would be treating a hoped-for property as a verified fact — the precise error this whole design exists to make mechanically hard.

---

## Appendix — provenance
- Design panel (Opus) → red-team panel (Sonnet, which proved the "essentially guarantee" over-claim) → **7 independent expert tiebreaks** (C1 claim-first/registry-bar · C2 N=3 CONFIRMED_ABSENT · C3 agent-only blocking · C4 semi-deterministic capture · C5 justified-`[unverified]` · C6 hybrid blocking + ≤5% promotion · C7 TTL+fingerprint). Web-grounded 2026-06-03 in AgentSpec (arXiv 2503.18666), CoVe (2309.11495), self-consistency limits (2502.15845), neurosymbolic-guardrail and paved-road sources.
- Worked example throughout: the Mermaid-renderer false-"blocked" incident — including that the false fact lived in a **PR body + issue posted via MCP**, which is why the `PreToolUse` MCP-body gate (not just git hooks) is load-bearing.
- Items flagged `[unverified]`: `CLAUDE_SESSION_ID` presence in the hook env; the N=3 / 5%-FP / 24h-TTL constants (engineering rules-of-thumb to calibrate against this repo's measured rates). Plan only — no hook/rule/skill changed by this document.
