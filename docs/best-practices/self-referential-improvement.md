# Using RavenClaude to improve RavenClaude

**Status:** **Pattern** — recommended default for any non-trivial change to the marketplace itself.

**Domain:** Meta / Cross-domain

**Applies to:** Working ON the RavenClaude marketplace (this repo, not a consumer project).

---

## Why this exists

The marketplace ships an opinionated team — Team Lead, architect, coders, reviewers, security-reviewer, designer, documentarian, project-manager, deep-researcher — and an opinionated governance stack — `comfort-posture.yaml`, hooks, the tribunal (the Thing), `decision-review`. **The same team that helps a consumer should help the maintainer.** When a workflow gap surfaces, the right move is rarely to hand-author the fix; it's to dispatch the team that builds those fixes for consumers every day.

Two failure modes this pattern prevents:

1. **Tooling drift between dogfood and ship.** A maintainer who hand-edits plugin files past the team is the only one who didn't experience the team's own gates. Diff-time `code-reviewer`, the tribunal's `package_install: ask` prompt, the `enforce-layout.sh` deny, the structured-output handoff — those are the experiences this marketplace IS the experience of. Skipping them in maintenance means shipping changes that work in the maintainer's workflow but surprise consumers.
2. **Quality regression from solo authoring.** Multi-agent dispatch surfaces ~3× the catches of solo work (the panel-review pattern documented in `docs/concepts.md`). For any change that's >100 LOC, touches CI, or changes a consumer-visible default, the maintainer should not be the only reviewer.

## How to apply

For any non-trivial change to this marketplace — a new plugin, a new skill, a hook contract change, a CI gate, a default flip, a security fix — follow this pattern:

### 1. Frame the change as a brief, not a task

Don't open the editor first. Open a chat with the Team Lead and describe the **outcome** — what should be different after this lands, who it helps, what the risks are. The Team Lead picks the playbook; you don't decide whether to use `architect` first or `code-reviewer` first.

```
> I want to add an `evals/` harness that scores .ravenclaude/runs/<id>/ output
> against a rubric. Audience is the maintainer (me, weekly). Risk is that the
> harness reads partner-confidential run data and we never want that committed.
```

### 2. Let the Team Lead dispatch

The Team Lead reads `plugins/ravenclaude-core/skills/spawn-team/SKILL.md` and picks. For a new feature: typically architect → coder → tester-qa → code-reviewer → security-reviewer. For a doc change: typically deep-researcher → documentarian → code-reviewer. The dispatch lives in `.ravenclaude/runs/<run-id>/`.

### 3. Use the same tribunal you ship to consumers

When the change touches anything in the security floor's neighborhood (posture defaults, `apply-comfort-posture.py`, the dashboard server, any hook contract), the `command-review` tribunal should be ON for the relevant categories. The maintainer-substrate exemption (`dev_repo_exempt: true` in this repo's `.ravenclaude/comfort-posture.yaml`) means an abstaining panel defers to you instead of failing closed — you get the panel's input without being locked out of your own substrate.

### 4. Route consequential yes/no questions through `decision-review`

A 4-seat tribunal can vote on "should the balanced seed flip this default?" or "is this PR safe to bundle?" The `decision-review` skill does the routing; bindings auto-resolve, defers come back to you. This is exactly the discipline `CLAUDE.md` says to apply for consumer dispatches — apply it to maintenance too.

### 5. Run `evals/runner.py` on the run before merging

If the change went through a multi-step dispatch, the run directory has a `summary.md` to score:

```
python3 evals/runner.py --case evals/cases/ravenclaude-core/governance-dispatch.yaml \
                        --run-id <id>
```

A passing record means handoffs were structured, gates were respected, escalations were appropriate, and token cost was within budget. A failing record is a real signal — the change might be ready to ship, but the **process** has a regression worth understanding.

### 6. Merge through the standard PR flow

Even for a maintenance change, open a PR. The same hooks fire (`format-on-write`, `regen-on-manifest-change`, `claim-grounding-lint`); the same CI gates run (`validate-marketplace.yml`, `validate-layout.yml`, the meta-test `audit-gates.sh`); the same release checklist applies.

## Worked example — Adding the `claude-app-engineering` plugin

Recorded in `docs/claude-app-engineering-plugin-analysis.md` (the design output) and the PR history. The flow was:

1. **Brief**: "We want a plugin for building on the Claude API + Agent SDK + MCP. 6 specialists. Knowledge bank with citation discipline. The plugin must not duplicate `prompt-engineer` or the third-party `claude-api` skill — distinct lanes."
2. **deep-researcher** ran a multi-source sweep (Anthropic docs + community blogs + the existing `prompt-engineer` agent) and emitted a competitive-mapping artifact.
3. **architect** drafted the 6 agent definitions + knowledge file layout + the decision-tree pre-action prior wiring; emitted to `.ravenclaude/runs/<run-id>/01-design.md`.
4. **backend-coder** (`prompt-engineer` for the agent prose, given the meta-domain) wrote the 6 `agents/*.md` files, the 9-doc knowledge bank, and the `plugin.json`.
5. **code-reviewer** + **security-reviewer** ran in parallel; the security review flagged "skills that fetch from claude.ai should NOT be added to the data-platform-confidential allowlist" — picked up before merge.
6. **architect** synthesized; opened the PR.
7. The standard release checklist ran; the meta-test confirmed every gate passed on known-bad and known-good fixtures.

Total maintainer keystrokes: the initial brief, the PR description tweaks, the merge. Everything else was the team.

## When NOT to apply

- **Typo fixes.** Open the file and edit.
- **Dependency bumps with no surface change.** `git push` away.
- **Hotfix for an outage** where the team's dispatch overhead is the bottleneck. Fix first; retroactively dispatch for the post-mortem.

The pattern is for **non-trivial** changes. The maintainer's judgment on "non-trivial" is the call.

## See also

- [`plugins/ravenclaude-core/skills/spawn-team/SKILL.md`](../../plugins/ravenclaude-core/skills/spawn-team/SKILL.md) — the dispatch playbook.
- [`plugins/ravenclaude-core/skills/decision-review/SKILL.md`](../../plugins/ravenclaude-core/skills/decision-review/SKILL.md) — yes/no routing.
- [`evals/runner.py`](../../evals/runner.py) — score the dispatch before merging.
- [`docs/best-practices/lessons-vs-best-practices.md`](lessons-vs-best-practices.md) — how to turn a learned pattern (like this one) into a durable doc.
- [`docs/concepts.md`](../concepts.md) — the multi-layer governance the maintenance flow runs through.

---

_Pattern documented 2026-06-01 as part of the P0-P2 gap-closure bundle (v0.101.0). The pattern itself predates the doc by many releases; what's new is making it explicit so a new maintainer doesn't have to re-derive it._
