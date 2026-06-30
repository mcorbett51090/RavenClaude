# FORGE plan — Generalize BTCSI pac-import flow-activation hardening into `power-platform`

**Slug:** pac-solution-import-hardening · **Depth:** standard · **Models:** A=opus, B=sonnet
**Date:** 2026-06-30 · **Owner:** Matt

## 1. What we're building (one paragraph)

A new **`managed-solution-import` skill** in the power-platform plugin that ships a **single generalized
Python file** (`managed_import.py`, underscore so it's importable) **co-located inside the skill dir**
(matching the existing `dataverse-payload-preflight/preflight.py` precedent — NOT a new top-level
`scripts/` surface, which both panels wrongly assumed). The script's **spine is the flow
reactivation + verify pass over the Dataverse Web API** — the genuinely novel, hard-to-get-right part
that nobody else does — fully usable standalone (no `pac` needed); the `pac solution import`
orchestration (`import` subcommand) is an **optional convenience** that composes preflight → baseline →
import → poll → reactivate → verify. Every BTCSI hardcode (env URLs, settings paths, timezone,
impersonation OID) is externalized to a committable, secret-free JSON config; secrets stay in env vars.
Shipped alongside: a knowledge doc, one best-practice (house-opinion), one dated scenario, compact agent
priors, bash-wrapped pure-logic tests, and the full CI-hygiene set — gated by a **mandatory
security-reviewer sign-off** (CLAUDE.md mandates it for SPN-secret-handling code).

## 2. Fact-grounded design corrections (from G1 — Microsoft Learn, 2026-06-30)

- `--activate-plugins` + `--settings-file` are the **default** flags. `--publish-changes` and
  `--force-overwrite` are **opt-in only** — Microsoft's performance guidance discourages both for
  managed imports. (Diverging from BTCSI's blanket usage is the correct generalization.)
- "Import drops flows to Draft" is **conditional**: the platform auto-reactivates only when flows were
  exported-on AND connection references are bound AND the importing identity has permission to the
  connections. **SPN-driven CI/CD frequently fails these → the explicit reactivation pass is precisely
  when it earns its keep.** For updates to existing flows, import preserves current target state
  (validates baseline-aware targeting). Supported API = Dataverse Web API (not `api.flow.microsoft.com`).

## 3. Phased plan + dependency DAG

```
Phase 0 (design-lock, light) ──► Phase 1 (script: pure core + I/O seam) ──► Phase 2 (security + tests) ──► Phase 4 (CI hygiene + PR)
        │                                                                          ▲
        └──► Phase 3 (docs quartet + agent priors, parallel off the schema lock) ──┘
```
Critical path: **Phase 0 → Phase 1 → Phase 2(security) → Phase 4.** Phase 3 parallelizes off the
Phase-0 schema/exit-code lock. Phase 4 skill-count bump needs Phase 3's skill to exist.

### Phase 0 — Design-lock (light; no heavyweight design-time threat gate — T8)
Freeze three contracts as the build's spine, then build: (a) the **config-file JSON schema**
(externalizes env URLs / settings-file paths / timezone / optional impersonation OID; loader rejects
secret-shaped values); (b) the **canonical exit-code table** (T7): `0` success / `2` usage-config /
`10` partial / `20` all-reactivation-failed / `40` auth / `50` pac-import-failed / `60` prod-guard /
`70` preflight-failed; (c) the **security-controls checklist** (the FM4/FM5/FM6 items below).
*Acceptance:* the three contracts written into SKILL.md draft tables; no code yet.

### Phase 1 — `managed_import.py` (pure-logic core + injected-I/O seam — T1, FM1)
File: `plugins/power-platform/skills/managed-solution-import/managed_import.py`. Single file, factored so
**pure functions** (config load/validate, prodguard verdict, exit-code mapping, pac-argv builder,
baseline-intersect set math, retry/backoff schedule, statecode parse) carry no network/subprocess
imports, and **I/O edges** (auth, Dataverse transport, subprocess) are injected so the pipeline is
testable with fakes. Subcommands: `import | preflight | baseline | reactivate | verify` — **reactivation
+ verify is the spine, standalone, pac-free** (CE-1/T15).
- **Auth (T9):** mirror `knowledge/dataverse-token-acquisition.md`'s 4-path ladder; client-credentials
  primary via **stdlib `urllib`** (zero deps on the hot path); `msal` lazy/optional for dev fallback.
- **pac flags:** `--activate-plugins`+`--settings-file` default ON; `--publish-changes`/`--force-overwrite`
  opt-in (G1). pac invoked as an **argv list, never `shell=True`**.
- **Reactivation (FM6 — BINDING):** baseline-aware (only flows Active pre-import); **reconcile baseline
  by a STABLE key (`uniquename`/category+name), not `workflowid`** (managed import can recreate the row
  with a new GUID); PATCH **both `statecode==1` AND `statuscode==2`**; **re-query and assert both** before
  counting activated (a 204 ≠ activated); degrade to an actionable warning otherwise.
- **403 handling (CE-4/T14):** distinguish transient-propagation (retry w/ backoff) from durable
  missing-permission (retry never fixes — emit the G1 remediation: "share the connection with / bind the
  connection reference for the importing identity").
- **poll-until-ready (T12/FM6):** enumerate ALL terminal async statuscodes (Succeeded/Failed/Canceled)
  with a **hard timeout + bounded attempts** — never spin forever; non-success → exit 50/10.
- **Security controls:**
  - **SSRF (FM4 — BINDING):** anchored host regex `^[a-z0-9-]+\.crm[0-9]*\.dynamics\.com$` **enumerating
    sovereign-cloud suffixes** (e.g. `*.crm.microsoftdynamics.us` GCC-High) so it neither passes
    `evil-dynamics.com` nor false-rejects sovereign clouds; **https-only**; a custom `HTTPRedirectHandler`
    that **refuses cross-host redirects / strips `Authorization` and re-validates host every hop** (urllib
    otherwise re-attaches the bearer token to a redirect target → token exfil). Validate host BEFORE any
    token attach AND on every redirect hop.
  - **Secret redaction (FM5):** a top-level `sys.excepthook` scrubs a module token register on ALL paths;
    never interpolate raw exception objects (extract `.code`/`.reason`); secrets env-only, never logged,
    never written to the baseline JSON. pac-auth secret: create the `pac auth` profile out-of-band OR
    verify pac's env/file secret-input at build time + document if argv is unavoidable.
  - **Impersonation (CE-5/T10):** OFF by default, GUID-validated, gated behind an explicit flag,
    documented `prvActOnBehalfOfAnotherUser` prerequisite + "runs under the impersonated user's
    connections" caveat.
  - **Path-traversal (T13/FM8):** resolve file args within cwd; out-of-cwd via an explicit absolute-path
    allowlist, NOT a blanket documented-default flag.
  - **Operator traps (FM7):** pre-flight `pac`-on-PATH → clean exit 2 (not a traceback); evaluate
    `--approved` BEFORE tz parsing can hard-fail; `pip install tzdata` documented; config loader echoes
    resolved host + a typed DEV/PROD label and requires `--approved` for any PROD-classified host.
- `--dry-run` executes nothing; prints prod-guard verdict, resolved pac argv, the reactivation plan, and
  decoded token claims (never the token).
*Acceptance:* `ruff check` clean; `python3 -m py_compile` clean; `--help`/`--dry-run` run without a tenant.

### Phase 2 — Security review (mandatory) + tests
- **`ravenclaude-core/security-reviewer`** on the script — sign-off MUST explicitly clear **FM4
  (redirect/token-leak) and FM6 (false-green)** plus shell/secret/SSRF/impersonation. Hard gate (CLAUDE.md).
- **Tests (T11/FM1):** `plugins/power-platform/hooks/tests/test-managed-import.sh` — bash wrapper →
  python heredoc that subprocesses the CLI / `spec_from_file_location`-loads `managed_import.py`; asserts
  exit-code mapping, prod-guard boundaries (08:59/09:00/17:00/17:01, weekend, `--approved`, non-prod
  never blocked, fail-closed on bad tz), SSRF accept/reject incl. `evil-dynamics.com` + a sovereign-cloud
  host + a cross-host redirect, GUID validation, **baseline-by-stable-key + statecode&&statuscode assert
  (the FM6 bidirectional fixture)**. Mirror the `test-preflight.sh` must-fail/must-pass mutant pattern;
  register in `audit-gates.sh`.

### Phase 3 — Docs quartet + agent priors (parallel off Phase-0 lock)
- `skills/managed-solution-import/SKILL.md` (SKILL.md only, no resources/ — T3): playbook + the
  conditional-reactivation decision tree (the G1 conditions) + exit-code & flag tables inline +
  CI-pipeline snippet; **stands alone / stays correct if the script ages**; carries a "verified against
  pac <version> / Dataverse Web API v9.2 on 2026-06-30; re-verify on pac upgrades" compatibility note
  (premise mitigation). **Quote the `description:` defensively.**
- `knowledge/managed-import-flow-reactivation.md` (NEW file — T4): the conditional auto-reactivation
  mechanics; `statecode`/`statuscode`/`category=5` enum marked **`[unverified — training knowledge]`**
  with the settling route (live `workflow` EntityDefinitions / Web API query); baseline-intersect
  algorithm; the two-cause 403 model; reciprocal cross-links to `dataverse-token-acquisition.md`,
  `programmatic-flow-creation.md`, `flow-decision-trees.md`.
- `best-practices/alm-reactivate-flows-after-managed-import.md` (ONE — T5): the house-opinion rule,
  folding the publish/force-overwrite flag-economy correction; cross-links (no duplication) to
  `alm-fresh-import-smoke-test-before-release.md`, `alm-connection-references-not-hardcoded-connections.md`.
  No new hook → no new house-opinions fixture (precedent: alm-fresh-import-smoke-test ships hookless).
- `scenarios/2026-06-30-managed-import-flows-deactivated.md`: the BTCSI war-story, **zero customer
  specifics** ("the customer environment", no URLs/OIDs/org names).
- Compact priors (in BODY, not description) on `flow-engineer`, `solution-alm-engineer`,
  `power-platform-admin` (T6) — **reference the skill, not script flags** (B GAP-12).
*Acceptance:* `check-frontmatter.py` passes on the 3 edited agents (descriptions ≤300 chars, untouched);
all cross-links resolve; new YAML validates with the generator's loader (FM3).

### Phase 4 — CI hygiene + PR
- plugin.json `"22 skills"→"23 skills"`; version `0.43.0→0.44.0` in **plugin.json AND marketplace.json**
  (Gate 12 checks plugin.json counts + the version sync). **LEAVE marketplace.json's "46 skills"
  boilerplate alone** (FM2 — ungated shared boilerplate; not this PR's job).
- Regen `dashboard.html`, `repo-guide.html`, Copilot package (FM3). `ruff check .`, `prettier --write . &&
  prettier --check .`, `python3 -m json.tool` on touched JSON, `bash -n` hooks, layout snippet,
  `scripts/audit-gates.sh` — all local, pre-push (FM8).
- PR via **GitHub MCP** (`mcp__github__create_pull_request`, load via ToolSearch first) on branch
  `feat/power-platform-managed-import-flow-reactivation`; confirm a CI run exists for the **current head
  SHA** (remote-CI runbook); **surface green to Matt — do NOT auto-merge** (his solo-dev preference);
  post-PR decision-review retrospective as a comment.

## 4. Risk matrix (critic + red-team, consolidated)

| Risk | Prob | Impact | Mitigation (gate) |
|------|------|--------|-------------------|
| Reactivation false-green (204≠active; baseline-by-GUID misses recreated flows) | Med | **High** | FM6 BINDING: assert statecode&&statuscode + stable-key baseline + bounded poll; bidirectional fixture |
| SSRF redirect token-exfil | Low-Med | **High** | FM4 BINDING: redirect handler + anchored multi-cloud regex + https-only; reviewer must-check |
| Secret leak via traceback / pac argv | Low | High | FM5: sys.excepthook scrub + out-of-band pac auth; security-reviewer gate |
| Impersonation knob abused / flagged in consumer review | Low | High | CE-5: off-by-default, gated, documented, reviewer-assessed |
| Activation mechanism differs in a consumer tenant | Med | High | CE-3: post-PATCH verify + degrade-to-warning + `[unverified]` doc + version-compat note |
| 403 misdiagnosis → wrong fix | High | Med | CE-4: two-cause split + G1 remediation message |
| Script ages vs pac flag surface (silent staleness) | Med | Med | Premise: standalone docs + compatibility note + co-location |
| Manifest "46" mis-"fixed" → breaks/widens drift | Low | Med | FM2: bump plugin.json only; leave boilerplate |
| Generator crashes on malformed new YAML | Low | Med | FM3: validate with generator loader; quote description |
| Operator copy-paste traps (no pac / no tzdata / wrong env) | Med | Med | FM7: pac pre-check + approved-before-tz + DEV/PROD label |

## 5. Alternatives considered
1. **Generalized monolith (BTCSI shape, externalized config)** — most portable single file, but I/O woven
   through logic = near-untestable. *Rejected*; recovered the portability via single-file + injected seam.
2. **Pip-installable package (pyproject + entry points)** — most product-grade, but convention drift (no
   other plugin packages). *Deferred.*
3. **Two scripts (orchestrator + standalone reactivate)** — clearer standalone naming, double the
   maintenance/test surface. *Rejected* — `managed_import.py reactivate` serves it at lower cost.
4. **Docs-only, no shipped script** — lowest maintenance; **Matt explicitly chose the shipped script**.
   Retained only as the survivable fallback if the script ages out (SKILL.md stands alone).
5. **PowerShell port** (ADO-native) — forks the Python auth story. *Future companion, not this deliverable.*

## 6. Definition of Done
- [ ] `managed_import.py` (underscore) co-located in the skill dir; pure core has no net/subprocess imports; stdlib-only hot path; msal lazy/optional.
- [ ] **FM4 BINDING:** anchored multi-cloud SSRF regex + https-only + cross-host-redirect refusal/auth-strip + per-hop revalidation.
- [ ] **FM6 BINDING:** baseline reconciled by stable key; PATCH+assert `statecode==1 && statuscode==2`; bounded poll over all terminal async statuscodes.
- [ ] 403 two-cause split with G1 remediation; impersonation off-by-default+gated; path-traversal allowlist; secret excepthook scrub; `--dry-run` leaks no token.
- [ ] pac flags: activate-plugins+settings-file default; publish-changes/force-overwrite opt-in.
- [ ] Operator traps handled (pac pre-check exit 2; approved-before-tz; DEV/PROD label; tzdata documented).
- [ ] `hooks/tests/test-managed-import.sh` (test-preflight.sh shape) covering exit codes, prod-guard boundaries, SSRF (+evil/sovereign/redirect), GUID, **FM6 bidirectional fixture**; registered in audit-gates.sh; `ruff check .` exit 0.
- [ ] `ravenclaude-core/security-reviewer` sign-off recorded, explicitly clearing FM4 + FM6; secret-scan clean; fixtures use placeholders only.
- [ ] SKILL.md (no resources/, description quoted, compatibility note) + NEW knowledge doc (`[unverified]` enum + settling route) + ONE best-practice + ONE sanitized scenario + priors on 3 agents (body, descriptions ≤300, reference skill).
- [ ] plugin.json 22→23 skills + 0.43.0→0.44.0; marketplace.json version 0.44.0 (LEAVE "46 skills"); dashboard/repo-guide/Copilot regenerated; prettier+ruff+json.tool+layout+audit-gates green.
- [ ] PR via GitHub MCP on `feat/power-platform-managed-import-flow-reactivation`; CI run confirmed for current head SHA; green surfaced to Matt (NOT auto-merged); decision-review retro posted.

## 7. Unverified claims carried forward (settling steps)
- `statecode=1`/`statuscode=2`/`category=5` enum — `[unverified — training knowledge]`; settle by a live
  `workflow` EntityDefinitions / Web API query in a real org before trusting a 204; doc carries the marker.
- 403 ConnectionAuthorizationFailed transient-vs-durable boundary — `[unverified — BTCSI-empirical + G1-consistent]`;
  settle by reproducing both causes in a target env; the two-cause handler degrades safely either way.
- pac secret-input (env/file vs argv) on the target pac version — verify at build time; accept-risk+document if argv-only.
