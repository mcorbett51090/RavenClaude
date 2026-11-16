# Cross-plugin invocation

**Last reviewed:** 2026-11-16 · **Owner:** ravenclaude-core  
**Code:** [`scripts/cross-plugin-invoke.py`](../scripts/cross-plugin-invoke.py)  
**Check:** `python3 plugins/ravenclaude-core/scripts/cross-plugin-invoke.py check`  
**CI:** [`.github/workflows/validate-cross-plugin-refs.yml`](../../../.github/workflows/validate-cross-plugin-refs.yml) runs that check and `--self-test` on every pull request.

The Team Lead is the only caller. This command resolves a plugin name and a target inside it. It does not run the plugin, does not start a shell, and does not pick a nearby name when the requested one is wrong.

## Threat model

| Actor | What they can try | What the resolver does |
|---|---|---|
| A brief, a report, or a ledger row names a plugin | Path traversal (`../`), an absolute path, a symlink that leaves `plugins/`, a prefix (`power` for `power-platform`), or a different case | Refuse with a stable `reason`. No closest match, no prefix completion, no path is returned. |
| The same input carries shell metacharacters | A name or an arg that would be dangerous if concatenated into a command string | Names that are not the exact pattern are refused. Args are a JSON object echoed back with `shell: false`. Nothing is interpolated into a shell command. |
| A resolved agent is over-privileged | `tools` contains `Agent`, `Task`, or `*` | Refuse `tools_overprivileged`. The plan's `tools` list is the allow-list the host passes on. Empty or missing tools refuse `tools_missing`. |
| A hop calls another hop | A cycle, or a chain longer than 3 | Refuse `cycle` or `depth_exceeded`. The caller must pass the `chain` the previous plan returned. |
| A plugin file or a specialist report contains instructions | "ignore previous instructions", a system-reminder block, a role rewrite | `resolve` does not put file bodies in the plan. `sanitize --file` returns the bytes as `DATA:` lines with `treated_as: untrusted_data`. Those lines are not instructions. |
| The catalog and the disk disagree | A catalog name with no directory, a directory with no catalog entry, a manifest `name` that does not equal the directory | That name is not callable. The reason names which of those it was. |
| A consumer install cannot see sibling plugins | Lifecycle install/uninstall still has to build an argv | Shape check still refuses traversal and metacharacters. Registry membership is enforced when the marketplace tree is visible (`RAVENCLAUDE_MARKET` or a parent that contains the catalog and `plugins/`). It is not enforced when that tree is absent, and `resolve` itself refuses `registry_unavailable` rather than skipping the check. |

`plugin-lifecycle.py` asks this resolver before it builds an install command string or an uninstall argv. A refused name produces no argv.

## Guarantees

A successful `resolve` plan includes `guarantees` and all of the following:

- **exact-name** — the plugin and the target match one registry key. No fuzzy match, no prefix match, no case fold.
- **registry-allowlist** — callable plugins are the catalog `plugins[].name` values that also exist as `plugins/<name>/.claude-plugin/plugin.json` with the same `name`, and the directory is not a symlink.
- **no-shell** — this process does not import a shell runner and does not set `shell` true.
- **no-fallback** — unknown plugin, unknown target, and the wrong `--kind` are refusals. An agent request does not silently return a skill of the same name.
- **args-are-data** — `--args` is a JSON object with short keys. It is copied into the plan and not executed.
- **output-is-data** — plugin file contents are not instructions. Use `sanitize` on a report before reading it as content.
- **least-privilege-tools** — an agent plan carries the `tools` line from that agent's frontmatter, minus any right to dispatch. A dispatch tool is a refusal, not a stripped list.
- **depth-limited** and **cycle-detected** — depth is `len(chain) + 1`, the maximum is 3, and a plugin already in the chain is a cycle.
- **deterministic failure** — the same arguments produce the same JSON (`sort_keys`) and the same exit code. Exit 0 is a plan. Exit 2 is a refusal or a check violation. Exit 1 is usage or a failed self-test.

## What this does not do

- It does not start the worker. `timeout_ms` (default 120000, allowed 1000–600000) is in the plan as `timeout_enforced_by: host`. The Team Lead stops the worker. The resolver's own reads are capped (64 KiB for manifests and frontmatter, 1 MiB for sanitize).
- It does not see a GitHub `owner/repo` mention as a plugin reference. The check flags a backtick token whose left side is a callable plugin and whose right side is not an agent, skill, or command of that plugin. On dispatch surfaces (core agents, commands, `rules/agent-collaboration.md`, `skills/spawn-team/SKILL.md`, `knowledge/agent-routing.md`) it also flags a left side that is neither a callable plugin nor a known non-plugin word such as `actions` or `scripts`.
- `works_with` on a core agent must name a core agent, or exactly one agent of that stem in another plugin. Zero matches and two matches both fail the check.
- A misspelled plugin name written outside those surfaces, in a shape that is also a GitHub repository, is not something the check can separate. `resolve` still refuses it at dispatch time.

## Check

`check` exits 2 when any of those references do not resolve, and exits 2 when the registry itself cannot be loaded. An empty result is not a pass from a missing tree. `python3 plugins/ravenclaude-core/scripts/cross-plugin-invoke.py --self-test` is the negative-test suite: traversal, absolute paths, symlinks, prefix names, wrong kind, over-privileged tools, cycles, depth, ambiguous `works_with`, and a misspelled plugin on a dispatch surface.

The audit-suite script was not given a new numbered gate in this change. Rewriting that file is refused by the command-review hard rule, because the file already contains text the rule will not write back. The workflow above is the check that runs in CI. The self-test is the negative suite, including a temporary tree with a planted unknown target.
