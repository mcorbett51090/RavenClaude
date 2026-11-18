# ravenclaude-core gap analysis — 2026-11-16

Branch `factory-loop/ravenclaude-core-gap-hardening`. Scope was `plugins/ravenclaude-core`, with the cross-plugin call path as the hardening target.

The call path before this pass was prose. `skills/spawn-team/SKILL.md` told the Team Lead which `power-platform` agent to name, and `scripts/plugin-lifecycle.py` built `claude plugin install` / `uninstall` argv from a ledger key. There was no allowlist read against the catalog and the `plugins/` tree, and no check that a written `plugin/target` token resolved.

## Pass 1

Gaps:

- Spawn-team still said finance, EdTech, and Salesforce should be added "as plugins land". Those plugins are in the catalog. The table was being treated as the allowlist.
- `knowledge/agent-routing.md` said 14 agents in one sentence and a 17-agent roster in the next. `agents/` has 18 files. `explore`, `viz-spec-reviewer`, and `source-control-coordinator` were not in the table. `knowledge/routing-map.md` said 17.
- The architect prior and `skills/scenario-retrieval/SKILL.md` said scenario banks existed only in `power-platform`. A directory count on this checkout found 102 plugins with at least one scenario file.
- `plugin-lifecycle.py` interpolated a plugin key into an install command string and passed it as uninstall argv after checking only that the marketplace name was `ravenclaude`.
- Nothing failed CI when a backtick reference named a real plugin and a target that plugin does not ship. `works_with` was not checked against other plugins' agents.

Fixes: `scripts/cross-plugin-invoke.py` (resolve, check, sanitize, self-test), lifecycle install/uninstall goes through that decision, spawn-team / agent-routing / routing-map / architect / data-engineer / prompt-engineer / scenario-retrieval / agent-collaboration updated, threat model in `knowledge/cross-plugin-invocation.md`, version `0.365.0` with the catalog entry derived by `scripts/sync-plugin-versions.py`.

## Pass 2

Gaps:

- The first checker treated every file under `rules/` as a dispatch surface, so `rules/git-workflow.md` examples of GitHub `owner/repo` names were reported as unknown plugins. Dispatch surfaces are now core agents, commands, `rules/agent-collaboration.md`, `skills/spawn-team/SKILL.md`, and `knowledge/agent-routing.md`. A token whose left side is a callable plugin is still checked in the rest of the plugin.
- `sanitize` matched a `system:` line only at the start of the file. The marker pattern is multiline now, and the self-test plants a mid-file `system:` line.
- Telemetry recorded whatever plugin prefix arrived on stdin, including a traversal-shaped name, before any resolver ran. Ledger writes now refuse that shape. A hook payload `{prompt: /../evil:cmd}` does not create a row (lifecycle fixture).
- The ledger check first imported the resolver from beside `__file__`. The existing teeth fixture copies `plugin-lifecycle.py` alone into a temp directory and then seeds. That copy crashed. The shape check is local to the lifecycle file. Install and uninstall still load the resolver, and refuse if it cannot be loaded.

Lifecycle fixture after this pass: 46 pass, 0 fail. Resolver self-test: pass.

## Pass 3

Gap: `knowledge/cross-plugin-invocation.md` named Gate 320. That gate is not in `scripts/audit-gates.sh`. Rewriting `scripts/audit-gates.sh`, `.github/workflows/validate-marketplace.yml`, and `plugins/ravenclaude-core/CHANGELOG.md` was refused: the edit is applied as a full-file write, and those files already contain text the command-review hard rule will not write back. The doc now points at `.github/workflows/validate-cross-plugin-refs.yml`, which runs `--self-test` and `check` on every pull request, and states that the audit script was not given a new numbered gate.

Also updated the review dates on `agent-routing.md` and `routing-map.md` so they match the roster correction.

## Pass 4

Re-read the resolver, the lifecycle gates, the threat model, and the workflow. Re-ran:

- `python3 plugins/ravenclaude-core/scripts/cross-plugin-invoke.py --self-test` — pass
- `bash plugins/ravenclaude-core/hooks/tests/test-plugin-lifecycle.sh` — 46 pass, 0 fail
- `python3 plugins/ravenclaude-core/scripts/cross-plugin-invoke.py check` — ok
- `python3 -m ruff check` on the two Python files — pass
- prettier on the new workflow, `plugin.json`, and `marketplace.json` — pass

Nothing new worth a code change.

Left as they are, with a reason:

- Abbreviated SHA equality in `plugin-lifecycle.py` (`_sha_equal`) is an integrity compare for install pins, not plugin-name resolution. Short pins stay accepted.
- A GitHub `owner/repo` mention outside a dispatch surface is not reported as a plugin reference. `resolve` still refuses a name that is not in the registry.
- `CHANGELOG.md` does not have a 0.365.0 entry. The version field in `plugin.json` was bumped and the catalog entry was derived. The changelog file itself could not be rewritten, for the reason in pass 3.
- `scripts/audit-gates.sh` has no new gate number, for the same reason. The pull-request workflow is the CI check.
