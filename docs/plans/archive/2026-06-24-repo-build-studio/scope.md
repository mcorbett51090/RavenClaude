# G0 — Scope: "Repo Build Studio" (a Claude-Design-style build surface)

## The idea (user, verbatim intent)
A web page — looking and feeling like **Claude Design's** chat-at-bottom-right + **live-preview frame on the right** — where the user **selects a GitHub repo and prompts Claude**, and as Claude builds a visual element (a website or a reporting dashboard) it is **visualized live, before your eyes**. GitHub Pages "surfaces" it; the repo is "connected on the backend"; the compute is "a Codespace running Claude."

## G0 decisions
- **Topology: recommend it — but a HARD UX constraint:** *it must NOT look like a Codespace.* The **custom HTML page is the entire surface** the user interacts with. Any Codespace/Agent-SDK/server compute that runs Claude is **headless and hidden** behind that page. (Crux fact to respect: **GitHub Pages is static — it cannot run Claude**; the live-build compute lives elsewhere and the page talks to it.)
- **Scope: all of the above, staged** — MVP for Raven Power (personal) → a reusable RavenClaude artifact (template repo + thin plugin/skill: "open → pick a repo → prompt → watch it build") → a standalone/sellable studio. Plan must layer so each stage stands alone.
- **First preview surface: both websites + dashboards** — the preview renders any served HTML/app (a marketing site OR a reporting dashboard), since both are "a dev server the backend runs."

## The architecture question the panels must resolve (the feasibility crux)
How does a **static, Pages-hosted HTML front-end** drive a **hidden Claude backend that has the repo + git + a live dev server**, while staying secure and not "looking like a Codespace"? Candidate shapes the panels must weigh:
1. **Pages = thin launcher; the studio HTML is SERVED BY the hidden backend** (Codespace forwarded port / a small host) which also runs Claude (Agent SDK) + the preview dev server; the front-end iframes the dev server for live preview.
2. **Pages-hosted static studio front-end ↔ a backend API** (Codespace forwarded port or a serverless/edge function) running the Claude Agent SDK; live preview via an iframe of the backend's dev-server URL.
3. A hybrid. Plus: repo selection (GitHub OAuth/App), the Claude auth/key, live-reload mechanism, and the security envelope (Claude editing arbitrary repos + running a server — RavenClaude's comfort-posture/tribunal/containment already exist and should be reused, not rebuilt).

## Out of scope (this round)
- Not rebuilding Claude Code itself; reuse the **Claude Agent SDK** as the engine where possible.
- No new model/inference work — it's an orchestration + UX + hosting build.

## Success signal
A user opens the page (no Codespace UI visible), picks one of their GitHub repos, types "build me a landing page / a sales dashboard," and watches it render live in the right-hand frame; changes commit back to the repo. Works for both a website and a dashboard.

## Load-bearing external facts to verify (G1)
- GitHub **Pages** is static-only (no server-side compute). [verify]
- **Codespaces** port-forwarding: visibility/auth model, public-vs-private forwarded ports, CORS, must-be-running/idle-timeout. [verify]
- **Claude Agent SDK**: can it run headless, stream to a custom UI, hold a session, use file+git tools, and be driven over an API? [verify]
- **Claude Code on the web / cloud** (claude.ai/code): what it already provides vs. what's net-new here. [verify]
- How **Claude Design's** preview actually works (server-rendered? iframe? its repo/GitHub connection). [verify]
- Live-reload / preview mechanisms for an iframed dev server. [verify]
