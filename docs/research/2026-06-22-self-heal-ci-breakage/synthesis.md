# Deep research synthesis — main's actual breakage (self-heal CI)

**Date:** 2026-06-22
**Question:** Why is `main` CI-red, and how do we fix it — the self-heal workflow's blocked push to a ruleset-protected `main` (GH013) and the secondary mermaid-cli render failure.
**Method:** `rc-deep-research` fan-out — 3 parallel WebSearch/WebFetch agents (ruleset bypass · create-PR/token/auto-merge · mermaid-cli CI), then cross-source adversarial verification. Confidence + source on every consequential claim.

---

## 0. The observed breakage (this repo, this session — verified)

`.github/workflows/regenerate-artifacts.yml` self-heals generated artifacts on every push to `main`, then runs `git push origin HEAD:main`. The latest run on `main` (`20c3171`, run `27978616874`) **failed**, log excerpt:

```
decision-tree SVGs stale — rendering with mermaid-cli.
RuntimeError: mermaid-cli failed: ... at #evaluate (...puppeteer/cdp/ExecutionContext.js)
::warning::decision-tree SVG render failed (mermaid) — reverting partial output, continuing self-heal
dashboard.html stale — regenerating.   [ok]
index.html stale — regenerating ...    [ok]
[main ea272a6] chore(artifacts): self-heal ...
remote: error: GH013: Repository rule violations found for refs/heads/main.
remote: - Changes must be made through a pull request.
 ! [remote rejected]   HEAD -> main (push declined due to repository rule violations)
##[error]Process completed with exit code 1.
```

**Two independent root causes**, both confirmed here:

1. **The push is blocked** by a branch-protection **ruleset** ("Require a pull request before merging") → `dashboard.html` + `index.html` regenerate but never land → they sit stale on `main` → `audit-gates.sh` Gate 13 (dashboard) + Gate 97 (index) fail in `validate-marketplace` → **every PR inherits the red.**
2. **The mermaid SVG render fails** (non-fatal in the workflow, so it warns + reverts) → decision-tree SVGs stay stale too.

Fixing #1 unblocks main; fixing #2 stops the SVGs drifting. Both are needed for a durable green.

---

## 1. Root cause #1 — push blocked by a ruleset (GH013)

### Which protection emits GH013 (HIGH)
`GH013` is emitted by **new-style rulesets** (Settings → Rules → Rulesets). Classic branch protection emits **GH006**. The bypass mechanics differ between the two, so this matters.
— Community Discussions [#110674](https://github.com/orgs/community/discussions/110674), [#136531](https://github.com/orgs/community/discussions/136531).

### The default `GITHUB_TOKEN` / `github-actions[bot]` cannot be granted a bypass (HIGH)
`github-actions[bot]` is a **built-in system account** (user id `41898282`), **not** a GitHub App. A ruleset **bypass list** accepts only **roles, teams, GitHub Apps, and deploy keys** (`RepositoryRole`/`Team`/`Integration`/`DeployKey`/`OrganizationAdmin`) — system accounts are not a bypassable actor type. So you cannot "just allow the Actions bot."
— Discussions [#175332](https://github.com/orgs/community/discussions/175332), [#110674](https://github.com/orgs/community/discussions/110674), [#13836](https://github.com/orgs/community/discussions/13836).

### Ranked fixes

**Approach A — dedicated GitHub App in the ruleset bypass list (RECOMMENDED, HIGH).**
Create a minimal GitHub App (permission: *Contents: read & write*), install it on the repo, add it to the ruleset **Bypass list** ("Always allow"), and push with its installation token instead of `GITHUB_TOKEN`:

```yaml
- uses: actions/create-github-app-token@v1
  id: app-token
  with:
    app-id: ${{ vars.APP_ID }}
    private-key: ${{ secrets.APP_PRIVATE_KEY }}
- uses: actions/checkout@v4
  with:
    token: ${{ steps.app-token.outputs.token }}   # MUST pass here, or persisted GITHUB_TOKEN creds win
# ... regenerate artifacts ...
- run: |
    git config user.name  "ravenclaude-selfheal[bot]"
    git config user.email "...@users.noreply.github.com"
    git commit -am "chore(artifacts): self-heal [skip ci]"
    git push origin HEAD:main
```
**Gotcha (HIGH):** the token must be passed to `actions/checkout` (or `persist-credentials: false` + manual remote), else the persisted `GITHUB_TOKEN` identity is used for the later push and it's rejected again.
Security: App token is scoped (contents-only), revocable, per-push auditable — strictly safer than a human PAT.
— Discussions [#136531](https://github.com/orgs/community/discussions/136531), [actions/create-github-app-token #75](https://github.com/actions/create-github-app-token/discussions/75); [GitHub Docs — About rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets).

**Approach B — open a PR instead of pushing (peter-evans/create-pull-request, HIGH).**
Aligns with "everything goes through a PR," but carries a sharp caveat:

> A PR created with the default `GITHUB_TOKEN` does **not** trigger `on: push`/`on: pull_request` workflows.
— GitHub's recursion-prevention rule ([Community #65321](https://github.com/orgs/community/discussions/65321)); restated in the action's [concepts-guidelines](https://github.com/peter-evans/create-pull-request/blob/main/docs/concepts-guidelines.md).

So a `GITHUB_TOKEN`-created artifact PR has **no checks** and "merge when green" never fires. Fix: create the PR with a **GitHub App token** (preferred) or a fine-grained **PAT** so CI runs. Auto-merge then needs: repo "Allow auto-merge" on + a branch rule with ≥1 required check. **Flagged caveat (MEDIUM-HIGH, official docs not yet updated):** community reports a **2026-03-25 change** where auto-merge can no longer be enabled until *all* PR requirements are already satisfied (HTTP 422 otherwise) — pushing teams toward **merge queues** ([Community #190610](https://github.com/orgs/community/discussions/190610)). This is the costlier path.

**Approach C — deploy key in the bypass list (MEDIUM-HIGH).** Works on personal repos, no App needed; one key per repo, coarser audit. — [Community #25305](https://github.com/orgs/community/discussions/25305).

**Approach D — role-based bypass + a human's PAT (MEDIUM).** Works but couples CI to a person's account; many policies forbid PATs in CI.

### Recommendation for this repo
**Approach A.** The self-heal artifacts are deterministic, freshness-gated, and already pushed with `[skip ci]` — a direct bot push restores exactly the behavior that worked *before* the ruleset was added, with no per-run PR overhead and no CI-thrash. Use a scoped GitHub App on the bypass list. Choose Approach B only if policy forbids *any* direct-to-`main` push — and budget for the token + post-2026-03 auto-merge/merge-queue friction.

---

## 2. Root cause #2 — mermaid-cli puppeteer failure (`#evaluate / ExecutionContext.js`)

Two HIGH-confidence causes, both addressed together:

**Cause 1 — Chromium sandbox blocked (HIGH).** `ubuntu-latest` is now Ubuntu 24.04, whose hardened AppArmor blocks unprivileged user namespaces, so Chromium's default sandbox can't start. Canonical fix — a puppeteer config passed to `mmdc -p`:
```json
{ "args": ["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage", "--no-zygote"] }
```
— [mermaid-cli linux-sandbox-issue.md](https://github.com/mermaid-js/mermaid-cli/blob/master/docs/linux-sandbox-issue.md), [PR #825](https://github.com/mermaid-js/mermaid-cli/pull/825) (the project's own CI hit this on the 24.04 switch).

**Cause 2 — floating `npx` version mismatch (HIGH).** The `#evaluate / ExecutionContext.js` frame is the puppeteer↔Chromium CDP layer — the classic signature of a mermaid-cli/puppeteer version mismatch, and mermaid-cli has shipped releases broken this way (e.g. [#556](https://github.com/mermaid-js/mermaid-cli/issues/556), deprecation churn [#981](https://github.com/mermaid-js/mermaid-cli/issues/981)/[#1005](https://github.com/mermaid-js/mermaid-cli/issues/1005)). **`npx @mermaid-js/mermaid-cli` (unpinned) resolves `@latest` every run**, so a bad release breaks CI that day with no repo change — exactly the intermittent self-heal failures we see. Fix: **pin the version** (latest stable ~`11.15.0`, re-verify at use): `npm i -g @mermaid-js/mermaid-cli@<pinned>`.

**Causes 3–4 (MEDIUM).** Missing system libs (`libnss3`, `libgbm1`, `libatk1.0-0`, …) or Chromium never downloaded — less likely on GitHub-hosted `ubuntu-latest`, but `npx puppeteer browsers install chrome` / `apt-get` are the remedies if the above two don't resolve it. — [Puppeteer troubleshooting](https://github.com/puppeteer/puppeteer/blob/main/docs/troubleshooting.md).

### Recommendation for this repo
Pin `@mermaid-js/mermaid-cli` in `render-trees.py` / `render-concepts.py` invocations (replace floating `npx`), and pass a `puppeteer-config.json` with `--no-sandbox …`. Note: `render-trees.py` already wipes-then-renders, so the workflow's revert-on-failure is correct; this just stops the failure happening.

---

## 3. Recommended remediation sequence (smallest-blast-radius first)

1. **Now / unblock main (PR path):** land the regenerated `dashboard.html` + `index.html` via a normal PR (the path the ruleset allows) so `validate-marketplace` goes green. *(This is what PR #428 can be expanded to do.)*
2. **Durable fix #1 (admin + workflow):** add a scoped GitHub App to the ruleset bypass list; switch `regenerate-artifacts.yml` to push with its token (Approach A). One-time admin setup.
3. **Durable fix #2 (workflow):** pin mermaid-cli + add the `--no-sandbox` puppeteer config so SVGs actually regenerate.
4. **Optional hardening:** keep `[skip ci]` on the self-heal commit; add branch `if:` guards on the secret-bearing job.

---

## 4. Verification / uncertainty ledger

| Claim | Confidence | Note |
|---|---|---|
| GH013 = rulesets (not classic GH006) | HIGH | cross-confirmed, 2 discussions |
| `GITHUB_TOKEN`/`github-actions[bot]` cannot be a bypass actor | HIGH | system account, not an App |
| GitHub App token + bypass list is the sanctioned bot-push path | HIGH | multiple working reports + docs |
| token must be passed to `actions/checkout` | HIGH | persisted-credentials gotcha |
| `GITHUB_TOKEN`-created PR doesn't trigger CI | HIGH | GitHub recursion rule + action docs |
| 2026-03-25 auto-merge "all requirements first" change → merge queues | MEDIUM-HIGH | community-reported; official docs not yet updated — **verify before relying** |
| `--no-sandbox` puppeteer config is the canonical CI fix | HIGH | mermaid-cli docs + PR #825 |
| unpinned `npx` mermaid-cli causes intermittent CI breakage | HIGH | release-broke precedents |
| latest stable mermaid-cli ~11.15.0 | MEDIUM | re-verify the exact pin at use |
| missing-libs uncommon on GitHub-hosted ubuntu-latest | MEDIUM | confirm with `dpkg -l` if 1+2 don't fix it |

**Could not fully verify:** exact UI flow of the Sep-2025 ruleset "exempt" bypass mode (docs.github.com 403'd); whether `github-actions[bot]` has any usable `actor_id` (open issue [rest-api-description #4406](https://github.com/github/rest-api-description/issues/4406)) — sources agree it does not.
