# Repo review — decisions needed (2026-10-02)

Companion to [`docs/reviews/2026-10-02-repo-review-findings.md`](reviews/2026-10-02-repo-review-findings.md).

The autonomous four-panel review fixed everything that was mechanical, bounded,
and fail-safe (one P1 security fix + four reproduced P2 shell bugs + six verified
broken-link/doc fixes — see that doc and the PR). The items below are **judgment
calls or high-blast-radius changes** a human should sign off on: they either
change a CI gate's pass/fail behaviour, require a human-reviewed re-seed, touch
the security perimeter's policy, or are a multi-file campaign whose batching is
Matt's call. Each has a recommendation and a ready-to-apply fix.

All findings were verified on the real `origin/main` tree (the branch was even
with `origin/main` at review time). Severity in brackets.

---

## A. Gate blind spots — checks that pass while the thing they guard is broken

These are the highest-value finds: the repo's own value system says "a gate that
runs without gating is invisible from a green dashboard." Each of these is a
`--check` that **fails on the real tree today but is not wired into CI**, or a
gate whose scope silently misses part of what it claims to cover. None can be
auto-fixed safely because fixing them either turns a currently-green required
surface red (needs a reviewed re-seed) or edits gate logic that the 700+-check
`audit-gates.sh` meta-test must then re-certify.

### A1 — skill-description cap/ratchet is dead in CI and fails today (P1)

`scripts/check-skill-descriptions.py --check` exits 1 on real main:
`[ratchet] posture drift: pinned skill_count=956, current skill_count=961` — five
skills were added past the seed and CI stayed green. Gate 281 only runs the
script's `--self-test` / `--must-fail` on scratch trees, so the cap + ratchet the
`ravenclaude-core/CLAUDE.md` constitution claims is "now enforced" is effectively
**not enforced on the real corpus**. (`ratchet_check` also returns clean when
`description-budget.json` is absent or malformed — a second fail-open.)

- **Question:** re-seed `description-budget.json` (`pinned_posture.skill_count` +
  the ceiling) and wire a real-tree `--check` into Gate 281, or drop the
  "enforced" claim from the constitution?
- **Recommendation (re-seed + wire, medium confidence):** the mechanism is
  sound; it just isn't bolted to the real tree. The ceiling raise is deliberately
  a human-reviewed act (the budget file says so), which is exactly why it wasn't
  done autonomously. A labelled budget-raise PR + a `must_pass` real-tree check +
  making `ratchet_check` fail closed on an absent/malformed budget closes it.

### A2 — Copilot tool projection fails OPEN to "all tools" (P2, latent privilege escalation)

`scripts/generate-copilot-plugin.py:project_tools` returns `[]` both for a
wildcard **and** for "restricted, but nothing maps," and `build_agent_doc` then
emits **no `tools:` line** — which Copilot reads as *all tools, including edit and
shell*. Confirmed: `project_tools(['TodoWrite'])`, `['Agent']`,
`['mcp__github__get_issue']`, `['NotebookEdit']` all return `[]`; a
`tools: Bash(git status, git diff)` splits naively and maps nothing. Gate 166's
guard `if expected and actual is None` skips the empty-expected case, so the gate
is blind to it. No current core agent triggers it (all 17 map at least one tool),
so it is latent — but it is the MH-10 escalation reopened inside the gate's blind
spot.

- **Question:** harden the projector to fail closed (raise when a non-empty,
  non-wildcard tool list maps to nothing), split `tools:` on top-level commas, and
  tighten the Gate 166 guard to `if declared and "*" not in declared and actual is
  None`?
- **Recommendation (do it, high confidence):** this is a security-posture fix with
  no behaviour change for today's agents. It needs verification of what Copilot
  does with an explicit `tools: []` (not documented in-repo), hence design-input.

### A3 — Codex hook-accounting gate red and unwired (P2)

`scripts/generate-codex-hooks.py --check` exits 1 on real main:
`prompt-optimizer-gate.sh` (a `UserPromptSubmit` hook added ~2026-09-20) is
neither wired nor in the Codex `_SKIP` map — though Gemini's `_SKIP` names it.
The gate is not run by CI (its copilot/cursor/gemini siblings are).

- **Question:** add `"prompt-optimizer-gate.sh": _EVENT_UNWIRED_REASON` to the
  Codex `_SKIP` and wire `generate-codex-hooks.py --check` into `audit-gates.sh`
  beside the gemini one?
- **Recommendation (do it, high confidence):** the `_SKIP` entry is a one-line,
  output-neutral Gemini-parity fix; the wiring must follow the gate-numbering /
  suite-membership rules (Gate 267), which is why it is owner-gated, not autofix.

### A4 — Gate 242 (no-`paths:` guard) covers 3 of 7 required checks (P2)

The live `main` ruleset requires **7** contexts (not the 3 that `AGENTS.md` /
`CLAUDE.md` state): the three validate-* checks **plus** Semantic PR title,
TruffleHog secret scan, workflow-permission lint, and zizmor. Gate 242's
`REQUIRED_WORKFLOWS` lists only the three validate-* files, so the four
`github-protocol-*` required checks are unguarded against the "a `paths:` filter
on a required check hangs the PR forever" trap. (Verified: none of the four has a
`paths:` filter today, so adding them to the guard will not newly-fail it.)

- **Question:** add the four `github-protocol-*.yml` to `REQUIRED_WORKFLOWS` and
  correct the "three required checks" wording in AGENTS.md / CLAUDE.md / the script
  messages to seven?
- **Recommendation (do it, high confidence):** closes a real P0-trap blind spot;
  the must-fail fixture keys off `len(REQUIRED_WORKFLOWS)` so it adapts. Owner-gated
  only because it changes a gate's scope + the two boundary docs. Re-run
  `audit-gates.sh` after.

### A5 — fail-closed / coverage hygiene on several gates (P2–P3, batch)

A cluster of smaller gate-correctness items, grouped because each edits gate logic
the meta-test must re-certify:

- **SH-8 (P2):** `check-hook-failclosed.sh` enumerator skips the three PreToolUse
  hooks registered as `bash .../scripts/X.sh` (`$1` is `bash`), so Gate 199 audits
  15 of 18 hooks (`preflight-command-review.sh`, `guard-remediation-cause.sh`,
  `guard-cause-closure.sh` unaudited). All three currently pass the hostile shapes,
  so the fix won't turn it red. Fix: strip a leading `bash|sh` token.
- **PY-5 (P3):** `check-inception-coverage.py` leaves rename-detection on, so a
  `git mv` into a gated root shows as `R` not `A` and bypasses the `covers[]`
  ratchet. Fix: `--no-renames`.
- **PY-6 (P3):** `check-guard-state-scope.py --discover` only finds hooks under
  `hooks/`, silently dropping the three `scripts/` PreToolUse hooks. Fix: resolve
  `${CLAUDE_PLUGIN_ROOT}/(hooks|scripts)/<name>`.
- **PY-7 (P3):** `check-shipped-references-resolve.py` Check C treats markdown `#`
  headings as shell comments, so a heading citing an unshipped script slips through.
  Fix: treat `#` as a comment only for `.sh`/`.yml` or inside fenced blocks.
- **PY-8 (P3):** `check-frontmatter.py`, `check-artifact-budgets.py`,
  `check-grep-ere-pcre.py`, `check-hook-stdin-fallback.py`,
  `check-mcp-attribution.py` pass on an empty scope (newer gates fail closed). Low
  impact (CI runs from root). Fix: exit non-zero when zero files/manifests scanned.
- **SH-9/12/13/14 (P3):** `audit-gates.sh` INT/TERM trap never exits; a double
  `FAIL++` in `check-hook-failclosed.sh`; a missing `else fail` in
  `check-worktree-state.sh`; `check-host-canary.sh`'s silent-mutant teeth can only
  fail on "anchor missing."

- **Question:** take these as one "gate-hardening" PR?
- **Recommendation (yes, as a dedicated PR with `audit-gates.sh` re-run per edit):**
  all are correctness improvements to the gate layer; PY-7 is the only one that
  could newly-fail a required check on the real tree (verify first).

---

## B. The `scan_target` PreToolUse campaign — 30 plugins still blind to new writes (P2)

30 non-core PreToolUse `Write|Edit|MultiEdit` anti-pattern hooks grep the **on-disk
file**, which at PreToolUse has not yet been written — so a new-file `Write` is
never scanned and an `Edit` is judged on stale content. The 2026-09-23 review fixed
29 sibling hooks with a `scan_target` block (build a temp file from
`.tool_input.content` / `new_string`); these 30 were missed. Reproduced on
`azure-cloud` (a new `*.bicep` with a plaintext secret → silence) and
`regulatory-compliance` (PII scrub blind to a new write; its header wrongly claims
pending content isn't visible).

Affected (30): api-engineering, applied-statistics, azure-cloud,
claude-app-engineering, construction-general-contractor, data-science-research,
developer-relations, email-engineering, event-management, field-service-management,
geospatial-engineering, graph-engineering, incident-response-dfir,
localization-i18n-engineering, microsoft-fabric, microsoft-graph,
network-engineering, open-source-maintenance, optometry-eyecare-practice,
physical-therapy-rehab-clinic, public-sector-govtech,
realtime-collaboration-engineering, regulatory-compliance, retail-store-operations,
sales-engineering, supply-chain-planning, tableau, technical-program-management,
trust-and-safety, wordpress-cms-engineering.

- **Question:** complete the 2026-09-23 work by porting `scan_target` to all 30 (+
  a CI check that every such hook references `scan_target`)?
- **Recommendation (yes, as its own focused PR):** it is mechanical with a proven
  template, but 30 heterogeneous hooks + 30 version bumps + CHANGELOGs is a large
  blast radius better landed as one reviewed batch than folded into this sweep's
  PR. The accompanying gate is what prevents a 31st from regressing. Not auto-done
  here purely on batch-size / review-surface grounds.

---

## C. CI workflow hardening & policy (CI panel)

All P2/P3; none is a current CI failure. Grouped because they touch
required-check workflows, secrets, or supply-chain policy.

- **C1 — trufflehog image is `:latest` (P2).** The action is SHA-pinned but its
  `version` input defaults to `latest`, so a required check runs a mutable image
  (supply-chain risk + a benign `:latest` bump can turn the required scan red on
  unrelated PRs). Fix: pin `version: "3.97.5"` (verify the ghcr tag first).
- **C2 — two "assert-not-a-required-check" steps always print OK (P2).** In
  `golden-set-inject-light.yml` and `inventory-sweep.yml` the guard queries the
  ruleset **list** endpoint (no contexts) and greps **step** names against **job**
  names, so it can never fail. Fix: query `rules/branches/main` and match job names;
  add `if: always()`.
- **C3 — quarantine spam-cap never fires (P2).** It counts open *issues* but closes
  every issue it processes (the queue is PRs); steady drip-spam keeps the count at
  ~1. Repo is public + form intake auto-labels. Fix: count open PRs; optional
  per-author cap.
- **C4 — docs-only fast-lane filter omits `ruff.toml` / `.prettierignore` (P2).** A
  PR editing only those gets `code=false`, skips the whole-tree lint (accepted as
  green), then the push-to-main run goes red and blocks every later PR. Fix: add
  `ruff.toml`, `.prettierignore`, `.prettierrc*` to the `code:` filter.
- **C5 — `workflow_dispatch` of the required secret-scan skips TruffleHog (P3).** A
  dispatched run of "Scan for committed secrets" goes green having scanned nothing;
  the quarantine PR (which carries external content) is exactly where a real scan
  matters. Fix: run TruffleHog on dispatch too (full-history default).
- **C6 — `pip install jsonschema` / `pyyaml` unpinned + Python `3.x` floating (P3)**
  in required checks (ruff/prettier are exact-pinned). The jsonschema CLI already
  warns it's deprecated. Fix: pin versions (or move to the library API) + pin a
  Python minor.
- **C7 — write perms at workflow level vs the `permissions: {}` floor doctrine
  (P3)** in `regenerate-artifacts.yml` / `quarantine-intake.yml`. Behaviour-identical
  today; a later second job would silently inherit write. Fix: `permissions: {}` at
  top, elevate per job.
- **C8 — `SELF_HEAL_PAT` is repo-level and the dispatch isn't `main`-restricted
  (P3).** Latent while solo-owned; any future write collaborator could dispatch the
  PAT (an admin identity with ruleset bypass). Fix: move the PAT to a `main`-scoped
  Environment; add `if: github.ref == 'refs/heads/main'`.
- **C9 — merge-wait race, hypothesis only (P3).** `regenerate-artifacts.yml` may
  squash-merge if a poll lands in the gap before a required job's check registers.
  Probe first; if real, assert every required context is present + `pass` before
  merging.
- **C10 — no `timeout-minutes` on several jobs (P3).** A hung macOS job (billed
  ~10x) can burn up to 360 minutes. Fix: add timeouts (30 min macOS, 10 elsewhere).
- **C11 — dependabot covers only `github-actions`, not the 7 tracked
  `package-lock.json` (P3).** Starter-dependency advisories surface only by hand (a
  Playwright advisory already was). Fix: add grouped `npm` entries.
- **C12 — stale rationale comments in `regenerate-artifacts.yml` (P3).** The step-4f
  and layout-check comments still say the job "pushes straight to main with [skip
  ci]" so "no PR gate ever runs"; it now opens a PR (gates run) and squash-merges
  with [skip ci] only in the merge subject. The `.prettierignore` entry for
  `researcher-reminder.yml` was removed in this sweep's PR (verified clean). Fix:
  correct the two comments to the current open-a-PR flow.

Also flagged (owner confirm, not a code change): the ruleset's bypass list has
**4 integration actors** (ids 946600, 1143301, 1236702, 2875373) beyond the
documented admin bypass — confirm they're intentional.

- **Recommendation:** C1/C4 are the highest-value (both are "goes red on main
  later" traps) and are small — fold into the gate-hardening PR or a CI-hygiene PR.
  C2/C3/C5–C9/C11 are genuine hardening; batch per your appetite. C10 is pure
  additive safety. C12 is a comment correction.

---

## D. Content & doctrine judgment calls

- **D1 — Power Platform "Recommended Resources" name 4 files that were never
  written (P2).** `power-automate/SKILL.md` and `power-bi/SKILL.md` list
  `resources/*.md` that don't exist. **Question:** author the four, or delete the
  bullets? (Content decision.)
- **D2 — 52 dangling `works_with` references across 37 agent files (P3).** They name
  agents that exist in no plugin (e.g. `ml-engineer`, `llm-strategist`,
  `security-engineering/security-reviewer` — the real one is `ravenclaude-core/`;
  `azure-cloud/entra-identity` → `entra-identity-engineer`). Portal-only impact
  (renders chips to nonexistent agents); the orchestrator prompt doesn't load the
  field; `check-frontmatter.py` only checks non-empty. **Recommendation:** add a
  resolution check to `check-frontmatter.py` and fix the 52 in the same PR — a
  37-file per-entry-judgment change is better reviewed than auto-applied.
- **D3 — heredoc commit subjects in `enforce-git-protocol.sh` (P2, opt-in only).**
  In `git_protocol: block` mode, a `-m "$(cat <<'EOF' … )"` commit (the repo's own
  standard style) is parsed as subject `$(cat <<'EOF'` and denied; in `warn` mode it
  gets a garbled nudge. **Question/Recommendation:** treat a subject starting with
  `$(`/backtick as "not inspectable" and skip it (matches the hook's own documented
  contract) — a conservative, fail-safe fix I left for you because it's a guard
  behaviour choice.
- **D4 — abandoned forward references (P3).** `webfetch-hardening/SKILL.md:135`
  points at `knowledge/webfetch-return-envelope-hardening.md` "shipping in the
  data-viz-designer PR (when it lands)"; no such file or agent exists. **Question:**
  delete the bullet, or is that build still planned?
- **D5 — root `STRATEGY.md` stub vs `docs/STRATEGY.md` content (P3, known as B10,
  2026-08-31).** Still open. **Question:** promote/redirect `docs/STRATEGY.md`?

---

## E. Latent ratchet hygiene (P3)

`scripts/artifact-budgets.seed.json` is stamped `measured_against: 4f3ced1` while
the current merge base is `121432c`. The **real** `check-ratchet-freshness.py`
gate exits 0 (advisory ✗, not a hard fail), so this is **not** a CI failure — but
it's the merge-time-restamp hygiene the ratchet doctrine calls out. **Not restamped
autonomously** because a restamp is merge-base-sensitive and the doctrine says to
do it "on rebased HEAD as the last step before merge." **Recommendation:** restamp
when next convenient (`python3 scripts/check-ratchet-freshness.py --stamp`), ideally
on a branch whose merge base is current.

---

## What was fixed autonomously (see the PR + findings doc)

**P1:** URL-authority parsing bypass in `guard-web-access.sh` / `mark-web-domain-seen.sh`
(deny-list bypass + allow-list spoof via `evil.example?@trusted.example`), reproduced
and fixed, validated end-to-end. **P2 (reproduced):** `runaway-brake.sh` silent deny
message; `enforce-layout.sh` glob-path over-block; `cleanup-branches.sh` tag/branch
name collision; `check-qa-test-automation-anti-patterns.sh` dead-on-arrival hook.
**Broken links / doc drift:** six fixes across AGENTS.md, CHANGELOG.md,
`plugin-discovery-routine-policy.md`, two rc-core docs + one agent, the
`psm-dashboard-build` tier table, and a regulatory cross-plugin reference.
