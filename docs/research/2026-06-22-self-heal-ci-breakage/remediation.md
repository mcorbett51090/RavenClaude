# Remediation — self-heal CI breakage (ready-to-apply)

Companion to [`synthesis.md`](./synthesis.md). Three tracks. Track 1 is **done** (this PR). Tracks 2–3 are **drafted, not applied** — track 2 needs an admin to create a GitHub App first (applying the workflow diff before the secrets exist would make the self-heal fail *earlier*), and track 3 is **unverifiable in the dev sandbox** (mermaid's render is network-blocked here), so it ships as a ranked proposal, not a confident fix.

---

## Track 1 — unblock main now (DONE in this PR)

Regenerated the three PR-blocking artifacts so `validate-marketplace` goes green:

- `feedback-report.html`, `index.html`, `dashboard.html` — regenerated (pure Python, deterministic), all `--check` fresh.
- The only PR-blocking freshness gates are **concepts-doc, index.html, feedback-report** (`audit-gates.sh:1671/3085/3212`); all fresh.
- **Decision-tree SVGs stay stale** — acceptable because the SVG "clean-tree must_pass" check was *removed from the PR path* (`audit-gates.sh:1660`); only the "mutated-manifest must_fail" teeth remain. Stale SVGs do **not** block PR CI.

This is the minimum to get `main` green. Tracks 2–3 stop it recurring.

---

## Track 2 — durable push fix: GitHub App bypass actor (ADMIN + workflow diff)

The self-heal's `git push origin HEAD:main` is rejected with `GH013` because a ruleset requires PRs and the default `github-actions[bot]` (a system account) cannot be a bypass actor. Fix = a scoped **GitHub App** on the ruleset bypass list, pushing with its installation token. *(HIGH confidence — see synthesis §1.)*

### Admin click-path (one-time; you must do this — it needs repo/owner admin)

1. **Create the App.** GitHub → Settings → Developer settings → **GitHub Apps** → **New GitHub App**.
   - Name: e.g. `ravenclaude-selfheal`.
   - Homepage URL: the repo URL (any valid URL).
   - Uncheck **Webhook → Active**.
   - **Permissions → Repository → Contents: Read and write** (nothing else).
   - "Where can this app be installed": **Only on this account**.
   - Create → **Generate a private key** (downloads a `.pem`) → note the numeric **App ID**.
2. **Install it** on `mcorbett51090/RavenClaude` (App page → **Install App** → select the repo).
3. **Add repo secrets/vars.** Repo → Settings → Secrets and variables → Actions:
   - Variable `SELFHEAL_APP_ID` = the App ID.
   - Secret `SELFHEAL_APP_PRIVATE_KEY` = the full `.pem` contents.
4. **Add the App to the ruleset bypass list.** Repo → Settings → **Rules → Rulesets** → open the ruleset protecting `main` → **Bypass list** → **Add bypass** → search the App by name → mode **Always allow** → Save.

### Workflow diff (apply AFTER steps 1–4)

In `.github/workflows/regenerate-artifacts.yml`:

```diff
 permissions:
   contents: write

 ...
 jobs:
   regenerate:
     name: Regenerate generated artifacts on main
     runs-on: ubuntu-latest
     steps:
+      - name: Mint a GitHub App token (so the push can bypass the main ruleset)
+        id: app-token
+        uses: actions/create-github-app-token@v1
+        with:
+          app-id: ${{ vars.SELFHEAL_APP_ID }}
+          private-key: ${{ secrets.SELFHEAL_APP_PRIVATE_KEY }}
+
       - name: Checkout (full history for accurate per-plugin "Last updated" dates)
         uses: actions/checkout@v4
         with:
           fetch-depth: 0
+          token: ${{ steps.app-token.outputs.token }}   # MUST be the App token, else the
+                                                         # persisted GITHUB_TOKEN identity is
+                                                         # used for the push and GH013 returns
```

And the commit-identity at the tail (`~line 210`):

```diff
-          git config user.name "github-actions[bot]"
-          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
+          git config user.name "ravenclaude-selfheal[bot]"
+          git config user.email "${{ vars.SELFHEAL_APP_ID }}+ravenclaude-selfheal[bot]@users.noreply.github.com"
```

`git pull --rebase origin main` + `git push origin HEAD:main` are unchanged — they reuse the App-token credentials persisted by `actions/checkout`. The `[skip ci]` on the self-heal commit stays, so the push creates no CI churn.

**Fallback if you'd rather never push to `main`:** Approach B (open a PR with `peter-evans/create-pull-request@v8` using the *same* App token so CI runs, + auto-merge). Heavier; note the flagged 2026-03 auto-merge change (synthesis §1, Approach B). Recommend Approach A.

---

## Track 3 — mermaid SVG render (PROPOSAL — unverified in this sandbox)

The SVG render fails in CI with `… at #evaluate (…ExecutionContext.js) … renderMermaid (…)`. **The obvious fixes are already in place:** `render-trees.py` / `render-concepts.py` already pin `MMDC_VERSION = "11.15.0"` and already pass `{"args":["--no-sandbox","--disable-setuid-sandbox"]}`. Reproduced identically in the dev sandbox at that pin — but the sandbox is **network-restricted** (mermaid's fetch is redirected to a `*.invalid` host), so **no fix can be verified here.** The candidates below are ranked from the research; apply + verify in CI (a `workflow_dispatch` of the SVG render is the cheap probe).

| # | Candidate | Why | Confidence |
|---|---|---|---|
| 1 | **Install a known-good Chrome explicitly** before render: `npx puppeteer browsers install chrome` (or set `PUPPETEER_SKIP_DOWNLOAD=false`) | mermaid-cli 11.15.0 bundles puppeteer `23.11.1`, which is flagged deprecated (needs `>=24.10.2`, mermaid-cli #981/#1005); the bundled Chromium may not match the runner | MEDIUM |
| 2 | **Bump `MMDC_VERSION`** to the newest release that ships puppeteer `>=24.10.2`, re-pin | resolves the CDP/version-mismatch class that the `ExecutionContext.js` frame points at | MEDIUM |
| 3 | **Add the puppeteer config `--disable-dev-shm-usage --no-zygote`** (beyond the current two args) | `/dev/shm` exhaustion is a common CI-only Chromium crash | LOW-MEDIUM |
| 4 | **Install Chromium system libs** (`libnss3 libgbm1 libatk1.0-0 …`) on the runner | less likely on GitHub-hosted ubuntu-latest, but cheap to rule out (`dpkg -l`) | LOW |

**Note:** this is *not* on the PR-blocking path (SVG clean-tree freshness was removed from PR CI), so it is lower urgency than tracks 1–2 — but until it's fixed, decision-tree SVGs stay frozen at their last-good render.

---

## Suggested order

1. Merge track 1 (this PR) → main green.
2. Admin does Track 2 click-path → apply the workflow diff → self-heal can push again.
3. `workflow_dispatch` the self-heal; if SVGs still fail, try Track 3 candidate 1, then 2.
