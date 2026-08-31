# GitHub Actions hardening — the rules behind every gold-standard gate

> **Last verified:** 2026-08-12. **Refresh trigger:** re-verify if GitHub Actions security-hardening guidance changes; the exemplar workflow files were read via the GitHub API on 2026-08-12.

This file is the **rules half** of the GitHub-development gold standard: the durable security-hardening rules an agent should apply to *any* `.github/workflows/**` it authors or reviews. The **dated snapshot of the 30 exemplar repos** those rules were extracted from — plus the full best-practices catalog — lives in the sibling [`github-gold-standard-repos.md`](github-gold-standard-repos.md); read it for the evidence, read this for the rules.

**Who consumes it:** an autonomous agentic AI CLI operating in a git repo. So each rule is phrased to be **enforceable by a hook/CI gate** OR **teachable to an agent** — never just "nice to know." Each carries its provenance marker.

**Provenance legend** (preserved from the verified research): **[obs]** = the doc/file demonstrably says/does this, checked 2026-08-12 · **[inf]** = a conclusion drawn from named evidence · **[unverified — training knowledge]** = recalled, not checked this session (with what would verify it).

---

## The rules

### 1. Least-privilege `permissions:` — set the floor, then elevate per-job

Set a **workflow-level** `permissions:` block to the floor, then let each job grant exactly what it needs. GitHub: *"Set the default permission for the `GITHUB_TOKEN` to read access only for repository contents. The permissions can then be increased, as required, for individual jobs."* **[obs]** — security-hardening doc, retrieved 2026-08-12.

The **strongest form is deny-all at the workflow level**:

```yaml
permissions: {}        # workflow-level deny-all — the strongest floor

jobs:
  build:
    permissions:
      contents: read   # this job elevates only what it needs
```

`permissions: {}` is what `changesets/changesets` `publish.yml` uses at the top; `ossf/scorecard` uses `permissions: read-all` and elevates `security-events: write` per-job. **[obs]**

- **Enforceable (hook/CI):** lint every workflow for a **top-level `permissions:` key**; fail if absent. A workflow with no `permissions:` block inherits the token's default scopes, which is the opposite of a floor.
- **Teachable (agent):** when authoring a workflow, write `permissions: {}` (or `read-all`) at the top *first*, then add the narrowest per-job grant that makes the job pass.

### 2. Pin third-party actions to a full-length commit SHA, not a tag

A tag or branch is **mutable and re-pointable** — the owner (or an attacker who compromises the account) can move `@v4` to point at new code you never reviewed. GitHub: *"Pinning an action to a full-length commit SHA is currently the only way to use an action as an immutable release."* **[obs]** The `tj-actions/changed-files` tag-hijack (March 2025) is the canonical real-world instance of the class.

```yaml
# ✅ pinned to an immutable 40-hex commit SHA, with a human-readable version comment
- uses: actions/checkout@<full-40-char-commit-sha>  # v4.2.2

# ❌ a mutable tag — re-pointable at code you never reviewed
- uses: actions/checkout@v4
```

- **Enforceable (hook/CI):** regex-gate every `uses:` line for a **40-hex commit SHA**, and require a trailing `# vX.Y.Z` comment for readability. Org/repo policy can *require* SHA-pinning outright.
- **Teachable (agent):** when adding an action, resolve the tag to its commit SHA and pin the SHA + keep the version in a trailing comment. Never introduce a bare `@vN` or `@main`.

### 3. OIDC over long-lived secrets

Prefer **OpenID Connect federation** to a stored cloud/registry credential: the workflow mints a short-lived token at run time instead of reading a long-lived secret. GitHub: workflows can *"authenticate directly to the cloud provider … stop storing these credentials as long-lived secrets."* **[obs]** Realized with a job-level `id-token: write` plus a federated identity configured on the provider side.

```yaml
permissions:
  contents: read
  id-token: write        # OIDC — mint a short-lived token; no stored secret to leak
```

Seen live in `astral-sh/uv` (PyPI trusted publishing), `changesets` (npm trusted publishing), and `sigstore/cosign` (keyless signing). **[obs]**

- **Teachable (agent):** when a workflow needs cloud or registry auth, reach for OIDC + `id-token: write` before adding a `secrets.*` credential. A stored publish token is the fallback, not the default.
- **Enforceable (hook/CI):** flag any publish/deploy job that reads a long-lived registry/cloud secret when the provider supports OIDC federation. `[inf]` — the *lint* is an inference; the *rule* is `[obs]`.

### 4. Never check out untrusted code under `pull_request_target` / `workflow_run`

Those two triggers run **in the base-repo context, with repo secrets and a write-scoped token**. GitHub: *"Workflows that use these triggers must not explicitly check out untrusted code, including from pull request forks."* **[obs]** Running fork code in that context hands a fork PR your secrets and write token.

- **Prefer `pull_request`** for anything that touches PR head code — fork PRs there run with a **read-only token and no secrets**.
- **Teachable (agent):** if you must use `pull_request_target`/`workflow_run`, do the privileged work against the *base* ref only; never run the checkout action against the PR head/fork ref in that job.
- **Enforceable (hook/CI):** flag a `pull_request_target`/`workflow_run` job whose checkout step references `github.event.pull_request.head` / a fork ref. `[inf]` for the lint shape.

### 5. ⛔ NEVER put a `paths:` / `branches:` filter on a *required* status check — it hangs the PR forever

**This is the trap most likely to bite an agent, so it leads the list of hard rules.** A required check that gets skipped by path/branch filtering does **not** report success — it stays **Pending**, and a PR requiring it is **blocked from merging permanently**. GitHub: a workflow skipped by path/branch filtering leaves its checks *"in a 'Pending' state and block[s] merging"* → *"Avoid requiring workflows that can be skipped."* **[obs]**, retrieved 2026-08-12. This is also codified in RavenClaude's own [`AGENTS.md`](../../../AGENTS.md) § "Required status checks."

- **The fix:** gate individual **steps** with `if:` *inside* the job — never the workflow `on:` trigger. A skipped *job* reports Success; a skipped *workflow* reports nothing at all.

  ```yaml
  # ✅ conditional STEP inside a job that always reports a status
  - name: heavy docs build
    if: contains(steps.changed.outputs.files, 'docs/')
    run: make docs

  # ❌ a paths: filter on a REQUIRED workflow's trigger — leaves it Pending, hangs the PR forever
  on:
    pull_request:
      paths: ['src/**']
  ```

- **Enforceable (hook/CI):** cross-check the repo ruleset's required-check list against each required workflow's `on.pull_request`/`on.push` triggers; **fail if any required workflow carries a `paths:` or `branches:` filter.**
- **Second-order trap:** a whole-tree validator (`prettier --check .`, `ruff check .`) can *never* be correctly `paths:`-filtered — any glob list fails **open** (the gate silently never runs). An allow-list is the wrong shape for a whole-tree reader; don't add one to trim minutes, gate the *steps* instead. **[obs — internal]** (RavenClaude patched exactly this list three times before removing it.)

### 6. Merge queue keeps the base branch green; CODEOWNERS routes reviewers

- **Merge queue** for busy default branches: GitHub batches PRs into a `merge_group` *"with the latest version of the `base_branch`"* and merges only once *"the checks required by the branch protections … pass"* — so the base branch is *"never broken by incompatible changes."* **[obs]** `renovatebot/renovate` evidences queue use (`cancel-stale-merge-queue-workflows.yml`). **Teachable (agent):** don't merge-by-hand ahead of the queue — a manual merge lands untested-against-latest-base code, which is the exact breakage the queue prevents.
- **CODEOWNERS** routes the right reviewers and can scope approvals **by path**: `kubernetes/kubernetes` root `OWNERS` runs hierarchical `approvers`/`reviewers` with per-path `required_reviewers` (e.g. `go.mod`/`go.sum` → `dep-approvers`); `grafana/grafana` runs a `codeowners-validator.yml`. **[obs]** **Enforceable (hook/CI):** validate `CODEOWNERS` parses and every pattern resolves (a stale owner path silently disables its rule).

### 7. Least-privilege `permissions:` for an agent-triggered workflow — and the default-token downstream trap

Rule 1 sets the `permissions:` floor for *any* workflow. A workflow whose **trigger is an AI agent** — a `@claude`-style mention, a bot-authored PR, an issue-comment automation — has a sharper least-privilege target and one non-obvious trap.

- **Scope the agent's job to exactly what its task needs.** `anthropics/claude-code-action`'s default `claude.yml` grants its job only `contents: write`, `pull-requests: write`, `issues: write`, `id-token: write`, `actions: read`, gated behind an `if:` on the trigger so it fires only on the intended event — not a blanket top-level grant. **[obs — claim 2]** (read via API, 2026-08-12.) **Teachable (agent):** an agent-driven job that only comments needs no `contents: write`; grant the write scope the *task* needs, per job, never repo-wide.
- **⛔ The default-`GITHUB_TOKEN` downstream-suppression trap (the high-leverage one).** A push (or a PR) made with the workflow's **default `GITHUB_TOKEN` does not fire downstream workflow runs** — GitHub's documented recursion guard, so a bot can't loop by triggering itself. **[obs — claim 10]** (GitHub "Automatic token authentication" docs + the claude-code-action troubleshooting note, read 2026-08-12; the differential that confirms it — an App/PAT-authed push *does* fire them.) **Consequence for an agent:** if the agent opens or updates a PR with the default token and then arms auto-merge, it can wait indefinitely on a required check **that never starts** — the PR sits without a run. This is the root cause behind the symptom [`remote-mcp-pr-landing.md`](remote-mcp-pr-landing.md) § "confirm a run fired" tells you to detect. **The fix:** authenticate the PR-creating / branch-pushing step as a **GitHub App** or a **custom token**, or use **OIDC / workload-identity federation** (Rule 3) — each is a distinct principal from the default token, so the push is a "real" event that fires the required checks. **[inf]**
- **Trigger-loop + untrusted-input floor still applies.** An agent-triggered workflow is still bound by Rule 4 (never check out untrusted PR head under `pull_request_target`/`workflow_run`) and by the trigger-write-access / bot-rejection defenses covered in [`claude-in-ci.md`](claude-in-ci.md).

See [`claude-in-ci.md`](claude-in-ci.md) for the full agent-in-CI wiring; this rule is the `permissions:`-specific slice.

---

## Branch protection — how to set it

The rules above (Rule 5 on never path-filtering a required check, and Rule 6 on the merge queue + CODEOWNERS) say *what* a protected branch should require. The **setup procedure** is scaffolded, guidance-first, by the [`/init-agent-ready`](../commands/init-agent-ready.md) gold-standard tier — it is a helper you run, never a default-on control:

- **[`../templates/agent-ready-repo/setup-branch-protection.sh.template`](../templates/agent-ready-repo/setup-branch-protection.sh.template)** — a **dry-run-by-default** helper. It prints the `gh api` repository-ruleset body it *would* POST (require-a-PR-before-merge + the four `github-protocol-*` workflows as required status checks + optional linear history) and **self-checks that none of those four workflows carries a `paths:`/`branches:` filter on its `pull_request` trigger** — the Rule-5 trap, applied to the exact checks about to become required. `--apply` is deliberately un-automatable: it requires a live `gh auth status` **and** a typed, terminal-only confirmation, and it refuses outright if the self-check finds a filter. The required-check *context* strings in the script are each workflow's job `name:` (that is how GitHub keys a required check).
- **[`../templates/agent-ready-repo/CODEOWNERS.template`](../templates/agent-ready-repo/CODEOWNERS.template)** — a commented-out starter for the path-scoped ownership Rule 6 describes; `setup-branch-protection.sh --require-codeowner-review` is what turns a code-owner's approval into a *required* one.

The ruleset REST shape the helper emits (`POST /repos/{owner}/{repo}/rulesets`, a `rules[]` array of `pull_request` / `required_status_checks` / `non_fast_forward` / `deletion`) was verified live on 2026-08-12; the optional `required_linear_history` rule is documented-but-unobserved and carries a verify-against-current-docs note in the script header.

---

## Copy-verbatim exemplars

When you need a hardened workflow to model, **copy from a file that was read whole and verified this session** rather than reconstructing from memory:

- **`sigstore/cosign` → [`.github/workflows/github-oidc.yaml`](https://github.com/sigstore/cosign/blob/main/.github/workflows/github-oidc.yaml)** — the least-privilege textbook: `permissions: {}` at the top, per-job `id-token: write` + `contents: read`, every action SHA-pinned, `persist-credentials: false`, keyless OIDC signing. Copy this for rules 1 + 2 + 3 together. **[obs]** (read via API, 2026-08-12.)
- **`changesets/changesets` → [`.github/workflows/publish.yml`](https://github.com/changesets/changesets/blob/main/.github/workflows/publish.yml)** — the publish-job masterclass: workflow-level `permissions: {}`, per-job explicit scopes, a **non-cancel release concurrency queue** (`cancel-in-progress: false, queue: max`), npm OIDC trusted publishing, a GitHub **App token** (not a PAT), and `skip-cache: true` in the publish job (anti-cache-poisoning). Copy this for a release/publish pipeline. **[obs]** (read via API, 2026-08-12.)

The full 30-repo table (which repo exemplifies which practice, and whether the file was read whole or the workflow directory only listed) is Section 2 of [`github-gold-standard-repos.md`](github-gold-standard-repos.md).

---

## Consciously deferred for the typical consumer (C5)

**SBOM-at-release, SLSA Build L3 provenance, and full release-automation are deliberately NOT part of the baseline this file enforces** — not because they're unimportant, but because they're **lower-leverage for the typical consumer**. This marketplace is a plugin marketplace (markdown + shell + JSON, no compiled artifact), and most consumer repos likewise don't build-and-ship a compiled binary or container. For those repos, the PR-flow, commit-hygiene, and secret gates above return far more security per unit of effort than an artifact-provenance pipeline for artifacts that don't exist. Adding SLSA/SBOM machinery to a repo that ships no artifacts is ceremony.

**If you *do* ship compiled artifacts** (a binary, a container, an npm/PyPI package), the exemplars to copy are: `oras-project/oras` [`release-github.yml`](https://github.com/oras-project/oras/blob/main/.github/workflows/release-github.yml) (Syft **SBOM** + GPG-signed release) **[obs]**; `changesets` / `semantic-release` (dogfooded **release automation**) and `aquasecurity/trivy` `release-please.yaml` **[obs]**; and `slsa-framework/slsa-github-generator` (`builder_*_slsa3.yml` — the canonical way to emit **SLSA Build L3** provenance from Actions) **[obs]**. SLSA L3 requires isolation between runs and keeps the signing key inaccessible to the build steps, so provenance is non-forgeable (slsa.dev/spec/v1.0/levels, retrieved 2026-08-12). Reach for these when the artifact exists to protect — see Sections 1.7–1.8 of [`github-gold-standard-repos.md`](github-gold-standard-repos.md).

---

## See also

- **[`github-gold-standard-repos.md`](github-gold-standard-repos.md)** — the full durable best-practices catalog (all 8 categories: Actions/CI, branch protection, worktrees, CI-gate design, PR flow, commit hygiene, release/versioning, supply chain), the dated 30-repo snapshot, and Section 3's "highest-leverage to enforce" ranking.
- **[`../rules/git-workflow.md`](../rules/git-workflow.md)** — the git-workflow rule (branch naming, Conventional Commits gate, worktrees, branch hygiene), which points back here for the Actions-hardening rules.
- **[`claude-in-ci.md`](claude-in-ci.md)** — running an agent safely as the GitHub actor from inside CI (invocation modes, the trust boundary, config restore, commit signing, structural anti-self-approval) — the full context for Rule 7's agent-triggered-`permissions:` slice.
- **[`agent-issue-triage.md`](agent-issue-triage.md)** — operating GitHub Issues as a primary actor: the minimal comment→label→link→close-with-a-reference shape, the default-branch-only auto-close trap, and the `state_reason` / silently-dropped-mutation traps a naive triage agent breaks on.
