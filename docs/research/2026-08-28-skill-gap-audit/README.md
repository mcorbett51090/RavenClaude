# Monthly skill-gap audit — 2026-08-28

Closes the *research* half of [#821](https://github.com/mcorbett51090/RavenClaude/issues/821). Adding a chosen skill is a separate plugin PR. **Matt still decides** which (if any) to author; “no gaps worth filling this month” is a valid close.

**Scope this run:** the seven plugins named in the issue prompt, plus a marketplace-wide census. The issue text still says “all 7 plugins”; the marketplace now has **182** plugins / **621** agents / **936** skills.

**Method:** `deep-researcher` per plugin (2026-08-28). HIGH = named in the agent *description* **and** a scenario, with zero `SKILL.md`. MEDIUM = partial coverage or command/template-only. Skip domain-policy (knowledge) and ravenclaude-core duplicates.

**Census (whole marketplace):** **0** plugins have agents and zero skills. Nine plugins have fewer skills than agents (`azure-cloud`, `construction-general-contractor`, `field-service-management`, `microsoft-365-copilot`, `microsoft-fabric`, `public-sector-govtech`, `regulatory-compliance`, `retail-store-operations`, `supply-chain-planning`) — that ratio is a *lead*, not a gap by itself.

## Recommended triage

If only a few skills ship this month, in this order:

| Pri | Plugin | Proposed skill | Why |
|---|---|---|---|
| 1 | power-platform | `platform-testing` | `power-platform-tester`’s whole job has no playbook (Test Studio / fixtures / `pac solution check`). |
| 2 | power-platform | `tenant-licensing-and-capacity-audit` | Admin scenario 2 (licensing + capacity table) is a best-practice sentence, not a method. |
| 3 | data-platform | `evidence-dev-scaffolding` | Case A starter scenario; Cube already has a skill, Evidence does not. |
| 4 | data-platform | `airbyte-cdk-authoring` | Promote `/build-incremental-connector` + BPs into an *agent-consumed* skill (do not write a third copy). |
| 5 | edtech-partner-success | `ferpa-comms-translation` | Translator’s core job is command-only; other function agents have command **and** skill. |
| 6 | web-design | `usability-heuristic-review` | UX starter scenario 3; `conversion-design` is conversion-only. |
| 7 | web-design | `site-copy-authoring` | Content starter scenario 1; style-guide template exists, no authoring playbook. |
| 8 | regulatory-compliance | `compliance-policy-authoring` | Policy writer scenarios 1+3 are command-only. |
| 9 | finance | `covenant-compliance` | Treasury scenario 2; 13-week cash is a different artifact. |

**Do not add this month unless you pick them:** finance `fx-hedge-design` / `409a-valuation`; web-design shadcn G5; regulatory TM-tuning / BSCR workpaper; core `log-pii-audit`.

**Prefer extend-or-wire over new files:** complete advertised-but-missing resources in `power-bi` and `power-automate`; add inline-priors from six *core* agents to existing sibling skills (flake, idempotency, CWV, STRIDE, a11y, dbt). Those are not new skills.

## Per-plugin verdicts

### ravenclaude-core (15 agents / 56 skills)
**No HIGH new-skill gaps.** Real hole is **missing inline-priors** from `tester-qa`, `backend-coder`, `frontend-coder`, `security-reviewer`, `designer`, `data-engineer` to sibling playbooks that already exist. One optional MEDIUM new skill: `log-pii-audit` (security-reviewer scenario 3; `pseudonymize` is the wrong tool).

### power-platform (11 / 23)
**HIGH:** `platform-testing`, `tenant-licensing-and-capacity-audit`. **MEDIUM (not new skills):** `power-bi` and `power-automate` `SKILL.md` files advertise four resource files that are **not on disk**. **MEDIUM new:** `custom-connector-authoring`, `canvas-component-libraries`. Six agents have no HIGH/MEDIUM gap.

### edtech-partner-success (6 / 16)
**HIGH:** `ferpa-comms-translation` (slash command exists; other agents cannot invoke it). **MEDIUM:** `partner-profile-curation` (stakeholders already in `executive-sponsor-mapping`). Other four agents map 1:1 onto existing skills. CLAUDE.md §8 omits `daily-action-queue` and `psm-dashboard-build` (docs-sync, not a gap).

### data-platform (4 / 13)
**HIGH:** `evidence-dev-scaffolding`, `airbyte-cdk-authoring` (promote the existing command). **MEDIUM:** spreadsheet→DB; MAR mitigation as a subsection of `connector-configuration`; embed *tool wiring* as a subsection of `jwt-embed-issuance`. June 2026 “skills SUFFICIENT” row is still right for dbt/RLS/Cube/JWT — not for Evidence or CDK-as-agent-consumed.

### finance (7 / 23)
**HIGH:** `covenant-compliance`, `fx-hedge-design`, `409a-valuation`. **MEDIUM:** comps/precedent playbook, PBC cadence, deficiency-remediation (prefer extend `soc-control-walkthrough`), model-refactor. `fpa-analyst`, `board-pack-composer`, and controller top-3 are already skilled. Several agents do not *link* skills they already consume (wiring).

### regulatory-compliance (12 / 10)
**HIGH:** `compliance-policy-authoring`. **MEDIUM:** `transaction-monitoring-tuning`, `bscr-capital-workpaper`. Five jurisdiction specialists are knowledge-backed — do **not** add BMA-style classification skills for Cayman/Bahamas/CI/UK/US.

### web-design (7 / 13)
**HIGH:** `usability-heuristic-review`, `site-copy-authoring`. **MEDIUM:** shadcn/G5 dispatch (new thin skill **or** seam to `frontend-engineering/react-component-craft`), SEO content briefs (prefer extend `content-audit`), re-platform go/no-go memo. a11y / perf / visual-designer scenarios already skilled. Wireframing is core `wireframe` — skip.

## Open questions for Matt

1. Treat slash commands as “good enough playbooks”? If yes, FERPA and policy-authoring drop HIGH → LOW.
2. Is Case A (Evidence.dev) still an active engagement shape? If idle, drop data-platform HIGH-1.
3. Inline-priors on core agents — in-scope for this audit’s “skills to add,” or a separate wiring PR?
4. Close #821 as “no skills this month” vs pick from the priority table.

## What this audit did not do

- Did not live-spawn the agents.
- Did not audit the other 175 plugins (census only).
- Did not author any `SKILL.md`.
