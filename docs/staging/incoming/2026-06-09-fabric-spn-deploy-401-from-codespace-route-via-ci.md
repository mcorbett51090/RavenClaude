<!-- RAVENCLAUDE-STAGING-METADATA
type: lesson
topic: power-platform
proposed-by: consumer engagement — Fabric/PBIP deploy from a GitHub Codespace via a service principal (Copilot CLI session)
proposed-on: 2026-06-09
target-file: plugins/power-platform/knowledge/fabric-deploy-from-codespace-route-via-ci.md
status: pending
-->

## 2026-06-09 — A Fabric SPN deploy that 401s from a Codespace deploys fine from the CI runner

**Context:** Deploying a regenerated PBIP `definition/` to a Fabric workspace using a service principal (SPN) whose secret is present in the Codespace as `AZURE_CLIENT_ID` / `AZURE_TENANT_ID` / `AZURE_CLIENT_SECRET`.

**What we tried first:** Ran the deploy script directly from the Codespace terminal against the Fabric API.

**Why it failed:** The call returned HTTP **401 Unauthorized** even though the SPN is authorised for the workspace and the same credentials succeed from CI. **The exact cause is `[unverified]`.** A 401 is an auth-token *rejection*, not a generic network failure — so do NOT codify "it's a network/routing-layer issue" as fact. The likely real culprits, in order to check: (a) a **token audience/scope mismatch** (decode the acquired token and inspect `aud` / `scp` — it must target the Fabric/Power BI resource, not Graph or ARM); (b) a **conditional-access / IP policy** that rejects the Codespace's egress IP while allowing the CI runner's; (c) a stale/rotated secret that differs between the two environments. Confirm before asserting a cause.

**What works:** Route the deploy through the **GitHub Actions runner** instead of the Codespace. Commit the regenerated `definition/` and push to the default branch; the deploy workflow (`.github/workflows/deploy-*.yml`) triggers and deploys successfully using the SAME SPN credentials from the runner. The runner's egress + token context satisfy whatever the Codespace's did not.

**How to apply:**
- When an SPN call works in CI but 401s from a Codespace, don't retry the same surface — route the deploy through the CI runner (push-to-branch → Actions workflow).
- Before pushing: regenerate the build output, `git add -A` (include ALL generated artifacts — e.g. every generated `visual.json`), push, and monitor the Actions run.
- Separately, diagnose the real 401 cause (decode the token's `aud`/`scp`; check conditional-access IP policy) rather than assuming the network — see the power-platform `dataverse-token-acquisition.md` token-decode discipline and "read the error before you re-route."

**Trace:** Consumer Fabric/PBIP deploy engagement (generalized; org/repo identifiers removed). The unverified root-cause is flagged deliberately per the marketplace's claim-grounding discipline; the durable, verified lesson is the CI-runner route + "diagnose the 401, don't assume it's the network."
