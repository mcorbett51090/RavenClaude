# Gap-delta — Panel A (opus/architect) vs Panel B (sonnet/skeptic) + G1 facts

## Strong convergence (both, independently) — the settled core
- **Topology:** the static HTML SPA is a **dumb client** (holds no secret); a **hidden backend** runs the Agent SDK + the repo checkout + the dev server, and **reverse-proxies the dev server under the studio's OWN domain** so the live-preview iframe is **same-origin + sandboxed** (dodges the CORS trap) — and nothing ever looks like a Codespace/editor.
- **Codespace forwarded ports are NOT a viable backend** (public = unauth'd Claude compute; private = CORS/302-preflight-blocked from a Pages origin; 30-min idle stop). MVP-for-Matt only, never the product host.
- **Agent SDK is the engine** (headless, streaming, file/git/bash tools, sessions) — don't rebuild Claude Code. **API-key auth required** for any non-personal use (claude.ai login is forbidden for 3rd-party products).
- **GitHub App** (not OAuth/PAT) for repo selection: user-picks-repos, 1-hour scoped install tokens, `/installation/repositories`, commit to `studio/*` branch + PR.
- **Live-reload** = the repo's own dev-server HMR (Vite/Next/Evidence) into the iframe; same-origin.

## Divergences + resolution
| # | Panel A | Panel B | Resolution (for synthesis) |
|---|--------|--------|----------------|
| 1 **Already built?** | Under-weighted; planned a backend MVP | **~65% exists**: Claude Code web (repo→sandbox→PR) + **Artifacts** (live-updating sandboxed HTML preview) + Claude Design. Net-new = skin + dev-server + iframe-bridge + commit-back. | **B.** Lead with the cheapest validation: try **Artifacts-as-preview** (Alt-A) + a **Phase-0 localhost proof-of-loop** BEFORE building any backend. |
| 2 **Security** | Reuse comfort-posture + tribunal + worktree | **Insufficient** — Claude running bash on an arbitrary repo is a NEW threat model: `postinstall` RCE, secret-exfil, cost-blowout. | **Synthesis:** reuse the existing controls as the BASE **+ add container-specific controls** — network-egress restriction, `npm install --ignore-scripts`, secret-scan gate before session start, per-session token-budget hard stop, ephemeral per-session container. New threat-model doc before any multi-tenant stage. |
| 3 **Scope ambition** | Linear MVP→artifact→**product** | Phase 3 (multi-tenant SaaS) **premature** per the consulting-first model; Phase 2 conditional on Phase-1 regular use. | **B.** Cap the plan at Phase 1 (personal) → Phase 2 (artifact, *conditional*). Phase 3 = a company decision, explicitly deferred, not designed-for now. |
| 4 **Backend lifecycle** | "Small always-on container" | **On-demand per-session** containers (Fly machine API), destroyed on idle. | **B** for cost/isolation; A's always-on is acceptable for the single-user MVP only. |
| 5 **Front-end host** | Pages (or backend-served) | Notes **Electron (Alt-C)** sidesteps cross-origin entirely; edge host (Cloudflare/Vercel) for an OAuth-callback serverless fn. | **User constraint wins:** they explicitly want an HTML **web page on Pages** → web, not Electron (record Electron as a rejected-by-constraint alt). Use an edge host only if a serverless OAuth callback is needed. |

## Correlated-error candidates (for the critic — where BOTH may agree on something wrong)
- Both assume **HMR-through-reverse-proxy-into-a-sandboxed-iframe actually repaints live** — neither PROVED it (A names it the #1 risk; B calls it "the iframe bridge"). Shared load-bearing unverified mechanism.
- Both assume **the live-build-watch experience is worth a custom studio at all** vs. just composing Claude Code web + Artifacts (B gates on it; A assumes it). Is the premise validated?
- Both treat **"websites + dashboards" as one preview problem** — B flags dashboards-need-data may be unsolvable generically; is even the *website* live-preview as clean as assumed?
