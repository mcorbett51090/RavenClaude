# Release checklist

Use this checklist when cutting a new version of any plugin in this marketplace (or the marketplace catalog itself). It's ordered: complete each section before the next.

Targets the flow that ships today — manual version bump in `plugin.json`, PR to `main`, optional tag, optional GitHub Release. The tag-driven `release.yml` workflow (added under the release-discipline PR) automates the GitHub Release once a tag is pushed.

---

## 0. Decide what kind of release this is

- [ ] **Patch** (`0.2.0 → 0.2.1`) — bug fix, doc fix, hook tweak, no consumer-visible behavior change
- [ ] **Minor** (`0.2.0 → 0.3.0`) — new agent, new skill, new hook, new template; backward-compatible for existing consumers
- [ ] **Major** (`0.2.0 → 1.0.0`) — removes or renames an agent/skill, changes a hook contract, or otherwise breaks an existing consumer's expectations

If unsure, mentally simulate: "a consumer runs `/plugin marketplace update ravenclaude` — what changes?" If the answer would surprise them, write a migration note in the PR body and consider major.

---

## 1. Pre-flight (before opening the PR)

- [ ] On a fresh feature branch off `main`, not `main` itself.
- [ ] Plugin `version` bumped in `plugins/<plugin>/.claude-plugin/plugin.json`.
- [ ] Catalog `version` bumped in `.claude-plugin/marketplace.json` (the version inside the relevant entry of `plugins[]`). Numbers must match — the version-drift CI step will fail if they don't.
- [ ] `plugins/<plugin>/CHANGELOG.md` updated with a new dated section describing the change. Top of file, reverse-chronological.
- [ ] If this is a minor or major release: top-level `CHANGELOG.md` also updated.
- [ ] **Regenerate the interactive repo guide:** `python3 scripts/generate-repo-guide.py`. Commit the updated `repo-guide.html` (at the repo root) along with the rest of the change — CI's `Verify repo-guide.html is fresh` step (and the meta-test) will fail otherwise.
- [ ] `docs/architecture.md` Status table updated if version numbers there are now stale.
- [ ] No secrets, no client identifiers, no internal URLs in the diff. Skim `git diff` once more.

### 1.5 Knowledge health (added 2026-06-01)

- [ ] **Run the knowledge-health sweep:** `python3 plugins/ravenclaude-core/scripts/knowledge-health.py`. The script lists every `plugins/*/knowledge/**.md` and groups them by `stale` (>90 days since last verified), `due_soon` (60-90 days), `untracked` (no date marker), `fresh` (<60 days).
- [ ] Any **stale** entry inside the release diff must be re-verified in this PR (or explicitly deferred with a memory entry + a follow-up issue). Stale content shipping unchanged into consumers is the highest-priority knowledge-layer failure mode the marketplace is set up to prevent.
- [ ] Any **untracked** entry: ideally add a `Last reviewed: YYYY-MM-DD` marker in this PR. If out of scope, file the gap as a follow-up — untracked files escape every future sweep.

### 1.6 Security floor invariant (added 2026-06-01)

- [ ] **Confirm the `security_deny` floor is non-removable:** `python3 tests/fixtures/test_security_deny_floor.py`. All 6 cases must pass. A regression here means a consumer could wipe the security floor from the dashboard by saving an empty list. **This is the highest-severity invariant the marketplace ships.**
- [ ] If this release changes `plugins/ravenclaude-core/scripts/apply-comfort-posture.py`, hand-confirm the diff does not weaken the `compute_emission` / `compute_emission_v5` union path.

---

## 2. Local validation

Run the same checks that CI runs, locally:

- [ ] `python3 -m json.tool .claude-plugin/marketplace.json > /dev/null` — catalog parses
- [ ] `for m in plugins/*/.claude-plugin/plugin.json; do python3 -m json.tool "$m" > /dev/null; done` — every plugin manifest parses
- [ ] `bash -n plugins/*/hooks/*.sh` — every hook is syntactically valid bash
- [ ] `find plugins/*/hooks -name '*.sh' -exec test -x {} \;` — hooks are executable (else CI fails)
- [ ] **Smoke install**: from a scratch directory, `/plugin marketplace add /path/to/RavenClaude`, then `/plugin install <plugin>@ravenclaude`, then `/reload-plugins`. Verify the plugin's agents appear in `/plugin` UI and at least one specialist responds via `spawn-team`.

If a step fails, fix it before pushing — don't push and hope CI catches it.

---

## 3. Open the PR

- [ ] PR title is Conventional Commits style: `feat(<plugin>): …` for minor, `fix(<plugin>): …` for patch, `feat(<plugin>)!:` or a `BREAKING CHANGE:` footer for major.
- [ ] PR body uses the default template. Fill the **Marketplace / meta change** section honestly.
- [ ] Migration note included if any consumer will notice a behavior change after `marketplace update`.
- [ ] Linked to the relevant issue (if any).

---

## 4. CI green

- [ ] `Validate Marketplace` workflow passes (JSON validity, hook syntax, executability, version-drift check).
- [ ] `shellcheck`, link-check, and the smoke-install step pass (added in the CI quality-gates PR).
- [ ] No new warnings in the workflow logs that you don't understand. Investigate, don't ignore.

---

## 5. Merge

- [ ] Matt approves and merges to `main`. (No self-merges; no force-push to `main`.)
- [ ] Branch is deleted from the remote after merge.

---

## 6. Tag and publish a GitHub Release

> **Today:** there is no `release.yml` workflow yet — drafting the GitHub Release is a manual step. A workflow that auto-drafts on tag is a planned follow-up; it needs a token with the `workflow` scope to land. Until then, follow the steps below verbatim.

- [ ] Pull `main` locally so your tag is on the merged commit, not the PR branch.
- [ ] Tag with the correct prefix (examples assume the next patch after current versions — substitute the actual next version):
  ```bash
  # For a ravenclaude-core release (current 0.6.0):
  git tag ravenclaude-core-v0.6.1
  git push origin ravenclaude-core-v0.6.1

  # For a power-platform release (current 0.7.0):
  git tag power-platform-v0.7.1
  git push origin power-platform-v0.7.1

  # For a top-level marketplace metadata release (current 0.4.0):
  git tag marketplace-v0.4.1
  git push origin marketplace-v0.4.1
  ```
- [ ] In the GitHub UI: **Releases → Draft a new release → choose the tag → paste the matching CHANGELOG section as the release notes → publish**.

---

## 7. Verify consumers pick it up

- [ ] From a separate test project: `/plugin marketplace update ravenclaude` then `/reload-plugins`. Confirm the new version is loaded (check `/plugin` UI or read the plugin's `plugin.json` from `~/.claude/plugins/cache/`).
- [ ] If the release adds an agent or skill, dispatch it once via `spawn-team` to confirm it loads cleanly.
- [ ] If the release adds or changes a hook, trigger a matching file edit and confirm the hook fires (or doesn't, if it was scoped down).

---

## 8. Communicate

- [ ] If consumers will see a behavior change after `marketplace update`, post a short note in the team channel: what changed, what (if anything) they need to do, and a link to the GitHub Release.
- [ ] If the release fixes a known bug, comment on the related issue and close it.

---

## Common failure modes (and what they actually mean)

| Symptom | Root cause |
|---|---|
| CI version-drift step fails | You bumped `plugin.json` but forgot the matching entry in `marketplace.json` (or vice versa). |
| `/plugin install` fails with "plugin not found" | Consumer is on a stale catalog. They need `/plugin marketplace update ravenclaude` first. |
| Hook doesn't fire on consumer machine | The hook isn't executable in the published version (CI catches this, but only if the workflow ran). Re-tag after fixing. |
| Imported skill missing on consumer machine | The skill folder was added but not committed (check `git status` before tagging). |
| `pbix-mcp-server` not found in consumer terminal | They haven't run `pip install pbix-mcp`. Note this in the release notes for any `power-platform` release that touches PBIP/DAX flows. |
