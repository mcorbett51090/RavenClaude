# Release checklist

Used when bumping a plugin or the marketplace metadata version. Tag releases as `v<marketplace-version>` on `main`. Per-plugin versions are pinned in each plugin's `.claude-plugin/plugin.json`.

## Before opening the release PR

- [ ] Each plugin's `CHANGELOG.md` has an entry under its new version (move items from `[Unreleased]`).
- [ ] Top-level `CHANGELOG.md` describes any marketplace-level changes (catalog edits, CI workflows, repo tooling).
- [ ] `plugins/<name>/.claude-plugin/plugin.json` `version` matches the changelog heading.
- [ ] `.claude-plugin/marketplace.json` `plugins[].version` matches each plugin's `plugin.json`.
- [ ] `.claude-plugin/marketplace.json` `metadata.version` bumped if the catalog itself changed shape (added/removed a plugin, changed schema).
- [ ] `docs/architecture.md` Status table reflects new versions.
- [ ] `README.md` install snippet still resolves (no breaking rename of a plugin's `source`).

## CI / local validation

- [ ] `validate-marketplace` workflow green on the release branch.
- [ ] Local: `python3 -m json.tool .claude-plugin/marketplace.json > /dev/null` and same for every `plugins/*/.claude-plugin/plugin.json`.
- [ ] Local: `bash -n plugins/*/hooks/*.sh` (shell syntax).
- [ ] Local: every `plugins/*/hooks/*.sh` is executable.
- [ ] Smoke test: from an unrelated project, `/plugin marketplace add ./` against this checkout, install both plugins, run one agent from each.

## On merge to `main`

- [ ] Tag the marketplace: `git tag v<marketplace-version> && git push origin v<marketplace-version>`.
- [ ] Consumers update via `/plugin marketplace update ravenclaude` followed by `/reload-plugins`.

## Notes

- The `release.yml` GitHub Actions workflow that would automate tag-and-publish is **deferred** until a `gh` token with `workflow` scope is available (`gh auth refresh -s workflow`). Until then, tag manually on merge.
- Breaking changes must include a migration note in the affected plugin's `CHANGELOG.md` entry — consumers running `/plugin marketplace update` should not silently break.
