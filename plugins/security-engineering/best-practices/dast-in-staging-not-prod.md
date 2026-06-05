# Run DAST against staging, not production

**Status:** Absolute rule
**Domain:** Application security testing
**Applies to:** `security-engineering`

---

## Why this exists

Dynamic Application Security Testing (DAST) sends malicious payloads (SQL injection strings, XSS probes, path traversal attempts) to the running application. Running DAST against production risks corrupting data, triggering production workflows (sending test emails to real users, creating billing records, initiating transactions), and generating noise in production logs and alerts. Staging provides a realistic target without the blast radius of production, and allows DAST to run without fear of side effects.

## How to apply

Configure the DAST tool (OWASP ZAP, Burp Suite Enterprise, StackHawk, Semgrep Supply Chain) to target the staging URL. Gate the DAST run to run post-deploy to staging, before promoting to production.

```yaml
# GitHub Actions: DAST with ZAP against staging after deployment
jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    outputs:
      staging-url: ${{ steps.deploy.outputs.url }}
    steps:
      - run: ./scripts/deploy.sh staging ${{ github.sha }}

  dast-scan:
    needs: deploy-staging
    runs-on: ubuntu-latest
    steps:
      - name: ZAP Full Scan
        uses: zaproxy/action-full-scan@v0.10.0
        with:
          target: ${{ needs.deploy-staging.outputs.staging-url }}
          rules_file_name: .zap/rules.tsv    # suppress known false positives
          cmd_options: '-a'                   # include ajax spider
          fail_action: true                   # fail the job on new high-risk findings

      - name: Upload ZAP report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: zap-report
          path: report_html.html
```

```
# .zap/rules.tsv — suppress known false positives
# Rule ID  Alert  Action  Comment
10096      IGNORE  # Timestamp disclosure — intentional in our health endpoint
10021      IGNORE  # X-Content-Type-Options — set via CDN, not app headers
```

**Do:**
- Tune the DAST tool with a suppression file for known false positives before enabling the CI gate.
- Use a dedicated test user with known, resettable credentials in staging — not a shared account.
- Run an authenticated scan (spider with a logged-in session) to cover authenticated endpoints.
- Route new DAST findings through the vulnerability triage process (`triage-by-exploitability-not-cvss.md`).

**Don't:**
- Run DAST against production without explicit consent, out-of-band notification to ops, and a carefully scoped ruleset.
- Disable the DAST CI gate because it takes too long — tune the ruleset or run it post-merge asynchronously.
- Use DAST as a substitute for SAST/SCA — they catch different vulnerability classes.

## Edge cases / when the rule does NOT apply

Annual or semi-annual penetration tests by an external firm are typically run against a production-like environment with explicit scope and rules of engagement. These are planned, scoped exercises — not the same as automated pipeline DAST. They may touch staging, pre-prod, or a prod-replica environment, never production unless the scope explicitly includes it.

## See also

- [`../agents/appsec-engineer.md`](../agents/appsec-engineer.md) — owns DAST configuration and the AppSec program.
- [`./shift-left-find-it-in-design-and-ci.md`](./shift-left-find-it-in-design-and-ci.md) — DAST is the runtime complement to SAST; both are needed.

## Provenance

Codifies standard DAST targeting practice (OWASP Testing Guide v4, OWASP ZAP documentation) and safe-testing principles that protect production data integrity.

---

_Last reviewed: 2026-06-05 by `claude`_
