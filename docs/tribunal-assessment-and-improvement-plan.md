# Command-review tribunal ("the Thing") — assessment & improvement plan

_Two-expert review, 2026-05-26. Expert 1 = firsthand reviewer (implemented T3). Expert 2 = independent senior security/systems architect (fresh read). Each produced a gap analysis + score; the two were then reconciled, with the firsthand reviewer verifying Expert 2's sharpest claims line-by-line. Assessed: `ravenclaude-core` tribunal as of T3 (v0.25.0)._

## Architecture summary

The Thing is an opt-in `PreToolUse(Bash)` gate layered on the comfort-posture permission system. When a command's category carries `thing: on`, `thing-orchestrator.sh` (the "Lawspeaker") adjudicates instead of interrupting the user:

1. **Short-circuit** — one `grep` on the posture file; no toggled category → exit 0 (true no-op for non-adopters).
2. **Routing + config** (`thing-decision.py`) — classify into a comfort-posture category via the shared `EMISSIONS` table, read the toggle, resolve panel config (precedence `comfort-posture.yaml command_review:` > `thing.yaml` > defaults), call `thing-concerns.py`.
3. **Deterministic screen** (`thing-concerns.py`) — regex `triggers` match candidate concerns; `pre_llm_deny` concerns (inline secret, injection shape, `curl|sh`, force-push) deny **before any model runs**; severity routes seats (critical→Forseti+Heimdall, high→all three, else→Mímir).
4. **Parallel seat fan-out** — each seat is `thing-seat.sh` via `claude -p`, per-seat `timeout`, bounded by a panel `setsid` watchdog (~75 s internal deadline, under the 90 s hook timeout to beat the platform's fail-*open*-on-timeout).
5. **Aggregation** — abstention gate → injection override → split/low-confidence escalation to Thor → unanimous tally → **EDIT re-validation** (`concerns(revised) ⊆ concerns(original) − {cited}`) → critical-concern veto backstop.
6. **Sága log** — best-effort per-verdict JSON under `.ravenclaude/runs/thing/`.
7. **Emit** the Claude Code verdict (`updatedInput` on EDIT). Fail-closed posture is per-category (deny for high-stakes, ask for read-only). Live for `shell_readonly`, `shell_remote_mutate`, `shell_code_exec`.

The state machine is coherent and the design doc is unusually honest about substrate constraints. This is a well-engineered T3 skeleton; the weaknesses below are about the **deterministic security primitives** (triggers, the prompt envelope) and the **injection path**, not the scaffolding.

---

## Expert 1 — firsthand assessment

### Gap analysis

- **Routing/aggregation:** criticals route to Forseti+Heimdall with **no Mímir** — yet Mímir is the EDIT-proposing seat, so EDITs on criticals are under-served. Unanimous-EDIT takes the first convened seat's edit by convening order (no merge). Thor sees peer verdict summaries, not full transcripts (acceptable simplification).
- **Seat sandboxing (security):** seats run `claude -p` with **no tool restriction**. `THING_SEAT_ACTIVE=1` prevents tribunal recursion and `guard-destructive` still fires, but a prompt-injected seat is not technically prevented from issuing tool calls. Defense-in-depth says run seats with tools disallowed.
- **Triggers:** matched against the raw string only; `sce.embedded-base64-payload`'s design intent (base64-decode + recursive concern check) is **unimplemented**; obfuscation/indirection evades regex triggers (the LLM seats are the real reviewers — the deterministic layer is shallow).
- **Cost/latency:** up to 4 `claude -p` calls per reviewed command; no caching/rate-limit; `shell_readonly` review is economically a foot-gun (every `cat`/`ls` becomes a multi-model round-trip).
- **Fail-closed:** strong overall, but a missing `thing-decision.py` emits **ask** even for high-stakes categories (the category posture is lost with the helper that knows it).
- **Testing:** Gate 14 covers the orchestration plumbing well via mocks, but **judgment is untested** (no live-seat coverage by necessity), triggers have no FP/FN unit tests, and `pre_llm_deny` is only exercised for the injection case (not force-push/`curl|sh`/secret).

### Score (Expert 1)

| Dimension | Weight | /10 |
|---|---:|---:|
| Orchestration & aggregation correctness | 20 | 7.5 |
| Security & prompt-injection robustness | 25 | 6 |
| Trigger determinism (FP/FN) | 15 | 6 |
| EDIT-safety invariant | 10 | 8 |
| Fail-closed behavior | 10 | 8.5 |
| Cost / latency | 5 | 6 |
| Observability / audit | 5 | 7 |
| Testing coverage | 10 | 6.5 |

**Weighted total ≈ 68 / 100** — solid fail-closed scaffolding; not yet a trustworthy autonomous safety gate because the LLM-judgment layer is untested and the deterministic layer is shallow.

---

## Expert 2 — independent assessment

### Gap analysis (verbatim highlights)

- **Prompt-injection robustness (weakest, weight 15, scored 4):** the adversarial envelope uses a **fixed literal delimiter** (`</untrusted command>`) — a command containing that literal can break out into instruction context (canonical delimiter injection). The injection-watcher (Heimdall) runs on the **weakest model** and is **absent on the low-severity path** (Mímir-only). §B.9.5 ("the Thing cannot disable itself") is **unimplemented** — nothing stops an ALLOW/EDIT of a command that writes `comfort-posture.yaml`/`thing.yaml`/`hooks.json`.
- **Trigger determinism (weight 12, scored 4):** `xc.secret-in-command`'s `'(^|\s)-p\S{6,}'` is a false-positive `pre_llm_deny`; `xc.no-undo`'s force regex lacks the `(?!-with-lease)` lookahead that `srm.force-push` has (the two concerns disagree on `--force-with-lease`); `sce.curl-pipe-shell` only catches a direct pipe (`curl … && sh /tmp/x` evades it); the base64 trigger `[A-Za-z0-9+/]{100,}` is a broad FP magnet and never decodes.
- **Classification holes:** leading-segment/prefix-literal matching misses env-var prefixes (`LS_COLORS=x ls`), absolute interpreter paths (`/usr/bin/python3`), `sudo`/`env`, and `git -c … push` → category `None` → silent fall-through (coverage hole, not a fail-open).
- **Fail-closed:** missing decision helper emits `ask` for high-stakes (loses category posture); watchdog kill can orphan a `claude` child if `setsid` is absent.
- **Observability:** Sága log is **silent on failure** (`|| true`) — a verdict can emit with no audit record; raw seat `reasoning` is interpolated into the user banner unbounded.
- **Parsing:** `grep -o '{.*}' | head -1` on seat output is greedy and mis-parses a verdict whose `reasoning` contains `}`.
- **Testing:** no FP fixtures, no real-seat-parse test, classification holes untested.

### Score (Expert 2)

Weighted across 10 dimensions (architecture 8, routing 6, aggregation 7, **injection 4**, **triggers 4**, EDIT-invariant 7, fail-closed 8, cost 6, observability 7, testing 6): **≈ 61 / 100.** "A solid, fail-closed-by-default skeleton whose deterministic security primitives are not yet trustworthy enough to match the confidence the design language projects."

---

## Reconciliation (firsthand verification of Expert 2's claims)

**Confirmed valid** (verified against the committed code): the envelope delimiter is a fixed literal (breakout risk); §B.9.5 self-protection is **not enforced for the live Bash categories** — the `fe.claude-dir-write` / `fe.ravenclaude-dir-write` concerns exist (catalog lines 214–232) but live under the non-live `file_edit_project` category, carry **no triggers**, and key off Edit/Write, so a `shell_code_exec` command that writes those files via `python3 -c "open(...)"` is not deterministically blocked; `xc.no-undo` (line 116) lacks the lookahead that `srm.force-push` (line 397) has, so `git push --force-with-lease` trips it; `curl … && sh` evades the direct-pipe trigger; the classification holes are real; the missing-helper→ask posture loss is real; the greedy JSON parse and silent Sága failure are real; Heimdall's placement (weakest model, absent on the low-severity path) is real.

**Corrected (Expert 2 overstated three points):**

1. **`-p\S{6,}` false-positives are narrower than stated.** The pattern needs **6+ non-space chars attached to `-p`**. Expert 2's examples don't qualify: `tar -pcvfz` (4), `ssh -p2222` (4), `ps -p12345` (5) — **none match**. Real false-positives require longer attached runs (`-private`, `-pdflatex`, heavily-combined `tar` flags). The fix still stands (any FP on a `pre_llm_deny` concern is a hard deny), but the everyday-flag frequency was overstated.
2. **The broad base64 trigger causes extra seat _cost_, not a hard deny.** The critical-concern veto backstop (orchestrator line 285) keys off `has_critical`, which is computed from the **seats' cited concerns** (`cited_ids`, line 215), not the deterministic regex match. A legitimate long token routes to two seats (cost), but if the seats don't cite it, the command is still **allowed**. Expert 2's "can only be EDITed or denied, never allowed" is incorrect.
3. **A 1-vote panel is _not_ treated as a 3-0 consensus.** The abstention gate (line 200, `n_abstain ≥ 2`) fires first: with 3 seats convened and 2 abstaining, it returns the fail-closed posture verdict. The single-vote-decides case only occurs in the **intended** low-severity single-seat (Mímir-only) routing.

**Reconciled score: ≈ 63 / 100.** The two reviewers agree on the shape — strong fail-closed scaffolding, weak deterministic security primitives + injection path. After the corrections, two of Expert 2's deductions soften, but the core security gaps (envelope breakout, self-protection, Heimdall placement, secret-regex sloppiness, classification holes) are genuine and pull the weighted security/trigger dimensions down. The Thing is good for **early-access / opt-in validation**, not yet for high-stakes autonomous reliance.

---

## Consolidated improvement plan

### Must-fix (security / correctness)

1. **Harden the adversarial envelope.** Per-call **random nonce** delimiter (`<untrusted-{nonce}>`), strip/escape any literal delimiter in the command, and extract heredoc/env-value bodies into their own nonce-tagged blocks (design §B.9.2). Test: a command containing the literal closing tag. _(Expert 2; highest security leverage.)_
2. **Implement §B.9.5 self-protection** as a `pre_llm_deny` trigger for any command (any live category, incl. `shell_code_exec`) that writes `comfort-posture.yaml`, `thing.yaml`, `hooks.json`, `hooks/thing-*`, or `scripts/thing-*`. _(Expert 2.)_
3. **Tighten `xc.secret-in-command`.** Replace `'(^|\s)-p\S{6,}'` with an anchored credential shape (`--password[=\s]\S+` + scoped DB-client forms). Add a Gate-14 fixture asserting a benign flag is **not** pre-denied. _(Both — a gate that false-denies everyday flags gets disabled by its users.)_
4. **Always screen for injection.** Convene Heimdall (or at least run the pre-LLM injection regex) on **every** reviewed command, not just high/critical, and move Heimdall off the weakest model. _(Both.)_
5. **Sandbox the seat.** Run `claude -p` with tools disallowed so a prompt-injected seat cannot issue tool calls (defense-in-depth beyond `THING_SEAT_ACTIVE` + `guard-destructive`). _(Expert 1.)_
6. **Reconcile the force-push regexes.** Give `xc.no-undo` the same `(?!-with-lease)` lookahead as `srm.force-push`. _(Expert 2.)_
7. **High-stakes helper failure → deny, not ask.** Recover the category on partial failure, or default unknown-but-toggled high-stakes categories to deny. _(Both.)_

### Should-fix

8. **Close classification holes:** strip leading env-var assignments + `sudo`/`env`/absolute-path prefixes before EMISSIONS matching; normalize `git -c … push`; add fixtures. _(Expert 2.)_
9. **Replace the greedy `grep -o '{.*}'`** seat-output parse with a `jq`-based last-JSON-object extractor; fixture with `}` inside `reasoning`. _(Expert 2.)_
10. **Make Sága-log failure loud:** if the audit write fails, downgrade the verdict to ask/deny rather than emitting an unrecorded allow. _(Expert 2.)_
11. **Convene Mímir on criticals** (so EDITs on criticals are served), or document that criticals are deny/Forseti-edit only. _(Expert 1.)_
12. **Unit-test the triggers** (FP/FN corpus) + `pre_llm_deny` firing for force-push/`curl|sh`/secret (not just injection). _(Both.)_
13. **Bound/escape interpolated seat `reasoning`** in user-facing banners. _(Expert 2.)_

### Nice-to-have

14. **base64 decode + recursive concern check** for `sce.embedded-base64-payload`, and narrow the broad 100-char match to cut needless 2-seat escalation cost. _(Both.)_
15. **Caching / bypass-list / session-fatigue counter** (already roadmapped T5).
16. **Dashboard YAML parse-back** so saved panel config survives reload. _(Expert 2.)_
17. **CI assertion** that every live category's concerns carry triggers (so routing can't silently collapse to Mímir-only). _(Expert 2.)_
18. **Persist per-seat full verdict JSON** in the Sága log for forensics. _(Expert 1.)_

**Highest leverage:** #1 (envelope) and #2 (self-protection) for security; #3 (secret-regex FP) for adoption.
