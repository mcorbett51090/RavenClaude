# Remote branch cleanup manifest

_Generated 2026-06-01. Branch state classified via the GitHub PR API (authoritative state field), not `git cherry` (which mis-reports multi-commit squash-merges)._

## Why this is a manifest, not a completed deletion

Remote branches could not be deleted from the session that produced this file:
- `git push origin --delete <branch>` → **HTTP 403** (the git remote is a local proxy that moves commits but refuses ref-deletion — see CLAUDE.md "Remote-environment PR mechanics").
- The GitHub MCP tool set has **no delete-branch tool** (`create_branch`/`list_branches` exist; no delete).

So deletion is a human/`gh` step. Pick one:
- **Best (ongoing):** GitHub → repo **Settings → General → Pull Requests → "Automatically delete head branches"**. Handles every future merged-PR branch with zero effort.
- **Bulk the existing backlog** from any machine with `gh` authenticated:
  ```bash
  # run from a clone; deletes every branch in the 'Safe to delete' list below
  gh api repos/mcorbett51090/RavenClaude/branches --paginate -q '.[].name' > /dev/null  # (optional: sanity list)
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/chore/remove-5stage-doc   # PR #162
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/claude/copilot-grounding-digest-OXFkX   # PR #169
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/claude/core-event-substrate-xZQyq   # PR #141
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/claude/dashboard-5-stage-process-B1dCc   # PR #160
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/claude/refine-local-plan-2ra0g   # PR #103
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/claude/repo-analysis-build-plan-1CWTV   # PR #119
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/claude/resumed-session-recovery-OXFkX   # PR #168
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/claude/whats-next-kkeBE   # PR #128
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/feat/applied-statistics-plugin   # PR #95
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/feat/buildout-batch1   # PR #136
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/feat/buildout-batch2   # PR #137
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/feat/dashboard-category-nav   # PR #164
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/feat/dashboard-pr2   # PR #139
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/feat/dashboard-pr3   # PR #140
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/feat/dashboard-raven-mark   # PR #166
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/feat/dashboard-ravenpower-look   # PR #163
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/feat/dashboard-semantic-colors   # PR #165
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/feat/dashboard-ux   # PR #138
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/feat/error-cause-probing   # PR #167
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/feat/microsoft-365-copilot   # PR #131
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/feat/microsoft-graph-plugin   # PR #135
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/feat/per-plugin-context   # PR #132
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/feat/power-platform-commands   # PR #156
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/feat/pp-sf-buildout   # PR #133
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/feat/ravenclaude-core-bifrost-install   # PR #151
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/feat/ravenclaude-core-capability-orientation   # PR #98
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/feat/ravenclaude-core-command-tab-foundation   # PR #154
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/feat/ravenclaude-core-dashboard-round1   # PR #158
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/feat/ravenclaude-core-heimdall   # PR #142
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/feat/ravenclaude-core-mcp-allowed-servers   # PR #110
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/feat/ravenclaude-core-mcp-allowlist-dashboard   # PR #111
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/feat/ravenclaude-core-nidhoggr-debt-watch   # PR #149
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/feat/ravenclaude-core-norns   # PR #144
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/feat/ravenclaude-core-orientation-runtime   # PR #146
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/feat/ravenclaude-core-pipeline-tab   # PR #129
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/feat/ravenclaude-core-ragnarok   # PR #153
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/feat/ravenclaude-core-route-awareness-salience   # PR #157
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/feat/ravenclaude-core-runtime-state-bp   # PR #145
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/feat/ravenclaude-core-scenario-surfacing-signal   # PR #148
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/feat/ravenclaude-core-sleipnir-worktree   # PR #152
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/feat/ravenclaude-core-thing-finishout   # PR #99
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/feat/ravenclaude-core-track-b-network-write   # PR #108
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/feat/ravenclaude-core-track-b-phase1-file-edit   # PR #106
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/feat/ravenclaude-core-track-b-phases-2-4-reads-net-mcp   # PR #107
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/feat/ravenclaude-core-tribunal-engine-foundation   # PR #105
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/feat/ravenclaude-core-verify-before-blocked   # PR #161
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/feat/ravenclaude-core-vidarr   # PR #143
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/feat/ravenclaude-core-wrap-runtime-context   # PR #147
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/feat/salesforce-commands   # PR #155
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/feat/salesforce-plugin   # PR #130
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/feat/tableau-plugin   # PR #134
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/feat/tribunal-tool-review-prephase   # PR #104
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/fix/ci-structural-integrity   # PR #171
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/fix/copilot-installer-status-project-flag   # PR #109
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/fix/microsoft-graph-knowledge-dates   # PR #173
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/fix/ravenclaude-core-guard-destructive-bypass   # PR #170
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/fix/ravenclaude-core-panel-p1-findings   # PR #150
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/fix/ravenclaude-core-skill-frontmatter   # PR #96
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/fix/salesforce-test-author-seam   # PR #172
  gh api -X DELETE repos/mcorbett51090/RavenClaude/git/refs/heads/fix/workstream-d-grok-persona-injection   # PR #174
  ```
- Or the GitHub UI **branches page** has a per-row trash icon.

## ✅ Safe to delete — closed PR, content resolved (60)

Each maps to a closed PR (merged into `main`, or superseded). Deleting them loses nothing.

- [ ] `chore/remove-5stage-doc` — PR #162
- [ ] `claude/copilot-grounding-digest-OXFkX` — PR #169
- [ ] `claude/core-event-substrate-xZQyq` — PR #141
- [ ] `claude/dashboard-5-stage-process-B1dCc` — PR #160
- [ ] `claude/refine-local-plan-2ra0g` — PR #103
- [ ] `claude/repo-analysis-build-plan-1CWTV` — PR #119
- [ ] `claude/resumed-session-recovery-OXFkX` — PR #168
- [ ] `claude/whats-next-kkeBE` — PR #128
- [ ] `feat/applied-statistics-plugin` — PR #95
- [ ] `feat/buildout-batch1` — PR #136
- [ ] `feat/buildout-batch2` — PR #137
- [ ] `feat/dashboard-category-nav` — PR #164
- [ ] `feat/dashboard-pr2` — PR #139
- [ ] `feat/dashboard-pr3` — PR #140
- [ ] `feat/dashboard-raven-mark` — PR #166
- [ ] `feat/dashboard-ravenpower-look` — PR #163
- [ ] `feat/dashboard-semantic-colors` — PR #165
- [ ] `feat/dashboard-ux` — PR #138
- [ ] `feat/error-cause-probing` — PR #167
- [ ] `feat/microsoft-365-copilot` — PR #131
- [ ] `feat/microsoft-graph-plugin` — PR #135
- [ ] `feat/per-plugin-context` — PR #132
- [ ] `feat/power-platform-commands` — PR #156
- [ ] `feat/pp-sf-buildout` — PR #133
- [ ] `feat/ravenclaude-core-bifrost-install` — PR #151
- [ ] `feat/ravenclaude-core-capability-orientation` — PR #98
- [ ] `feat/ravenclaude-core-command-tab-foundation` — PR #154
- [ ] `feat/ravenclaude-core-dashboard-round1` — PR #158
- [ ] `feat/ravenclaude-core-heimdall` — PR #142
- [ ] `feat/ravenclaude-core-mcp-allowed-servers` — PR #110
- [ ] `feat/ravenclaude-core-mcp-allowlist-dashboard` — PR #111
- [ ] `feat/ravenclaude-core-nidhoggr-debt-watch` — PR #149
- [ ] `feat/ravenclaude-core-norns` — PR #144
- [ ] `feat/ravenclaude-core-orientation-runtime` — PR #146
- [ ] `feat/ravenclaude-core-pipeline-tab` — PR #129
- [ ] `feat/ravenclaude-core-ragnarok` — PR #153
- [ ] `feat/ravenclaude-core-route-awareness-salience` — PR #157
- [ ] `feat/ravenclaude-core-runtime-state-bp` — PR #145
- [ ] `feat/ravenclaude-core-scenario-surfacing-signal` — PR #148
- [ ] `feat/ravenclaude-core-sleipnir-worktree` — PR #152
- [ ] `feat/ravenclaude-core-thing-finishout` — PR #99
- [ ] `feat/ravenclaude-core-track-b-network-write` — PR #108
- [ ] `feat/ravenclaude-core-track-b-phase1-file-edit` — PR #106
- [ ] `feat/ravenclaude-core-track-b-phases-2-4-reads-net-mcp` — PR #107
- [ ] `feat/ravenclaude-core-tribunal-engine-foundation` — PR #105
- [ ] `feat/ravenclaude-core-verify-before-blocked` — PR #161
- [ ] `feat/ravenclaude-core-vidarr` — PR #143
- [ ] `feat/ravenclaude-core-wrap-runtime-context` — PR #147
- [ ] `feat/salesforce-commands` — PR #155
- [ ] `feat/salesforce-plugin` — PR #130
- [ ] `feat/tableau-plugin` — PR #134
- [ ] `feat/tribunal-tool-review-prephase` — PR #104
- [ ] `fix/ci-structural-integrity` — PR #171
- [ ] `fix/copilot-installer-status-project-flag` — PR #109
- [ ] `fix/microsoft-graph-knowledge-dates` — PR #173
- [ ] `fix/ravenclaude-core-guard-destructive-bypass` — PR #170
- [ ] `fix/ravenclaude-core-panel-p1-findings` — PR #150
- [ ] `fix/ravenclaude-core-skill-frontmatter` — PR #96
- [ ] `fix/salesforce-test-author-seam` — PR #172
- [ ] `fix/workstream-d-grok-persona-injection` — PR #174

## ⛔ KEEP — open PR (1)

- `feat/ravenclaude-core-dashboard-round5` — PR #159 (**OPEN** — do not delete)

## ⚠️ Needs a human call — no PR found (4)

These remote branches have no associated PR, so their content can't be confirmed shipped. `dashboard-round2/3/4` are very likely superseded intermediates (round1 = PR #158, round5 = PR #159 open), and `core-event-substrate` likely predates `claude/core-event-substrate-xZQyq` (PR #141) — but verify before deleting.

- `feat/core-event-substrate`
- `feat/ravenclaude-core-dashboard-round2`
- `feat/ravenclaude-core-dashboard-round3`
- `feat/ravenclaude-core-dashboard-round4`

