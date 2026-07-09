# G1 — Claims table (fact-verification gate)

All external claims verified against Microsoft Learn in-session on **2026-06-30**.

| # | Claim | Tier | Source / marker | Settling gate |
|---|-------|------|-----------------|---------------|
| 1 | `pac solution import` supports `--activate-plugins`/`-ap` ("Activate plug-ins and workflows on the solution") | BLOCK | ✅ [pac solution reference](https://learn.microsoft.com/power-platform/developer/cli/reference/solution#pac-solution-import) (2026-06-30) | settled |
| 2 | `pac solution import` supports `--publish-changes`/`-pc` ("Publish your changes upon a successful import") | BLOCK | ✅ same source | settled |
| 3 | `pac solution import` supports `--settings-file` (".json with deployment settings for connection references and environment variables") | BLOCK | ✅ same source | settled |
| 4 | `pac solution import` supports `--force-overwrite`/`-f` ("Force an overwrite of unmanaged customizations") | BLOCK | ✅ same source | settled |
| 5 | **Microsoft DISCOURAGES `--publish-changes` for managed solutions and `--force-overwrite` generally** (both "slow down the deployment"; publish-all "shouldn't be used for managed solutions") | BLOCK | ✅ [Performance recommendations](https://learn.microsoft.com/power-platform/alm/performance-recommendations) (2026-06-30) | **G4a/G6 — recipe must make these opt-in, not always-on** |
| 6 | Importing a solution turns its flows off and on again ("the flows in that solution are turned off and turned on again") | BLOCK | ✅ [Import a solution FAQ](https://learn.microsoft.com/power-automate/import-flow-solution#faq) (2026-06-30) | settled |
| 7 | Platform auto-reactivation is CONDITIONAL: only "if the flows were on when exported AND any connection references get connections" — and the importing user must have permission to all connections to turn flows on | BLOCK | ✅ same FAQ + [share connections](https://learn.microsoft.com/power-apps/maker/data-platform/create-connection-reference) | **G6 — reframes the premise: explicit reactivation needed when SPN/CI conditions unmet** |
| 8 | For an UPDATE to an already-existing flow, import does not change its state ("if the flow is turned off in the target environment and an update is imported, the flow remains turned off") | BLOCK | ✅ same FAQ | settled — **validates baseline-aware targeting** |
| 9 | The supported programmatic flow-state API is the Dataverse Web API; `api.flow.microsoft.com` is explicitly unsupported | BLOCK | ✅ [Work with cloud flows using code](https://learn.microsoft.com/power-automate/manage-flows-with-code#import-flows) (2026-06-30) | settled — script PATCHes Dataverse Web API (correct) |
| 10 | After import, all solution components are owned by the importing identity (relevant to SPN ownership/impersonation) | BLOCK | ✅ [Import a solution](https://learn.microsoft.com/power-automate/import-flow-solution) (2026-06-30) | settled |
| 11 | Cloud flows are `workflow` rows with `category=5`; `statecode=1`=Activated, `0`=Draft; reactivate via PATCH statecode/statuscode | BLOCK | [unverified — training knowledge; widely-documented Dataverse schema, Contoso verified empirically]. Justification: schema enum not surfaced in this session's searches; route to verify = Dataverse `workflows` metadata or a live `pac`/Web API query | G5/G8 — note as `[unverified]`; script must tolerate schema variance |
| 12 | `ConnectionAuthorizationFailed` (403) occurs when activating a flow whose connection reference isn't yet bound/propagated; retry-after-propagation succeeds | BLOCK | [unverified — training knowledge + Contoso empirical]. Consistent with claim 7 (connection-permission gating). Route to verify = reproduce in a real env | G5 — red-team treats as the primary retry trigger |
| 13 | power-platform plugin ships 22 skills, zero `scripts/`, and `.repo-layout.json` already allows `plugins/*/scripts/**` | WARN (repo-structural, confirmed in-session) | ✅ `ls`/`wc`/`python3` this session | settled |
| 14 | power-platform CLAUDE.md already mandates `security-reviewer` sign-off for any shipped code handling SPN secrets | WARN | ✅ `grep` CLAUDE.md §~303 this session | settled — security pass is mandatory, not optional |

## Net effect on the plan

G1 caught a **correlated error in the source material**: Contoso's recipe hardcodes `--publish-changes`
and `--force-overwrite` as standing rules, but Microsoft's performance guidance discourages both for
managed imports. The generalized plugin recipe must default to `--activate-plugins` + `--settings-file`
(both confirmed-good) and treat `--publish-changes`/`--force-overwrite` as **deliberate, documented
opt-ins** — not always-on. G1 also sharpened the central premise (claim 7): automatic reactivation is
conditional, and the explicit reactivation pass earns its keep specifically in **SPN-driven CI/CD**
where those conditions aren't met at import time. Both findings flow into the panel briefs.
