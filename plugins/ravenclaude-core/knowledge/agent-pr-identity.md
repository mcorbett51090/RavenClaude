# Agent-PR identity & attribution — how an agent-authored PR names itself

> **Last verified:** 2026-08-12. **Refresh trigger:** re-verify if GitHub's signature-verification model, the `create-pr` skill's footer, or the frontier agents' identity docs (Devin / aider) change. The external facts here were verified via `gh api` + WebFetch on 2026-08-12 and live in the run's `research/agentic-github-gold-standard.md` + `claims-table.md`.

This file is the **identity half** of "an agent as a GitHub actor" — the companion to [`github-actions-hardening.md`](github-actions-hardening.md) (the workflow-security half). It answers one question: **when a RavenClaude agent opens a pull request, whose name is on it, and how is that made legible to a reviewer?**

**Who consumes it:** an agentic AI CLI that is about to author a commit or open a PR in a git repo. Each point is either a rule the agent applies or a fact it should not misstate — never just "nice to know." Every point carries a provenance marker.

**Provenance legend** — **[obs]** = a source or repo file demonstrably says/does this, checked 2026-08-12 (with the backing claim # from `claims-table.md` where external); **[inf]** = a conclusion drawn from named evidence; **[unverified — training knowledge]** = recalled, not checked this session.

---

## 1. Why identity matters for an agent-authored PR

A reviewer reads an agent-authored PR differently than a human's, and the frontier tools encode that difference in product behavior — so the provenance has to be **legible on the PR itself**, not implied.

- **The frontier treats an agent contributor as a distinct governance class.** GitHub's Copilot coding agent is *"treated like an outside contributor"* — its pushes need a human's approve-and-run before CI even fires, and its approval does not count toward required reviews **[obs, claim #18/#19]**. Devin runs as a **named org-level contributor with its own PR template** **[obs, claim #27/#28]**. The common thread: the platform wants to *know* a change is agent-authored so it can apply the right gate.
- **So the identity signal is load-bearing, not cosmetic.** If a reviewer can't tell an agent wrote the change, they can't apply the extra scrutiny an agent PR warrants (injection-surface review, "did it actually verify the claim it asserts," self-merge prevention) **[inf, from #18/#19/#27/#28]**.
- **Legibility is a two-part signal:** *attribution* (the commit/PR names the agent as author or co-author — §2) and *identity* (which account/App the change is committed under, and whether its signature verifies — §3) **[inf]**.

---

## 2. Attribution — mark agent-authored work unambiguously

**RavenClaude's convention: every agent-authored change carries an explicit attribution mark**, in two places that a reviewer and `git log` both see.

| Surface | What ships | Marker |
|---|---|---|
| **PR body** | The `🤖 Generated with [Claude Code]` footer in the [`create-pr` skill](../skills/create-pr/SKILL.md) (its final line) | **[obs]** — `create-pr/SKILL.md` footer, verified this session |
| **Commit message** | A `Co-Authored-By: Claude <noreply@anthropic.com>` trailer as the last line of the commit | **[obs]** — RavenClaude commit-message convention |

- **This is a field standard, not a RavenClaude quirk.** aider marks agent-authored work the same way: it appends **`(aider)`** to the git author/committer name, or emits a **`Co-authored-by`** trailer under `--attribute-co-authored-by`, and defaults its subjects to **Conventional Commits** **[obs, claim #25]**. RavenClaude's `Co-Authored-By:` trailer + Conventional-Commits subjects are the same pattern, independently arrived at.
- **Attribution is a setting, not a habit.** The mark ships in the skill and the commit convention, so an agent doesn't have to *remember* to add it — the point of encoding it is that a forgotten mark is the failure mode **[inf, from #25]**.
- **Branch name is a third, weaker attribution signal.** The convention prefixes in [`git-workflow.md`](../rules/git-workflow.md) (`feat/`, `fix/`, `chore/`, `agent/<role>/`) let a PR read as scoped, agent-owned work at a glance **[obs]** — repo rule, verified this session.

---

## 3. Bot vs named principal vs dedicated account — the trade-off, and RavenClaude's default

There are three identities an agent PR can be committed under. They differ mainly on **signature verification** — GitHub verifies a commit signature against the **author identity**, so "verified" attribution and "which account" are the same question.

| Identity | What it buys | What it costs |
|---|---|---|
| **The human's own git identity** (RavenClaude default) | Zero setup; the change lands under the maintainer already accountable for the repo | No independent agent signature; attribution rides on the trailer + footer, not a verified badge **[inf]** |
| **A named human principal** | Clean human accountability | Same as above; the agent's hand is legible only via the attribution mark |
| **A dedicated agent account / GitHub App** | A **stable author identity** whose signature GitHub can verify, and a distinct governance handle | Provisioning + credential custody for a second account; Devin needs exactly this — it runs under **org-level** permissions and requires a **dedicated account** *because GitHub verifies signatures against the author identity* **[obs, claim #27]** |

**RavenClaude's default, stated plainly: the human's git identity + the `Co-Authored-By:` trailer. No bot account is shipped.** The [`create-pr` skill](../skills/create-pr/SKILL.md) opens the PR under the user's own `gh` auth and refuses to self-merge (*"The user merges"*) — there is no dedicated-account or bot provisioning anywhere in the plugin **[obs]** — repo-structural, verified this session.

- **When the default isn't enough — verified signatures.** If a repo *requires* verified commit signatures (a branch-protection rule), the answer is the GitHub-App "verified" path, not a bot PAT: commit through the App's API so commits are *"automatically signed as verified from the GitHub App"* (an SSH signing key is the alternative when git-CLI history operations are needed) **[obs, claim #8]**. That option and its wiring are documented in [`claude-in-ci.md`](claude-in-ci.md).
- **A dedicated identity is a deliberate upgrade, not the baseline.** Adopt it only when you need verified signing *or* a distinct governance handle (org-level scoping, an agent-specific approval gate) — it adds a credential to steward **[inf, from #27/#8]**.

---

## 4. Agent-specific PR template — prefer it over the human template

An agent PR needs a **different body** than a human PR: it should surface what the agent verified, what it left as `[TBD]`, its confidence, and the injection/scope review a reviewer must apply. Devin ships exactly this pattern — an agent-specific template at `.github/PULL_REQUEST_TEMPLATE/<agent>_pr_template.md`, **preferred over the human template**, *so you can give the agent its own template without modifying your default human-facing one* **[obs, claim #28]**.

- **RavenClaude's implementation:** the scaffold [`PULL_REQUEST_TEMPLATE-agent.md.template`](../templates/agent-ready-repo/PULL_REQUEST_TEMPLATE-agent.md.template) — an agent-tailored PR body a consumer repo drops into `.github/PULL_REQUEST_TEMPLATE/` **[obs]** — repo scaffold (phase P6 of this plan).
- **Before opening a PR, look for a template first.** GitHub's own MCP-server guidance says to check for a PR template before creating the PR; the agent template, when present, wins over the human one **[obs, claim #28]** / **[unverified — training knowledge]** (the "look first" step is standard MCP guidance, not re-verified against a live registry this session).

---

## 5. What to do — minimal identity hygiene for an agent opening a PR here

1. **Commit under the maintainer's configured git identity.** RavenClaude ships no bot account; don't invent one **[obs]**.
2. **Append both attribution marks** — the `Co-Authored-By:` commit trailer and the [`create-pr`](../skills/create-pr/SKILL.md) PR-body footer — so the agent's hand is legible to `git log` and the reviewer **[obs, #25]**.
3. **Use a convention branch prefix** (`feat/` … `agent/<role>/`, per [`git-workflow.md`](../rules/git-workflow.md)) so the PR reads as scoped agent work **[obs]**.
4. **Fill the agent PR template if the repo has one** — the [scaffold](../templates/agent-ready-repo/PULL_REQUEST_TEMPLATE-agent.md.template) or the consumer's `.github/PULL_REQUEST_TEMPLATE/<agent>_pr_template.md`; prefer it over the human template **[obs, #28]**.
5. **Do not self-merge.** Surface the green PR and let the human land it — the [`create-pr`](../skills/create-pr/SKILL.md) skill enforces this **[obs]**.
6. **Only if verified signatures are required**, escalate to the GitHub-App signing / dedicated-identity path in [`claude-in-ci.md`](claude-in-ci.md) — a considered upgrade, not the default **[obs, #8/#27]**.
