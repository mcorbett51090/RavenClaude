# Repository review — 2026-09-22

Autonomous whole-repo review run on branch `claude/stoic-fermat-wnm3aw`. Three-panel
expert process (Panel 1: 6 dimension reviewers → Panel 2: consolidation/validation →
Panel 3: tie-break of ambiguous items), then per-finding grounding against the actual
code before any edit, then implementation of the confirmed, low-risk, no-design-input
fixes.

## Baseline: the repo is healthy on every automated check

Before the expert panels, the repo's own ground-truth gates were run and all passed:
`prettier --check .`, `ruff check .`, `check-frontmatter.py`, `bash -n` on all
hooks+scripts, hook executability, `sync-plugin-versions.py --check`, `check-md-links.py`,
JSON manifest validity, and the `audit-gates.sh` meta-suite (250+ gates, all green). The
branch is level with `origin/main`. Findings below are logic-level issues that the
automated gates do not fully cover.

## Implemented in this PR

Grouped by priority. None required a plugin version bump — every changed file is
marketplace tooling (`scripts/`, `.github/workflows/`) or a root boundary file
(`CLAUDE.md`), not shipped plugin content, so no `plugins/*` manifest, generated
artifact, or Copilot projection changed.

### P2 — real bugs

- **SIGPIPE + `pipefail` fail-open in the golden-set self-required-check assertion.**
  `.github/workflows/golden-set-inject-light.yml` — `echo "$rules" | grep -Fqi …` under
  `set -euo pipefail`: when the workflow name _is_ present (the state the control exists
  to catch) and the rulesets JSON exceeds the pipe buffer, `grep` closes the pipe early,
  `echo` dies with SIGPIPE, `pipefail` flips the `if` to its false branch, and the step
  reports **OK / exit 0** — the control silently never fires. Fixed with a here-string
  (`grep -Fqi "…" <<<"$rules"`), the exact remedy already used at
  `validate-marketplace.yml:648` (documented there as seen on PR #1155).

- **Same SIGPIPE fail-open in the inventory-sweep self-required-check assertion.**
  `.github/workflows/inventory-sweep.yml` — `printf '%s' "$rules" | grep -q 'Inventory
  sweep'`, same class, distinct file. Fixed with the same here-string remedy.

### P3 — tech-debt / robustness

- **`generate-cursor-hooks.py --check` lacked the stale-`_SKIP` detection its siblings
  carry.** The copilot (`:282`) and codex generators both fail `--check` when the skip map
  names a hook that no longer exists in `hooks.json`; cursor did not, so a hook deleted
  from the manifest but left in cursor's `_SKIP` would pass green while the siblings
  failed, shipping a dead `_not_wired` entry. Added the
  `stale = set(_SKIP) - canonical → return 1` block, mirroring the copilot sibling.

- **`generate-gemini-hooks.py --check` had the same gap.** Same fix, distinct file.

- **`install-copilot-mcp.py` rewrote the global `mcp-config.json` even when no server was
  added.** An unconditional `dest.write_text(...)` re-serialized the parsed JSON (normalizing
  the user's hand-formatting) on every run, even a no-op one. Added `if not added: return 0`
  before the write, mirroring `install-codex-mcp.py`'s early return on an empty add set.

### P3 — docs accuracy

- **`CLAUDE.md` § "Slash commands shipped by the plugin" understated the count and pointed
  at a nonexistent table.** It said "ships **9** slash commands" (actual: 12 `commands/*.md`)
  and referenced `README.md`'s "What's in each plugin" table, which does not exist (verified
  by grep). Rather than reset the number to 12 — which would just re-stale on the next command
  added — the fix follows the repo's own **owner decision D1** (`check-description-count-literals.py`:
  drop prose count literals, don't sync them) and drops the hard number entirely, repointing
  to `plugins/ravenclaude-core/commands/` as the authoritative, self-updating list. The root
  CLAUDE.md prose is not in any count gate's scope, which is exactly why "9" drifted unnoticed.

## Rejected after grounding — a false positive, no change made

- **`sync-plugin-versions.py --must-fail` "returns exit 0 when the gate's teeth fail".**
  The panel flagged the `if rc == 0: … return 0` teeth-failure branch (`scripts/sync-plugin-versions.py:501`)
  as a bug and proposed `return 1`. **Grounding shows the current behavior is correct and
  load-bearing.** `audit-gates.sh` invokes `--must-fail` inside a `must_fail` wrapper that
  expects a non-zero exit and specifically asserts exit **2**:
  - `--check 226` dispatcher (`:1295-1296`): `[ "$_mf" -eq 2 ] || rc=1`
  - main sequence (`:9213-9216`): `gate "…planted catalog drift IS caught" must_fail "$rc"`
    then `[ "$rc" -eq 2 ]`.

  On teeth-pass, `--must-fail` returns 2 (the inner `evaluate --check` reddens at 2), so both
  assertions hold. On teeth-**failure** (planted drift not caught, `rc == 0`), returning `0`
  makes the primary `must_fail "$rc"` assertion fail loudly — exactly the intended surfacing of
  a broken gate. Changing it to `return 1` would make that primary assertion falsely **pass**
  (1 ≠ 0), leaving only the secondary exit-2 assertion to catch the breakage — a net weakening.
  **No change made.**

## Needs your input — deferred with recommendations

### D1. `dod-gate.sh` trust-separation greps `trusted:`/`cmd:` file-wide (P2, security)

`plugins/ravenclaude-core/hooks/dod-gate.sh:135-136` resolve the `trusted:`/`cmd:` line
numbers with `grep -n -m1 -E` **unanchored to any YAML block**, then compare their git-blame
commits to decide whether trust was granted separately from the command (the b26
anti-self-attestation hardening). Because `web_access.trusted: true` is a real, documented
second `trusted:` key elsewhere in the same posture file (`guard-web-access.sh:170`), a repo
that has `web_access.trusted: true` committed _above_ the `definition_of_done` block, plus an
attacker PR that adds `definition_of_done.cmd` + `trusted: true` in one commit, gets:
`trusted_line` binding to the older `web_access` line, `cmd_line` to the attacker's line,
different blame commits → `dod_trust_sep=true` → the first-run confirm-file challenge is
skipped → `$dod_cmd` executes unprompted on the next `Stop`.

- **Impact:** bypasses the exact single-commit trust+cmd injection b26 was built to stop.
  **Conditional:** requires `web_access.trusted: true` live, ordered before the dod
  `trusted:` line, committed separately; the shipped balanced template ships both `false`
  and orders `definition_of_done` first, so the shipped seed is not vulnerable.
- **Recommended fix (mechanical, low-risk):** resolve `trusted_line`/`cmd_line` only within
  the `definition_of_done` block's line range via a single block-scoped `awk` pass — the exact
  pattern already used at `route-decision-review.sh:73-81` for its nested `mode:` key. The
  correctly-scoped `__DOD_TRUSTED_PY` block (`:116-117`) already parses `definition_of_done.trusted`
  properly; only the blame-separation line-number lookup reads the wrong line.
- **Why deferred, not implemented:** the command-review tribunal is active in this repo and its
  `xc.tribunal-self-disable` concern denies, unilaterally and pre-LLM, any mutation of the plugin
  `hooks/` directory — an autonomous session cannot edit `dod-gate.sh`. This is the correct
  guardrail behavior for an agent-authored change to a security hook. **Apply from the dashboard
  or an interactive maintainer session**, where the edit is not tribunal-denied.

### D2. Two gate checkers use a non-recursive hook glob with no zero-file guard (P3)

`scripts/check-grep-ere-pcre.py:143` and `scripts/check-hook-stdin-fallback.py:73` both scan
`os.path.join(root, "plugins", "*", "hooks", "*.sh")` — one level deep, and with no assertion
that at least one file was scanned. If the glob ever matched zero files (a refactor moving
hooks, a wrong `--root`), both print "passed" and exit 0 — the fail-open pattern the repo
elsewhere treats as a defect.

- **The recommended fix has a real trade-off that needs a decision.** Switching to a recursive
  glob (`plugins/*/hooks/**/*.sh`) would also scan `plugins/*/hooks/tests/*.sh`, which contain
  `grep -P` / stdin patterns as **test fixtures** — likely new false positives that could break
  CI. `check-hook-stdin-fallback.py` already skips `test-`-prefixed basenames, but the coverage
  intent (are nested non-test hooks in scope? are `hooks/tests/` fixtures deliberately excluded?)
  is a judgment call, not mechanical.
- **Recommendation:** add the **zero-file fail-closed guard** to both (safe — there are always
  hook files at the one-level path, so it never fires falsely, but it closes the fail-open hole),
  and decide separately whether to widen to recursive with an explicit `hooks/tests/` exclusion.
  Deferred because the recursive half is a scope decision with CI-breakage risk, and this is an
  unattended run.

## Method notes

- Panel model tiering followed the task: Panel 1 dimension reviewers at medium effort, Panel 2
  consolidation and Panel 3 tie-break at high effort.
- Every implemented fix was validated post-edit: `ruff`, `py_compile`, the relevant `--check`
  scripts (cursor/gemini/copilot hooks all green, unchanged wired/skipped counts), `check-md-links.py`,
  `check-marketplace-claims.py`, `check-description-count-literals.py`, and whole-tree
  `prettier --check .` (CI parity) — all pass.
- No generated/committed artifact required regeneration: the `--check`-path edits do not change
  what the generators produce, and no `plugins/*` manifest or version was touched.
