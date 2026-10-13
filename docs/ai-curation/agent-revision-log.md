# Agent revision log

One line per change to an agent, skill or rule **definition** (`plugins/*/agents/*.md`,
`plugins/*/skills/*/SKILL.md`, `plugins/*/rules/*.md`). The `prompt-engineer` agent's
"Authority to edit agent files" protocol (step 3) writes here; anyone else changing a
definition should too.

This log starts on 2026-10-13. Earlier changes are not back-filled here: use
`git log -- plugins/*/agents plugins/*/skills plugins/*/rules` and the plugin
CHANGELOGs for history before that date.

Format: `YYYY-MM-DD | path | what changed | why | PR`

## Entries

- 2026-10-13 | plugins/ravenclaude-core/agents/prompt-engineer.md | model opus→sonnet, effort high→xhigh; flat `skills/*.md` paths fixed to `skills/*/SKILL.md`; revision-log reference made concrete | approved repin (Oct 13); stale-path cleanup | feat/prompt-eng-gaps (PR number TBD)
