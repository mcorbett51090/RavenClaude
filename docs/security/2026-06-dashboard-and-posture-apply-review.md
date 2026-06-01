# Security review — dashboard server + posture-apply pipeline (2026-06-01)

**Reviewer:** `ravenclaude-core/security-reviewer` (4-seat panel, bundled gap-closure PR)
**Scope:** `scripts/serve-dashboards.py` + its plugin twin, `plugins/ravenclaude-core/scripts/apply-comfort-posture.py`, `plugins/ravenclaude-core/templates/comfort-posture-balanced.yaml`, this repo's `.ravenclaude/comfort-posture.yaml`.
**Method:** Read-only audit of the working tree at v0.100.0 + cross-check against memory `project_dashboard_server_drift` (the documented twin-drift hazard).
**Status:** Two findings fixed in this PR (one HIGH, one MEDIUM-as-default-change). Three findings logged as follow-ups.

---

## Findings

| # | File:line | Issue | Severity | Status in this PR |
|---|---|---|---|---|
| 1 | `plugins/ravenclaude-core/scripts/apply-comfort-posture.py:482-490, 609-615` | `security_deny` substitution treated `None` as "use baseline" but accepted an explicit empty list `[]` — wiping the entire `DEFAULT_SECURITY_DENY` floor (force-push, `rm -rf`, `curl \| sh`, secret reads, host credential stores). A user saving an empty `security_deny:` from the dashboard would lose every guardrail. | **HIGH** | **FIXED** — baseline is now always unioned; cannot be wiped. Regression test in `tests/fixtures/test_security_deny_floor.py`. |
| 2 | `plugins/ravenclaude-core/templates/comfort-posture-balanced.yaml:111-114` | `shell_package_install: allow` at the project layer let `npm install` / `pip install` run without prompting. A malicious dependency in `package.json` plus the agent triggering an install = silent code execution. | MEDIUM | **FIXED** — flipped to `ask` in the balanced seed (consumer-visible default change; migration note in CHANGELOG). |
| 3 | `scripts/serve-dashboards.py` + `plugins/ravenclaude-core/scripts/serve-dashboards.py` (both copies — drift twin per memory `project_dashboard_server_drift`) | Codespace forwarded ports default to **Private** but a user can manually flip a port to **Public**. If they do, the `/__save` + `/__run` POST surface is reachable from the public internet on a path the server doesn't expect to be public. | MEDIUM | **LOGGED** — startup banner check ("if `GITHUB_CODESPACES_PORT_VISIBILITY=public`, refuse `0.0.0.0` and log guidance") is a follow-up. Documented in `SECURITY.md` §Defaults and floors. |
| 4 | `scripts/serve-dashboards.py` CSRF posture | Guard relies on `Origin`/`Host` header check + `Sec-Fetch-Site`. A scripted HTTP client can omit `Origin` and set `Host: 127.0.0.1:8000` to bypass. Mitigated today by loopback / private-port-forwarding; not bypassable from the wider internet under normal Codespace use. | MEDIUM | **LOGGED** — per-process random CSRF token (embedded in `dashboard.html` head, checked on state-changing endpoints) is a belt-and-suspenders follow-up. |
| 5 | `apply-comfort-posture.py:318-431` (`_minimal_yaml_parse`) | Hand-rolled YAML parser used when PyYAML missing. No exec risk (output constrained to str/int/bool/null), but no max input size — a malicious 10 MB posture file would OOM the dashboard process. | LOW (NOTE) | **LOGGED** — 256 KB cap on posture file before parse is a follow-up. |
| 6 | `serve-dashboards.py` various lines | `int(Content-Length)` parsing has no try/except — a non-numeric value raises ValueError and the handler returns 500 with traceback. Info leak in dev mode. | LOW (NOTE) | **LOGGED** — wrap in try/except → 400 is a follow-up. |

No BLOCKER findings. No live secrets in working tree (skim of `git diff origin/main`). The constant-argv subprocess pattern used by `_handle_run` / `_handle_classify` (`scripts/serve-dashboards.py` ~line 1289-1297) is the right pattern and is preserved.

## What this PR ships

1. **The HIGH fix.** `apply-comfort-posture.py` `compute_emission` and `compute_emission_v5` now always union `DEFAULT_SECURITY_DENY` with whatever the user supplied, in baseline-first order. Custom rules append. An empty list, a missing field, or a custom-only list all produce a deny bucket that starts with the baseline. See `tests/fixtures/test_security_deny_floor.py` (6 cases, all pass) for the regression contract.

2. **The MEDIUM-as-default-change.** `templates/comfort-posture-balanced.yaml`'s `shell_package_install` default is `ask` (was `allow`). The change is documented in the consumer-facing CHANGELOG with a migration note: "consumers on `/plugin marketplace update` will see one new prompt per `npm install` / `pip install`; opt back to `allow` from the dashboard if undesired." The `shell_code_exec` default stays `allow` — see PR body §Deferred decisions for the rationale (over-friction risk).

3. **`SECURITY.md` is updated** with a new §"Defaults and floors" section documenting:
   - The non-removable `security_deny` floor (with the union semantics).
   - The Codespace port-visibility expectation (private only).
   - The CSRF posture and its known limit.
   - The `shell_package_install: ask` default change.

4. **Release checklist** gains a security-relevant step: verify the `security_deny` floor is intact in the candidate release by running the unit test.

## What this PR does NOT ship (logged follow-ups)

- The Codespace port-visibility startup banner check (#3).
- The per-process CSRF token (#4).
- The posture-file size cap (#5).
- The Content-Length try/except (#6).

These are non-emergency hardening items and are deliberately scoped out to keep the bundled PR reviewable. A follow-up PR `chore(security): serve-dashboards hardening pass` will close them; tracking comment added to memory `project_dashboard_server_drift` so the next session does not lose them.

## Threat model recap

The dashboard server is **local-only** by design. The realistic attacker is:

1. **A malicious webpage in the same browser session** trying to POST to `127.0.0.1:8000` from a remote origin (mitigated today by the Origin/Host check; finding #4 is the belt-and-suspenders).
2. **A supply-chain compromise in `node_modules`** triggered by an agent-driven `npm install` (mitigated by the `ask` default — finding #2).
3. **A misconfigured Codespace port** flipped to Public by the user (#3 hardens this).
4. **A user mistakenly believing `security_deny: []` is "use defaults"** (#1 — the HIGH-severity floor union).

The marketplace is private (`SECURITY.md` discloses the policy; AGENTS.md §PR conventions enforces the `email`-field-removal rule before any public push). This review is filed under `docs/security/` not in the plugin distribution.

## Provenance

This artifact was generated by the security-reviewer seat of the 4-seat panel that reviewed the gap-closure PR plan (`/home/codespace/.claude/plans/cozy-foraging-snowglobe.md`). Findings #1-#6 are the panel's full list; the PR body's "Security-relevant changes" section enumerates the consumer-visible subset.
