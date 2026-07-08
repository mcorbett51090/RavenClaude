# Secrets / PII scan gate for the finance plugin

_Last reviewed: 2026-07-06 · Confidence: high (mechanically verified by `scripts/test_secrets_gate.py`, 13/13)_

The FORGE red-team's P0 follow-up on the controller-autopilot: finance deliverables
carry the marketplace's most sensitive data (bank details, wire instructions, payroll,
customer PII), and the autopilot writes CSV/JSON/Markdown artifacts under
`plugins/finance/`. This gate is the mechanical last line of defence that catches a
secret or PII **shape** before it lands in a committed artifact.

Engine: [`../hooks/scan-finance-secrets.sh`](../hooks/scan-finance-secrets.sh) (bash, `set -euo pipefail`, POSIX-ERE `grep`).

## Honest scope — read this first

This is a **shape detector, not a secret manager.** It matches the textual *shape* of a
secret (an `AKIA…` key, a `-----BEGIN … PRIVATE KEY-----` header, an `NNN-NN-NNNN` SSN);
it does not authenticate, decrypt, or verify that a match is a live credential. Two honest
consequences:

- A **clean run means "no obvious secret shape found", never "proven secret-free."** A
  base64 blob, an encrypted value, or a novel token format can pass. It is one control in
  depth, not a guarantee.
- It will produce **false positives** (an IBAN-shaped hash, an SSN-shaped ID). That is by
  design — a shape scanner errs toward flagging. In advisory mode a false positive costs
  nothing; in `--ci` you scrub or move the value out of the scanned tree.

For real secret management, credentials belong in an env var / secret store referenced by
**NAME only** (§3 #10 of [`../CLAUDE.md`](../CLAUDE.md)) — which is exactly the pattern this
gate treats as clean (see Exclusions).

## What it detects

| Rule | Shape | ERE (capturing groups, never PCRE `(?:…)`) |
|---|---|---|
| `aws-access-key` | AWS access key | `(AKIA\|ASIA)[0-9A-Z]{16}` |
| `pem-private-key` | PEM private-key header | `-----BEGIN [A-Z ]*PRIVATE KEY-----` |
| `slack-token` | Slack token | `xox[baprs]-[A-Za-z0-9-]{10,}` |
| `bearer-token` | Bearer token | `[Bb]earer[[:space:]]+[A-Za-z0-9._~+/=-]{20,}` |
| `oauth-client-secret` | `client_secret = <value>` | `client_secret["' ]*[:=]…{8,}` |
| `generic-secret-assignment` | `api_key`/`password`/`token`/… `= <value>` | keyword + `[:=]` + `[^"'\s]{6,}` |
| `us-ssn` | US SSN | `\b[0-9]{3}-[0-9]{2}-[0-9]{4}\b` |
| `credit-card-pan` | Visa / Mastercard / Amex / Discover PAN | `\b(4[0-9]{12}([0-9]{3})?\|5[1-5]…\|3[47]…\|6(011\|5[0-9]{2})…)\b` |
| `iban` | IBAN | `\b[A-Z]{2}[0-9]{2}[A-Z0-9]{11,30}\b` |

All patterns are POSIX ERE (`grep -E`). Groups are ERE **capturing** groups `(...)`;
`grep -E` does not support PCRE non-capturing `(?:...)`, so those are deliberately avoided.

## Two modes

| Mode | Invocation | On a finding | Use as |
|---|---|---|---|
| **Advisory** (default) | `scan-finance-secrets.sh <paths…>` | print to stderr, **exit 0** | non-blocking PostToolUse hook |
| **CI gate** | `scan-finance-secrets.sh --ci <paths…>` | print to stderr, **exit 1** | pre-merge gate that fails the build |

With no path arguments the default scope is `plugins/finance/`. Directories scan recursively;
binary files are skipped (`grep -I`).

## Exclusions — what never counts as a finding

- **The sanctioned "env-var NAME only" reference.** `os.environ[…]`, `getenv`, `process.env`,
  `${VAR}`, `client_secret_env` — referencing a credential by its env-var NAME is the
  *correct* pattern and must not trip the gate. This is the whole point of §3 #10: names in
  code, values in the secret store.
- **Documented placeholders:** `ENV-VAR NAME`, `<out-of-band>`, `example.com`.
- **The gate's own files:** the script, this doc, and `test_secrets_gate.py` (they contain
  the patterns as documentation).

## Fail-safe posture

If `grep` is unavailable the scan cannot run; it warns and **exits 0** rather than spuriously
blocking an edit or failing a gate on a missing tool. (`grep` is universally present — this
branch is defensive only.)

## Intended wiring (Team Lead owns `hooks.json`)

This doc + the script header specify the wiring; the Team Lead reconciles
[`../hooks/hooks.json`](../hooks/hooks.json) centrally. The intended PostToolUse entry
(alongside the existing `flag-finance-anti-patterns.sh`), matcher `Edit|Write|MultiEdit`:

```json
{
  "type": "command",
  "command": "${CLAUDE_PLUGIN_ROOT}/hooks/scan-finance-secrets.sh \"$CLAUDE_TOOL_FILE_PATH\"",
  "comment": "Advisory secret/PII shape scan on every finance edit. Non-blocking; run with --ci in CI to gate a merge."
}
```

`${CLAUDE_PLUGIN_ROOT}` resolves to the installed plugin location (not the consumer's repo
root), matching the existing hook. For pre-merge enforcement, add a CI step that runs
`scan-finance-secrets.sh --ci plugins/finance/` and treats a non-zero exit as a failure.

## Relationship to the existing anti-pattern hook

[`flag-finance-anti-patterns.sh`](../hooks/flag-finance-anti-patterns.sh) already advisory-flags
PII shapes (SSN/IBAN/credit-card) on finance-conventional file names as one of four broad
house-opinion checks. This gate is the **dedicated, secret-focused** counterpart: a wider
credential-shape catalogue (AWS/Slack/OAuth/PEM/bearer/generic assignments), a hard `--ci`
mode for pre-merge gating, and the env-var-NAME allow-list. Run both — they overlap on PII
by design (defence in depth) and diverge on credentials.

## Verification

- Acceptance suite: [`../scripts/test_secrets_gate.py`](../scripts/test_secrets_gate.py) —
  stdlib-only, shells out to the hook against synthetic temp fixtures, asserts `--ci` blocks
  on a fake secret and stays green on a clean file, and confirms advisory mode never blocks.
  **13/13 passing** as of 2026-07-06.
- Syntax: `bash -n hooks/scan-finance-secrets.sh` (clean).
