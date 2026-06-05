# Tactical build plan — Plugin bundling expansion

**Companion to:** `docs/plan/plugin-bundling-options.md` (strategic what/why)
**Branch:** `claude/plugin-bundling-options-QCDnG`
**Date:** 2026-06-05
**Status:** tactical (how) — pre-Panel-2

## Guiding decisions (from the updated strategic plan + Panel 1)

1. **Pilot order = risk-adjusted, not leverage-ranked:** Tier D → `userConfig` →
   one referenced read-only MCP server. 1–2 plugins, never fleet-wide.
2. **Install stays side-effect-free.** No auto-starting backend server or background
   process on enable. Always-on = opt-in via `userConfig`.
3. **Codify the existing power-platform MCP doctrine** as a marketplace rule + CI gate
   rather than inventing a new one.
4. **CI tests only hermetic properties.** Live-backend behavior is manual/integration.
5. **Secrets = references, never literals.** ✅ **RESOLVED (Panel 2, doc-cited):**
   `sensitive:true` does **NOT** keep a value out of subprocess env — per
   `code.claude.com/docs/en/plugins-reference` §"User configuration", *all* values are
   exported to `CLAUDE_PLUGIN_OPTION_<KEY>`; `sensitive:true` only (a) masks the
   enable-prompt input and (b) stores at rest in the system keychain (vs `settings.json`).
   So the enforceable property is **"bundle a reference (Key Vault URI / `op://` / env-var
   *name*), never a literal — server dereferences at runtime"**, NOT "keep sensitive out of
   `CLAUDE_PLUGIN_OPTION_*`" (that's impossible). T2.2's gate must enforce the former.

## Workstreams & tasks

### WS0 — Foundations (must land before any pilot PR)

- **T0.1 Layout allow-list.** Add to `.repo-layout.json` `allowed_globs` the literal
  entries the later tiers need, in the *first* pilot PR (PR #32 lesson):
  `plugins/*/.mcp.json`, `plugins/*/.lsp.json`, `plugins/*/monitors/**`,
  `plugins/*/output-styles/**`, `plugins/*/bin/**`, plus any new `schemas/*.json`.
  Verify with the AGENTS.md layout-discipline snippet before push.
- **T0.2 Schemas.** Add JSON Schemas under `schemas/` for `.mcp.json`, `userConfig`
  blocks in `plugin.json`, and (later) `monitors.json` / `.lsp.json`. Wire into
  `validate-schemas.yml`.
- **T0.3 Gate-audit fixtures.** For every new gate below, author the **bad+good fixture
  pair** in `scripts/audit-gates.sh` (non-negotiable per `docs/best-practices/ci-gate-audit.md`).
- **T0.4 Verify the unverified.** Three this-session doc checks against
  `code.claude.com/docs/en/plugins-reference` before the dependent task ships:
  (a) `userConfig sensitive:true` on-disk persistence + transcript flow;
  (b) `bin/` PATH-injection-on-enable behavior;
  (c) `settings.json` `agent` main-thread-vs-subagent write-authority semantics.
  Record results inline in the strategic plan, replacing the `[unverified]` markers.

### WS1 — Tier D pilot (richer bundled files) — *lowest risk, ship first*

- **T1.1** Pick **1 plugin** with an existing data-file pattern (candidate:
  `applied-statistics` or `analytics-engineering` — both already have `knowledge/` +
  skills). Add a structured **lookup/fixtures** asset (JSON data + a JSON Schema it
  validates against), mirroring `ravenclaude-core/concepts.json`.
- **T1.2** Add a CI gate: every shipped `*.json` data file that declares `$schema`
  validates against it (extend `validate-schemas.yml`). Bad+good fixtures (T0.3).
- **T1.3** Reference the new asset from ≥1 agent/skill so it's demonstrably *used*,
  not vanity (devil's-advocate filter).
- **T1.4** Semver bump in `plugin.json` **and** `marketplace.json`; prettier-write;
  gate-audit; layout-check. Open PR.

### WS2 — `userConfig` pilot — *secret-safe config, no runtime yet*

- **T2.1** On the same pilot plugin (or power-platform, which already has MCP), add a
  `userConfig` block declaring **non-secret** config first (e.g. an endpoint/region).
- **T2.2** Add the secrets rule + CI gate: a `${user_config.<key>}` marked
  `sensitive:true` must **not** be interpolated into a command-line, an `env` export, or
  a `CLAUDE_PLUGIN_OPTION_*` position — only into a runtime-dereferenced reference field.
  Grep-gate with bad+good fixtures.
- **T2.3** Add a "no literal secrets bundled" gate (extend the email-leak guard in
  `validate-marketplace.yml`). Bad+good fixtures.
- **T2.4** Document the config in the plugin README ("Configuration" section) — the
  devil's-advocate baseline (docs-first) is satisfied even if `userConfig` is thin.

### WS3 — One referenced read-only MCP server — *gated, demand-pulled*

- **T3.1 Demand gate.** ✅ **Resolved (maintainer decision, 2026-06-05): a maintainer-logged
  request is sufficient** in this private single-maintainer marketplace. Proceed when the
  maintainer records, in the WS3 ADR, a dated one-line rationale naming the *specific plugin +
  the concrete agent task* the tools enable (e.g. "power-platform: let an agent evaluate DAX
  against a .pbix live, not just describe the API"). This is intentionally self-attested — the
  guard against feature-FOMO is the *named concrete task* (vanity if you can't name one), not an
  external party. WS3/WS4 stay in scope. (Supersedes R-PM1's external-issue recommendation.)
- **T3.2 Resolve Gate-25 interaction (ADR).** Decide: does a bundled server auto-add to
  `mcp.allowed_servers`, and if so does it bypass the write-deny? **Default stance:
  bundled servers are still subject to the allowlist; ship read-only verbs so the
  write-deny never triggers.** Write `docs/adr/bundled-mcp-and-gate25.md`.
- **T3.3** Codify the precedent as a rule + gate: any `mcpServers` entry whose `command`
  is **third-party** must have a NOTICE/attribution file and a documented
  loud-but-non-fatal degrade path (the pbix-mcp pattern). CI gate with bad+good fixtures.
- **T3.4** Add the server **referenced** (pinned + checksum where the runtime allows),
  **read-only**. ✅ **Corrected (Panel 2, doc-cited):** bundled user-scope MCP servers
  **auto-start on enable** — "declared-but-dormant / no auto-start" is impossible at user
  scope. The real lever is **`"defaultEnabled": false`** in `plugin.json` (requires
  CC ≥ 2.1.154): the plugin installs *disabled*, so **install** is side-effect-free and
  *enabling* is the explicit opt-in that starts the server. Document the `/mcp` + `/plugin`
  Errors-tab check on failure (power-platform §9). Declare least-privilege scopes in
  `plugin.json` + README. **Also add the §9-shaped agent doctrine block** (see R-PE1 below)
  so agents actually reach for the tool.
- **T3.5** Migration note (House Rule #3): a new backend-reaching server materially
  changes a consumer's attack surface on `/plugin marketplace update`.

### WS4 — Domain-neutral core MCP server (read-only reporting) — *optional, after WS1–3*

- **T4.1** First-party server (bundle code) exposing **read-only** tools only:
  `knowledge-health`, layout-check, version-drift (Heimdall/Níðhöggr signals).
- **T4.2** **Explicitly exclude** any tool that mutates posture or invokes the tribunal
  (`thing-decide`) — deferred until the self-disable/self-tamper interaction is designed.
- **T4.3** If server code ships, add `pip-audit`/`npm audit` + lockfile-presence to
  `audit-gates.sh` before merge (first runtime deps in the repo).

### WS5 — Deferred / likely-cut (record decision, don't build)

LSP servers, monitors, output styles, `settings.json` auto-activation defaults, and
themes are **not built in this effort**. Monitors and `settings.json` defaults, if ever
revisited, are off-by-default opt-in and CI-forbidden from touching `permissions.*` /
making uncontained network egress. `bin/` is demoted pending T0.4(b) and the
live-clone-model conflict; prefer Bash-tool skills.

## Sequencing & gates

```
WS0 (foundations) ──► WS1 (Tier D) ──► WS2 (userConfig) ──► WS3 (1 referenced MCP, demand-gated)
                                                                   └─► WS4 (core read-only MCP, optional)
```

Each WS is its own PR. No WS starts until its predecessor has survived a real
`/plugin marketplace update` simulation and CI is green (layout + prettier-whole-tree +
gate-audit + version-drift cross-check).

## Definition of done (per PR)

- New dirs/files in `.repo-layout.json` `allowed_globs` (verified with the snippet).
- New component types declared in `plugin.json` + explained in the plugin's CLAUDE.md.
- Semver bumped in `plugin.json` **and** `marketplace.json` (no drift).
- Every new CI gate has a bad+good fixture pair in `audit-gates.sh`.
- `prettier --check .` exits 0; `scripts/audit-gates.sh` passes.
- Migration note added if a consumer's project could change on update.
- The new asset is *referenced by ≥1 agent/skill* (anti-vanity check).

## Risks & mitigations

| Risk | Mitigation |
|---|---|
| Maintenance treadmill (64 plugins × component churn, single maintainer) | Pilot 1–2 plugins; reference (don't vendor) third-party servers; cut LSP/monitors/styles |
| Bundled MCP defeats Gate-25 perimeter | T3.2 ADR; read-only verbs; bundled ≠ exempt from allowlist |
| Secret leakage via `userConfig`/env/transcripts | References not literals; T0.4(a) verify; grep-gates; scrub-path review |
| Install side-effects break consumer envs | Side-effect-free invariant; declared-but-dormant; migration notes |
| Supply chain (vendored deps / hijacked external) | Pin + checksum; `pip-audit`/`npm audit` gate before first runtime dep |
| Feature-FOMO over real demand | T3.1 demand gate; anti-vanity DoD; Tier-D-first bias |

---

# Appendix — P0/P1 Recommendations (Panel 2 cold-review synthesis)

Four fresh lenses (tester-QA, project-manager, deep-researcher, prompt-engineer) cold-reviewed
this build plan. The deep-researcher verified the load-bearing capability claims against the
official docs; two were **refuted** and are corrected inline above (guiding decision #5, T3.4).
The remaining must-fix items, in priority order:

## P0 — fix before any pilot PR

- **R-DR1 (deep-researcher) — `sensitive:true` ≠ secret-out-of-env. [REFUTED, corrected].**
  Already folded into guiding decision #5 + T2.2. The gate enforces *reference-not-literal*,
  not "absent from `CLAUDE_PLUGIN_OPTION_*`." Replace the `[unverified]` markers in
  `plugin-bundling-options.md` §5/Q5 with this resolution.

- **R-PE1 (prompt-engineer) — Re-anchor Tier D off `concepts.json`; it has NO runtime agent
  consumption path** (grep confirms only build scripts read it — it feeds the dashboard
  generator). Mirroring it produces a validated-but-unread file — the exact vanity failure.
  **Re-anchor T1.1 on the `scenario-retrieval` pattern**: the asset is reached by an explicit
  retrieval step an agent is told (inline prior) to perform. Agents consume **markdown**, not
  raw JSON, as reasoning input — a JSON lookup needs a markdown "how to consult me" wrapper
  (sibling SKILL.md describing glob/read/filter) + an inline prior on the consuming agent.

- **R-QA1 (tester-QA) — Bad fixtures must be synthesized at runtime into `$TMP`, never
  committed.** CI runs `prettier --check .` whole-tree, so a committed malformed-JSON or
  secret-shaped fixture breaks the tree-wide gate for *every* PR. Follow Gate 25/26's existing
  `$TMP`-fixture pattern. Make this an explicit T0.3 constraint governing all downstream gates.

- **R-QA2 (tester-QA) — Gate the real format: `mcpServers` in `plugin.json`, not `.mcp.json`.**
  Zero `.mcp.json` files exist; the shipping precedent (power-platform) and `plugin.json` schema
  are the reality. Add an `mcpServers` definition to `schemas/plugin.schema.json` (currently
  `additionalProperties:true`, so malformed server blocks pass today). The NOTICE gate's "good"
  fixture **must be power-platform's real `plugin.json`** — if it can't pass on the precedent it
  claims to codify, it's testing the wrong thing.

- **R-PM1 (project-manager) — The demand gate (T3.1) is self-attested.** ✅ **Resolved by
  maintainer decision (2026-06-05): a maintainer-logged request is accepted as the signal**
  (this is a private single-maintainer marketplace; an external-issue gate would never trigger).
  WS3/WS4 stay in scope. The anti-FOMO discipline is preserved differently: the ADR must name
  the **specific plugin + concrete agent task** the tools enable — if no concrete task can be
  named, that *is* the FOMO signal to stop. (See updated T3.1.)

- **R-PM2 (project-manager) — Add a hard stop-and-reassess off-ramp after WS2.** Declare
  **WS1 + WS2 the shippable v1**; WS3/WS4 are separately greenlit v2. Default after WS2 = STOP
  unless the R-PM1 external signal exists. This honors the recorded devil's-advocate dissent
  (Tier-D-only) instead of conveyor-belting past it.

## P1 — fix during the relevant workstream

- **R-PE2 — Upgrade the anti-vanity DoD from "referenced" to a 3-part test:** (1) named
  **trigger** (the request signal), (2) named **retrieval/invocation mechanism** (concrete
  Glob/Read/validator/tool call), (3) a **worked example** showing the asset changing the answer.
  "Referenced by ≥1 agent/skill" is a static-grep property satisfied by one bullet-list mention;
  borrow the shape from `scenario-retrieval/SKILL.md`.

- **R-PE3 — Every bundled MCP server needs a `power-platform/CLAUDE.md` §9-shaped doctrine
  block** (capability summary, which agents reach for it, trigger conditions, the boundary of
  what it is NOT, the `/mcp`+Errors-tab failure path). Read-only verbs control blast radius;
  this controls whether the tool is *used at all*. Make it a DoD line for any MCP PR. (Folded
  into T3.4.)

- **R-PE4 — Own the discovery surface per tier.** New assets plug into none of the existing
  discovery mechanisms (SessionStart capability banner, Team-Lead routing tree). Decide per tier
  how an agent *learns the asset exists*; confirm whether the capability banner enumerates a
  declared bundled MCP server, or add it.

- **R-QA3 — NOTICE/secret gates are heuristic; anchor them declaratively.** "Is third-party" is
  not mechanically decidable (`python` launches both first- and third-party). Require every
  `mcpServers` entry to carry an explicit `x-attribution` field (`"first-party"` or a NOTICE
  path); gate on presence + resolvability. Rename the secret gate a **tripwire, not a proof** in
  `ci-gate-audit.md`; pair it with the decidable reference-not-literal structural gate (T2.2).

- **R-QA4 — Add three cheap hermetic correctness gates the DoD misses:** (a) every
  `${user_config.K}` placeholder resolves to a *declared* key (typo catch); (b) every
  server/reference entry has required pin/checksum/attribution fields present + well-formed
  (note: the pbix-mcp precedent has no pin/checksum — decide whether to backfill or scope the
  gate); (c) each schema ships a **"too-loose tripwire" fixture** — a plausible-but-invalid
  instance that MUST be rejected — proving the schema actually constrains.

- **R-QA5 — "Live-backend = manual" needs a written checklist, or it's undefined not deferred.**
  Commit a manual test checklist under `docs/` for WS2/WS3: (1) install → no backend process
  started (`defaultEnabled:false` / side-effect-free); (2) enable with a `sensitive:true` value →
  literal absent from disk/transcript (this *is* the now-resolved R-DR1 — make it a repeatable
  procedure); (3) absent backend → loud-but-non-fatal degrade; (4) Gate-25: bundled server's
  write verb still DENIED when not allowlisted.

- **R-QA6 / R-DR2 — Lock the Gate-25 decision with a fixture, not just the ADR.** Extend Gate 25
  in the same PR as T3.2/T3.4: prove (1) a *bundled* server name not in `allowed_servers` still
  pre-denies a write verb, and (2) install/enable does not mutate `allowed_servers`. Both hermetic.

- **R-DR3 — `bin/`→PATH is CONFIRMED, not unverified** (docs: "invokable as bare commands…while
  the plugin is enabled"). Remove the `[unverified]` on T0.4(b)/strategic line 43. Nuance: `bin/`
  commands run *via the Bash tool*, so PreToolUse Bash guards **do** see the command string — the
  real residual risk is **name shadowing** (mitigated by the `rc-*` namespacing rule), softening
  the "bypasses all guards" framing. The demotion still stands on the live-clone-model conflict.

- **R-DR4 — `monitors`/`themes` are under the `experimental.*` manifest key** (not bare keys) and
  `monitors` requires CC ≥ 2.1.105 + runs unsandboxed; `settings.json` is hard-capped to `agent`
  + `subagentStatusLine` (so a plugin *cannot* set `permissions.*` — bounds the WS5 blast radius).
  Drop the invented "main-thread-vs-subagent write-authority" sub-question from T0.4(c); it has no
  docs referent. If WS5 is ever revisited, add `plugins/*/settings.json` to the allow-list first.

- **R-PM3 — Tighten WS0 scope + parallelize.** Don't pre-add allow-list globs for deferred/cut
  tiers (`bin/`, `monitors/`, `output-styles/`, `.lsp.json`) — that's dead config for assets no
  gate validates. Scope T0.1 to what WS1/WS2 touch. Split WS0: **T0.4 doc-verification starts
  now, in parallel** (it gates nothing upstream); T0.1–T0.3 gate WS1.

- **R-PM4 — Move WS4 out of this plan.** First-party server code = first runtime deps + lockfiles
  + `pip/npm audit` = a maintenance *category change* for a one-person repo, parked at the end
  where under-resourced plans never reach. Make it a separate, independently-greenlit proposal.
  Committed scope here = **WS0–WS2 (+WS3 only on the R-PM1 signal).**

- **R-PM5 — Make soft DoD items mechanical:** anti-vanity = grep that fails if the only hit is a
  comment; read-only = an allow-list of permitted verbs in the schema, gate-checked; T0.4 = explicit
  branch logic ("if check (a) contradicts the assumption, the dependent task is blocked / falls back").

## Net verdict

The plan's guardrail engineering (schemas, fixtures, read-only verbs, side-effect-free *install*,
migration notes, risk-ascending order) is sound and should ship. The two systemic gaps:
**(1) consumption** — it treats "validates + a file names it" as the finish line when the
marketplace's own evidence (scenario-retrieval, the §9 MCP doctrine) shows the finish line is
"an agent is told it exists, when to reach for it, and how — with a worked example"; and
**(2) realism** — the demand gate isn't falsifiable, there's no off-ramp, and WS4 is a
category-change that doesn't belong. Adopt v1 = **Tier D (re-anchored on scenario-retrieval) +
userConfig (reference-not-literal)**, behind a hard post-WS2 reassessment, and the plan is
deliverable by a single maintainer without diluting the marketplace's curation moat.
