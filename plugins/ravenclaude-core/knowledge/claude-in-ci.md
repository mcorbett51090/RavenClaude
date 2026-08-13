# Claude in CI — wiring an agent in as the GitHub actor, safely

**Audience:** an autonomous agent that operates GitHub *from inside CI* — the agent **is** the CI
actor that pushes, reviews, files issues, opens PRs, and (sometimes) merges. This is host-general;
`anthropics/claude-code-action` is the worked example throughout because it ships this posture as
code, not prose. `[inf]`

**Provenance key:** `[obs]` = sourced this session (claim # cited), `[inf]` = reasoned from those
sources, `[unverified — training knowledge]` = recalled only, verify before building on it.

> **Companion files:** identity, signing & attribution → [agent-pr-identity.md](agent-pr-identity.md);
> the Actions-hardening rules this leans on → [github-actions-hardening.md](github-actions-hardening.md);
> who-merges → [git-workflow.md](../rules/git-workflow.md).

## Why this is a distinct problem

When the agent holds the token, the usual "a careful human is at the keyboard" assumption is gone.
Every guardrail below exists because the actor is a program that can be **triggered by untrusted
input** and can **act on itself**. RavenClaude ships no equivalent guidance today — a repo-wide grep
this session found zero `@claude`-in-CI references in shipped content `[obs, claim 31]` — so treat
this file as the reference, not a restatement.

## 1. One action, three modes — auto-detected from the event

The action picks its mode from the triggering event, not from a config flag `[obs, claim 3]`:

| Mode | Fires on | The agent's job |
|---|---|---|
| **PR review** | a pull-request event | review the diff |
| **Mention-triggered** | an `@claude` mention in an issue / PR / comment / review | do what the mention asks |
| **Automation** | any event, when a `prompt` input is supplied | a scripted, unattended task |

Design consequence `[inf]`: the *same* token and workflow are reachable three ways, so the trigger
gate (next) has to hold for all three — you cannot assume "only a human mention starts this."

## 2. Trigger-loop defense — write access required, bots rejected by default

Triggering the agent requires the actor to have **write access** to the repo, and **bot-authored
events are rejected unless the bot is explicitly allow-listed** `[obs, claim 4]`. This is precisely
what stops the agent from triggering *itself* in a loop — its own comment or push would otherwise
re-fire the workflow. Keep the bot allow-list empty unless you have a named, trusted automation to
add to it.

## 3. The untrusted-input trust boundary

`pull_request_target` and `workflow_run` run with the **base repository's secrets** while the
triggering PR is untrusted. The rule: **do not bring the untrusted PR head into the workspace root**
`[obs, claim 5]`. The safe shape (check out the base ref at root, the PR head into a subdirectory)
and the full `permissions:` / checkout discipline live in
[github-actions-hardening.md](github-actions-hardening.md) §4 — read it there; it is not duplicated
here.

## 4. Restore agent config from the base ref

On PRs the action restores `.claude/`, `.mcp.json`, `CLAUDE.md`, and hook config **from the base
branch**, so a malicious PR cannot ship its own agent instructions `[obs, claim 6]`. The gap it does
**not** close: manifests and lockfiles stay at the PR head and can hijack a hook that shells out to a
package script — so **pin the tool version and invoke the tool directly** in any hook, rather than
running it through a PR-controlled script `[obs, claim 6]`.

## 5. Human-oversight default — propose, don't self-open

The documented default is **not** to open the PR itself: the action **links to the PR-creation page**
and the human clicks it `[obs, claim 7]`. Same spirit as RavenClaude's own rule — the human approves
the merge; see [git-workflow.md](../rules/git-workflow.md), "Pull requests." The agent is a PR
*proposer*, not a self-serve merger.

## 6. Verified commit signing

`use_commit_signing: true` signs commits through the GitHub API, so they show as **verified** — but
that API path cannot rebase or cherry-pick. An SSH signing key is the git-CLI alternative when you
need history operations `[obs, claim 8]`. Which identity signs, and how attribution should read, is
[agent-pr-identity.md](agent-pr-identity.md).

## 7. Structural anti-self-approval

If the agent is ever allowed to **approve** a PR, exclude it *structurally* — a prompt instruction is
not enough. The `agent-approval-check.yml` pattern carries an in-file guard (it "cannot edit this
check to approve itself") plus an `excluded_approvers` knob `[obs, claim 9]`. `/init-agent-ready` can
drop in the
[agent-approval-check.yml.template](../templates/agent-ready-repo/agent-approval-check.yml.template)
scaffold.

## 8. The base-action trust-boundary lesson

The lower-level base action just runs the model. It does **NOT** perform actor-permission checks and
does **NOT** restore project config from the base ref `[obs, claim 29]`. So a "just run the agent"
primitive is **not** safe behind an untrusted trigger — use the full action, or re-implement §2–§4
yourself before you expose the bare runner.

## What this means for RavenClaude

- RavenClaude **teaches** this pattern; it does not run a hosted bot on your behalf. `[inf]`
- **No bot account ships by default** `[inf]` — the agent is a PR *proposer*, and the human approves
  the merge (the [git-workflow.md](../rules/git-workflow.md) rule) `[obs, claim 7]`.
- New agent-GitHub guardrails default **fail-safe** (off / warn, no-op without posture), consistent
  with House Rule 3. `[inf]`
