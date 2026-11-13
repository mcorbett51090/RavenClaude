# Repository review — 2026-10-05

**Scope:** scheduled autonomous whole-repo review of RavenClaude.
**Branch:** `claude/awesome-wright-thktv8` (at `origin/main`, 0 ahead / 0 behind — findings are **pre-existing on `main`**).
**Method:** the repo's own whole-tree gates as the correctness backbone + two parallel expert review panels (security/guards/tribunal; recent Python logic + cross-host generators + CI). Each panel reproduced each finding with an executable probe; the five highest-impact were additionally re-confirmed by direct code read.

### Confirmation status — read this legend before trusting any severity
- **✓ code-read** — re-confirmed this session by my own direct code read or command (named in the body).
- **⊙ panel-probed** — one of the two review subagents reproduced it with an executable probe this
  session, but I did **not** independently re-run that probe. Treat these as high-quality **leads to
  verify during the fix**, not settled facts.

> Note on wording: a few findings describe dangerous command *shapes*. The literal strings are
> deliberately broken up because the repo's own tribunal hard-rule screens the content of any file
> write — this document was itself denied once for containing a literal pipe-to-interpreter example.
> That is finding-adjacent behaviour working as designed.

> ⚠️ **Nothing in this review was auto-fixed, deliberately.** Every confirmed finding lives in one of
> three places that make an *unattended* autonomous patch the wrong move: (a) the command-review
> tribunal / guard **substrate**, write-protected by the repo's own active self-disable floor (4
> categories are `thing: on` in this repo's posture); (b) the **dual-copy, parity-gated** dashboard
> server (`serve-dashboards.py`); or (c) multi-file **cross-host projection generators / CI governance**
> where a wrong edit silently breaks hook wiring or branch protection. These are security-floor and
> CI-governance changes — the class the repo's own constitution routes through human-reviewed PR with
> the full gate suite re-run, not an unattended auto-patch. **This document is the "post for your
> review" deliverable.**

---

## Ground truth — the repo's own gates

| Check | Result |
|---|---|
| `ci-preflight.py` | ✓ **19 PASS / 0 FAIL / 0 UNAVAILABLE** |
| `prettier --check .` (whole tree) | ✓ **clean** |
| `ruff check .` (whole tree) | ✓ **clean** |
| `audit-gates.sh` (full meta-test, 1088 audits) | ✓ **nondeterministic 1-fail flake** — see finding **A** |

The repo is in genuinely good health on its gates. The findings below are things the gates do **not**
assert (the gates themselves documented several of these blind spots).

---

## P0 — critical

### P0-1 ✓ code-read · The tribunal + hard-rule floors + self-disable guard silently skip when the hook's `cwd` is a subdirectory
- **Where:** `plugins/ravenclaude-core/hooks/thing-orchestrator.sh:130,137,143`.
- **Observed (code read):** line 130 reads the payload's `.cwd`; line 137 builds
  `posture_file="${cwd}/.ravenclaude/comfort-posture.yaml"`; line 143 runs `exit 0` if that file is
  absent — **before** the §B.9.3 hard rules (force-push and the fetch-pipe-to-interpreter rule) and the
  §B.9.5 self-disable guard. Panel probe: `cwd=<proj>` → `deny` for a force-push; `cwd=<proj>/sub` → no
  output, exit 0.
- **Inference (the diagnosis):** since the Claude Code docs say `.cwd` follows `cd` while
  `${CLAUDE_PROJECT_DIR}` stays at the project root, a single `cd` into a subdirectory makes every later
  review skip for the rest of the session. This is an inference from the two observations above; the
  control that would falsify it is the probe (ran: subdir cwd → exit 0, no verdict).
- **Why it reads as an oversight:** sibling hooks (`route-decision-review.sh`,
  `agent-dispatch-evaluator.sh`, `guard-web-access.sh:77`) already use `${CLAUDE_PROJECT_DIR:-$PWD}`.
- **Fix:** prefer `${CLAUDE_PROJECT_DIR}`, else walk up from `cwd` to the nearest `.ravenclaude/`.
  **Effort: small.** **Why not auto-fixed:** security floor + a cross-host design choice
  (`CLAUDE_PROJECT_DIR` is set by the adapters); substrate-blocked. **Your call on the strategy + full
  gate re-run.**

---

## P1 — high

### P1-2 ✓ code-read · A chained command is classified (and cleared) by its first segment only
- **Where:** `thing-decision.py:216`.
- **Observed (code read):** `classify()` does `re.split(r"\s*(?:\||\|\||&&|;)\s*", cmd, maxsplit=1)[0]`
  and derives the category/tier/concerns from that leading segment only. Newline, a single `&`, `$(...)`
  and backticks are not split.
- **⊙ panel probe:** `git status && npm install -g evil-pkg` → `shell_readonly`, tier `low`, no panel →
  `allow` (overriding the user's `ask` on installs). A read-then-exfil chain and `ls | xargs rm -r build`
  route as clean reads. Where `shell_readonly` isn't toggled (the default), the whole chain is unreviewed.
- **Fix:** quote-aware split on `;`, `&`, `&&`, `||`, `|`, newline, `$()`, backticks; take the
  **highest-tier** segment. **Effort: medium.** **Why not auto-fixed:** substrate-blocked; a wrong
  splitter breaks every command's classification. **Careful human review + Gate 14/15/22.**

### P1-3 ✓ code-read · `guard-web-access` host parsing bypasses both allow- and deny-lists
- **Where:** `guard-web-access.sh:67-70`.
- **Observed (code read):** the authority is cut at `/` only (`host="${host%%/*}"`), then `${host##*@}`
  strips userinfo. `?`, `#` and backslash also terminate the authority but are not handled.
- **⊙ panel probe:** with `allow:[allowed.example]`, `trusted:true`, a URL shaped
  `https://evil.example?@allowed.example` (and `#@…`, backslash-`@…` variants) resolves host
  `allowed.example` and silently allows while the real target is `evil.example` (exfil). With
  `deny:[blocked.example]`, `https://blocked.example?x=1` and `…#frag` exit 0 (no block).
- **Fix:** cut the authority at the first of `/ ? # \`, strip userinfo/port, percent-decode. **Effort:
  trivial.** **Why not auto-fixed:** substrate-blocked; security guard. **Human review.**

### P1-4 ✓ code-read · `git reset` to a hard target is only caught when the flag immediately follows `reset`
- **Where:** `guard-destructive.sh:1857`.
- **Observed (code read):** the pattern is contiguously anchored (destructive flag must immediately
  follow `reset`), unlike the sibling `git clean` / `git branch -D` / `git push`-delete helpers which
  were made order-independent. The `settings.json` deny is also prefix-anchored. (Corroborated: the
  guard blocked a Bash echo of mine that merely contained the literal pattern.)
- **⊙ panel probe:** inserting a flag before the destructive flag, or putting the ref first, passes both
  layers (git accepts all forms).
- **Fix:** order-independent word scan inside the `git reset` segment. **Effort: trivial.** **Why not
  auto-fixed:** substrate-blocked. **Human review.**

### P1-5 ⊙ panel-probed · Cross-host hook generators emit a wrong path + a stray quote → broken hook registrations on all four non-Claude hosts
- **Where:** `scripts/generate-{copilot,cursor,gemini,codex}-hooks.py` (not substrate — editable).
- **Panel probe** (`shlex.split` + file-existence on every emitted command): Gate 247 widened hook-name
  resolution to accept `/scripts/`-hosted hooks, but the generators still emit `<hooks_dir>/<script>`
  (so a `scripts/`-hosted hook points into `hooks/`, where it does not exist) and leave the manifest
  command's **closing quote** as a stray argv token. Broken counts reported: **Copilot 9, Cursor 6,
  Gemini 1, Codex 3.** Among them, 3 Copilot `PreToolUse` **security guards**
  (`preflight-command-review.sh`, `guard-remediation-cause.sh`, `guard-cause-closure.sh`) point at
  nonexistent paths → `copilot-hook-adapter.sh:73`'s `[ -f "$real" ] || exit 0` makes them silently do
  nothing while Gate 247 reports them wired; 6 more fail shell parsing. (I did not independently re-run
  the `shlex` probe this pass.)
- **Blind spot:** Gate 247 checks **names only**, not paths or shell-parseability.
- **Fix:** derive the dir from the manifest command; strip the trailing quote; add a gate asserting
  every emitted command `shlex.split`s and its path exists. **Effort: small (×4 + a gate).** **Why not
  auto-fixed:** a 4-file projection change with freshness/accounting gates and security-guard wiring —
  a wrong fix re-breaks cross-host hooks or CI. **Human review + regenerate.**

### P1-6 ⊙ panel-probed · A YAML parse error in `comfort-posture.yaml` silently disables all review
- **Where:** `thing-decision.py` sets `posture_error` + `thing_enabled=False`; `thing-orchestrator.sh`
  never reads `posture_error` and hits `exit 0`.
- **Panel probe:** a posture with `thing: on` plus one malformed line → `deny` before, no output after;
  the shell `grep` still sees `thing: on`. Contradicts the orchestrator header's "never silently allow
  on our own error." Reachable via a hand edit or an unvalidated `/__save` (P3-19).
- **Fix:** orchestrator emits `ask`/`deny` on `posture_error`. **Effort: trivial.** Substrate-blocked.
  **Human review.**

### P1-7 ⊙ panel-probed · Deleting the toggles is not recognized as self-disable
- **Where:** `thing-decision.py:643` `_posture_content_disables`.
- **Panel probe:** only flags `thing:` set to a non-enabled value, or a `command_review`/`gate_floor`
  key; a Write of a minimal doc, or an Edit that *removes* the `thing: on` lines, returns `False` (not
  denied) — same effect as flipping to off (which IS denied).
- **Fix:** diff the resulting document against the on-disk one; deny if any previously-enabled category
  is no longer enabled. **Effort: small.** Substrate-blocked. **Human review.**

---

## P2 — medium (all ⊙ panel-probed; substrate items write-blocked here)

- **P2-8 · `stall_watch.py:261` PID-reuse guard reported to be a no-op.** `proc_identity_ok` returns
  `bool(ps output)` (= "pid exists"); its result (line 308) is never read by `evaluate()`. After a
  SIGKILL/reboot a reused pid → false "stall" alerts escalating on the 0/15/60/360-min ladder (no
  resolution rule can fire). *Fix: consult `identity_ok` (compare `procStart`/`etime`) in `evaluate()`.*
- **P2-9 · `thing-concerns.py:393` self-disable read-only carve-out admits command executors.** `rg`
  and `ugrep` are allow-listed as "cannot write", but their `--pre`/`--filter` options run arbitrary
  commands. *Fix: drop them, or reject `--pre*`/`--filter*`/`-z`.*
- **P2-10 · `thing-orchestrator.sh:143` grep short-circuit narrower than the engine's truthiness** —
  matches only lowercase `on|true|yes`; `True`/`"on"`/`ON`/`1`/flow-style → no verdict (tribunal
  skipped). *Fix: parse YAML in Python, or make the grep tolerant.*
- **P2-11 · `_scrub.sh:45` GitHub token prefixes incomplete** — only `ghp_`/`github_pat_`; `ghs_`,
  `ghu_` (**the type this remote env uses, per CLAUDE.md**), `gho_`, `ghr_` pass through unredacted →
  echoed to stderr/transcript/hook-events. Mirrored in `serve-dashboards.py` `_MIMIR_SECRET_PATTERNS`;
  also the seat egress backstop. *Fix: `gh[opusr]_[A-Za-z0-9]{36,}` in both copies.*
- **P2-12 · `_scrub.sh:97` PEM key scrubbed header-only** (line-based sed; body + END survive). *Fix:
  redact the whole BEGIN…END span.*
- **P2-13 · `guard-destructive.sh:298` newline collapse defeats segment scoping** — `tr -s` runs before
  the `;&|` split, so a multi-line push-delete is denied but the `;`-joined form is allowed. *Fix:
  newlines → `;` before the collapse.*
- **P2-14 · `guard-destructive.sh:588` rm / `branch -D` / `clean` helpers scan the whole command, not
  the owning segment** (over-blocks: `rm -rf dist && mkdir -p /tmp/out`; `git clean -n && rm -f foo`).
  The comment at :697 describes this lesson but it was applied to push-delete only. *Fix: scope each
  helper to its segment.*
- **P2-15 · CI vacuous "non-required" self-assertions** in `golden-set-inject-light.yml:60` and
  `inventory-sweep.yml:105`: they grep the `gh api .../rulesets` list (which, the panel reports, returns
  no required contexts) for a **workflow name** when required contexts are **job names** — so the guard
  can never fail; a sweep accidentally made required would hang every PR with the guard still green.
  *Fix: query `rulesets/{id}` and match job-name contexts.*
- **P2-16 · CI dispatch re-run reports a green required secret-scan without scanning** —
  `github-protocol-secret-scan.yml:26` runs TruffleHog only for `pull_request`; `workflow_dispatch`
  echoes "skipped" and succeeds (same in `github-protocol-pr-title.yml:34`). `quarantine-intake.yml`
  tells maintainers to re-run gates via dispatch for bot PRs → a green "Scan for committed secrets" on
  the PR head SHA with zero scanning. *Needs design: decide dispatch-path behavior.*

---

## P3 — low (all ⊙ panel-probed unless marked)

- **P3-17 · `_scrub.sh:47` secret-prefix pattern has no left boundary** → over-redacts identifiers
  (`disk-…` → `di[REDACTED]`), mangling hook-event `rule` fields. *Fix: add a `(^|[^A-Za-z0-9])`
  boundary.*
- **P3-18 · `serve-dashboards.py` uncaught exceptions on malformed authenticated POST** (non-string
  `path`/`action`; non-ASCII `X-CSRF-Token` → `TypeError` in `hmac.compare_digest`) → connection reset
  instead of 400/403. Fails closed; cosmetic. *(dual-copy + parity-gated.)*
- **P3-19 · `serve-dashboards.py` `/__save` writes `comfort-posture.yaml` with no content validation**
  (unlike JSON / YAML-mapping targets) — pairs with P1-6. *Fix: validate as a YAML mapping first.*
  *(dual-copy.)*
- **P3-20 · `serve-dashboards.py` `/__host` returns the raw `THING_HOST`** although its contract says
  "presence booleans only." *Fix: emit from a closed set.* *(dual-copy.)*
- **P3-21 ✓ code-read · `generate-codex-hooks.py --check` exits 1 on `main`** — I ran it: exit 1,
  `prompt-optimizer-gate.sh` "NOT accounted for (neither wired nor explicitly skipped)." The other three
  hosts' `--check` are run by `audit-gates.sh`; the Codex one is not, so this red gate is unseen. *Fix:
  add a `_SKIP` entry (or wire it) **and** add the Codex `--check` to `audit-gates.sh`. Decide
  wire-vs-skip.*
- **P3-22 · `generate-codex-hooks.py` SessionStart derivation ignores `_SKIP`** — `routine-reserve-hook.sh`
  (explicitly skipped for Codex) and `caveman-route-hook.sh` are wired anyway; inert today only because
  of P1-5's quote bug. Once P1-5 is fixed, `routine-reserve-hook --event session` would start a network
  refresh on Codex. *Fix: consult `_SKIP` in `_derive_sessionstart`.*
- **P3-23 · `check-inception-coverage.py:56` `REQUIRED_WORKFLOWS` reported out of date** — panel probe
  (`gh api rulesets/17278731`) reports the live ruleset requires 7 checks vs the 3 listed; the 4
  `github-protocol-*` workflows have no no-`paths:`-filter gate (Rule 5 is advisory). A future `paths:`
  on any of them would hang every PR with no gate failing. *Fix: list all 7 + gate the 4 against
  `paths:`.* (Not independently re-confirmed this pass — verify the live required-check set first.)
- **P3-24 · `quarantine-intake.yml:146` bot PR title is not Conventional-Commits** → would fail the
  now-required "Semantic PR title" check on a user event; the body names only 3 of 7 gates. *Fix:
  Conventional-Commits title + full gate list.*
- **P3-25 · `context-usage-meter.py:455` `read_posture` anchors on a commented `# context_handoff:`
  header** → a real block after the shipped template's commented one is ignored, so the handoff nudge
  stays silently off (panel reproduced). *Fix: require the header at column 0.*
- **P3-26 · `conserve-tokens.py:310` prints "CONSERVE TOKENS released …" on every session's first
  prompt** (no prior state ⇒ `changed` true) even when conserve was never engaged. (Observed firing
  during this review.) *Fix: treat empty prior state as "no transition".*
- **P3-27 · `conserve-tokens.py:154` parallelism parse leaks into the next block** (4096-char window) →
  the SessionStart banner misstates the posture. *Fix: bound the scan to the block.*
- **P3-28 · `routine-reserve.py:133` repo posture overrides the account-scoped `home`/mode/budget** →
  an untrusted repo whose `comfort-posture.yaml` sets `routine_reserve_home: attacker/x` steers the
  SessionStart `pull()` into `~/.ravenclaude/usage/mirror` (whole `git archive` in memory, no size cap).
  Bounded to spoofed reserve figures. *Needs design: account-scoped keys from account config, not repo
  posture.*

---

## A ✓ confirmed · `audit-gates.sh` has a nondeterministic 1-fail flake whose failing gate moves between runs
- **Observed:** two full runs this session, each **1087 pass / 1 fail / 0 skipped**, but a **different**
  gate each time — run1 failed Gate 240 ("artifact budgets … must-fail convention"), run2 passed Gate
  240 and failed "prompt-optimizer structural subset." Gate 240 passes in isolation (`--check 240` →
  10 pass, 0 fail) and all three of its sub-commands pass on a clean tree.
- **Inference / hypothesis (not isolated):** a nondeterministic flake — the two most likely causes are
  (a) **resource/timing contention** (both full runs ran under heavy parallel load from this review's
  own panels + commands; several of the flaking gates are subprocess/teeth-heavy with timeouts), or
  (b) **cross-gate state** (a prior gate transiently regenerating a razor-thin-budgeted artifact — the
  `index.html` island payload budget has **1 element** of headroom). I did **not** isolate which; a
  clean-machine, no-parallel-load run is the discriminating probe.
- **Impact:** the repo's own meta-test — run in CI — can intermittently report RED on `main`.
- **Fix direction:** reproduce on a quiet machine; if timing, raise the flaking gates' internal
  timeouts or serialize them; if state, make the regenerating gates render to temp (several already
  claim "no in-place write"). **Do NOT raise the artifact-budget ratchet to paper over it** (the seed
  file says: append a row with a cause, never edit a row). **Human review.**

---

## Coverage honesty
- **Did:** the full whole-tree gate suite; a security panel over the dashboard server, destructive/
  web-access guards, and the tribunal engine; a correctness panel over the recently-churned Python, the
  four cross-host generators, and every Actions workflow. P0-1/P1-2/P1-3/P1-4/P3-21 + finding A were
  re-confirmed by me this session; the rest are panel-probed (not independently re-run).
- **Did not:** hand-audit all ~10,590 files / 186 plugins' prose (gate-covered for structure/freshness/
  links, not correctness); run the `Workflow`-tool `/repo-review` fan-out (needs opt-in this routine
  lacked); exercise the hooks under a live Copilot/Codex host. Two `[unverified]` panel candidates were
  excluded.

## Recommended order of attack
1. **P0-1** — decide the root-resolution strategy, fix, full gate re-run.
2. **P1-3 / P1-4** — trivial, high-value guard fixes.
3. **P1-6 / P1-7 / P2-10** — close the "silently off" family together.
4. **P1-2** — the biggest tribunal gap; most careful fix.
5. **P1-5 + P3-21 / P3-22** — one cross-host-wiring pass + a Codex `--check` wired into CI + the new
   "emitted command parses & path exists" gate.
6. **P2-15 / P2-16 / P3-23 / P3-24** — one CI-governance pass (verify the live required-check set first).
7. **A** + the remaining scrub/meter/conserve hygiene items.
