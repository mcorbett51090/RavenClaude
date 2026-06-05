# Review access and permissions on a regular cadence — entitlement creep is a vulnerability

**Status:** Absolute rule
**Domain:** Identity and access management
**Applies to:** `security-engineering`

---

## Why this exists

Access entitlements only accumulate over time without active review: an engineer promoted to a new team retains their old permissions; a contractor whose engagement ended still has production access; a service account created for a one-off migration still has write access to the database. Each of these is a lateral movement opportunity for an attacker who compromises those credentials. Access reviews convert the principle of least privilege from a point-in-time configuration into a sustained posture.

## How to apply

Schedule access reviews at a defined cadence. Review human access quarterly, service account access semi-annually, and privileged/admin access monthly. Use your IAM provider's access review tooling where available (AWS IAM Access Analyzer, Azure AD Access Reviews, GCP Access Transparency).

```bash
# AWS IAM: generate a credential report and flag unused credentials
aws iam generate-credential-report
aws iam get-credential-report --output text --query Content | base64 -d > credentials.csv

# Flag credentials unused for > 90 days
python3 - <<'PY'
import csv, sys
from datetime import datetime, timezone, timedelta

threshold = datetime.now(timezone.utc) - timedelta(days=90)
with open('credentials.csv') as f:
    for row in csv.DictReader(f):
        last_used = row.get('access_key_1_last_used_date', 'N/A')
        if last_used not in ('N/A', 'no_information') and datetime.fromisoformat(last_used) < threshold:
            print(f"STALE: {row['user']}, last used: {last_used}")
PY
```

Access review checklist:

- [ ] Human accounts: still employed and in the right role?
- [ ] Service accounts: still needed? Minimum necessary permissions?
- [ ] Privileged/admin access: break-glass only? Not used as day-to-day account?
- [ ] External/third-party access: vendor still engaged? Scope still justified?
- [ ] Inactive credentials (> 90 days unused): disable or revoke.

**Do:**
- Remove access at offboarding automatically via your IdP (Okta, Azure AD) — human review confirms the automation worked.
- Use groups and roles rather than per-user IAM policies so review covers the group membership, not hundreds of individual grants.
- Log every access review with who reviewed, what was revoked, and the date.

**Don't:**
- Treat quarterly reviews as a compliance checkbox — if you find a stale account, dig into how it got there.
- Leave access in place pending a "later cleanup" ticket; revoke on discovery, not on schedule.
- Use the same service account for multiple services — it makes access review ambiguous and scope wide.

## Edge cases / when the rule does NOT apply

Emergency break-glass accounts (for production incident access without the normal SSO path) are intentionally persistent but must be separately tracked, their credentials stored in a vault with time-limited checkout, and every use logged and reviewed post-use.

## See also

- [`../agents/cloud-security-engineer.md`](../agents/cloud-security-engineer.md) — owns IAM posture assessment and access review for cloud environments.
- [`./least-privilege-by-default.md`](./least-privilege-by-default.md) — access reviews sustain the least-privilege posture over time.

## Provenance

Codifies ISO 27001 A.9.2.5 (Review of User Access Rights) and CIS Controls v8 Control 5.3 (Disable Dormant Accounts), applied to cloud IAM and service accounts.

---

_Last reviewed: 2026-06-05 by `claude`_
