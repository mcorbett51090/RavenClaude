---
name: secrets-detection-and-remediation
description: "Playbook for detecting secrets committed to Git — pre-commit hooks, CI scanning, historical repo scanning — and the full remediation procedure when a secret is found: rotation, history rewrite, and the post-incident checklist."
---

# Secrets Detection and Remediation

## When to invoke

Use when adding secrets scanning to a CI/CD pipeline, investigating a potential leaked credential, responding to a GitHub push-protection alert, or auditing a legacy repository for historical leaks.

## Step 1 — Pre-commit detection (shift-left)

Block secrets before they ever hit the remote:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.4
    hooks:
      - id: gitleaks
        name: Detect hardcoded secrets

  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
```

Install on the repo and for every contributor:
```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files   # baseline scan
```

`detect-secrets` uses the baseline file to suppress known false positives — update it when you intentionally add a token-shaped test fixture.

## Step 2 — CI scanning gate

Pre-commit is advisory (devs can skip with `--no-verify`). The CI gate is the enforced backstop:

```yaml
# .github/workflows/security.yml
name: Secret Scanning

on: [push, pull_request]

jobs:
  gitleaks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }   # full history for diff scanning
      - uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GITLEAKS_LICENSE: ${{ secrets.GITLEAKS_LICENSE }}  # required for org scans
```

`fetch-depth: 0` is required — shallow clones miss secrets introduced in older commits of a PR.

**GitHub native push protection:** enable under Organization → Settings → Code Security → Secret scanning → Push protection. This blocks the push at the server before it lands, for known high-entropy patterns (AWS keys, GCP SA keys, Stripe keys, etc.).

## Step 3 — Full repository historical scan

For legacy repositories or post-incident audits:

```bash
# Full history scan (all branches, all commits)
trufflehog git file://. \
  --only-verified \
  --json \
  | tee trufflehog-results.json

# Or with gitleaks on full history
gitleaks detect \
  --source . \
  --log-opts="--all" \
  --report-path gitleaks-report.json \
  --report-format json
```

`--only-verified` (TruffleHog): tests each found credential against its API — reduces false positives significantly. Active credentials are the priority.

## Step 4 — Triage findings

For each finding:

| Field | Record |
|---|---|
| Secret type | AWS access key, GitHub PAT, DB password, etc. |
| First introduced | Commit SHA + date |
| Last seen | Most recent commit containing it |
| Current status | Active (verified) / Expired / Unknown |
| Blast radius | What can this credential access? |

**Prioritize by:** verified/active first → then by blast radius (prod credentials > dev > test) → then by exposure window (public repo > private).

## Step 5 — Remediation procedure

### 5a. Rotate immediately (before history rewrite)

Rotation stops active exploitation. History rewrite comes second.

```
AWS: IAM → Security credentials → Deactivate → Create new key → Update consumers → Delete old
GCP: IAM → Service Accounts → Keys → Add key → Update consumers → Delete old key
GitHub PAT: Settings → Developer settings → Personal access tokens → Regenerate
DB passwords: ALTER USER ... PASSWORD '...' + update all connection strings
```

### 5b. Rewrite Git history

Use `git-filter-repo` (not the deprecated `filter-branch`):

```bash
pip install git-filter-repo

# Remove a specific file that contained the secret
git filter-repo --path path/to/secret-file.env --invert-paths

# Or replace the exact secret string across all history
git filter-repo --replace-text <(echo "AKIAIOSFODNN7EXAMPLE==>REDACTED_AWS_KEY")
```

**Before rewriting:**
1. Notify all team members — their local clones will diverge.
2. Create a backup branch/tag.
3. Force-push to all remotes (`git push --force --all`).
4. All contributors must re-clone or `git fetch --all && git reset --hard origin/main`.

### 5c. Invalidate caches and forks

- GitHub: Contact GitHub Support to invalidate cached views (forks, PR diffs, search index).
- Private repos: ensure no forks exist with the compromised history.
- CI artifact caches: purge any CI cache that may have captured the secret in logs or build artifacts.

## Step 6 — Post-incident checklist

```
[ ] Secret rotated and old credential deleted/deactivated
[ ] Git history rewritten; no trace in any branch or PR diff
[ ] All consumers (apps, CI, scripts) updated to use new credential
[ ] Audit log reviewed: was the secret used between first-commit and rotation?
[ ] Platform logs checked (AWS CloudTrail / GCP Audit Logs / GitHub audit log)
[ ] Incident note written: type, exposure window, scope, remediation
[ ] Pre-commit hook and CI gate added/verified to prevent recurrence
[ ] Team notified of the rewritten history + required re-clone
```

## Pitfalls

- **Rotating without checking the audit log first** — if the secret was used maliciously, you need the log before it ages out; rotation alone without investigation leaves the breach scope unknown.
- **Removing the file but not the Git history** — deleting the file in a new commit doesn't remove the secret from `git log`; the history rewrite is mandatory.
- **Skipping the force-push to all branches** — a history rewrite on `main` that doesn't cover `develop`, `release/*`, and every open PR branch leaves copies of the secret in the remote.
- **`--only-verified` masking unverified but real secrets** — TruffleHog verified mode skips expired/rate-limited creds; run an unverified scan too on critical repos and manually triage.
- **No `.gitleaksignore` or secrets baseline** — without a suppression file, scan noise from test fixtures blocks the CI gate with false positives; establish a baseline on day one.
