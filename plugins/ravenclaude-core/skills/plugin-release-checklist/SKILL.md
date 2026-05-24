---
name: plugin-release-checklist
description: Pre-release checklist for shipping any plugin update through this marketplace — plugin.json + marketplace.json + architecture.md version-mirror discipline, .repo-layout.json glob coverage for new dirs, CLAUDE.md skill / template tables synced, JSON validation, prettier check, audit-gates meta-test, and the consumer migration-note rule. Includes the exact bash commands to run (Windows PowerShell + bash). Reach for this skill at the end of any plugin PR or before merging a release-candidate branch. Used by the maintainer (primary) plus `project-manager`.
---

# Skill: plugin-release-checklist

You are about to ship a plugin update through the RavenClaude marketplace. This checklist is the gate. Every numbered step has a command to run and a "what good looks like" line. Skip a step only if its sub-rule (at the bottom) authorizes the skip.

The checklist is not a substitute for CI — CI runs most of these gates and will block on failures. The checklist is what you run *before* opening or merging the PR, so the CI feedback loop is short and the PR doesn't ping-pong through fix-up commits.

## When to invoke this skill

- At the end of any plugin PR before requesting review.
- Before merging a release-candidate branch to main.
- Quarterly maintainer audit even if no release is pending — drift in version-mirror discipline is silent until the next release.

---

## The checklist

### 1. Plugin version bumped in `plugins/<plugin>/.claude-plugin/plugin.json`

Semver semantics — patch for fixes, minor for additive features, major for breaking changes that require consumer migration.

```bash
# bash
grep '"version"' plugins/<plugin>/.claude-plugin/plugin.json
```

```powershell
# PowerShell
Select-String -Path "plugins\<plugin>\.claude-plugin\plugin.json" -Pattern '"version"'
```

**What good looks like:** version is one increment higher than the last merged main commit's version on this file. `git log -p plugins/<plugin>/.claude-plugin/plugin.json | head -50` confirms.

---

### 2. SAME version mirrored in `.claude-plugin/marketplace.json`

The CI workflow `validate-marketplace.yml` fails on drift between the two files. Mirror by hand or via a release script.

```bash
# bash
jq -r '.plugins[] | select(.name=="<plugin>") | .version' .claude-plugin/marketplace.json
# must match the plugin.json value from step 1
```

```powershell
# PowerShell
(Get-Content .claude-plugin\marketplace.json | ConvertFrom-Json).plugins | Where-Object name -eq '<plugin>' | Select-Object -ExpandProperty version
```

**What good looks like:** the two values are identical strings.

---

### 3. SAME version mirrored in `docs/architecture.md` Status table (if present)

The architecture doc has a per-plugin status row that lists the current version. Update it in the same commit as the plugin.json bump.

```bash
# bash
grep -A2 '<plugin>' docs/architecture.md | grep -i version
```

```powershell
# PowerShell
Select-String -Path "docs\architecture.md" -Pattern '<plugin>' -Context 0,2
```

**What good looks like:** the architecture-doc row shows the same version as steps 1 and 2. If the architecture doc has no row for the plugin, this step is N/A — note that in the PR description.

---

### 4. JSON validity for all manifests

```bash
# bash
python3 -m json.tool .claude-plugin/marketplace.json > /dev/null
for m in plugins/*/.claude-plugin/plugin.json; do python3 -m json.tool "$m" > /dev/null; done
python3 -m json.tool .repo-layout.json > /dev/null
```

```powershell
# PowerShell — invoke python3 if available, else fallback
python3 -m json.tool .claude-plugin\marketplace.json > $null
Get-ChildItem plugins\*\.claude-plugin\plugin.json | ForEach-Object { python3 -m json.tool $_.FullName > $null }
python3 -m json.tool .repo-layout.json > $null
```

**What good looks like:** every command exits 0. No trailing-comma errors, no parse errors.

---

### 5. `.repo-layout.json` updated if any new top-level dir under `plugins/<plugin>/`

If the PR introduces a new directory (e.g. `plugins/<plugin>/scenarios/`, `plugins/<plugin>/decisions/`), the corresponding glob MUST appear in `.repo-layout.json` `allowed_globs`. Otherwise `validate-layout.yml` blocks the merge.

```bash
# bash — see the verification snippet in AGENTS.md "Layout-allow-list discipline"
python3 - <<'PY'
import fnmatch, json, subprocess
allowed = json.load(open(".repo-layout.json"))["allowed_globs"]
new = subprocess.run(["git", "diff", "--name-only", "--diff-filter=A", "main"],
                     capture_output=True, text=True).stdout.splitlines()
violations = [f for f in new if not any(fnmatch.fnmatchcase(f, g) for g in allowed)]
if violations:
    print("LAYOUT VIOLATIONS — add globs to .repo-layout.json first:")
    for v in violations: print(f"  - {v}")
else:
    print("Layout OK — every new file matches at least one allowed glob.")
PY
```

**What good looks like:** "Layout OK." If violations appear, add the appropriate globs to `.repo-layout.json` (and run step 4 again to confirm JSON validity).

---

### 6. Hook syntax + executability

```bash
# bash
bash -n plugins/*/hooks/*.sh
find plugins/*/hooks -name '*.sh' -exec test -x {} \; -print
```

```powershell
# PowerShell — use bash via WSL/Git Bash for -n parse-check
Get-ChildItem plugins\*\hooks\*.sh | ForEach-Object { bash -n $_.FullName }
# Executability check is a no-op on Windows filesystems; trust CI.
```

**What good looks like:** every `bash -n` exits 0 with no output. On Linux/macOS, every hook file appears in the executability list.

---

### 7. Prettier `--write` on the whole tree, then `--check`

CI runs `prettier --check .` against the entire working tree. A single mis-formatted file in main blocks every subsequent PR's CI. Always run `--write .` before pushing, even on markdown-only PRs.

```bash
# bash
npx --yes prettier --write . --log-level warn
npx --yes prettier --check . --log-level warn
```

```powershell
# PowerShell
npx --yes prettier --write . --log-level warn
npx --yes prettier --check . --log-level warn
```

**What good looks like:** `--check` exits 0 with no file listed as "would change." If `--write` made changes, commit them in the same PR.

---

### 8. Layout-violation pre-flight

This is the same check CI runs in `validate-layout.yml`. Running it locally catches the failure before pushing — see the AGENTS.md note "Layout-allow-list discipline" added 2026-05-21 after PR #32 failed.

The snippet in step 5 already runs this check. If you ran step 5, this is redundant — but include it explicitly when the PR added no new directories, just to be safe.

**What good looks like:** "Layout OK — every new file matches at least one allowed glob."

---

### 9. `scripts/audit-gates.sh` meta-test

The meta-test proves each CI gate fails on a known-bad fixture AND passes on a known-good one. Required reading before adding or changing any CI step: [`docs/best-practices/ci-gate-audit.md`](../../../../docs/best-practices/ci-gate-audit.md).

```bash
# bash
scripts/audit-gates.sh
```

```powershell
# PowerShell — call via WSL/Git Bash
bash scripts/audit-gates.sh
```

**What good looks like:** every gate logs "OK: must_fail_on triggered failure" and "OK: must_pass_on cleared." If the PR added or changed a CI step, the gate's fixture pair must exist in `audit-gates.sh` before merge.

---

### 10. Plugin's CLAUDE.md updated

Confirm three things in the plugin's CLAUDE.md:

**10a. §8 Skills table includes every new skill.**

```bash
# bash — list skills present on disk
ls plugins/<plugin>/skills/
# then grep the CLAUDE.md skills table for each
grep -E '^\| .* \|' plugins/<plugin>/CLAUDE.md | grep -i skill
```

**10b. §5 Capability Grounding Protocol skill list mentions new skills** if they're CGP-relevant.

**10c. Any new scenarios / hooks / templates / commands appear in their respective tables.** Cross-check the disk against the tables.

**What good looks like:** every file in `plugins/<plugin>/skills/`, `plugins/<plugin>/hooks/`, `plugins/<plugin>/templates/`, `plugins/<plugin>/commands/` appears in the CLAUDE.md tables. No orphans on disk; no rows pointing to deleted files.

---

### 11. README.md updated if user-facing description changed

The plugin's `README.md` is the first thing a consumer reads after `/plugin install`. If the change altered scope, added a major capability, or removed something visible, update the README.

```bash
# bash
git diff main -- plugins/<plugin>/README.md
```

**What good looks like:** if no user-visible scope change, README diff is empty — fine. If scope changed, README shows the update.

---

### 12. Migration-note in PR description (if the change could break a consumer)

A consumer who runs `/plugin marketplace update ravenclaude` followed by `/reload-plugins` should not be surprised. If the change could break their existing project (renamed skill, removed agent, changed hook behavior, renamed template), the PR description MUST include a `## Migration` section explaining:

- What changed
- Who's affected (which consumer patterns trip)
- The 1-line action they need to take

Use this template in the PR body:

```markdown
## Migration (consumer-facing)

**What changed:** <one line>

**Who's affected:** <which consumers — e.g. "anyone whose agent files import `agents/old-name.md`">

**Action required:** <one-line fix — e.g. "rename the import to `agents/new-name.md`">
```

**What good looks like:** no Migration section needed (purely additive change), or the section is present and accurate.

---

### 13. Local install test

From a separate test project (NOT the marketplace itself):

```bash
# In a separate test project
/plugin marketplace add /path/to/RavenClaude
/plugin install <plugin>@ravenclaude
# Confirm agents appear in /plugin UI.
# Run a quick smoke-test invocation of the new skill or agent.
```

**What good looks like:** plugin installs without error, new components appear in the UI, smoke-test produces expected output.

---

## If you're shipping with a hot fix

Hot fixes can't always wait for the full checklist. The minimum set that **absolutely cannot be skipped**:

- **Step 1** — plugin.json version bump (otherwise consumers don't get the fix on `/plugin marketplace update`)
- **Step 2** — marketplace.json version mirror (CI fails on drift; hot fix can't merge)
- **Step 3** — architecture.md mirror if present (same CI rationale)
- **Step 4** — JSON validity (a broken manifest blocks every subsequent install)

These four are non-negotiable. The remaining steps can be **deferred but tracked**:

- **Step 10 (CLAUDE.md tables)** — file a follow-up issue and link it in the hot-fix PR
- **Step 11 (README)** — same as above if user-visible
- **Step 13 (local install test)** — defer only if the change is text-only (no schema, no manifest, no hook). Schema/manifest hot fixes always run the install test.

Steps 5-9 (layout, hooks, prettier, audit-gates) CI catches at PR time — but for a hot fix you're racing to merge, run them locally first to avoid a CI ping-pong.

---

## Anti-patterns

- **Bumping plugin.json without mirroring to marketplace.json.** CI blocks. Always commit both in the same change.
- **Bumping the version "later, in a follow-up PR."** A change that goes out without a version bump is invisible to consumers — they won't `/plugin marketplace update` to a version they don't see.
- **Running `prettier --check` without running `--write` first.** If the check fails, `--write` would have fixed it. Always run `--write` first; the redundancy is cheap.
- **Skipping step 5 (.repo-layout.json) because "I didn't add a new top-level dir."** Did the PR add `plugins/<plugin>/scenarios/2026-05-21-foo.md`? That's a new file path under an existing allowed_glob — fine. Did it add `plugins/<plugin>/decisions/2026-05-21-bar.md`? That's a NEW dir; allow-list update needed.
- **Treating step 9 (audit-gates) as optional because "I only changed docs."** True — but a green audit-gates run is the proof for the next reviewer that no gate was inadvertently broken. Run it anyway; it's fast.
- **Deferring step 10 (CLAUDE.md) past the merge.** Skills/agents/templates on disk that aren't in the CLAUDE.md tables are functionally invisible to the next maintainer. Update the tables in the same PR.
- **Migration note in the commit message but not the PR description.** The PR description is what consumers see in release notes. Migration notes belong there.

---

## See also

- [`audit-ci-gates.md`](../audit-ci-gates/SKILL.md) — step 9's underlying meta-test.
- [`knowledge-file-staleness-sweep.md`](../knowledge-file-staleness-sweep/SKILL.md) — the pre-release knowledge-freshness gate that pairs with this checklist.
- [`../../../docs/best-practices/plugin-versioning.md`](../../../../docs/best-practices/plugin-versioning.md) — semver semantics for the marketplace.
- [`../../../docs/best-practices/ci-gate-audit.md`](../../../../docs/best-practices/ci-gate-audit.md) — the audit-by-fixture rationale for step 9.
- [`../../../AGENTS.md`](../../../../AGENTS.md) — the canonical version of the testing-instructions block this checklist operationalizes.
- [`../CLAUDE.md`](../../CLAUDE.md) — plugin-internal layout conventions referenced by step 10.
