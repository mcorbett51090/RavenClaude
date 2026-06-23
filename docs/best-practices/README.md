# Best-practice docs

This folder collects **named rules** that apply across any Claude work in this marketplace. Each file is one rule — read, applied, and cited as a whole.

For the companion log of dated, story-shaped findings (incidents we tried-failed-fixed), see [`../memory-bank/lessons-learned.md`](../memory-bank/lessons-learned.md). For the rule deciding which one a new finding belongs in, see [`lessons-vs-best-practices.md`](./lessons-vs-best-practices.md).

---

## Index

| Doc | Status | Use when |
|---|---|---|
| [`authoring-plugin-slash-commands.md`](./authoring-plugin-slash-commands.md) | Pattern | Writing a `plugins/<plugin>/commands/*.md` slash command — frontmatter, the namespaced `/<plugin>:<command>` invocation, multi-step body shape, and why the dashboard is copy-to-run (not press-to-run) |
| [`bundled-mcp-servers.md`](./bundled-mcp-servers.md) | Pattern (+2 absolute rules) | Giving a plugin's agents a real tool via MCP — the bundle / recommend / evaluate-first decision, pinning, the auto-start reality, the CLAUDE.md doctrine block that makes agents actually reach for the tool, and the never-ship-literal-secrets / gate-write-capable-servers absolutes |
| [`ci-gate-audit.md`](./ci-gate-audit.md) | Absolute rule | Adding or changing any CI step that claims to enforce a property — every gate must fail on a known-bad input AND pass on a known-good input |
| [`ci-on-github-token-pushes.md`](./ci-on-github-token-pushes.md) | Primary diagnostic | A PR head shows zero checks after a session pushed it — `GITHUB_TOKEN` pushes don't trigger `pull_request` CI; trigger each workflow with `workflow_dispatch` and poll `get_check_runs` |
| [`cross-plugin-references.md`](./cross-plugin-references.md) | Absolute rule | One plugin references another plugin's agents/skills/knowledge — keep it soft (self-contained first, conditioned on presence, no hard `requires`) so it degrades gracefully when the sister plugin isn't installed |
| [`diagrams-in-docs.md`](./diagrams-in-docs.md) | Pattern | Adding any conceptual / flow diagram to a markdown doc — reach for mermaid, not ASCII box-art |
| [`hook-authoring.md`](./hook-authoring.md) | Pattern | Writing a new PreToolUse / PostToolUse / Stop hook for a plugin |
| [`lessons-vs-best-practices.md`](./lessons-vs-best-practices.md) | Pattern | Capturing a finding — deciding whether it's a lesson (story), a best-practice (rule), or both |
| [`plugin-versioning.md`](./plugin-versioning.md) | Absolute rule | Touching any shipped plugin content — bumps the three version mirrors (plugin.json + marketplace.json + architecture.md) |
| [`pr-vs-direct-push.md`](./pr-vs-direct-push.md) | Pattern | Deciding whether a change opens a PR or commits direct to main |
| [`skill-authoring.md`](./skill-authoring.md) | Pattern | Writing a `plugins/<plugin>/skills/<name>/SKILL.md` — the discovery-carrying `description`, the ≤500-line lean body, splitting depth into sibling files/scripts (progressive disclosure), and `allowed-tools` least-privilege |

---

## How to add a new entry

1. Decide it belongs here (rule, not story) — see [`lessons-vs-best-practices.md`](./lessons-vs-best-practices.md).
2. Copy [`_TEMPLATE.md`](./_TEMPLATE.md) to a new descriptive slug — e.g. `secret-handling.md`, not `secrets.md`.
3. Fill in every section (Status, Domain, Applies to, Why this exists, How to apply, Edge cases, See also, Provenance, Last reviewed line).
4. Append a row to the index table above.
5. Cross-link from any related doc (sibling best-practices, lessons it codifies, plugin agents that should consult it).

For consumer-project Claude sessions contributing back via the staging path, the flow is automated through the [`contribute-finding`](../../plugins/ravenclaude-core/skills/contribute-finding/SKILL.md) and [`review-staged-contributions`](../../plugins/ravenclaude-core/skills/review-staged-contributions/SKILL.md) skills — the index here gets updated when the maintainer promotes a staged best-practice.

---

## See also

- [`../memory-bank/lessons-learned.md`](../memory-bank/lessons-learned.md) — companion log of dated trial-and-error findings
- [`../memory-bank/decision-log.md`](../memory-bank/decision-log.md) — architectural decisions with rationale
- [`../staging/README.md`](../staging/README.md) — staging area for contributions from consumer projects
- [`../../CONTRIBUTING.md`](../../CONTRIBUTING.md) — branch-and-PR flow for direct collaborators
