# Tune SAST rules to signal, not noise — an ignored scanner is no scanner

**Status:** Pattern
**Domain:** Application security testing
**Applies to:** `security-engineering`

---

## Why this exists

A SAST tool running with default rules against a typical codebase will produce hundreds of findings on day one, most of which are false positives or low-severity noise. Developers learn quickly that the scanner "always has findings" and stop looking at it. An unreviewed scanner is worse than no scanner — it gives a false sense of security while adding CI noise. Tuning the scanner to a small set of high-confidence, high-impact rules and suppressing known false positives makes every remaining finding credible and actionable.

## How to apply

Start with a curated baseline ruleset. Suppress confirmed false positives with inline comments or a suppression file. Enforce only high-confidence rules in the blocking CI gate; route medium/low to a dashboard for async review.

```yaml
# Semgrep CI configuration: only block on high-confidence rules
# NOTE: returntocorp/semgrep-action (the wrapper Action) is DEPRECATED and its repo
# archived (2024-04-09) — "stop using this wrapper script and migrate to native
# Semgrep support instead" (github.com/semgrep/semgrep-action). Run the `semgrep`
# CLI directly, e.g. via the official container image, instead of a wrapper Action.
semgrep-scan:
  runs-on: ubuntu-latest
  container:
    image: semgrep/semgrep
  steps:
    - uses: actions/checkout@v4
    - name: Semgrep SAST scan
      # Use `semgrep scan` with explicit --config rulesets (repeatable), not `semgrep
      # ci`. The `ci` subcommand REFUSES --config when SEMGREP_APP_TOKEN is set — it
      # expects rulesets to come from the AppSec Platform instead, and errors out
      # ("Cannot run `semgrep ci` with --config while logged in"). This example
      # curates its own baseline ruleset inline, so it stays on `scan` with no token.
      # Switch to `semgrep ci` (drop --config, set SEMGREP_APP_TOKEN) if you manage
      # rules in the Semgrep AppSec Platform UI instead of inline --config flags.
      run: >-
        semgrep scan
        --config p/owasp-top-ten --config p/secrets --config p/sql-injection
        --sarif --sarif-output=semgrep.sarif
    - name: Fail on high severity findings only
      run: |
        jq -e '.runs[].results[] | select(.level == "error")' semgrep.sarif && exit 1 || exit 0
```

```python
# Inline suppression (use sparingly, with justification)
password = get_env("DB_PASSWORD")  # nosemgrep: hardcoded-secret — not a hardcoded password; reads from env
```

Tuning process:
1. Run the scanner and triage all findings in the first pass.
2. Mark confirmed false positives in the suppression file with the justification.
3. Mark confirmed true positives — fix them or file a tracked vulnerability.
4. Restrict the blocking CI gate to severity HIGH and rules with < 5% false-positive rate.
5. Review the suppression list quarterly; a suppression that is no longer valid should be removed.

**Do:**
- Suppress false positives in a centrally reviewed suppression file, not scattered inline `nosec` comments.
- Review the suppression list in security code review — a suppression comment is a security decision.
- Enable only the rules that apply to the language/framework in use — unused rules add noise.

**Don't:**
- Suppress entire rule categories (`# nosec`) — suppress specific findings with a specific justification.
- Treat "the scanner passes" as "the code is secure" — SAST covers a subset of vulnerability classes.
- Introduce a SAST gate with 300 findings and call it "CI" — fix or suppress before the gate goes live.

## Edge cases / when the rule does NOT apply

New projects may run SAST in "report only" mode during onboarding to build the initial suppression list without blocking development. Gate onboarding at 30 days; after that the gate is live.

## See also

- [`../agents/appsec-engineer.md`](../agents/appsec-engineer.md) — owns the SAST program, rule selection, and suppression-list governance.
- [`./shift-left-find-it-in-design-and-ci.md`](./shift-left-find-it-in-design-and-ci.md) — SAST is the CI-phase anchor of shift-left security.

## Provenance

Codifies OWASP SAST tuning guidance and Semgrep's recommended "start with p/security-audit, narrow to p/owasp-top-ten" ramp-up strategy from their enterprise documentation. `returntocorp/semgrep-action` (archived 2024-04-09; github.com/semgrep/semgrep-action) is deprecated in favor of running the `semgrep` CLI natively — see the example above.

---

_Last reviewed: 2026-09-23 by `claude` (replaced the deprecated `semgrep-action` wrapper with the native `semgrep ci` CLI pattern, and fixed the `nosec`→`nosemgrep` suppression example, per the 2026-09-23 weekly research sweep — see `CHANGELOG.md`)_
