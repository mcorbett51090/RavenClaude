# Fabric SPN deploy 401s from a Codespace but succeeds from CI — triage the token, don't just switch runners

> **Last reviewed:** 2026-09-11. Source: consumer Fabric/PBIP deploy engagement, 2026-06-09 (Copilot CLI session; org/repo identifiers removed). The root cause was never confirmed in that engagement — this file documents the triage checklist and the stopgap that unblocked the deploy, not a diagnosed fix. Refresh this file the first time someone actually confirms which of the three candidate causes below was real; until then, treat the whole "Codespace vs CI" framing as a symptom description, not a root-cause claim.
>
> **Claim-grounding note.** `[unverified]` applies to the entire causal explanation in this file. What is verified: the SPN, the target Fabric workspace, and the deploy payload were identical between the Codespace attempt and the CI attempt; the Codespace attempt returned HTTP 401 and the CI attempt succeeded. What is NOT verified: which specific difference between the two execution contexts caused the 401. Do not read "route through CI" as a confirmed fix — it is a working-in-practice stopgap for one engagement.
>
> **When to read this file.** A Fabric (or other Azure-AD-token-gated) deploy fails with 401 from one execution environment (a Codespace, a local dev box) using a service principal that is known-good in another (a CI runner) — same SPN, same target resource, same payload. Use this as a triage checklist before concluding "the network/routing layer is broken" or assuming a permanent fix requires abandoning the Codespace route.

---

## The symptom

A deploy script pushes a regenerated PBIP `definition/` to a Fabric workspace using a service principal whose secret is present as environment variables (e.g. `AZURE_CLIENT_ID` / `AZURE_TENANT_ID` / `AZURE_CLIENT_SECRET`). Run from inside a GitHub Codespace terminal, the call returns **HTTP 401 Unauthorized**. Run with the identical credentials from a GitHub Actions runner, it succeeds.

A 401 is an auth-token **rejection**, not a generic network failure — the token was presented and refused, or no valid token was acquired at all. Don't codify "it's a network/routing-layer issue" as fact from this symptom alone; a 401 says the auth layer said no, and there are several distinct reasons it might.

## Triage checklist — run these before touching the deploy route

In order of cheapest-to-check:

1. **Token audience/scope mismatch.** Decode the acquired token (a JWT — paste into any offline JWT decoder, or use `jwt` CLI / `python -c` with `base64`) and inspect `aud` and `scp`/`roles`. It must target the Fabric/Power BI resource (`https://analysis.windows.net/powerbi/api` or the equivalent Fabric API resource ID), not Microsoft Graph or Azure Resource Manager. A token acquired against the wrong resource is a 401 with everything else looking correct.
2. **Conditional-access / IP allow-list policy.** If the tenant's Azure AD Conditional Access rules (or the Fabric workspace's network policy) restrict sign-in by source IP or network location, a Codespace's egress IP can be rejected while a GitHub-hosted runner's IP range is allowed (or vice versa) — check with whoever administers Conditional Access for the tenant.
3. **Stale or rotated secret that differs between environments.** Confirm the `AZURE_CLIENT_SECRET` value actually loaded in the Codespace matches the one CI uses — a Codespace secret can silently go stale (rotated in one place, not refreshed in the other). Cross-check secret update timestamps, not just that a variable is set.

Confirm one of these (or something else entirely) **before** asserting a cause. See also `dataverse-token-acquisition.md` for the general token-decode discipline this checklist borrows from — the same "decode before you diagnose" rule applies to any Azure-AD-gated API, not just Dataverse.

## The stopgap that worked (not a fix)

Routing the deploy through a GitHub Actions runner instead of the Codespace unblocked this engagement: commit the regenerated `definition/` (including every generated artifact — e.g. every generated `visual.json`), push to the default branch, and let the deploy workflow (`.github/workflows/deploy-*.yml`) run using the same SPN credentials from the runner.

Treat this as a **stopgap**, not a resolution: it changes the execution context enough to route around whichever of the three candidates above was actually the cause, without identifying which one it was. If the underlying cause is (2) a Conditional Access IP policy, this stopgap works indefinitely (CI's IP range is durably allow-listed). If the underlying cause is (3) a stale secret, this stopgap only works until the CI-side secret also goes stale, at which point both routes 401 and the "just use CI" workaround stops being available at all.

## How to apply

- When an SPN call works in CI but 401s from a Codespace (or any other environment), don't retry the identical call expecting a different result — but also don't jump straight to "route around it" without running the triage checklist above at least once.
- If you do route around it as a stopgap, say so explicitly in the deploy runbook — future readers need to know this is masking an undiagnosed cause, not documentation of an intentional architecture choice.
- Regenerate build output and stage every generated artifact before pushing (`git add -A` scoped to the output directory) — a partial commit of generated files is a separate, unrelated failure mode that looks similar (deploy runs, output is stale) but has nothing to do with the 401.

## Edge cases / when this checklist does not apply

- If the 401 also reproduces from CI (not just from the Codespace), this is not an environment-parity problem — the SPN itself lacks a role assignment or the app registration is misconfigured; that's a permissions problem, not a triage-the-token problem.
- If the error is 403 rather than 401, the token was accepted but the principal lacks authorization for the specific action — a different, more specific class of problem than "which environment produced a rejected token."

## Provenance

Consumer Fabric/PBIP deploy engagement, 2026-06-09: a deploy from a GitHub Codespace 401'd while the identical SPN succeeded from a CI runner. The engagement routed around the problem via CI rather than confirming the root cause; this file exists to give the next occurrence a triage order to run through before repeating that same unconfirmed workaround. Generalized; org/repo identifiers removed. Revised 2026-09-11 during promotion from staging to make explicit that "route via CI" is a stopgap, and to reframe the file as a triage checklist rather than a diagnosed fix.

---

_Last reviewed: 2026-09-11 by consumer-project session_
