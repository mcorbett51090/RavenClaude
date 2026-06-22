# Security & Performance Audit — <site>

> Output template for `wordpress-ops-engineer` (with `wordpress-developer` for code-level findings). Report findings by severity with fixes. Fill every section; delete the guidance in italics.

## Scope
- **Site / environment:** _what was audited_
- **Inputs reviewed:** _custom code, config, plugins, caching, update posture_

## Security findings
| Severity | Finding | Fix |
|---|---|---|
| _high/med/low_ | _e.g. unsanitized $_POST, missing nonce, $wpdb concatenation, file editor enabled, out-of-date plugin_ | _the specific remediation_ |

- **Sanitize-in / escape-out:** _gaps found_
- **Prepared SQL:** _any concatenation found_
- **Nonce + capability:** _any unguarded action / open REST route_
- **Config hardening:** _DISALLOW_FILE_EDIT, HTTPS, least-privilege roles, secrets/salts, login/xmlrpc_
- **Update posture:** _what's out of date_

## Performance findings
| Severity | Finding | Fix |
|---|---|---|
| _high/med/low_ | _e.g. no persistent object cache, unbounded WP_Query, expensive query per request, unversioned assets_ | _the specific remediation_ |

- **Caching layers present:** _page / object (persistent?) / fragment / CDN_
- **Expensive queries:** _identified + caching plan_
- **Measurement:** _what profiling showed_

## Safe-change plan
- **Backup + staging + rollback:** _the runbook for applying these fixes_

## Seams handed off
- _Infra perf budget → performance-engineering · formal security verdict → security-engineering · code fixes → wordpress-developer_

---
_Plus the ravenclaude-core Structured Output block._
