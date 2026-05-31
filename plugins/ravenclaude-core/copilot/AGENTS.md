# ravenclaude-core — Copilot grounding instructions

<!-- AUTO-GENERATED from the root AGENTS.md by scripts/generate-copilot-plugin.py. Do not edit by hand; edit the root AGENTS.md and regenerate. The --check freshness gate fails CI on drift. -->

GitHub Copilot reads `AGENTS.md` natively from the repo root, the current
working directory, or any directory named in the
`COPILOT_CUSTOM_INSTRUCTIONS_DIRS` environment variable. When you install
the `ravenclaude-core` agents into your own repo via
`copilot --plugin-dir plugins/ravenclaude-core/copilot`, add this
directory to that variable so the claim-grounding discipline below loads
alongside the agents — it lives in RavenClaude's root AGENTS.md, which
Copilot would otherwise not see from your repo:

```shell
export COPILOT_CUSTOM_INSTRUCTIONS_DIRS=plugins/ravenclaude-core/copilot
```

---

## Accuracy discipline (cross-tool pointer)

Confident reasoning errors — a flawed belief about a tool/platform/API stated as fact with no uncertainty marker — are as dangerous as hallucinations and harder to catch. For any **consequential** claim (one that gates an irreversible action or gets written into a durable doc): **cite the this-session check that backs it inline, or mark it `[unverified — training knowledge]` and offer to verify before acting** — and never falsely concede (or dig in) when corrected; verify first. This applies to every agentic tool reading this file (Claude Code, GitHub Copilot CLI routing Claude/GPT/Grok, Cursor, Codex). Full protocol + the enforced complements: [`plugins/ravenclaude-core/CLAUDE.md`](plugins/ravenclaude-core/CLAUDE.md) § "Claim Grounding & Source Honesty".

**The same discipline governs the mirror-image error — falsely claiming you _can't_ do something** (the costlier one in practice: it silently abandons work and wastes a round-trip). A `command not found`, an HTTP 401/403, a deferred/MCP tool whose schema isn't loaded yet, or an "API doesn't support X" recalled from training is evidence about **one route**, **never** proof the capability is absent. Before any "I can't" / "that's not possible" / "no PR capability here" leaves an agent: (0) **read the actual error first and name its specific mechanical cause** — the status code *and* the body/stderr, not the headline. The cause **selects** the next move and is not interchangeable: an expired/missing-token `401` means re-authenticate then **retry the same route** (do not switch surfaces); an insufficient-scope `403` means a surface that already holds the scope; a `command not found` means the tool is absent *on this host*; an unloaded MCP schema means search/await it. Guessing the cause picks the wrong fix. (1) **load the sanctioned route first** — e.g. an MCP tool that shows as "still connecting" or name-only must be searched/awaited before you call it, and a missing-schema error is a not-loaded-yet signal, not an absent tool; (2) **enumerate ≥2 alternative paths and try the next-easiest** before reporting blocked; (3) report blockage only with the this-session checks you ran (`command + output`, or `file:line`) and the alternatives tried — same falsifiability bar as a positive claim. A wrong path is not a missing capability, and a CLI/API dead-end is not a verdict on the goal. _Worked example (this repo): creating a PR in the web/remote environment is **only** the GitHub MCP path — `gh`/`hub` are absent and the direct API 403s, so a session that concluded "can't create a PR" from those two dead-ends skipped step 1 (load the MCP tool) and step 2 (try the sanctioned route)._
