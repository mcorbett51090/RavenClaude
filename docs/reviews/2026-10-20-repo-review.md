# Repo review — 2026-10-20 (autonomous scheduled routine)

An unattended review of the RavenClaude marketplace, run against `main` at `6f11a68`. It found one P0, which was live on the day of the run. Every PR's CI had just started failing because six concept entries passed their 90-day verification window. That fix is the first commit of PR #1389. Three panels found and triaged 153 further findings. The implementable ones are fixed in the same PR, grouped by priority below. Everything that needs your decision is written up with a recommendation.

## Scope: why this run is not another full sweep

Yesterday's run left draft PR #1387 open. It touches 214 files and fixes 141 findings across the tribunal, core hooks, core scripts, the dashboard servers, root scripts and 13 domain plugins. Re-sweeping that code would duplicate its findings and conflict with its diff. So this run reviewed only the 920 executable files #1387 does not touch, de-duplicated every finding against #1387's 226-item list, and planned no edits to any file #1387 changes. Each slice was risk-ranked:

| Slice | Files | Focus |
|---|---|---|
| A | 54 | finance, team-portfolio, generative-web-media, web-design scripts |
| B | 44 | report-regeneration pipeline, Power Platform hooks and skills |
| C | 88 | ravenclaude-core skills, `bin/`, monitors, VS Code extension, templates |
| D | 175 | root `scripts/` not in #1387, `.claude/workflows`, `.github`, plus a date-bomb hunt |
| E | 71 | data-platform and web-commerce templates, which consumers copy into their own projects |
| FG | 130 | ravenclaude-core hooks and scripts not in #1387, focused on the last week's commits |
| H | 193 | about 60 domain plugins' calculators and anti-pattern hooks |

## Method and model assignment

- **Objective layer, run first by the orchestrator.** `ci-preflight.py`, `ruff`, `prettier@3.9.4` and the full `audit-gates.sh`. This is where the P0 surfaced.
- **Panel 1 (find): seven Sonnet reviewers**, one per slice. Each P0/P1 needed a reproduction run on a copy.
- **Panel 2 (validate): Sonnet.** It re-reproduced all 14 P1s independently (14/14 reproduced) and re-verified 58 more findings. It refuted none, moved 4 P1s down and 5 findings up, merged duplicates, and flagged 13 ambiguous items.
- **Panel 3 (tie-break and disposition): Opus.** It ruled on every ambiguous item and gave every finding a final disposition: `implement`, `design`, `owner-route` or `defer`. It split the 108 `implement` findings into six packages with no shared files.
- **Implementation: six package agents in isolated worktrees.** Opus took the security-sensitive and core packages; Sonnet took the bounded ones. Each one reproduced every finding first, made one commit per finding, and added a regression test proven by reverting the fix.
- **Re-verification of the P0: Sonnet.** It re-fetched every `sources:` URL of the ten concepts. The orchestrator spot-checked the surprising claims against the raw pages.

## P0: the platform-fact time bomb (fixed, commit `6eb60794`)

`scripts/concepts.py` blocks any `kind: platform-fact` concept whose `last_verified` is older than 90 days, by design: the population is small and is kept current by re-verification. On 2026-10-20 six concepts stamped 2026-07-21 crossed that line. `concepts.py --check` failed, and so did the real-corpus rows of Gates 237 and 239, which run on every PR. `main` was green at 2026-10-19 15:43 UTC; only the calendar changed. Four more concepts, stamped 2026-07-28, would have failed the same way on 2026-10-27.

All ten were re-verified against their live sources and corrected where the vendor docs had moved: Cloudflare's Worker size limit and `nodejs_compat` default, WAF Free-plan availability, the R2 price ratio, Google's sensitive-scope review time, Claude Code's `onFailure: "block"`, the `//path` absolute-path syntax, `auto` mode no longer being a preview, and SessionStart delaying the first response. Only the two changed diagrams were re-rendered.

**Overlap with #1392.** While this run was in progress, #1392 merged to `main` with its own re-verification of six of the same concepts (the four Cloudflare ones, `oauth-scope-cost` and `subscription-billing-model`). The two passes agreed on every substantive correction. When `main` was merged into this branch, the four conflicted Cloudflare files took `main`'s text with one exception: `main` says R2 writes cost "12×" what reads cost, but the prices in the same sentence ($4.50 / $0.36) give 12.5×, so this branch keeps 12.5×. The other four re-verified concepts (`hook-lifecycle`, `permission-layers`, `permission-modes`, `session-start-context`) appear only in this PR.

**The next wave lands on 2026-11-23:** seven Foundations concepts stamped 2026-08-24 (`agent-harness-loop`, `context-window`, `mcp`, `model-selection`, `source-control-basics`, `subagents`, `tool-use`). Slice D found no other date-dependent gate in the next 30 days. It shifted the Python clock +35 days for the `check-*.py` scripts, +400 days for the generators, and re-ran every `--check`.

## Outcome in one paragraph

All 108 findings planned for implementation were fixed: 11 P1, 50 P2 and 47 P3. Each one was reproduced on the unmodified code before it was fixed, and each has a regression test that was shown to fail with the fix reverted. Three merged duplicates (H-11, H-12, H-14, folded into H-15) were fixed alongside H-13, and only H-15's gate half is deferred. 16 findings need a design decision, 14 have exact patches for the tribunal-protected substrate, and 11 are deferred: 7 because they overlap #1387, 4 for low value. Panel 2 refuted none of the 153 findings.


## Counts

Final priority × disposition after Panel 3 (149 canonical findings; 4 more merged into others).

| Priority | implement | design | owner-route | defer | total |
|---|---|---|---|---|---|
| P1 | 11 | 0 | 1 | 0 | 12 |
| P2 | 50 | 10 | 7 | 2 | 69 |
| P3 | 47 | 6 | 6 | 9 | 68 |

Plus the P0 time bomb fixed in the first commit, which no panel slice owned because the orchestrator found it in the objective layer.


## Fixed in this PR, by priority

Every fix was reproduced on the unmodified code first and carries a regression test that fails with the fix reverted. Commits name the finding id.


### P1 (11)

| id | Where | What was wrong |
|---|---|---|
| `A-1` | [`plugins/finance/scripts/remeasure.py:325`](../../plugins/finance/scripts/remeasure.py#L325) | CTA self-check falsely BLOCKS correct translations: per-line rounding accumulates past 0.0 |
| `B-1` | [`plugins/report-regeneration/skills/rebind-html/rebind_html.py:411`](../../plugins/report-regeneration/skills/rebind-html/rebind_html.py#L411) | Regenerate templates render in an unsandboxed Jinja Environment: new-data string -> RCE |
| `B-10` | [`plugins/report-regeneration/skills/infer-office/infer_office.py:344`](../../plugins/report-regeneration/skills/infer-office/infer_office.py#L344) | infer_office never descends into w:hyperlink / w:sdt / w:ins / w:smartTag / w:fldSimple wr |
| `B-2` | [`plugins/report-regeneration/skills/rebind-manifest/build_manifest.py:867`](../../plugins/report-regeneration/skills/rebind-manifest/build_manifest.py#L867) | build_manifest drops needs-review nodes whose RSG role is static-chrome: stale values ship |
| `B-3` | [`plugins/report-regeneration/skills/report-fidelity-harness/harness.py:866`](../../plugins/report-regeneration/skills/report-fidelity-harness/harness.py#L866) | HTML V4 taint scan never matches raw/ungrouped numbers (data attrs, script JSON, plain dig |
| `C-1` | [`plugins/ravenclaude-core/skills/repo-review/workflows/repo-sweep.workflow.js:495`](../../plugins/ravenclaude-core/skills/repo-review/workflows/repo-sweep.workflow.js#L495) | Default run id is the constant 'repo-sweep-1001', so every sweep shares one findings dir |
| `C-2` | [`plugins/ravenclaude-core/skills/repo-review/workflows/repo-sweep.workflow.js:129`](../../plugins/ravenclaude-core/skills/repo-review/workflows/repo-sweep.workflow.js#L129) | max/ultra default batch budgets demand 1,200-4,800 agent() calls; no guard vs 1,000 cap |
| `E-1` | [`plugins/web-commerce/templates/stripe/framework/checkout.ts:61`](../../plugins/web-commerce/templates/stripe/framework/checkout.ts#L61) | Stripe framework checkout route charges whatever price the browser sends |
| `E-2` | [`plugins/data-platform/templates/cube-astro-dashboard-starter/src/lib/mint-cube-token.ts:22`](../../plugins/data-platform/templates/cube-astro-dashboard-starter/src/lib/mint-cube-token.ts#L22) | Astro starter: documented 'cp env.example .env; npm run dev' leaves JWT key and CSP origin unset |
| `H-1` | [`plugins/api-engineering/scripts/openapi_diff.py:167`](../../plugins/api-engineering/scripts/openapi_diff.py#L167) | openapi_diff never follows $ref, so most real specs report 'no breaking change' |
| `H-5` | [`plugins/microsoft-graph/scripts/graph_scope_analyzer.py:71`](../../plugins/microsoft-graph/scripts/graph_scope_analyzer.py#L71) | Application Mail/Calendars/Contacts permissions are not escalated (only '.All' names are) |

### P2 (50)

| id | Where | What was wrong |
|---|---|---|
| `A-10` | [`plugins/finance/scripts/schedule_engine.py:267`](../../plugins/finance/scripts/schedule_engine.py#L267) | Prepaid / deferred-revenue schedules are nonsense for negative amounts (credit memos) yet  |
| `A-11` | [`plugins/finance/scripts/close_state.py:210`](../../plugins/finance/scripts/close_state.py#L210) | SoD gate compares the signed amount: a negative or NaN package amount lets the preparer se |
| `A-12` | [`plugins/finance/scripts/close_state.py:272`](../../plugins/finance/scripts/close_state.py#L272) | verify() does not cover state.json or tail truncation, contradicting 'any retroactive edit |
| `A-14` | [`plugins/finance/scripts/connectors/suiteql.py:104`](../../plugins/finance/scripts/connectors/suiteql.py#L104) | pull() defaults sleep to a no-op, so the documented Retry-After backoff never waits |
| `A-15` | [`plugins/finance/scripts/remeasure.py:255`](../../plugins/finance/scripts/remeasure.py#L255) | remeasure --out-tb emits synthetic __CTA__/__REMEAS_GL__ rows that a consumer COA lacks, s |
| `A-16` | [`plugins/finance/scripts/tb_stage.py:145`](../../plugins/finance/scripts/tb_stage.py#L145) | CLI --period/--entity/--currency are silently ignored when the column-map maps that column |
| `A-17` | [`plugins/finance/scripts/reconcile_summary.py:41`](../../plugins/finance/scripts/reconcile_summary.py#L41) | _tb_net overwrites duplicate account rows instead of summing them, giving a wrong book bal |
| `A-19` | [`plugins/finance/skills/warehouse-dashboard/models/rls/run_rls_denial_test.sh:20`](../../plugins/finance/skills/warehouse-dashboard/models/rls/run_rls_denial_test.sh#L20) | RLS denial test exits 0 on SKIP (no docker) although it advertises 'exit 0 iff every asser |
| `A-20` | [`plugins/generative-web-media/scripts/gen-budget.py:41`](../../plugins/generative-web-media/scripts/gen-budget.py#L41) | Budget guard fails open on NaN: one 'nan' line (or --budget nan) makes status report over_ |
| `A-21` | [`plugins/team-portfolio/scripts/portfolio-collect.py:183`](../../plugins/team-portfolio/scripts/portfolio-collect.py#L183) | Team login match is case-sensitive, so a roster entry with different capitalisation silent |
| `A-22` | [`plugins/team-portfolio/scripts/portfolio-collect.py:236`](../../plugins/team-portfolio/scripts/portfolio-collect.py#L236) | A truncated/reset/timed-out response crashes the whole run despite the 'fail soft per repo |
| `A-24` | [`plugins/web-design/scripts/flesch_kincaid.py:61`](../../plugins/web-design/scripts/flesch_kincaid.py#L61) | `check` PASSES (exit 0, FK 0.0) on empty, markup-only or non-Latin text instead of failing |
| `A-3` | [`plugins/generative-web-media/scripts/web-optimize/optimize-image.mjs:65`](../../plugins/generative-web-media/scripts/web-optimize/optimize-image.mjs#L65) | Documented `npx --package=sharp node optimize-image.mjs` can never resolve sharp (always L |
| `A-4` | [`plugins/generative-web-media/scripts/provenance.py:42`](../../plugins/generative-web-media/scripts/provenance.py#L42) | FLUX-dev non-commercial trap detector misses the official and common spellings of the mode |
| `A-5` | [`plugins/generative-web-media/scripts/provenance.py:145`](../../plugins/generative-web-media/scripts/provenance.py#L145) | `audit --dir media` ingests gen-budget's spend.jsonl and fails every spend line as 'missin |
| `A-7` | [`plugins/finance/scripts/finance_calc.py:79`](../../plugins/finance/scripts/finance_calc.py#L79) | npv-irr crashes with ZeroDivisionError for streams of 81+ flows (monthly flows beyond ~7 y |
| `A-8` | [`plugins/finance/scripts/finance_calc.py:281`](../../plugins/finance/scripts/finance_calc.py#L281) | unit-economics accepts '--gross-margin 78' as 7800% and never range-checks gross margin |
| `A-9` | [`plugins/finance/scripts/statement_engine.py:279`](../../plugins/finance/scripts/statement_engine.py#L279) | Draft cash flow's net_change_in_cash is identically the PRIOR period's net income, never t |
| `B-12` | [`plugins/report-regeneration/skills/rebind-manifest/build_manifest.py:744`](../../plugins/report-regeneration/skills/rebind-manifest/build_manifest.py#L744) | Template data-bind attribute is interpolated into a DAX query that powerbi_ingest runs und |
| `B-14` | [`plugins/power-platform/skills/managed-solution-import/managed_import.py:509`](../../plugins/power-platform/skills/managed-solution-import/managed_import.py#L509) | PROD business-hours guard is keyed on the --env name only; --env-url bypasses it silently |
| `B-15` | [`plugins/power-platform/skills/managed-solution-import/managed_import.py:520`](../../plugins/power-platform/skills/managed-solution-import/managed_import.py#L520) | Re-running `import` after a failed pac import re-baselines and forgets the flows the impor |
| `B-16` | [`plugins/power-platform/skills/managed-solution-import/managed_import.py:809`](../../plugins/power-platform/skills/managed-solution-import/managed_import.py#L809) | URLError/KeyError/FileNotFoundError escape main(): traceback, exit 1, outside the document |
| `B-18` | [`plugins/report-regeneration/scripts/powerbi_probe.py:593`](../../plugins/report-regeneration/scripts/powerbi_probe.py#L593) | Playwright fallback attaches the bearer token to every request the page makes (all origins |
| `B-19` | [`plugins/report-regeneration/skills/report-fidelity-harness/harness.py:143`](../../plugins/report-regeneration/skills/report-fidelity-harness/harness.py#L143) | Non-UTF-8 templates and bad JSON crash every stage with a traceback; harness exits 1 like  |
| `B-4` | [`plugins/report-regeneration/skills/report-fidelity-harness/harness.py:2353`](../../plugins/report-regeneration/skills/report-fidelity-harness/harness.py#L2353) | build_manifest's taint-dict@1 cannot be fed to harness --taint (V4 PROBE_ERROR); only comm |
| `B-5` | [`plugins/report-regeneration/skills/rebind-manifest/build_manifest.py:772`](../../plugins/report-regeneration/skills/rebind-manifest/build_manifest.py#L772) | Earned-frozen taint / new-dataset / detector checks silently never run for id-less (css_se |
| `B-6` | [`plugins/report-regeneration/skills/rebind-html/rebind_html.py:232`](../../plugins/report-regeneration/skills/rebind-html/rebind_html.py#L232) | Attribute writes are unescaped (HTML injection) and re.sub treats the value as a replaceme |
| `B-7` | [`plugins/report-regeneration/skills/rebind-html/rebind_html.py:152`](../../plugins/report-regeneration/skills/rebind-html/rebind_html.py#L152) | id-regex attribute helpers hit the wrong tag (data-id=, commented-out markup); old src sur |
| `B-8` | [`plugins/report-regeneration/scripts/rr_anchor.py:115`](../../plugins/report-regeneration/scripts/rr_anchor.py#L115) | Source offsets use str.splitlines() but html.parser counts only '\n': U+2028/U+0085/FF/VT  |
| `B-9` | [`plugins/report-regeneration/skills/infer-report-structure/infer.py:273`](../../plugins/report-regeneration/skills/infer-report-structure/infer.py#L273) | HTML fragments with several top-level elements get '#document ...' anchors that rr_anchor  |
| `C-11` | [`plugins/ravenclaude-core/templates/dashboard-launcher/dashboard.sh:39`](../../plugins/ravenclaude-core/templates/dashboard-launcher/dashboard.sh#L39) | Per-repo dashboard.sh runs pkill -f serve-dashboards.py, killing every project's dashboard |
| `C-3` | [`plugins/ravenclaude-core/skills/repo-review/workflows/repo-sweep.workflow.js:1286`](../../plugins/ravenclaude-core/skills/repo-review/workflows/repo-sweep.workflow.js#L1286) | Verify agents that error or omit verdicts vanish from open count; false 'CONVERGED' |
| `C-7` | [`plugins/ravenclaude-core/monitors/watch-run-state.sh:190`](../../plugins/ravenclaude-core/monitors/watch-run-state.sh#L190) | Monitors drop the first event of every new log and flap across concurrent sessions |
| `C-8` | [`plugins/ravenclaude-core/bin/probe-kit.sh:290`](../../plugins/ravenclaude-core/bin/probe-kit.sh#L290) | rc probe dns says 'control ALSO failed' instead of INCONCLUSIVE with no network |
| `C-9` | [`plugins/ravenclaude-core/skills/refine-to-rubric/scripts/evaluate.py:96`](../../plugins/ravenclaude-core/skills/refine-to-rubric/scripts/evaluate.py#L96) | A hard-gate dimension with no bound signal is silently dropped instead of failing closed |
| `D-1` | [`scripts/check-hook-launch-line.py:61`](../../scripts/check-hook-launch-line.py#L61) | Hardened-launch-line gate lets a second command ride behind it on a new line |
| `D-2` | [`.github/scripts/check-workflow-hygiene.py:69`](../../.github/scripts/check-workflow-hygiene.py#L69) | Workflow-hygiene Rule 1 accepts `permissions: write-all`; quoted `uses:` values mis-parsed |
| `D-3` | [`scripts/check-github-status.sh:35`](../../scripts/check-github-status.sh#L35) | check-github-status.sh prints a green check for an open Actions incident with no component association |
| `D-4` | [`scripts/gh-health.py:429`](../../scripts/gh-health.py#L429) | gh-health status probe treats any 200 body shape as healthy; incidents:null crashes |
| `D-6` | [`scripts/worktree-new.sh:59`](../../scripts/worktree-new.sh#L59) | worktree-new.sh silently reuses a stale agent/<slug> branch and prints a base it did not use |
| `E-3` | [`plugins/data-platform/templates/cube-denial-test-harness/tests/cross-tenant-denial.test.ts:158`](../../plugins/data-platform/templates/cube-denial-test-harness/tests/cross-tenant-denial.test.ts#L158) | Denial harness RLS tests use 'SET LOCAL ... = $1', which Postgres rejects, so both always fail |
| `E-6` | [`plugins/data-platform/templates/cube-nextjs-dashboard-starter/lib/csv.ts:30`](../../plugins/data-platform/templates/cube-nextjs-dashboard-starter/lib/csv.ts#L30) | CSV export prefixes an apostrophe to every negative number, corrupting refunds and credits |
| `E-7` | [`plugins/data-platform/templates/cube-nextjs-dashboard-starter/lib/cube-client.ts:20`](../../plugins/data-platform/templates/cube-nextjs-dashboard-starter/lib/cube-client.ts#L20) | fetchToken has no single-flight, so each page load POSTs /api/cube-token once per query against a 30/min limit |
| `E-8` | [`plugins/data-platform/templates/superset-guest-token-endpoint.ts:60`](../../plugins/data-platform/templates/superset-guest-token-endpoint.ts#L60) | Superset guest-token call authenticates with the host's own JWT, which Superset does not accept |
| `H-2` | [`plugins/experimentation-growth-engineering/scripts/experiment_calc.py:220`](../../plugins/experimentation-growth-engineering/scripts/experiment_calc.py#L220) | experiment_calc mde caps the search at min(p, 1-p) and wrongly says 'underpowered' |
| `H-3` | [`plugins/security-engineering/scripts/sec_risk.py:89`](../../plugins/security-engineering/scripts/sec_risk.py#L89) | sec_risk fail-safe is inverted for --auth-required (default and 'unknown' = yes) |
| `H-4` | [`plugins/salesforce/scripts/apex_governor_smell.py:126`](../../plugins/salesforce/scripts/apex_governor_smell.py#L126) | apex_governor_smell misses loops whose '{' is not on the same line as for/while/do |
| `H-6` | [`plugins/graph-engineering/scripts/lint_graph_shape.py:43`](../../plugins/graph-engineering/scripts/lint_graph_shape.py#L43) | Unbounded variable-length path check misses typed edges ([:KNOWS*], [r:KNOWS*1..]) |
| `H-7` | [`plugins/edtech-partner-success/templates/dashboard-tier-0.5-reference/export-psm-dashboard.py:191`](../../plugins/edtech-partner-success/templates/dashboard-tier-0.5-reference/export-psm-dashboard.py#L191) | exporter's json.dump crashes on Snowflake Decimal/date values and never decodes OBJECT/ARRAY columns |
| `H-9` | [`plugins/fintech-payments-engineering/scripts/recon_diff.py:115`](../../plugins/fintech-payments-engineering/scripts/recon_diff.py#L115) | recon_diff crashes (exit 1 = 'discrepancy') on short CSV rows with --net-fees and rejects BOM CSVs |

### P3 (47)

| id | Where | What was wrong |
|---|---|---|
| `A-23` | [`plugins/web-design/hooks/check-web-anti-patterns.sh:19`](../../plugins/web-design/hooks/check-web-anti-patterns.sh#L19) | Strict mode claims exit 2 'BLOCKS' but the hook is PostToolUse, where the edit has already |
| `A-25` | [`plugins/web-design/hooks/check-web-anti-patterns.sh:41`](../../plugins/web-design/hooks/check-web-anti-patterns.sh#L41) | Color check is skipped for any path containing 'tokens'/'colors.'/'palette.', and 8-digit  |
| `A-26` | [`plugins/finance/scripts/tb_stage.py:273`](../../plugins/finance/scripts/tb_stage.py#L273) | _atomic_write is dead code; cmd_stage writes via an unconditional path that crashes on a m |
| `A-27` | [`plugins/finance/scripts/statement_engine.py:167`](../../plugins/finance/scripts/statement_engine.py#L167) | Non-strict run KeyErrors on an IS account mapped to a non-IS section instead of returning  |
| `A-28` | [`plugins/finance/scripts/test_close_identity.py:139`](../../plugins/finance/scripts/test_close_identity.py#L139) | Test crashes (BaseException) when PyJWT is installed but cryptography is broken, instead o |
| `A-29` | [`plugins/team-portfolio/scripts/portfolio-collect.py:111`](../../plugins/team-portfolio/scripts/portfolio-collect.py#L111) | Pagination ceiling (20 pages x 100) silently truncates busy repos with no warning in error |
| `A-30` | [`plugins/team-portfolio/scripts/portfolio-report.py:207`](../../plugins/team-portfolio/scripts/portfolio-report.py#L207) | 'Merged PRs' counts PRs merely updated in the window; Open PR/issue counts are 'seen in wi |
| `A-31` | [`plugins/team-portfolio/scripts/portfolio-config-check.py:128`](../../plugins/team-portfolio/scripts/portfolio-config-check.py#L128) | Config check accepts malformed team logins ('@alice', emails, spaces) that then silently m |
| `A-33` | [`plugins/generative-web-media/scripts/provenance.py:113`](../../plugins/generative-web-media/scripts/provenance.py#L113) | Audit treats null/empty-container required fields as present (str(None) == 'None') |
| `A-6` | [`plugins/finance/scripts/finance_calc.py:133`](../../plugins/finance/scripts/finance_calc.py#L133) | variance-bridge's 'mix/interaction' term is always 0: the interaction is folded into price |
| `B-20` | [`plugins/power-platform/hooks/nudge-dataverse-preflight.sh:38`](../../plugins/power-platform/hooks/nudge-dataverse-preflight.sh#L38) | Dataverse nudge misses $batch writes and goes silent on large multi-line commands (pipefai |
| `B-21` | [`plugins/power-platform/hooks/validate-tmdl-measure-metadata.sh:33`](../../plugins/power-platform/hooks/validate-tmdl-measure-metadata.sh#L33) | Power Platform PostToolUse hooks are silently inert when jq is missing (no diagnostic) |
| `B-22` | [`plugins/report-regeneration/skills/report-fidelity-harness/render_referee.py:246`](../../plugins/report-regeneration/skills/report-fidelity-harness/render_referee.py#L246) | Every Playwright harness run leaves a full-page screenshot of the report in the temp dir |
| `B-23` | [`plugins/report-regeneration/skills/report-fidelity-harness/SKILL.md:71`](../../plugins/report-regeneration/skills/report-fidelity-harness/SKILL.md#L71) | SKILL.md says a disabled leg 'reports pass unconditionally'; code reports 'disabled' and f |
| `B-24` | [`plugins/power-platform/skills/pbir-ref-integrity/check_refs.py:83`](../../plugins/power-platform/skills/pbir-ref-integrity/check_refs.py#L83) | Docstring says parse errors exit 2; unparseable JSON / missing definition/ exit 1 |
| `B-25` | [`plugins/power-platform/skills/report-visualization-design/grid.py:91`](../../plugins/power-platform/skills/report-visualization-design/grid.py#L91) | golden-overview fails on common 16:9 canvases (1600x900, 1440x810, 960x540); margin/gap ar |
| `B-28` | [`plugins/report-regeneration/skills/report-fidelity-harness/harness.py:1169`](../../plugins/report-regeneration/skills/report-fidelity-harness/harness.py#L1169) | Office V4 silently stops reading a docx after 8,000 parts; no per-part size cap anywhere |
| `B-29` | [`plugins/report-regeneration/skills/report-fidelity-harness/harness.py:458`](../../plugins/report-regeneration/skills/report-fidelity-harness/harness.py#L458) | V1 locate-at-anchor silently skips bindings with css_selector anchors |
| `C-13` | [`plugins/ravenclaude-core/skills/refine-to-rubric/scripts/converge.py:110`](../../plugins/ravenclaude-core/skills/refine-to-rubric/scripts/converge.py#L110) | keep_best ignores hard gates; a RED iteration can be emitted as best under rubric-pass |
| `C-14` | [`plugins/ravenclaude-core/skills/terminal-status-indicators/setup-terminal-indicators.sh:165`](../../plugins/ravenclaude-core/skills/terminal-status-indicators/setup-terminal-indicators.sh#L165) | Idempotent re-run replaces a symlinked ~/.bashrc with a mode-0600 regular file |
| `C-15` | [`plugins/ravenclaude-core/skills/authoring-org-skills/scripts/packer.py:124`](../../plugins/ravenclaude-core/skills/authoring-org-skills/scripts/packer.py#L124) | `._*` AppleDouble files in subfolders are neither excluded by pack nor flagged by ZP07 |
| `C-16` | [`plugins/ravenclaude-core/skills/wireframe/wireframe_lint.py:307`](../../plugins/ravenclaude-core/skills/wireframe/wireframe_lint.py#L307) | mermaid_label strips the semicolons from the entity escapes it just inserted |
| `C-17` | [`plugins/ravenclaude-core/skills/declarative-visualization/lint.py:419`](../../plugins/ravenclaude-core/skills/declarative-visualization/lint.py#L419) | Deeply nested JSON crashes dv/pbir linters with exit 1 (read as 'violations found') |
| `C-18` | [`plugins/ravenclaude-core/skills/repo-review/scripts/fix_summary.py:99`](../../plugins/ravenclaude-core/skills/repo-review/scripts/fix_summary.py#L99) | fix_summary crashes on non-dict applied entries; silent empty patch when git fails |
| `C-19` | [`plugins/ravenclaude-core/monitors/watch-run-state.sh:78`](../../plugins/ravenclaude-core/monitors/watch-run-state.sh#L78) | newest_log forks one stat per run dir per poll; ~6s per call at 1,500 run dirs |
| `C-4` | [`plugins/ravenclaude-core/skills/rc-deep-research/rc-deep-research.js:1181`](../../plugins/ravenclaude-core/skills/rc-deep-research/rc-deep-research.js#L1181) | A single refuting vote lets the claim survive, then Synthesize crashes on best.confidence |
| `D-11` | [`scripts/content-scan.py:155`](../../scripts/content-scan.py#L155) | content-scan SSRF guard still accepts 100.64.0.0/10 (Alibaba metadata) and IPv4-mapped forms |
| `D-12` | [`scripts/content-scan.py:339`](../../scripts/content-scan.py#L339) | Scan digests embed untrusted titles/excerpts as live markdown under docs/research, breaking the md-links gate |
| `D-13` | [`scripts/install-codex-mcp.py:148`](../../scripts/install-codex-mcp.py#L148) | install-codex-mcp.py rewrites a CRLF config.toml to LF while claiming a pure append |
| `D-14` | [`scripts/check-ratchet-freshness.py:159`](../../scripts/check-ratchet-freshness.py#L159) | check-ratchet-freshness --check exits 0 when every ratchet file is absent |
| `D-15` | [`scripts/assert-not-required-check.sh:51`](../../scripts/assert-not-required-check.sh#L51) | assert-not-required-check reports OK from an unparseable or differently-shaped ruleset body |
| `D-8` | [`scripts/concepts.py:598`](../../scripts/concepts.py#L598) | A future-dated last_verified never goes stale (freshness gate silently disarmed) |
| `E-10` | [`plugins/web-commerce/templates/square/framework/square-client.ts:58`](../../plugins/web-commerce/templates/square/framework/square-client.ts#L58) | Provider HTTP calls (Square, Shopify Storefront) have no timeout or abort signal |
| `E-11` | [`plugins/data-platform/templates/jwt-issuer.ts:21`](../../plugins/data-platform/templates/jwt-issuer.ts#L21) | jwt-issuer.ts documents RS256 private-key support but hard-codes HS256 |
| `E-12` | [`plugins/data-platform/templates/cube-nextjs-dashboard-starter/env.example:12`](../../plugins/data-platform/templates/cube-nextjs-dashboard-starter/env.example#L12) | env.example says next.config.js builds the CSP, but CSP moved to middleware.ts |
| `H-10` | [`plugins/data-streaming-engineering/scripts/stream_sizing.py:52`](../../plugins/data-streaming-engineering/scripts/stream_sizing.py#L52) | partitions: float ceiling adds a phantom partition (100 msg/s x 1.1 / 10 -> 12, not 11) |
| `H-13` | [`plugins/localization-i18n-engineering/hooks/check-localization-i18n-engineering-anti-patterns.sh:78`](../../plugins/localization-i18n-engineering/hooks/check-localization-i18n-engineering-anti-patterns.sh#L78) | i18n hook check 4b is dead (invalid range `[/\-.]`) and 4c never matches a literal "$" |
| `H-16` | [`plugins/tableau/hooks/flag-tableau-anti-patterns.sh:49`](../../plugins/tableau/hooks/flag-tableau-anti-patterns.sh#L49) | `grep -c ... \|\| echo 0` yields '0\n0' and a bash syntax error on files with no <datasource |
| `H-17` | [`plugins/qa-test-automation/scripts/qa_suite_metrics.py:48`](../../plugins/qa-test-automation/scripts/qa_suite_metrics.py#L48) | pyramid_ratio --dir classifies by substring of the absolute path ('_it', ancestor dir names) |
| `H-18` | [`plugins/email-engineering/scripts/email_auth_lint.py:72`](../../plugins/email-engineering/scripts/email_auth_lint.py#L72) | SPF lint warns 'No terminal all' for a valid redirect= record |
| `H-19` | [`plugins/observability-sre/scripts/slo_calc.py:96`](../../plugins/observability-sre/scripts/slo_calc.py#L96) | burn-rate does not validate --window-days (ZeroDivisionError / negative hours) |
| `H-20` | [`plugins/clinical-trials/scripts/trials_calc.py:173`](../../plugins/clinical-trials/scripts/trials_calc.py#L173) | retention-roi footer text is backwards and impossible break-evens are not flagged |
| `H-21` | [`plugins/claude-app-engineering/scripts/claude_cost_estimator.py:93`](../../plugins/claude-app-engineering/scripts/claude_cost_estimator.py#L93) | claude_cost_estimator accepts negative/nonsensical inputs and the cache break-even loop is O(requests) |
| `H-22` | [`plugins/hospice-referral-sales/scripts/hospice_calc.py:85`](../../plugins/hospice-referral-sales/scripts/hospice_calc.py#L85) | _pct treats a bare '1' as 100%, and malformed --admit-rate/--weight-loss tracebacks |
| `H-23` | [`plugins/esg-sustainability-reporting/scripts/ghg_calc.py:164`](../../plugins/esg-sustainability-reporting/scripts/ghg_calc.py#L164) | inventory crashes with TypeError on CSV rows shorter than the header |
| `H-25` | [`plugins/memory-engineering/scripts/memory_engineering_calc.py:334`](../../plugins/memory-engineering/scripts/memory_engineering_calc.py#L334) | cache-economics: 'cache-breaking' comes out cheaper than 'stable' when invalidations are 0 or <1/month |
| `H-8` | [`plugins/edtech-partner-success/templates/dashboard-tier-0.5-reference/export-psm-dashboard.py:242`](../../plugins/edtech-partner-success/templates/dashboard-tier-0.5-reference/export-psm-dashboard.py#L242) | --allow-real-ids is inert and --validate points at a schema path that cannot exist |

## What needs you, in order

1. **Artifact budget — resolved on your instruction ("do it, but find where you can trim").** After merging `main`, the standalone `dashboard.html` was 5 island elements and 5,132 bytes over its ceilings. Trims came first:
   - The concept-diagram theme CSS now groups selectors with `:is()` (`render-concepts.py`, normalizer v5). This saved 87 KB, with computed styles proven identical in Chromium.
   - Three duplicate source links were merged, and a broken empty code span in `runaway-brake` was fixed (-4 elements).

   That leaves bytes 82,472 under the ceiling, so there is no byte raise. The remaining 1 element is covered by one payload row (33,200 → 33,210) in `scripts/artifact-budgets.seed.json`. A fourth duplicate-link merge was dropped to stay within the 20-concept render cap.
2. **Apply the FG-1 owner-route patch (P1).** `guard-premise.sh` looks for its recorder at `<project>/plugins/ravenclaude-core/hooks/log-probe.sh`, a path that exists only in the marketplace clone. In every consumer install it therefore reads itself as blind and denies the first new source file. The patch is in the appendix: rc 2 before, rc 0 after, on a scratch copy.
3. **Decide D-1, open since 2026-10-14.** It has new evidence. The SessionStart `reapply-posture` hook rewrites `.claude/settings.json` in every session. It drops the six committed Gmail MCP allows and now also writes an `env` block (`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`). That `env` block makes Gate 305 row 17a fail locally in every session. Measured this run: Gate 305 is 81/1 on the working tree and 82/0 in a clean worktree of `HEAD`. Recommendation, unchanged: move the Gmail allows into `comfort-posture.yaml` so the generator stops dropping them, and keep the generator from writing `env` into this repo's settings.
4. **Re-verify the seven concepts due on 2026-11-23** a few days ahead, or take a policy decision. The 90-day platform-fact block is meant to be serviceable, but concepts authored in waves expire in waves, which is the outage `concepts.py`'s own header warns about for the inventory corpus. Options: (a) keep blocking on PRs and schedule the re-verification, which this run did for ten; (b) warn on PRs, block on the scheduled sweep, and notify 14 days ahead. **Recommendation: (b).** D-10 below is the same coupling seen from the gate side.
5. **PR #1387 needs you before it can merge.** It currently has a merge conflict (`mergeable_state: dirty`), and its CI was already red: `hooks/_web.sh` needs its executable bit, which its own notes say only you can set. It will also hit this P0 until #1389 or an equivalent restamp lands. Merging #1389 first, then bringing `main` into #1387, avoids re-deriving the concept restamp twice.

6. **One new test file still needs a CI runner: `plugins/web-commerce/templates/stripe/framework/tests/checkout.test.ts`** (E-1). The other five new regression files run in CI through the new **Gate 317**. That gate sits in the `core` suite and is placed after Gate 282, so it avoids #1387's `audit-gates.sh` hunks (#1387 takes Gates 310-316). The five files are `scripts/check-review-2026-10-20-{core,scripts,domain}.py`, `plugins/team-portfolio/scripts/test_portfolio.py` and `plugins/web-design/scripts/test_web_design_checks.py`. The Stripe test needs that template's node toolchain, which no CI job installs today. It passed 10/10 in this session. Tests that extend existing suites (finance, report-regeneration, Power Platform, Gate 260, `check-hook-launch-line.py`) already run wherever those suites run.

### Observed live during the run (no new findings, recorded as evidence)

- **FG-10 reproduced itself.** The conserve-tokens `UserPromptSubmit` hook engaged when a subagent's report contained the words "save tokens". No human prompt was involved. The design item for FG-10 is below.
- **The concurrent-audit hazard.** `audit-gates.sh` backs files up, mutates them and restores them in the live tree. Running it while an agent edited `permission-layers.md` silently reverted that edit, and it was caught only by re-listing `last_verified`. That is not a bug in the gate; the full suite assumes a quiet tree. It is worth one line in `AGENTS.md` § Testing.


## Needs your decision — design list

Each item needs a policy or contract call, so none of them was changed. Ordered by priority.


### A-13 (P2) — BS-cumulative + IS-period-only query cannot foot to zero once any earlier period has P&L a

**Where:** [`plugins/finance/scripts/connectors/suiteql.py:58`](../../plugins/finance/scripts/connectors/suiteql.py#L58)

**Question.** Should the staged NetSuite TB be a fiscal-YTD trial balance with a synthetic retained-earnings row, or period-activity P&L with a separate RE input?

**Recommendation.** Fiscal-YTD IS plus a computed prior-year retained-earnings row, which matches how statement_engine treats equity. Add the cause to RANKED_ROOT_CAUSES. Build a ledger fixture first; Panel 1's evidence is a static arithmetic model.


### A-18 (P2) — Tolerance matching is unbounded in aggregate and ignores sign: +0.50 pairs with -0.50, 3,0

**Where:** [`plugins/finance/scripts/recon_match.py:150`](../../plugins/finance/scripts/recon_match.py#L150)

**Question.** Should tolerance-matched deltas count toward the per-account materiality bound, and what is the sign-flip policy for tolerance/grouped matches?

**Recommendation.** Same-sign only for tolerance and grouped matches, and the aggregate |matched_delta| per account counts toward materiality. Decide with A-2: it is the same net-vs-gross choice.


### A-2 (P2) — Auto-certification judges the NET of unmatched items, so offsetting material breaks pass -

**Where:** [`plugins/finance/scripts/recon_match.py:185`](../../plugins/finance/scripts/recon_match.py#L185)

**Question.** Should auto-certification judge the GROSS of unmatched items (and any single unmatched item) against materiality, instead of the net residual? (Netting is the documented rule today; offsetting material breaks auto-certify.)

**Recommendation.** Yes. Certify only when sum(|unmatched|) < materiality AND no single unmatched item >= materiality, and keep the net residual as the displayed figure. Decide together with A-18. Announce it in the finance CHANGELOG as a behaviour change, because accounts with offsetting breaks move from AUTO-CERTIFIED to FLAGGED.


### B-11 (P2) — qa_gate trusts any well-formed receipt: TTL and env fingerprint never enforced, receipt no

**Where:** [`plugins/report-regeneration/skills/report-qa-gate/qa_gate.py:223`](../../plugins/report-regeneration/skills/report-qa-gate/qa_gate.py#L223)

**Question.** Should fidelity receipts carry subject digests (schema bump) and qa_gate re-hash the named files and enforce the TTL, or should qa_gate stay receipt-only and document that it certifies nothing about the files?

**Recommendation.** Bind the receipt: fidelity-receipt@2 with sha256 of template/output/manifest/new-data; qa_gate takes --output/--template, re-hashes them, and enforces generated_at + ttl_seconds. Until that ships, say plainly in SKILL.md that qa_gate certifies the receipt only.


### B-13 (P2) — Imperative blocklist is a substring match: 'wireless', 'overrides', 'remittance volumes' h

**Where:** [`plugins/report-regeneration/skills/report-injection-guard/injection_guard.py:509`](../../plugins/report-regeneration/skills/report-injection-guard/injection_guard.py#L509)

**Question.** The injection guard's imperative list is substring-matched, so 'wireless', 'hardwired' and 'overrides' are blocking hits (and 'remittance' is listed outright). Do we trade some recall for precision on a security guard?

**Recommendation.** Yes, narrowly. Use inflection-aware word-boundary patterns (\bwire[sd]?\b, \bremit(?:s|ted)?\b, \boverride[sd]?\b, \breroute[sd]?\b ...), which keep every inflection the list was written for. Make bare payment nouns ('remittance', 'wire') blocking only in combination with an un-provenanced account number or email, advisory otherwise. Marked design, not implement, because it narrows a security guard's matching.


### B-17 (P2) — baseline/reactivate act on every category=5 flow in the environment, not the imported solu

**Where:** [`plugins/power-platform/skills/managed-solution-import/managed_import.py:440`](../../plugins/power-platform/skills/managed-solution-import/managed_import.py#L440)

**Question.** Should flow baseline/reactivation be limited to the imported solution (which needs a solution unique-name input), or stay environment-wide as implemented?

**Recommendation.** Scope it to the imported solution (require --solution-unique-name and join solutioncomponents for its workflow ids), and keep environment-wide behaviour only behind an explicit --all-flows flag.


### C-10 (P2) — svg-report-lint and dv lint reject all consumer files from plugin cache (like corescripts-

**Where:** [`plugins/ravenclaude-core/skills/svg-report-lint/lint.py:84`](../../plugins/ravenclaude-core/skills/svg-report-lint/lint.py#L84)

**Question.** The same trust-boundary decision as corescripts-8 (open in the 2026-10-19 decision list): what root do skill linters run from the plugin cache accept input paths under?

**Recommendation.** Option A from corescripts-8: a shared _sandbox_root() ($RAVENCLAUDE_SANDBOX_ROOT, then $CLAUDE_PROJECT_DIR, then the git toplevel of cwd, then the legacy root), applied to all four linters (svg-report-lint, declarative-visualization, visual-feedback-loop driver, pbir-layout-engine) at once, keeping the '..' and realpath-escape fixtures.


### D-10 (P2) — Gates 237 and 239 couple a unit test to live-corpus freshness, so every concept expiry reddens audit-gates

**Where:** [`plugins/ravenclaude-core/hooks/tests/test-gate237-inventory-staleness.sh:184`](../../plugins/ravenclaude-core/hooks/tests/test-gate237-inventory-staleness.sh#L184)

**Question.** Gates 237/239's unit tests couple to live-corpus calendar freshness, so every concept expiry reddens audit-gates (premise fixed at HEAD by 6eb60794, coupling still real). Should those unit tests assert freshness at all? The file is protected substrate (plugins/ravenclaude-core/hooks/tests/), and changing what a gate asserts is a gate change.

**Recommendation.** No. Pin the clock (add a --today flag to scripts/concepts.py, or assert only the schema/registry/drift exit classes via RC-CONCEPTS-CLASS), so freshness is owned solely by the one real freshness gate. Owner applies it.


### E-4 (P2) — Astro CSP nonce is stamped onto every <script>, so it no longer blocks injected scripts

**Where:** [`plugins/data-platform/templates/cube-astro-dashboard-starter/src/middleware.ts:76`](../../plugins/data-platform/templates/cube-astro-dashboard-starter/src/middleware.ts#L76)

**Question.** The Astro starter stamps the CSP nonce onto every <script>, so CSP no longer blocks injected scripts. Allow-list known inline bootstrap scripts by hash, bump to Astro >=5.9 native CSP hashing, or keep the blanket stamp and document it?

**Recommendation.** Short term: document in the starter that script-src is not an injection control here. Next starter refresh: bump to Astro >=5.9 and use native CSP hashing.


### E-5 (P2) — Stripe event normalization misreports partial refunds and maps one purchase to repeated payment.* events

**Where:** [`plugins/web-commerce/templates/stripe/framework/provider.ts:59`](../../plugins/web-commerce/templates/stripe/framework/provider.ts#L59)

**Question.** Which Stripe event is canonical for each commerce transition? Today charge.refunded and refund.created both map to payment.refunded (a partial refund books twice, once at the full charge amount), and amount_capturable_updated maps to payment.succeeded (an authorisation and its capture both read as succeeded).

**Recommendation.** payment.refunded only from refund.created (amount = refund.amount, reference = object.payment_intent); charge.refunded -> unknown. Add a 'payment.authorized' CommerceEventType for amount_capturable_updated, which needs a shared commerce-types change plus a Square/Shopify mapping review. Apply to stripe/static/provider.ts too, with a partial-refund test. Decide E-13 in the same pass.


### A-34 (P3) — typeface_count check trusts a self-declared marker and is not scoped to section 2 as docum

**Where:** [`plugins/web-design/skills/brand-guidance-authoring/scripts/brand_guidance_lint.py:111`](../../plugins/web-design/skills/brand-guidance-authoring/scripts/brand_guidance_lint.py#L111)

**Question.** Is brand_guidance_lint's self-declared typeface marker meant to be the only source of truth, or should it be cross-checked against section 2's table?

**Recommendation.** Keep the marker authoritative, scope the search to section 2 as documented, and WARN when it disagrees with the table's row count.


### D-17 (P3) — Gate 302 headroom is 49 files now and about 21 after PR #1387

**Where:** [`scripts/check-repo-file-budget.py:51`](../../scripts/check-repo-file-budget.py#L51)

**Question.** Gate 302 headroom is 49 files now (9,941 / 9,990, measured this session) and about 21 after #1387 merges. This run's packages add at most 6 more. What do we pack or prune next?

**Recommendation.** Before #1387 merges, run `python3 scripts/check-repo-file-budget.py --report`, pick the largest generated per-file family, and pack it with the visual_pack.py pattern. Do not raise FAIL_AT.


### D-18 (P3) — Data-platform freshness sweep is warn-only and green, so 36 stale files have no visible signal

**Where:** [`scripts/check-data-platform-knowledge-freshness.py:92`](../../scripts/check-data-platform-knowledge-freshness.py#L92)

**Question.** The data-platform knowledge-freshness sweep is warn-only and green with 36 stale files (re-observed). Should stale files produce a visible signal?

**Recommendation.** Keep CI warn-only, but have the scheduled sweep open or refresh a single tracking issue when count > 0 (the atlas-watch pattern), or post through scripts/notify.sh.


### FG-10 (P3) — conserve-tokens engage phrases ('save tokens', 'minimize tokens') match ordinary prose

**Where:** [`plugins/ravenclaude-core/scripts/conserve-tokens.py:100`](../../plugins/ravenclaude-core/scripts/conserve-tokens.py#L100)

**Question.** Which conserve-tokens engage phrasing is specific enough to avoid prose false positives ('save tokens' and 'minimize tokens' match ordinary sentences)? Protected substrate.

**Recommendation.** Require an imperative or first-person shape ('conserve tokens', 'please save tokens', 'low token mode') at sentence start or after an instruction verb, and drop the bare 'save tokens' and 'minimize tokens' entries.


### FG-15 (P3) — dod-gate treats any dirty working tree as 'changed this session'

**Where:** [`plugins/ravenclaude-core/hooks/dod-gate.sh:113`](../../plugins/ravenclaude-core/hooks/dod-gate.sh#L113)

**Question.** What defines 'changed this session' for dod-gate: a SessionStart baseline, or the PostToolUse edit events in hook-events? Today any dirty tree counts. Protected substrate.

**Recommendation.** Record a SessionStart baseline (a git status hash plus a per-file mtime snapshot) and gate only on paths changed since. It is cheap, and it does not depend on event capture working.


### H-24 (P3) — risk-band ignores CVSS for every internet-exposed finding (CVSS 2.0 -> CRITICAL/72h)

**Where:** [`plugins/security-engineering/scripts/sec_risk.py:102`](../../plugins/security-engineering/scripts/sec_risk.py#L102)

**Question.** Should sec_risk's CRITICAL/HIGH leaves require a minimum CVSS base score, or is exposure alone meant to drive the band (CVSS 2.0 internet-exposed -> CRITICAL/72h)?

**Recommendation.** Keep exposure-driven banding, cap CVSS < 4.0 at MEDIUM, and print the base score in the 'why' line.


## Owner-route — clear fixes in the tribunal's protected substrate

These files are under `plugins/ravenclaude-core/hooks/`, `plugins/ravenclaude-core/scripts/` or `scripts/generate-dashboards.py`, which the command-review tribunal protects from agent edits. That is correct for an unattended run, so each fix is written up as a patch for you to apply (patches are in the appendix). They were syntax-checked, and FG-1, FG-6, FG-8, FG-12 and FG-14 were behaviour-checked on scratch copies; none was applied to the repo. Apply **FG-1 first**: it is the only P1.

| id | Priority | Where | What is wrong | Fix |
|---|---|---|---|---|
| `FG-1` | P1 | [`plugins/ravenclaude-core/hooks/guard-premise.sh:527`](../../plugins/ravenclaude-core/hooks/guard-premise.sh#L527) | guard-premise falsely BLINDs and denies the first new source file in consumer installs | guard-premise.sh: also probe for log-probe.sh beside the gate itself (the hook's own directory, passed into the python block as argv[2]) before the marketplace-relative path. |
| `FG-2` | P2 | [`plugins/ravenclaude-core/hooks/format-on-write.sh:133`](../../plugins/ravenclaude-core/hooks/format-on-write.sh#L133) | format-on-write runs `ruff format` on lint-only ruff configs, rewriting whole files | format-on-write.sh: run `ruff format` only when the project configures ruff's formatter ([format] in ruff.toml/.ruff.toml or [tool.ruff.format] in pyproject.toml). Shared patch with FG-3. |
| `FG-3` | P2 | [`plugins/ravenclaude-core/hooks/format-on-write.sh:136`](../../plugins/ravenclaude-core/hooks/format-on-write.sh#L136) | format-on-write's `ruff check --fix` deletes the import an agent just added (F401) | format-on-write.sh: drop the per-edit `ruff check --fix` (formatters only). Same patch as FG-2. |
| `FG-4` | P2 | [`plugins/ravenclaude-core/hooks/dod-gate.sh:121`](../../plugins/ravenclaude-core/hooks/dod-gate.sh#L121) | dod-gate skips entirely when the only new source files sit in a new directory | dod-gate.sh: add -uall to `git status --porcelain=v1 -z` so the untracked files inside a new directory are listed individually. |
| `FG-6` | P2 | [`plugins/ravenclaude-core/hooks/stream-session-close.sh:252`](../../plugins/ravenclaude-core/hooks/stream-session-close.sh#L252) | stream-session-close fires on every Stop, logging a session_closed event per turn | stream-session-close.sh: append session_closed only once per session_id (later Stops only refresh state.md). |
| `FG-7` | P2 | [`plugins/ravenclaude-core/hooks/spectate-steer.sh:86`](../../plugins/ravenclaude-core/hooks/spectate-steer.sh#L86) | spectate-steer pause/note/approve never fire on native Claude Code (event from env only) | spectate-steer.sh: when neither CLAUDE_HOOK_EVENT nor the hint is set, read hook_event_name / hookEventName from the payload (as spectate-emit.sh's detect_event does). |
| `FG-8` | P2 | [`plugins/ravenclaude-core/hooks/worktree-guard.sh:506`](../../plugins/ravenclaude-core/hooks/worktree-guard.sh#L506) | worktree-guard FOREIGN-TREE check bypassed by '..' through a not-yet-created directory | worktree-guard.sh: lexically normalise '.'/'..' (pure bash, no python dependency) before the nearest-existing-ancestor walk. |
| `FG-9` | P2 | [`plugins/ravenclaude-core/scripts/handoff-nudge.py:361`](../../plugins/ravenclaude-core/scripts/handoff-nudge.py#L361) | handoff-nudge cites a repo-relative context-handoff.py path that consumers do not have | handoff-nudge.py: cite the resolved, shell-quoted path of context-handoff.py (HERE / 'context-handoff.py') instead of the marketplace-relative path. |
| `D-16` | P3 | [`scripts/generate-dashboards.py:9214`](../../scripts/generate-dashboards.py#L9214) | host-support payload (and the learn/trees/commands payloads) are spliced into <script> blocks without '<' escaping | generate-dashboards.py: apply the same '<' -> \u003c escape to the learn/commands/trees payloads and to the host-support payload. |
| `FG-11` | P3 | [`plugins/ravenclaude-core/hooks/codex-hook-env.sh:108`](../../plugins/ravenclaude-core/hooks/codex-hook-env.sh#L108) | codex-hook-env turns a hook's exit 0 into 141 when it leaves a large stdin unread | codex-hook-env.sh: exit with the hook's own status (PIPESTATUS[1]), not the pipeline status, so a printf SIGPIPE cannot turn rc 0 into 141. |
| `FG-12` | P3 | [`plugins/ravenclaude-core/scripts/substrate-tier-map.js:31`](../../plugins/ravenclaude-core/scripts/substrate-tier-map.js#L31) | substrate-tier-map.js resolves inherited keys (constructor, toString) as hosts and throws | substrate-tier-map.js: use hasOwnProperty for the host and tier lookups. |
| `FG-13` | P3 | [`plugins/ravenclaude-core/scripts/handoff-spawn.sh:683`](../../plugins/ravenclaude-core/scripts/handoff-spawn.sh#L683) | handoff-spawn types the unquoted launch path into the VS Code/Cursor terminal | handoff-spawn.sh: type `bash <_shq launch>` instead of the raw path into the VS Code and Cursor terminals (two sites). |
| `FG-14` | P3 | [`plugins/ravenclaude-core/scripts/forge-publish-session-plan.sh:134`](../../plugins/ravenclaude-core/scripts/forge-publish-session-plan.sh#L134) | forge-publish-session-plan _safe_copy truncates the destination before checking the source | forge-publish-session-plan.sh _safe_copy: read and validate the source before opening the destination with O_TRUNC, and write in a loop. |
| `FG-5` | P3 | [`plugins/ravenclaude-core/hooks/remind-tests.sh:62`](../../plugins/ravenclaude-core/hooks/remind-tests.sh#L62) | remind-tests misses spaced/non-ASCII/untracked-dir source files (awk $2 on porcelain) | remind-tests.sh: use `git status --porcelain=v1 -z -uall \| tr '\0' '\n'` and match the extension on the whole record, as dod-gate does. |

## Deferred

| id | Priority | Where | What | Why deferred |
|---|---|---|---|---|
| `C-5` | P2 | [`plugins/ravenclaude-core/bin/rc:203`](../../plugins/ravenclaude-core/bin/rc#L203) | `rc spectate` attaches to another project's Spectate server on the same port | overlaps #1387 (plugins/ravenclaude-core/bin/rc). |
| `C-6` | P2 | [`plugins/ravenclaude-core/bin/rcwt:53`](../../plugins/ravenclaude-core/bin/rcwt#L53) | `rcwt new/rm` run from inside a linked worktree nests worktrees and cannot remove siblings | overlaps #1387 (plugins/ravenclaude-core/bin/rcwt). Merged D-7 (worktree-new.sh / worktree-swarm.sh nesting) rides with it: fix both sites with the same git-common-dir pattern in one follow-up after #1387 merges. |
| `A-32` | P3 | [`plugins/team-portfolio/scripts/portfolio-report.py:164`](../../plugins/team-portfolio/scripts/portfolio-report.py#L164) | Untrusted issue/PR titles are interpolated into committed markdown without escaping | Low confidence and low value: GitHub's markdown renderer already sanitises active content, and escaping changes every bracketed title in committed reports. Revisit if the reports are rendered anywhere else. |
| `B-26` | P3 | [`plugins/power-platform/skills/record-screen/scripts/setup.sh:6`](../../plugins/power-platform/skills/record-screen/scripts/setup.sh#L6) | setup.sh installs unpinned npm deps (ffmpeg-static downloads a binary) with no lockfile; f | Needs a generated package-lock.json (network access, plus one more file under file-budget pressure), and record-screen is mid-change in #1387. |
| `B-27` | P3 | [`plugins/report-regeneration/skills/infer-report-structure/infer.py:299`](../../plugins/report-regeneration/skills/infer-report-structure/infer.py#L299) | Raster rule only covers <img>: CSS background data-URIs / external images stay frozen | M-effort classifier-policy change (which CSS image forms count as raster). Revisit after B-2's needs-review fix lands. |
| `C-12` | P3 | [`plugins/ravenclaude-core/bin/rcwt:163`](../../plugins/ravenclaude-core/bin/rcwt#L163) | rcwt rm/done calls squash-merged branches 'unmerged' and keeps them | overlaps #1387 (plugins/ravenclaude-core/bin/rcwt). |
| `D-5` | P3 | [`scripts/open-dashboard.sh:236`](../../scripts/open-dashboard.sh#L236) | open-dashboard.sh announces another checkout's dashboard when it cannot verify ownership | The proper fix needs a server identity endpoint in serve-dashboards.py, which overlaps #1387. The trigger is narrow (no working lsof, plus two checkouts on one port). |
| `D-9` | P3 | [`.github/workflows/inventory-sweep.yml:77`](../../.github/workflows/inventory-sweep.yml#L77) | Sweep job runs the calendar-age gate before the evidence scan and the ruleset assertion, so a stale concept skips both | overlaps #1387 (.github/workflows/inventory-sweep.yml). |
| `E-13` | P3 | [`plugins/web-commerce/templates/square/framework/provider.ts:131`](../../plugins/web-commerce/templates/square/framework/provider.ts#L131) | Square refund PENDING is returned as PaymentStatus 'authorized' | Low confidence, and it needs a new shared PaymentStatus value across providers (a contract change). Decide together with E-5. |
| `E-9` | P3 | [`plugins/data-platform/templates/cube-nextjs-dashboard-starter/lib/session.ts:39`](../../plugins/data-platform/templates/cube-nextjs-dashboard-starter/lib/session.ts#L39) | Session seam ships an env-var auth bypass at the top of the function consumers must edit | overlaps #1387: the stub is selected by DATA_PLATFORM_STARTER_CI_SESSION, which .github/workflows/validate-data-platform-starters.yml (in #1387) sets, so any change to the stub selection must change that workflow. |
| `H-15` | P3 | [`scripts/check-grep-ere-pcre.py:51`](../../scripts/check-grep-ere-pcre.py#L51) | Gate 106 cannot see backslash escapes inside bracket expressions or invalid ERE ranges | overlaps #1387 (scripts/check-grep-ere-pcre.py) for the gate half. The three hook-site fixes it absorbed (H-11, H-12, H-14) are not deferred: they ride in PK-6 with H-13. |

## Merged duplicates

- `D-7` → `C-6`
- `H-11` → `H-15`
- `H-12` → `H-15`
- `H-14` → `H-15`

## Appendix — owner-route patches

Apply from the repo root with `git apply <file>` after saving each block. They were written against `6eb60794`.


<details><summary><code>D-16.patch</code></summary>

```diff
--- a/scripts/generate-dashboards.py
+++ b/scripts/generate-dashboards.py
@@ -256,7 +256,7 @@
         # NOW-rendered DOM. Those four were load-time IIFEs; converting them to on-activate
         # named functions is the "gets updated and fixed" work the §0.2 ruling funded.
         # Their existing `if (!panel) return` guards make them safe to never-fire at load.
-        "learn_json": json.dumps(_render_learn_tab(plugin_dir)),
+        "learn_json": json.dumps(_render_learn_tab(plugin_dir)).replace("<", "\\u003c"),
         "saga_html": _render_saga_tab(),
         # panel-commands (~6,308 elements, the 2nd-largest panel) is DOM-island-loaded
         # exactly like panel-trees / panel-learn: its card-grid markup ships in a
@@ -270,7 +270,7 @@
         # calls initLearn()/initConceptSteppers() AFTER mount.innerHTML = ... The
         # <noscript> fallback is a POINTER, never the full markup (html.parser counts
         # elements inside <noscript>, so inlining it there would defeat the island).
-        "commands_json": json.dumps(_render_commands_tab()),
+        "commands_json": json.dumps(_render_commands_tab()).replace("<", "\\u003c"),
         # panel-trees is the single largest panel (~20,612 elements, ~36% of the whole
         # DOM). It is DOM-island-loaded: its markup ships inside a <script
         # type="application/json"> payload (html.parser puts that in CDATA, so its
@@ -281,7 +281,9 @@
         # trees / dt-store / __openPlugin (the couplings the plan flagged). The
         # <noscript> fallback is a POINTER, never the full markup — html.parser counts
         # elements inside <noscript>, so inlining it there would defeat the island.
-        "trees_json": json.dumps(_render_trees_tab(include_trees=include_trees)),
+        "trees_json": json.dumps(_render_trees_tab(include_trees=include_trees)).replace(
+            "<", "\\u003c"
+        ),
         "activity_html": _render_activity_tab(),
         "heimdall_html": _render_heimdall_tab(),
         "vidarr_html": _render_vidarr_tab(),
@@ -9211,7 +9213,9 @@
     path = REPO_ROOT / "plugins" / "ravenclaude-core" / "knowledge" / "host-support.json"
     data = json.loads(path.read_text(encoding="utf-8"))
     data["mcp"] = _mcp_inventory()
-    payload = json.dumps(data, separators=(",", ":"))
+    # D-16: same "<" -> \u003c escape as the other inline payloads, so a
+    # "</script" inside any string cannot close the block early.
+    payload = json.dumps(data, separators=(",", ":")).replace("<", "\\u003c")
     return (
         '<div id="hc-root" class="hc-root"></div>\n'
         "<noscript><p>The host matrix needs JavaScript. The same data is in "
```

</details>

<details><summary><code>FG-1.patch</code></summary>

```diff
--- a/plugins/ravenclaude-core/hooks/guard-premise.sh
+++ b/plugins/ravenclaude-core/hooks/guard-premise.sh
@@ -111,6 +111,10 @@
 [ -z "$_input" ] && exit 0
 
 _dir="${CLAUDE_PROJECT_DIR:-$PWD}"
+# FG-1: the recorder ships NEXT TO this gate. In a consumer install the gate runs
+# from the plugin cache and $CLAUDE_PROJECT_DIR has no plugins/ directory, so the
+# project-relative probe below can never find it.
+_gp_hooks_dir="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd -P || true)"
 
 _verdict="$(printf '%s' "$_input" | python3 -c '
 import hashlib, json, os, re, sys
@@ -524,8 +528,13 @@
     # not wired" (blind). Distinguish by asking whether the recorder EXISTS to be
     # wired. If it is installed but has never run, no tool call has happened yet,
     # so there is no probe to be unresolved -> clean.
-    rec = os.path.join(proj, "plugins", "ravenclaude-core", "hooks", "log-probe.sh")
-    if os.path.exists(rec):
+    # FG-1: look beside this gate first (consumer installs run from the plugin
+    # cache), then the marketplace-relative path (the dev checkout).
+    _hooks_dir = sys.argv[2] if len(sys.argv) > 2 else ""
+    _recs = [os.path.join(proj, "plugins", "ravenclaude-core", "hooks", "log-probe.sh")]
+    if _hooks_dir:
+        _recs.insert(0, os.path.join(_hooks_dir, "log-probe.sh"))
+    if any(os.path.exists(r) for r in _recs):
         sys.exit(0)
     # A BLANKET control file is the recorded, attributed equivalent of
     # RC_PREMISE_OVERRIDE=1 — same power, reachable from a subagent, and it names
@@ -602,7 +611,7 @@
     say("DENY", os.path.basename(path),
         "%s returned %s (%s)" % (e.get("subject"), e.get("label"), e.get("tool")),
         rc_note())
-' "$_dir" 2>/dev/null || true)"
+' "$_dir" "${_gp_hooks_dir:-}" 2>/dev/null || true)"
 
 [ -z "$_verdict" ] && exit 0
```

</details>

<details><summary><code>FG-11.patch</code></summary>

```diff
--- a/plugins/ravenclaude-core/hooks/codex-hook-env.sh
+++ b/plugins/ravenclaude-core/hooks/codex-hook-env.sh
@@ -105,5 +105,8 @@
 export THING_HOST="${THING_HOST:-codex}"
 
 # INVARIANTS 1 + 3 — byte-identical stdin, verbatim exit code.
+# FG-11: take the HOOK's status, not the pipeline's. A hook that exits 0 without
+# reading a large stdin kills printf with SIGPIPE, and pipefail reports 141.
 printf '%s' "$_payload" | "$_hook" "$@"
-exit $?
+_rc_status=("${PIPESTATUS[@]}")
+exit "${_rc_status[1]}"
```

</details>

<details><summary><code>FG-12.patch</code></summary>

```diff
--- a/plugins/ravenclaude-core/scripts/substrate-tier-map.js
+++ b/plugins/ravenclaude-core/scripts/substrate-tier-map.js
@@ -28,10 +28,11 @@
   const blob = data || loadMap();
   const hosts = blob.hosts || {};
   let h = host && String(host).trim() ? String(host).trim() : DEFAULT_HOST;
-  if (!hosts[h]) h = DEFAULT_HOST;
+  const own = (o, k) => Object.prototype.hasOwnProperty.call(o, k);
+  if (!own(hosts, h)) h = DEFAULT_HOST;
   const table = hosts[h];
   let t = tier && String(tier).trim() ? String(tier).trim() : "balanced";
-  if (!table[t]) t = "balanced";
+  if (!own(table, t)) t = "balanced";
   return normalizeRow(table[t]);
 }
```

</details>

<details><summary><code>FG-13.patch</code></summary>

```diff
--- a/plugins/ravenclaude-core/scripts/handoff-spawn.sh
+++ b/plugins/ravenclaude-core/scripts/handoff-spawn.sh
@@ -680,7 +680,7 @@
 delay 0.55
 tell application "System Events"
   tell process "Code"
-    keystroke "$(printf '%s' "$launch" | sed 's/\\/\\\\/g; s/"/\\"/g')"
+    keystroke "$(printf 'bash %s' "$(_shq "$launch")" | sed 's/\\/\\\\/g; s/"/\\"/g')"
     key code 36
   end tell
 end tell
@@ -701,7 +701,7 @@
 delay 0.55
 tell application "System Events"
   tell process "Cursor"
-    keystroke "$(printf '%s' "$launch" | sed 's/\\/\\\\/g; s/"/\\"/g')"
+    keystroke "$(printf 'bash %s' "$(_shq "$launch")" | sed 's/\\/\\\\/g; s/"/\\"/g')"
     key code 36
   end tell
 end tell
```

</details>

<details><summary><code>FG-14.patch</code></summary>

```diff
--- a/plugins/ravenclaude-core/scripts/forge-publish-session-plan.sh
+++ b/plugins/ravenclaude-core/scripts/forge-publish-session-plan.sh
@@ -127,6 +127,17 @@
     if not stat.S_ISREG(st2.st_mode):
         sys.stderr.write("forge-publish-session-plan: dest exists and is not a file: %s\n" % dst)
         sys.exit(2)
+# FG-14: read and validate the source BEFORE opening the destination with
+# O_TRUNC, so an empty or unreadable source never truncates a good copy.
+try:
+    with open(src, "rb") as fh:
+        data = fh.read()
+except OSError as e:
+    sys.stderr.write("forge-publish-session-plan: read source failed: %s\n" % e)
+    sys.exit(2)
+if not data:
+    sys.stderr.write("forge-publish-session-plan: source empty\n")
+    sys.exit(2)
 flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
 if hasattr(os, "O_NOFOLLOW"):
     flags |= os.O_NOFOLLOW
@@ -136,12 +147,9 @@
     sys.stderr.write("forge-publish-session-plan: open dest failed: %s\n" % e)
     sys.exit(2)
 try:
-    with open(src, "rb") as fh:
-        data = fh.read()
-    if not data:
-        sys.stderr.write("forge-publish-session-plan: source empty\n")
-        sys.exit(2)
-    os.write(fd, data)
+    view = memoryview(data)
+    while view:
+        view = view[os.write(fd, view):]
 finally:
     os.close(fd)
 ' "$1" "$2"
```

</details>

<details><summary><code>FG-2_FG-3.patch</code></summary>

```diff
--- a/plugins/ravenclaude-core/hooks/format-on-write.sh
+++ b/plugins/ravenclaude-core/hooks/format-on-write.sh
@@ -132,8 +132,15 @@
     # Undeclared -> silent no-op, even when ruff or black is installed.
     if _up_has 'ruff.toml' '.ruff.toml' || _up_mentions pyproject.toml 'tool\.ruff'; then
       if command -v ruff >/dev/null 2>&1; then
-        run ruff format "$abs"
-        run ruff check --fix --quiet "$abs"
+        # FG-2: a ruff LINT config is not a formatter declaration. Run `ruff format`
+        # only when the project configures ruff's formatter, or a lint-only repo gets
+        # whole-file rewrites on every edit.
+        # FG-3: never apply lint autofixes per edit. `ruff check --fix` removes an
+        # import the agent added one edit before its first use (F401).
+        if _up_mentions ruff.toml '^\[format\]' || _up_mentions .ruff.toml '^\[format\]' \
+          || _up_mentions pyproject.toml '^\[tool\.ruff\.format\]'; then
+          run ruff format "$abs"
+        fi
       else
         _missing ruff
       fi
```

</details>

<details><summary><code>FG-4.patch</code></summary>

```diff
--- a/plugins/ravenclaude-core/hooks/dod-gate.sh
+++ b/plugins/ravenclaude-core/hooks/dod-gate.sh
@@ -118,7 +118,9 @@
 # grep -c matches the extension as a whole-line suffix (not a fixed field), so
 # spaces in the path are irrelevant; -z rename records emit old+new as separate
 # raw records, both scanned — we only need whether ANY changed path is source.
-code_changed="$(git -C "$cwd" status --porcelain=v1 -z 2>/dev/null \
+# -uall: list each untracked FILE; without it a brand-new directory is one
+# "?? dir/" record that never ends in a source extension (FG-4).
+code_changed="$(git -C "$cwd" status --porcelain=v1 -z -uall 2>/dev/null \
   | tr '\0' '\n' \
   | grep -cE '\.(ts|tsx|js|jsx|mjs|cjs|py|go|rs|java|kt|rb|php|cs|swift|scala)$')" || true
 [ "${code_changed:-0}" -eq 0 ] && exit 0
```

</details>

<details><summary><code>FG-5.patch</code></summary>

```diff
--- a/plugins/ravenclaude-core/hooks/remind-tests.sh
+++ b/plugins/ravenclaude-core/hooks/remind-tests.sh
@@ -60,8 +60,9 @@
 # filtering and counting so a "no matches" result doesn't break the
 # pipeline under `set -e -o pipefail` (the previous grep + wc chain did).
 code_changed="$(
-  _git status --porcelain 2>/dev/null \
-    | awk '$2 ~ /\.(ts|tsx|js|jsx|mjs|cjs|py|go|rs|java|kt|rb|php|cs|swift|scala)$/ {n++} END {print n+0}'
+  _git status --porcelain=v1 -z -uall 2>/dev/null \
+    | tr '\0' '\n' \
+    | awk '/\.(ts|tsx|js|jsx|mjs|cjs|py|go|rs|java|kt|rb|php|cs|swift|scala)$/ {n++} END {print n+0}'
 )"
 
 [ "$code_changed" -eq 0 ] && exit 0
```

</details>

<details><summary><code>FG-6.patch</code></summary>

```diff
--- a/plugins/ravenclaude-core/hooks/stream-session-close.sh
+++ b/plugins/ravenclaude-core/hooks/stream-session-close.sh
@@ -65,20 +65,30 @@
     # How many events does this stream already carry? (a derived count only)
     events = m.read_history(root, active)
     count = len(events)
-    # Append a derived session-close marker (no prompt text anywhere).
-    m.append_event(
-        root,
-        active,
-        kind="session_closed",
-        session_id=session_id,
-        summary=f"session ended; {count} event(s) recorded on this stream",
+    # FG-6: Stop fires every turn. Record ONE session_closed per session id; later
+    # Stops only refresh the resume snapshot below.
+    already = bool(session_id) and any(
+        isinstance(e, dict)
+        and e.get("kind") == "session_closed"
+        and e.get("session_id") == session_id
+        for e in events
     )
+    if not already:
+        # Append a derived session-close marker (no prompt text anywhere).
+        m.append_event(
+            root,
+            active,
+            kind="session_closed",
+            session_id=session_id,
+            summary=f"session ended; {count} event(s) recorded on this stream",
+        )
+        count += 1
     # Refresh the resume snapshot so a crash/resume can pick up here.
     m.write_state(
         root,
         active,
         summary=(
-            f"Stream '{active}' had {count + 1} recorded event(s) as of the last "
+            f"Stream '{active}' had {count} recorded event(s) as of the last "
             "session close. Resume by re-activating it: rc streams set-active "
             f"{active}. (This snapshot carries derived labels only — see history.jsonl.)"
         ),
```

</details>

<details><summary><code>FG-7.patch</code></summary>

```diff
--- a/plugins/ravenclaude-core/hooks/spectate-steer.sh
+++ b/plugins/ravenclaude-core/hooks/spectate-steer.sh
@@ -84,6 +84,15 @@
 
 pending = store.read_steer_pending(project, sid) or {}
 event = (os.environ.get("CLAUDE_HOOK_EVENT") or os.environ.get("SPECTATE_EVENT_HINT") or "").lower()
+if not event:
+    # FG-7: native Claude Code passes neither; the event name is in the payload
+    # (spectate-emit.sh detect_event reads the same keys).
+    try:
+        _p = json.loads(os.environ.get("SPECTATE_PAYLOAD") or "{}")
+        if isinstance(_p, dict):
+            event = str(_p.get("hook_event_name") or _p.get("hookEventName") or "").lower()
+    except Exception:
+        event = ""
 event_key = event.replace("_", "").replace("-", "")
 
 paused = bool(pending.get("paused"))
```

</details>

<details><summary><code>FG-8.patch</code></summary>

```diff
--- a/plugins/ravenclaude-core/hooks/worktree-guard.sh
+++ b/plugins/ravenclaude-core/hooks/worktree-guard.sh
@@ -503,10 +503,28 @@
 # Resolve a path for FOREIGN-TREE. An existing directory (git -C <worktree>)
 # is itself. A file or a not-yet-created path walks to the nearest existing
 # ancestor (same walk as _wg_path_under_tree).
+# FG-8: collapse "." and ".." LEXICALLY, as the host's file tools do (Node
+# path.resolve), before probing the filesystem. Otherwise "new/../../sibling/x"
+# walks up from the not-yet-created "new" and resolves to THIS tree.
+_wg_lexnorm() {
+  local part out=() parts=()
+  IFS=/ read -r -a parts <<<"$1"
+  for part in "${parts[@]}"; do
+    case "$part" in
+      ""|.) ;;
+      ..) [ "${#out[@]}" -gt 0 ] && unset "out[$((${#out[@]} - 1))]" ;;
+      *) out+=("$part") ;;
+    esac
+  done
+  local IFS=/
+  printf '/%s' "${out[*]}"
+}
+
 _wg_resolve_existing() {
   local p="$1" d parent rp
   [ -n "$p" ] || return 1
   case "$p" in /*) d="$p" ;; *) d="$cwd/$p" ;; esac
+  d="$(_wg_lexnorm "$d")"
   if [ ! -d "$d" ]; then
     d="$(dirname "$d")"
     while [ -n "$d" ] && [ ! -d "$d" ]; do
```

</details>

<details><summary><code>FG-9.patch</code></summary>

```diff
--- a/plugins/ravenclaude-core/scripts/handoff-nudge.py
+++ b/plugins/ravenclaude-core/scripts/handoff-nudge.py
@@ -36,6 +36,7 @@
 import json
 import os
 import re
+import shlex
 import sys
 import time
 from datetime import datetime, timezone
@@ -352,20 +353,23 @@
         # The nudge states the cost honestly, names /compact as the default, and
         # walks a four-step procedure (write -> detached fill -> finalize -> compose) so the
         # brief is a real artifact rather than advice nobody acted on.
+        # FG-9: cite the script that is actually installed (plugin cache in a
+        # consumer repo), not the marketplace-relative path.
+        _ch = shlex.quote(str(HERE / "context-handoff.py"))
         ctx = (
             f"Context is hot (~{pct}% used; soft threshold {threshold}%, "
             f"auto-compact ~{auto_txt}). DEFAULT: /compact and keep going — "
             f"compaction appends, it does not delete the transcript (pre-boundary "
             f"turns and thinking blocks are retained). Before compacting, run this "
             f"4-step procedure once: "
-            f"(1) `python3 plugins/ravenclaude-core/scripts/context-handoff.py write "
+            f"(1) `python3 {_ch} write "
             f"--task-id {task_id} --host <this-host-pair>` to produce handoff.md + "
             f"handoff-seed.txt — no egress, no cheap-lane call, no "
             f"precompact-digest.py involvement of any kind. "
-            f"(2) `python3 plugins/ravenclaude-core/scripts/context-handoff.py fill "
+            f"(2) `python3 {_ch} fill "
             f"--task-id {task_id}` — detached fit-tier fill (default haiku) of the eight "
             f"MODEL FILL sections; do NOT burn the session model on extract/format. "
-            f"(3) `python3 plugins/ravenclaude-core/scripts/context-handoff.py "
+            f"(3) `python3 {_ch} "
             f"finalize --task-id {task_id}` to re-scrub and re-chmod the file now "
             f"that the sensitive content actually exists. "
             f"(4) Compose the /compact steering text yourself, in this same turn, "
```

</details>

---
_Autonomous review. Panel artifacts (Panel 1 findings, Panel 2 validation, Panel 3 canonical list) are in the session scratch space, not committed._
