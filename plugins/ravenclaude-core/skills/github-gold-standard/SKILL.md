---
name: github-gold-standard
description: "Score a consumer repo's GitHub-development protocol against the shipped gold-standard catalog and produce a remediation queue ranked by leverage. A 10-row core rubric (mapping 1:1 to the P3 exemplar-repo catalog + the P4 Actions-hardening rules) plus 3 agent-operability rows for the agent-as-primary-GitHub-operator bar — each row is a check the agent runs against .github/workflows/*, the repo's .git, and its ruleset, a pass/partial/fail verdict, and the shipped fix (an /init-agent-ready template or a knowledge file). Proportional banding (dynamic denominator). Use to measure a repo against the best-of-the-best bar before calling its CI/branch-protection done. Honest scope: it measures STRUCTURAL COVERAGE, not taste."
---

# GitHub gold-standard scorecard

"Gold standard" here means **the repo's development protocol clears an executable bar drawn from 30 exemplar repositories and the security-hardening rules extracted from them** — not "a maintainer eyeballed the workflows." Run this to measure a consumer repo against that bar, then hand back a remediation queue ordered so the highest-leverage fix is first.

> **Honest scope — read this before you report a score.** The rubric measures **structural coverage**: is the gate/control *present and correctly shaped?* It does **not** measure taste, nor does a green score certify the repo is secure — a repo can pass every row and still ship a bad workflow the rubric's shape-checks don't model (a logic bug in a `run:` step, an over-scoped OIDC trust policy, a stale pinned SHA). Say this in the report. The score is a floor that says "the known-high-leverage controls exist," not a ceiling that says "nothing is wrong."

## What it scores against (read these first)

The rubric maps **1:1** onto the two shipped knowledge files — every row cites its source, so a verdict is always traceable back to the catalog, never invented:

- **[`../../knowledge/github-gold-standard-repos.md`](../../knowledge/github-gold-standard-repos.md)** (P3) — the durable 8-category best-practices catalog + the dated 30-repo snapshot + Section 3's "highest-leverage to enforce" ranking. The **leverage tiers** below come straight from its Section 3.
- **[`../../knowledge/github-actions-hardening.md`](../../knowledge/github-actions-hardening.md)** (P4) — the six numbered Actions-hardening rules the enforceable rows are checked against.

The **shipped remediation** each row points at is an [`/init-agent-ready`](../../commands/init-agent-ready.md) template or a sibling skill — so a `fail` is never "go read the internet," it's "scaffold this specific file."

## The rubric — 10 core dimensions + 3 agent-operability rows, each a falsifiable check

Score every row **2 (pass) / 1 (partial) / 0 (fail)**. Row 10 is **optional** (score it, but keep it out of the core denominator — see Scoring). The three **agent-operability rows (A1–A3)** below the core table are **N/A as a group** unless the repo runs an agent-in-CI workflow. Each row's "Check" is read-only: it reads `.github/workflows/*`, the repo's `.git` state, and the repo ruleset. It never mutates the repo.

| # | Dimension | Catalog source | Pass / Partial / Fail | Shipped remediation |
|---|---|---|---|---|
| 1 | **Branch-delete recovery ships + works** | P3 §House-rule / [`branch-archive`](../branch-archive/SKILL.md) | **Pass:** a sanctioned tag-before-delete recovery path exists so a branch force-delete can never silently lose unmerged work. **Partial:** the guard blocks the delete but no recovery escape hatch. **Fail:** neither. | The [`branch-archive`](../branch-archive/SKILL.md) skill (tag the tip → push the tag → audit-log → delete via the low-level ref primitive). |
| 2 | **Workflow static analysis** (zizmor / actionlint) | P4 catalog §1.1 "Statically analyze the workflows themselves" (the emergent gate most repos still lack) | **Pass:** a workflow or CI step runs `zizmor`/`actionlint` (or the shipped hygiene scanner) over `.github/workflows/*`. **Partial:** a linter is present but not wired as a gate. **Fail:** none. | [`check-workflow-hygiene.py.template`](../../templates/agent-ready-repo/check-workflow-hygiene.py.template) + [`github-protocol-workflow-hygiene.yml.template`](../../templates/agent-ready-repo/github-protocol-workflow-hygiene.yml.template). |
| 3 | **Least-privilege `permissions:` floor** | P4 Rule 1 | **Pass:** every workflow carries a top-level `permissions:` floor (`{}` or read-only), elevating per-job. **Partial:** some workflows do. **Fail:** none, or a broad top-level grant. | `check-workflow-hygiene.py` Rule 1 (HARD). |
| 4 | **SHA-pinned actions** | P4 Rule 2 | **Pass:** every third-party `uses:` is pinned to a full 40-hex commit SHA (official `actions/*` and local `./` exempt). **Partial:** most are; a few float on a tag. **Fail:** bare `@vN`/`@main` on third-party actions. | `check-workflow-hygiene.py` Rule 2 (HARD). |
| 5 | **OIDC over long-lived secrets** | P4 Rule 3 / P3 §1.1 | **Pass:** publish/deploy jobs authenticate via OIDC (`id-token: write` + a federated identity), no long-lived cloud/registry secret. **Partial:** OIDC for some, a stored token for others. **Fail:** long-lived secrets where the provider supports OIDC. **N/A:** repo ships no artifact to publish. | Teachable — P4 Rule 3 (`id-token: write` pattern). No template gate: OIDC trust is provider-side config, not a file the scaffolder can write. |
| 6 | **Semantic-PR / commit-message gate** | P3 §1.5 (Conventional Commits) — a top-4 highest-leverage gate | **Pass:** a required check enforces Conventional-Commits PR titles and/or commit-message shape. **Partial:** a linter runs but isn't required. **Fail:** none. | [`github-protocol-pr-title.yml.template`](../../templates/agent-ready-repo/github-protocol-pr-title.yml.template) + [`github-protocol-commit-lint.yml.template`](../../templates/agent-ready-repo/github-protocol-commit-lint.yml.template). |
| 7 | **Secret scanning + push protection** | P4 catalog §1.6 — a top-4 highest-leverage gate | **Pass:** push protection is on (rejects a credential at push time) **and** a CI scanner (gitleaks/trufflehog) runs on PRs. **Partial:** only one of the two. **Fail:** neither. | [`github-protocol-secret-scan.yml.template`](../../templates/agent-ready-repo/github-protocol-secret-scan.yml.template) + the native push-protection Settings toggle it documents. |
| 8 | **Required checks are NOT path-filtered** | P4 Rule 5 — *the single trap most likely to bite* | **Pass:** no required-status-check workflow carries a `paths:`/`branches:` filter on its `pull_request`/`push` trigger. **Partial:** an unfiltered required check exists but coverage is thin. **Fail:** a required check is path/branch-filtered (hangs the PR forever). | [`setup-branch-protection.sh.template`](../../templates/agent-ready-repo/setup-branch-protection.sh.template) (self-checks the four would-be-required workflows for a filter and refuses to apply if it finds one) + `check-workflow-hygiene.py` Rule 5 (advisory). |
| 9 | **Worktree lifecycle hygiene** | P4 catalog §1.3 | **Pass:** parallel/agent work uses one branch per worktree and finished worktrees are removed with `git worktree remove` + `prune`, not a raw directory delete. **Partial:** worktrees used, cleanup ad-hoc. **Fail:** no isolation / stash-juggling. | The [`cleanup-worktrees`](../cleanup-worktrees/SKILL.md) skill (list → remove finished → prune stale admin files). |
| 10 | **Merge queue / CODEOWNERS** *(optional)* | P4 Rule 6 / P3 §1.2 | **Pass:** a merge queue guards a busy default branch **and** `CODEOWNERS` routes reviewers by path. **Partial:** one of the two. **Fail/N/A:** neither (fine for a low-traffic repo — score it N/A, don't penalize). | [`CODEOWNERS.template`](../../templates/agent-ready-repo/CODEOWNERS.template) + `setup-branch-protection.sh --require-codeowner-review`. |

### Agent-operability rows (N/A **as a group** if the repo runs no agent-in-CI workflow)

These three rows measure the *agent-as-primary-GitHub-operator* bar — score them only when the repo runs (or is set up to run) an AI agent as a GitHub actor in CI. If it doesn't, they are **N/A as a group** (out of the denominator), not 0.

| # | Dimension | Leverage | Pass / Partial / Fail | Shipped remediation |
|---|---|---|---|---|
| A1 | **Agent-workflow least-privilege + default-token-suppression avoided** | A | **Pass:** an agent-triggered workflow carries a per-job least-privilege `permissions:` grant **and** any push that must trigger downstream is authed as a GitHub App / custom token / OIDC (not the default `GITHUB_TOKEN`, which does not fire downstream runs). **Partial:** one of the two. **Fail:** a blanket grant, or a default-token push relied on to trigger a required check. | [`github-actions-hardening.md`](../../knowledge/github-actions-hardening.md) Rule 7 + `check-workflow-hygiene.py` Rule 3 (advisory). |
| A2 | **Agent PR template present** | B | **Pass:** `.github/PULL_REQUEST_TEMPLATE/agent_pr_template.md` exists with a structured body + a `Co-Authored-By:` provenance footer. **Partial:** a generic template only. **Fail:** none. | [`PULL_REQUEST_TEMPLATE-agent.md.template`](../../templates/agent-ready-repo/PULL_REQUEST_TEMPLATE-agent.md.template) (opt-in via `/init-agent-ready`) + [`agent-pr-identity.md`](../../knowledge/agent-pr-identity.md). |
| A3 | **Structural anti-self-approval present** | A | **Pass:** `agent-approval-check.yml` exists with ≥1 `EXCLUDED_APPROVERS` entry, only counts write-access reviewers, runs from the base branch, and the PR initiator is excluded from the required-approval count. **Partial:** the workflow exists but its exclusion set is empty. **Fail:** none, or an agent PR can self-approve. | [`agent-approval-check.yml.template`](../../templates/agent-ready-repo/agent-approval-check.yml.template) (opt-in) + [`claude-in-ci.md`](../../knowledge/claude-in-ci.md). |

### How to run each check (read-only)

- **Workflows (rows 2–6, 8):** enumerate `.github/workflows/*.yml` / `*.yaml`. For each, read the top-level keys and every `uses:`/`permissions:`/`on:` block. The shipped `check-workflow-hygiene.py` already encodes rows 3, 4, and the row-8 advisory — run it if present, or read the workflows directly with the same rules. For row 5, look for `id-token: write` + an OIDC login action in publish/deploy jobs vs. a `secrets.*` registry/cloud token.
- **Ruleset (rows 7, 8, 10):** read the branch ruleset / protection (via `gh api repos/{owner}/{repo}/rulesets` or the repo's committed setup script) for the **required-check list** and cross-check each required workflow's trigger for a `paths:`/`branches:` filter (row 8 — the hang-forever trap). Check the Settings-level secret-scanning **push-protection** state for row 7 (a repo API read; if unavailable, mark row 7 partial and note the toggle can't be read).
- **Git state (rows 1, 9):** read the presence of a branch-recovery path (a `branch-archive`-style script/skill or a destructive-op guard) for row 1; `git worktree list` (read-only) + any cleanup routine for row 9.

Every check is a **read**. If a control can't be observed from this session (e.g. the push-protection toggle behind Settings), score conservatively and say *why* in the row's note — never guess a pass.

## Scoring — PROPORTIONAL (dynamic denominator)

- **Core (rows 1–9, each 0/1/2): / 18** — always applicable.
- **Agent-operability (rows A1–A3, each 0/1/2): / 6 — or N/A as a GROUP** when the repo runs no agent-in-CI workflow (no `claude-code-action`/`@claude`-style workflow). N/A rows are **excluded from the denominator**, scored neither 0 nor 2.
- **Row 10** (merge-queue / CODEOWNERS) stays separate and optional.
- **Band = round(100 × score ÷ applicable_max)**, where `applicable_max` = **18** (no agent workflow) or **24** (agent workflow present → the three agent rows apply):
  - **≥ 89% — gold:** the known-high-leverage controls are all present and shaped right.
  - **61–88% — silver:** the load-bearing gates exist; a few high-leverage rows are partial/missing.
  - **< 61% — bronze:** at least one top-4 gate or the row-8 trap is failing; start at the top of the queue.
- **Why proportional (RT-4):** the agent rows introduce a dynamic denominator (18 or 24), and a percentage band expresses both — so a no-agent-workflow repo stays eligible for gold on /18 while an agent-in-CI repo is judged on /24. Report the per-row breakdown, the score, `applicable_max`, and the band.

The band names structural coverage only — re-read the honest-scope note before attaching any "secure/done" claim to it.

## The remediation queue — ranked by leverage, not by row order

Do **not** hand back failures in table order. Rank every `fail`/`partial` (and any row-8 filtered-required-check, always first) by **leverage tier**, taken from catalog Section 3:

- **Tier A (highest leverage / the trap) — fix first:** row 8 (path-filtered required check — hangs the PR forever, always top), then rows 2, 4, 6, 7 (the four cheap high-leverage gates Section 3 names: workflow static analysis, SHA-pinning, the semantic-PR gate, secret-scan + push protection), plus the agent-operability gates **A1** (agent-workflow least-privilege + default-token-suppression) and **A3** (structural anti-self-approval) when they apply.
- **Tier B — next:** rows 3 (permissions floor), 5 (OIDC), 1 (branch-delete recovery), and **A2** (agent PR template) when it applies.
- **Tier C — last:** row 9 (worktree hygiene), row 10 (merge-queue/CODEOWNERS, optional).

Within a tier, a `fail` outranks a `partial`. Each queue item carries: the dimension, its verdict, the exact shipped remediation to apply (the template path or skill), and the catalog citation. See [`resources/scorecard.md`](resources/scorecard.md) for the fill-in template.

### Structured output (Structured Output Protocol)

End the run with the machine-readable block alongside the human-readable scorecard:

```
---RESULT_START---
{
  "core_score": 0,
  "agent_operability_score": 0,
  "agent_rows_applicable": true,
  "applicable_max": 18,
  "band_pct": 0,
  "band": "gold|silver|bronze",
  "optional_row_10": "pass|partial|fail|n/a",
  "rows": [
    {"n": 1, "dimension": "branch-delete-recovery", "verdict": "pass|partial|fail", "leverage": "A|B|C", "evidence": "one line", "source": "P3 §…", "remediation": "template/skill path"}
  ],
  "remediation_queue": [
    {"n": 8, "verdict": "fail", "leverage": "A", "fix": "setup-branch-protection.sh.template — remove the paths: filter"}
  ],
  "scope_note": "structural coverage only; not a security certification",
  "confidence": 0.0
}
---RESULT_END---
```

## Why honest scope is the point

A scorecard that quietly implies "18/18 = safe" would be worse than no scorecard — it launders coverage into certification and stops the next reader from looking for the bug the shape-checks can't see. So the rubric is deliberately framed as **structural coverage of known-high-leverage controls**, each traceable to the catalog, with the four highest-leverage gates and the one hang-forever trap surfaced first in the queue. Where a control is provider-side (OIDC trust policy, the push-protection toggle) or content-level (a `run:` logic bug), the rubric says so and scores conservatively rather than pretending its shape-check reached it.
