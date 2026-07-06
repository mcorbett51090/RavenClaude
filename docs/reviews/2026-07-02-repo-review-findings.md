# Repo review — 2026-07-02 (3-panel expert review)

**Method.** A three-panel workflow (Panel 1 find + categorize → Panel 2 analysis/priority validation → Panel 3 tie-break) with an adversarial verification pass, run across the shared infrastructure that can actually break consumers: `ravenclaude-core` hooks + tribunal engine, the top-level `scripts/` CI-gate + generator suite, `.github/workflows/`, the `power-platform` plugin, and a structural sweep of the marketplace breadth. Model assignment followed the brief — lighter models (Sonnet/Haiku) for finding/categorizing, Opus for the analysis and tie-break panels.

**Result.** 29 raw findings → 28 after dedup → **14 confirmed-actionable** (0 refuted by the adversarial pass), 3 needing design input, 11 P3. Deterministic gates (prettier, ruff, JSON validity, manifest version-drift, shell syntax, frontmatter/description-cap) were all clean at baseline.

## Implemented in this PR (20 fixes)

Grouped by priority in the PR body. All verified (unit fixtures / behavioral tests / gate runs). Highlights:

- **P1 security** — two verified command-substitution bypasses of `guard-destructive.sh` (a double-quoted `-m "$(…)"` body and a bare-`<<EOF` heredoc body were blanked before the destructive-pattern scan while bash still executed them), plus a bonus command-boundary fix so `$(rm …` with no separator is caught; a GitHub Actions script-injection via unquoted `${{ github.base_ref }}`; and a plugin hook shipped non-executable.
- **P2** — two secret-leak paths (event-log `path` field + guard stderr), three `</script>` breakout escapes in HTML generators, two git branch-safety bugs (`archive-branch.sh` other-worktree, `cleanup-branches.sh` merged-PR-by-tip), an unbounded download in the gate meta-test, a one-directional manifest cross-check, and a false-positive in the Dataverse preflight.
- **P3** — two non-dict-JSON crash guards in the tribunal engine, grep long-option detection, a CSS `@media(` parse edge, curl `--json` write detection, an `open-dashboard.sh` `/tmp` symlink race, and YAML-scalar escaping in the run-context serializer.

---

## Needs your decision (design input) — 3 items

These change a contract or safety semantic, so they were **not** auto-implemented.

### D1 — `guard-recursive-spawn.sh` "strict hard-block" is non-functional
[`plugins/ravenclaude-core/hooks/guard-recursive-spawn.sh:129`](../../plugins/ravenclaude-core/hooks/guard-recursive-spawn.sh#L129)

The header advertises `RC_GUARD_RECURSIVE_SPAWN_STRICT=1` as a **hard block**, but the hook is registered `PostToolUse` on `Edit|Write|MultiEdit` and exits `1` — so (a) it fires *after* the tool ran (nothing to block), and (b) exit 1 is non-blocking anyway (only exit 2 blocks). The house policy is deliberately *soft* (warn, not block — see the core constitution), so the advertised strict mode contradicts both the wiring and the policy.

**Question:** keep the guard warn-only and **delete the misleading `STRICT` env-var + hard-block prose**, or make strict genuinely block (move to `PreToolUse` on the spawn tool + exit 2)? Recommendation: **warn-only, remove the dead strict claim** — it matches the stated single-orchestrator policy and avoids a false sense of enforcement.

### D2 — Tie-breaker's own confidence is never gated
[`plugins/ravenclaude-core/scripts/thing-decide.py:444`](../../plugins/ravenclaude-core/scripts/thing-decide.py#L444)

`_tally()` convenes Thor exactly on the split/defer/low-confidence conditions the docstring says should defer — but after Thor runs, **its own `confidence` is never compared to the threshold**, so a low-confidence tie-breaker verdict can still become `binding`.

**Question:** should Thor's verdict bind only when its confidence clears the same threshold (else `defer`)? This is a tribunal safety semantic — recommend routing through the decision-review tribunal / architect before changing. Recommendation: **gate it** (low-confidence tie-break → `defer`), consistent with the fail-safe envelope.

### D3 — Self-heal commit uses `[skip ci]`
[`.github/workflows/regenerate-artifacts.yml:233`](../../.github/workflows/regenerate-artifacts.yml#L233)

The auto-regenerate commit ends in `[skip ci]`, which suppresses **all** validation workflows for that commit (not just the regen job).

**Question:** acceptable (the regeneration is deterministic and its inputs were already validated on the triggering PR), or should the regen commit run validation? Recommendation: **acceptable as-is** but worth a one-line comment stating the rationale so it isn't read as an accidental gate bypass.

---

## Deferred implementable items (with exact fixes) — not design, but out of safe auto-scope here

### F1 — Pin `peter-evans/create-pull-request@v6` to a commit SHA (P2)
[`.github/workflows/quarantine-intake.yml:137`](../../.github/workflows/quarantine-intake.yml#L137)

A movable major tag on a third-party action in an externally-triggerable write workflow. The fix is real, but resolving the exact immutable SHA for the current `v6.x` requires the action's own repository, which is **outside this session's GitHub scope** — guessing a SHA would break the intake workflow, so it is deferred rather than committed unverified.

**Exact remediation:** resolve `git ls-remote https://github.com/peter-evans/create-pull-request refs/tags/v6.<latest>` → pin `uses: peter-evans/create-pull-request@<sha> # v6.x` and add Dependabot (`.github/dependabot.yml`, `package-ecosystem: github-actions`) to bump the pin deliberately.

### F2 — `check-layout.py` `*` matches across `/` (P3)
[`scripts/check-layout.py:34`](../../scripts/check-layout.py#L34)

`fnmatchcase` translates `*` to `.*`, which spans `/`, so single-segment globs like `plugins/*/CLAUDE.md` also match deep paths. **Deferred because tightening to segment-aware matching changes gate semantics and could reject currently-passing deep paths.** Correct sequence: implement a segment-aware matcher, then run it against every tracked file and confirm zero *new* violations before committing.

### F3 — First-party GitHub actions pinned to floating major tags (P3, preference)
`actions/checkout@v4`, `setup-node@v4`, `setup-python@v5`, `github-script@v7`. GitHub-owned actions are materially lower supply-chain risk than third-party ones, and floating first-party majors is a common, defensible choice. Left as a **policy call** — adopt SHA-pinning + Dependabot only if you want uniformity with F1.

### F4 — Markdown-heading neutralization in external intake (P3)
[`scripts/process-scenario-submission.py:309`](../../scripts/process-scenario-submission.py#L309)

Submitter free-text isn't neutralized against `##`-heading injection into the staged doc. Low incremental risk (the path already scrubs secrets/injection deterministically, opens a PR — never pushes — and a maintainer reviews before promotion). **Exact fix:** prefix a zero-width-safe escape or blank line before any line matching `^\s*#` in the `problem`/`resolution` bodies before interpolation.

### F5 — `guard-recursive-spawn.sh` stdin file-path fallback (P3)
[`plugins/ravenclaude-core/hooks/guard-recursive-spawn.sh:50`](../../plugins/ravenclaude-core/hooks/guard-recursive-spawn.sh#L50)

Reads the touched path only from `$1`/`$CLAUDE_TOOL_FILE_PATH` and no-ops when Claude Code passes the path via stdin JSON — a sibling hook already added this fallback. Deferred to bundle with **D1** (same file, same contract discussion) and to mirror the sibling implementation exactly.

---

*Generated by the 3-panel review workflow. Panel verdicts and the adversarial verification notes are in the run transcript.*
