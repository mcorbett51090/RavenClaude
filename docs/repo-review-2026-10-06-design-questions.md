# Repo review — 2026-10-06 — design-input summary & questions

**Routine:** scheduled whole-repo review (3 expert panels → tie-break → autonomous implementation → this doc).
**Branch / PR:** `claude/awesome-wright-hc1i7c`.
**Scope reviewed:** top-level `scripts/` (129 py + 23 sh), `plugins/ravenclaude-core/hooks/` + adapters, the
19 `.github/workflows/`, and repo-wide architecture / doc-drift. 184 plugins; coverage is honest, not
exhaustive — plugin *knowledge-file content* and the non-core plugins' internals were not deep-read.

## Provenance & verification status (read before acting on anything below)
Deterministic ground truth first: `ci-preflight.py` was **19/19 PASS**, `ruff`/`prettier` clean, and
`audit-gates.sh` green at session start — the repo is **healthy by its own extensive standards**. The real
findings are therefore subtle: *gate-teeth weaknesses* (gates that structurally cannot fail on the property
they exist for — the repo's own pet concern), a handful of latent correctness/security bugs, and doc drift.

Two tiers of confidence, kept separate on purpose:
- **The 21 fixes in the companion PR** were each **independently verified by this session** — read, reproduced
  where possible, and re-run against the repo's own gates (all green).
- **The findings in THIS document are REVIEWER-REPORTED** by the three review panels and are **design-input
  items**. Each is cited to `file:line`, but — except where a control is noted — they are **relayed, not
  independently re-verified here. Verify each against current code before acting.** Representative spot-checks
  were run (e.g. **F-06 confirmed**: the 3 hook names are in `hooks.json` and absent from `.claude/settings.json`
  — `grep -c` {2,3,1} vs {0,0,0}, 2026-10-06), which is evidence the panels' findings are genuine, not that
  every one below was re-checked.

> ⚠️ **The single most important section is the next one.** The highest-severity findings in the whole review
> are **reported P1 fail-open security bugs in shipped guards**, and every one is in the tribunal-write-protected
> `plugins/ravenclaude-core/hooks/` substrate — so the routine structurally *cannot* patch them (the standing
> decision from the 2026-09-22 review: substrate findings are human/maintainer work). They are listed first.

---

## A. P1 — reported fail-open SECURITY bugs in shipped guards (SUBSTRATE-LOCKED → maintainer work)

All four are in `plugins/ravenclaude-core/hooks/`; the Panel-1 shell reviewer reports reproducing each. They
are the guards that *are* the perimeter. **Verify each reproduction before fixing** — then fix under the
maintainer-substrate exemption.

| # | File:line | Reported defect | Reviewer's proposed fix |
|---|---|---|---|
| **SH-F1** | `cursor-hook-adapter.sh:144`, `gemini-hook-adapter.sh:140` | The Cursor & Gemini adapters check only the hook's **exit code**, but `thing-orchestrator.sh` emits deny verdicts as **JSON `permissionDecision` + exit 0** — so the command-review tribunal + the hard-rule floor would be **inert on Cursor/Gemini** (a deny never blocks). Gate 208 uses an exit-2 stub, so it would not catch this. | Capture the hook's stdout; translate `.hookSpecificOutput.permissionDecision == deny` into the host's block. Add a Gate-208 fixture that denies via JSON+exit-0. |
| **SH-F2** | `guard-web-access.sh:67` | Host extraction does `${host##*@}` **before** stripping `/ ? # \`, so `https://blocked.test#@ok.test/` would parse the host as `ok.test` → deny list bypassed, allow list spoofable. | Cut at the first `/?#\` **before** the userinfo strip; reject control chars. |
| **SH-F3** | `guard-destructive.sh:277` | A command > 128 KiB (`MAX_ARG_STRLEN`) makes the anti-obfuscation preprocessor's `exec` fail with E2BIG; the `\|\|` swallows it, so an obfuscated `rm -rf` would be allowed. The header says this exact fail-open was closed. | Pass the command on **stdin**; fail **closed** if the preprocessor returns empty on non-empty input, or if `${#cmd}` exceeds a cap. |
| **SH-F4** | `thing-orchestrator.sh:130`, `runaway-brake.sh:41`, `dod-gate.sh:41`, `guard-probe-validity.sh:174` | Posture file resolved from the payload `cwd` with **no walk-up / no `CLAUDE_PROJECT_DIR` fallback** — IF hook `cwd` follows the Bash tool's persistent working dir, the tribunal + brake + DoD gate would **no-op after a `cd` into a subdirectory**. Conditional on that one unverified inference. | Resolve the root via `${CLAUDE_PROJECT_DIR:-<walk-up>}`. **One probe settles it:** log the hook payload's `.cwd` after a `cd subdir`. |

**Decision needed:** fix these under the maintainer-substrate exemption (the documented mechanism for editing
the tribunal's own files), or track? SH-F2/SH-F3 are reported S-effort and unambiguous; SH-F1/SH-F4 (SH-F4
pending the one-line cwd probe) are the higher-value ones.

Also reported substrate, same lock:
- **SH-F6** `guard-destructive.sh:588/642/657` — dangerous-target test reportedly runs against the **whole**
  command, not the rm/find/truncate segment, so `cd /tmp/build && rm -rf dist` would be a **false-positive
  deny** (reportedly blocked the reviewer's own diagnostic commands). Fix: split on `;&&||`, test per-segment.
- **SH-F5** `runaway-brake.sh:169` — `exec 9>… 2>/dev/null` reportedly redirects the hook's stderr permanently,
  so a tripped brake's reason never reaches the agent. Fix: brace-scope the redirect.
- **SH-F11** `hooks.json` — reportedly 50/62 commands use **unquoted** `${CLAUDE_PLUGIN_ROOT}` → a root with a
  space → exit 127 → guards fail open. Fix: quote all (+ the settings.json mirror) + a gate.
- **SH-F7/F8/F9/F10** — `keep-awake.sh` fd-3 leak; `enforce-git-protocol.sh` flags an idiomatic heredoc commit;
  `claim-grounding-lint.sh` ~20 s on a large doc; `setup-worktree-hygiene.sh --with-git-hook` replaces the
  global `core.hooksPath`. Verify + decide.

---

## B. P1 — architecture / process (reported; need a decision, not a patch)

- **F-01 — the catalog reportedly diverges from the manifests at scale, with no gate.** `marketplace.json`
  `description` reportedly differs from `plugin.json` for **53/184** plugins, `keywords` for **49/184**
  (e.g. `ai-red-teaming` "OWASP … 2025" vs "2026"; `aws-cloud` "App Runner" vs "ECS Express Mode"). The repo
  fixed this "two hand-edited copies of one fact" shape for `version` and stopped there. **Recommendation:**
  extend `sync-plugin-versions.py` to also derive `description` + `keywords` from `plugin.json` + add a `--check`
  parity mode, then realign once. **Decision needed:** confirm manifest-is-authoritative, and whether the catalog
  should carry `requires`. *Large marketplace.json diff → deliberately not done autonomously.*
- **F-02 — the review routine's own output accumulates.** Reportedly 13 open PRs (12 drafts), oldest 2026-09-24;
  prior backlogs unmerged. The routine cannot patch the substrate it audits. **Recommendation:** a weekly
  maintainer merge window, a stale-draft supersede rule, or extending the substrate exemption so the routine can
  land substrate fixes under review.
- **PB-1 — host hook generators reportedly emit unrunnable commands.** `generate-{copilot,cursor,gemini,codex}-
  hooks.py` reportedly emit a stray quote (shlex.split raises on 16/148) + the wrong dir (`hooks/` vs `scripts/`),
  and `copilot-hook-adapter.sh`'s `[ -f "$real" ] || exit 0` makes the command-review guard a no-op; `--check`
  only counts. **Regen-heavy** (projected files across 4 hosts) → deferred. Fix per the reviewer: capture the dir
  group, strip the leading quote, add `--check` file-exists + `shlex.split` assertions, honor `_SKIP`.

---

## C. P2/P3 — implementable but deferred (regen-heavy, or a judgment call)

- **PA-2** `check-guard-state-scope.py:204` reportedly resolves guards only under `hooks/`, dropping 4
  `scripts/`-hosted PreToolUse guards. **Decision:** fixing the resolver turns the gate red until the 3 newest
  deny-guards declare `rc-state-*` markers (or get an `EXEMPT` entry).
- **PA-8** `check-dom-budget.py:1008` — the DOM-budget "monotonic" ratchet reportedly has no base-ref
  comparison (history rewritten in lockstep). **Decision:** owner-approved table edits, or a base-ref baseline?
- **PA-14** `check-hooks-selftest.py:175` reportedly mutates the real tracked `copilot-hook-adapter.sh` in place
  (restore only in `finally`). Fix: copy to temp. *Low-risk; deferred only to keep this PR tight.*
- **PA-15 / PB-14** reported latent XSS-shaped bugs in generated output (`_index_dashboard_template.py:1296`;
  `generate-copilot-plugin.py:331` drops `tools:` when all unmapped → Copilot reads ALL tools). Both latent
  (repo-controlled names) but require regenerating committed generated files.
- **PB-8** `check-pipeline-lanes.py:86` regex reportedly misses 9 `scripts/`-resident hooks. Fix needs a
  per-hook stage decision → design input.
- **CI-04** four workflows' "assert NOT a required check" step reportedly greps the ruleset **list** endpoint
  (no rule contexts) → can never fire. Fix: fetch each ruleset detail + compare job names. *Runtime gh-api
  change to 4 workflows → deferred.*
- **CI-05** `regenerate-artifacts.yml` self-heal reportedly commits the whole tree (no `add-paths:`) after npx-
  fetched code, then squash-merges at 0 approvals. Fix: an `add-paths:` allowlist. **Careful** — a wrong list
  breaks regeneration silently.
- **CI-06** `quarantine-intake.yml` spam cap reportedly counts issues the run itself closes → never trips for
  sequential submissions. Fix: count open PRs.

---

## D. P2/P3 — doc drift & missing features (decisions)

- **F-03** core `plugins/ravenclaude-core/CLAUDE.md` is a **5,363-line changelog**; the team-roster table is
  reportedly empty and many agents/skills unmentioned, while the root README says the Team Lead reads it and
  "sees the team roster". **Decision:** split it (short constitution + generated roster/skill table; dated
  narrative → CHANGELOG) + a size-cap / name-coverage gate.
- **F-04** `docs/architecture.md` hand-maintained counts reportedly drifted (core 14 agents/22 skills/13 hooks vs
  disk 17/68/56; ~42 row mismatches by the reviewer's own regex — unconfirmed per-row). Fix: generate counts
  from disk or drop them; extend `check-marketplace-claims.py` 4a.
- **F-06** `.claude/settings.json` dev-mirror omits 4 hook registrations `hooks.json` has — **CONFIRMED by
  control** (handoff-tax-meter, plugin-lifecycle-telemetry ×2, explore-tier-pin absent from the mirror;
  2026-10-06). Gate 259 checks SessionStart only. **Decision:** mirror them, or an explicit intentional-omission
  allow-list + generalize Gate 259's parity to all events. *Editing settings.json reformats/drops comments →
  deliberately not touched autonomously.*
- **F-07** reportedly 21/132 plugin `CHANGELOG.md` violate "top entry = current version" (8 missing the heading,
  13 appended below), no gate. **Decision:** add the gate + backfill — the 8 missing entries need per-plugin
  content (maintainer knowledge).
- **F-08** two `STRATEGY.md`: root reportedly says "Stub pending Matt" + a dead pointer to a nonexistent
  `docs/gap-closure-plan-2026-06-01.md`, while `docs/STRATEGY.md` is a substantive memo on the same topic.
  **Decision:** point the root at `docs/STRATEGY.md`, or promote/merge.
- **F-13** no branch-on-main gate, though CLAUDE.md:59-62 calls the port a "live follow-up". **Decision:**
  PreToolUse hook vs CI gate; detached-HEAD handling.
- **F-12 / F-14 / F-15** reported roster tier skew (opus 434 / sonnet 188 / haiku 1 = 69.66% frontier vs the
  "cheapest tier" doctrine — set a burn-down target or accept 70% as steady state); agent-dispatch-evaluator
  P5/P6 + classifier flag-flip unbuilt (honest, default-off); Copilot Chat probes UNFILLED. All already honestly
  documented in-repo; collected here for one place.

### Reclassified during tie-break (Panel 3)
- **CI-02** (`workflow_dispatch` reportedly yields a vacuous green for the secret-scan + pr-title **required**
  checks) was flagged `design:no` by the reviewer but **conflicts with the documented
  `remote-ci-autotrigger-runbook`**, which relies on dispatching workflows to satisfy required checks after a
  no-auto-run incident. → **needs a decision** (accept the fail-open, or drop `workflow_dispatch` and lose the
  recovery lane). Kept P2.
- **CI-01** the required-check set is reportedly **7, not 3** (Gate 242 `REQUIRED_WORKFLOWS` + the runbook + docs
  all say "three"); the 4 `github-protocol-*` workflows would be unguarded against a `paths:`-filter hang. Doc +
  guard change spanning a gate fixture + 3 docs → routed here as one coherent unit.

### Self-admitted open follow-ups (from the docs themselves — consolidated)
Branch-on-main gate; agent-dispatch-evaluator P5 sampler + `#/evaluator` tab (`eval-dispatch-quality.py`
absent); adaptive-run-classifier Phase 6 flag-flip; Mímir `claude --status --json` watch; Copilot Chat ceiling
probes; session-handoff verify; chat-write-deny leftovers; root `STRATEGY.md`; the 2026-09-10 close-out items;
and the unverified Cursor/Windsurf host lanes (`AGENTS.md:13-14`).

---

## E. Minor (reported, not actioned)
`check-skill-descriptions` token checks reportedly skip silently without `tiktoken` yet print "clean";
`serve-dashboards` `/__save`/`/__run` membership test on unvalidated JSON → reported uncaught `TypeError`;
`thing-golden-eval` reported vacuous 0/0 pass; `ci-preflight` git-status fail-open; `check-ratchet-freshness
--stamp` writes before validating; `enforce-layout.sh:112` reportedly denies filenames with two dots;
`audit-gates.sh:2897` reportedly mutates the live tribunal outside the backup registry + executes a planted
`/tmp/actionlint`; `ensure-plugin-installed.sh` worst-case 180 s > the 30 s SessionStart hook timeout.

---

_Produced by the scheduled repo-review routine. The implemented, independently-verified fixes are in the
companion PR on `claude/awesome-wright-hc1i7c`; this document is the reviewer-reported design-input remainder
for maintainer decisions — verify each finding against current code before acting._
