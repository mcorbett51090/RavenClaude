---
name: create-pr
description: Open a pull request for the current branch using the project's standard template. Verifies the branch is green, summarizes the diff against main, and pushes only after the user confirms.
---

# Skill: create-pr

## Pre-flight checks (run all before drafting)
1. `git status` — working tree clean? If not, surface and stop.
2. `git rev-parse --abbrev-ref HEAD` — confirm we're not on `main`.
3. `git log main..HEAD --oneline` — list commits going into the PR.
4. `git diff main...HEAD --stat` — size up the diff.
5. Run [`run-full-test-suite`](./run-full-test-suite.md). If anything is red, **stop** — do not open a PR on a broken branch.

## Draft the PR
Use this template. Fill every section; delete sections that genuinely don't apply (don't leave placeholder text).

```markdown
## Summary
<2–4 bullets — what changed and why, not how>

## Motivation
<the problem this solves; link to issue / ticket / incident if applicable>

## Approach
<one paragraph — the design, briefly. Defer to architect notes if linked.>

## Test plan
- [ ] <unit tests added — file paths>
- [ ] <integration / e2e cases exercised>
- [ ] <manual verification steps if UI>
- [ ] all gates green locally (format, lint, typecheck, tests)

## Risk & rollout
- Reversible? <yes/no — and how>
- Migration / backfill? <none / details>
- Feature flag? <none / flag name + default>

## Screenshots / recordings
<paste here if UI>

## Out of scope
<list the things you noticed but did NOT touch — keeps reviewers focused>

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

## Open the PR
- Push the branch with `-u` if it's not yet on the remote.
- `gh pr create --title "<type(scope): subject>" --body "$(cat <<'EOF' … EOF)"`.
- Title follows Conventional Commits, ≤ 72 chars.
- Return the PR URL to the user.

## Don'ts
- Don't merge. Even on a green PR with one commit. The user merges.
- Don't `--force`. If the remote diverged, surface it and ask.
- Don't skip CI by editing workflow files in the same PR.

## Why a skill, when Claude Code has a built-in PR-creation flow?
Claude Code's built-in `gh pr create` flow is generic and pulls the title/body from recent commits. This skill enforces the RavenClaude team conventions on top of that: it gates on `run-full-test-suite` first (no PRs on a broken branch), uses the team's fixed PR template (Summary / Motivation / Approach / Test plan / Risk & rollout / Screenshots / Out of scope), enforces Conventional Commits title format ≤72 chars, and refuses to merge after creating the PR. Use the built-in flow for quick one-off PRs in personal projects; use this skill on RavenClaude-managed work where the team's review rubric assumes the template is filled in.
