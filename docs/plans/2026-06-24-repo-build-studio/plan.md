# FORGE plan — "Repo Build Studio" (verdict: COMPOSE-EXISTING; build-thin only on demonstrated need; do NOT build the product)

## The honest headline
The dream is "a Claude-Design-style page where you pick a repo, prompt Claude, and watch a site/dashboard render live + commit back." FORGE's verdict after two panels + a fact-check + an adversarial critic: **most of it already exists, the one part that would justify a custom build is the least-buildable + most security-expensive part, and the business model doesn't want the product.** So the plan is mostly *compose existing surfaces*, not *build an app*.

## The correlated blind spot the critic caught (why the obvious build is a trap)
Both panels independently canonized the live-preview mechanism as "**same-origin (to dodge CORS) + sandboxed (it's untrusted Claude-generated code) iframe, fed by the repo's HMR through a reverse proxy**" — and that is **self-canceling**:
- An `iframe sandbox` with BOTH `allow-scripts` + `allow-same-origin` can script-remove its own sandbox and reach the parent — WHATWG/MDN say *don't ship it*. You get CORS-free same-origin **or** a real sandbox around untrusted code, not both. `[verified this session — MDN/WHATWG]`
- HMR through a path-rewriting proxy is per-framework fragile and **falls back to connecting directly to the origin dev server, bypassing the proxy** — exactly the assumption a Pages front-end can't satisfy. Makeable per-repo, not generically. `[verified — Vite #6473]`
Agreement was read as validation; neither panel ran the check. **The signature "watch it repaint live" feature has the lowest probability of working generically and the highest security cost when it does.**

## What already exists (so don't rebuild it) `[verified this session]`
- **Claude Code on the web** (claude.ai/code): repo-clone → isolated **Anthropic-managed** cloud sandbox → branch → **PR**, sessions persist. This is the entire "connected on the backend, Claude runs it, commits back" spine — already hosted + secured, and the `npm install` runs **off your machine**.
- **Artifacts**: a live-updating sandboxed HTML preview — but **no network egress beyond CDN** (can't hit your API/DB), self-contained pages only.
- **Claude Design**: chat+canvas live render — but **read-only**, no commit-back.
- **The Willison pattern (the smoking gun):** point Claude Code web at a repo → "build a **self-contained HTML file, vanilla JS, no build step, CDN deps**" → it pushes a branch → point **GitHub Pages at that branch** → the rendered page previews live (updates on each push) → PR. **This IS the Phase-1 success signal, assembled from existing parts, $0 build, no Codespace UI, commits back.** Its only gap vs the dream is in-place HMR — which §"blind spot" shows the custom build can't reliably beat.

## The plan (three tiers; each stands alone; ambition descends, not ascends)

### Tier 0 — COMPOSE-EXISTING (do now; ~1 day; zero backend, zero hosting, zero new attack surface) ★ recommended
Ship a RavenClaude **skill + runbook** — `repo-build-studio` (or fold into `website-design`/`data-platform`): the Willison loop, productized as guidance + a thin starter.
- The runbook: open Claude Code on the web → pick repo → prompt with the **self-contained-HTML constraint** → branch → **GitHub Pages preview** → PR. (Optionally: use **Artifacts** for the in-chat live-repaint feel on self-contained pages.)
- A **template repo** preconfigured for it (Pages-from-branch wired, a `studio/*` branch convention, a self-contained-HTML scaffold for both a marketing page and a static dashboard).
- Covers the **website + self-contained-dashboard** case completely, today.
- **Deliverable:** a skill `SKILL.md` + a knowledge runbook + the template. **Acceptance:** Matt opens it, picks a repo, prompts, sees the page render via Pages, and a PR lands — with no custom infra.

### Tier 1 — BUILD-THIN, PERSONAL-ONLY (only on *demonstrated* need: a real **data-connected dashboard** the static path can't show)
Trigger condition: Matt repeatedly hits the wall where a dashboard needs **live data** (a DB/API) the self-contained/Artifacts path can't render. Only then:
- **Studio HTML served same-origin FROM the backend** (NOT Pages → real same-origin, so the iframe needs no faked sandbox-and-same-origin; the preview origin is genuinely the studio's). Single user (Matt), his own key.
- **Agent SDK** headless engine in an **ephemeral, network-egress-allow-listed container per session**, destroyed on idle. `npm install --ignore-scripts` by default. **No host secrets in the container** — mint a **short-lived scoped GitHub App token into the session**, never a PAT/API key in env. **Secret-scan gate before the install.**
- Security envelope = existing comfort-posture + tribunal (high-blast→defer on commit/push) + `new-worktree` **+ the new container controls above**.
- Live-preview: **"supported frameworks only"** (Vite/Next/Evidence with pinned HMR client config) OR a coarse file-watch→`location.reload()` fallback. Do **not** promise generic HMR.
- **Riskiest assumption to spike first (1 day) IF pursued:** same-origin-served HMR repaint in a sandboxed-by-isolation (not by-attribute) container — but prefer the Willison/static path; this tier exists only for the data case.

### Tier 2 — THE PRODUCT (multi-tenant SaaS studio) — **KILLED, not deferred**
Fails on both axes: (a) feasibility — the live-preview signature is the unreliable part + multi-tenant turns the `npm install` RCE/secret-exfil/cost surface into a real SaaS-security project; (b) business — consulting-first (RavenClaude = proof-of-craft; the website is a consulting front-door; ~$25–50k engagements, SaaS is a long bet). **Do not design for it now.** Revisit only if Tier 0/1 generate concrete paying demand.

## Risk matrix (critic + red-team, deduped)
| # | Risk | P×I | Mitigation / kill-criterion |
|---|---|---|---|
| R1 | Live HMR doesn't repaint generically (sandbox-vs-same-origin paradox + per-framework proxy fragility) — the signature feature | H×H | **Kill:** if the Willison static-Pages preview satisfies the real need, never build the HMR path. If built: same-origin-served + per-framework pinned config + "supported frameworks," not "any repo." |
| R2 | **First `npm install` of a real repo = arbitrary code execution** (npm lifecycle hooks; Shai-Hulud/Mastra 2025–26) — bites the **personal** MVP | H×H | Ephemeral egress-allow-listed container, `--ignore-scripts`, no host secrets (scoped token into session), secret-scan gate. **Or compose-existing — Claude Code web runs install in Anthropic's sandbox off your machine.** Threat-model doc **before the first real-repo install**. |
| R3 | Premise already shipped (~65%: CC-web + Artifacts + Pages) → custom build is sunk effort | H×M-H | Adopt Tier 0; kill Tier 2. |
| R4 | Dashboards-need-data unsolvable generically (a preview can't invent the data plane) | M-H×M | Split website (Tier 0) from data-dashboard (Tier 1-only, on need); route the data plane to `data-platform`. |
| R5 | Codespace forwarded port as backend (public=unauth Claude compute; private=CORS-blocked from Pages; 30-min idle) | H×H (if attempted) | Already rejected; Tier 1 serves same-origin from a real container, never a CS port. |
| R6 | Cost/runaway blowout | M×M-H | Per-session hard token budget + idle teardown; CC-web already meters this (Tier 0 win). |

## Alternatives considered
- **Compose-existing (Willison: CC-web + Pages-branch-preview + PR)** — Tier 0, recommended. 80%+ of the value, ~0 build, no new attack surface.
- **Artifacts-as-preview** — in-chat live repaint for self-contained pages; pairs with Tier 0; no network egress (no data dashboards).
- **Own backend container + Agent SDK + reverse-proxy** — Tier 1, only for the data case, personal-only, same-origin-served.
- **Electron desktop app** — sidesteps cross-origin entirely; **rejected by the user's constraint** ("an HTML page... uses Pages" → web, not desktop).
- **Codespace forwarded port backend** — rejected (R5).
- **Claude Code Web as the engine with a skin** — rejected (Anthropic branding terms forbid it + it's an editor surface).

## Definition of done
- **Tier 0 skill/runbook + template:** `SKILL.md` (≤300-char descriptions where agent frontmatter applies; scenario schema if an agent), knowledge runbook, template repo; `audit-gates.sh` green; layout-allow-list updated; version bump; **no new infra/secrets**. Migration: none.
- **Tier 1 (only if triggered):** the threat-model doc lands **first**; the HMR same-origin spike passes or the file-watch fallback is accepted; `security-reviewer` signs off the container + iframe boundary; per-session budget + egress allow-list verified.
- **Tier 2:** explicitly out of scope.

## Honest scope
FORGE's value here was **not greenlighting a build**: it found the signature feature is a self-canceling design, that the spine already ships, and that the real risk (supply-chain `npm install`) bites the personal MVP. The recommendation is to **compose what exists into a skill (Tier 0) now**, build the thin personal studio **only** for the data-dashboard case on demonstrated need (Tier 1, with the supply-chain threat model first), and **not build the product**.
