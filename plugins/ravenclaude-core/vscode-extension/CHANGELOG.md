# Changelog

## 0.2.0

Proactive compaction, without any custom trigger mechanism. Built via FORGE
(`.ravenclaude/runs/forge/copilot-preemptive-compact/`), after research settled that a third-party
extension cannot see Copilot Chat's own session token usage (`ChatContext.history` is scoped to your
own participant) — so a "predict overflow and block" mechanism cannot be built. Instead:

- **`contributes.configurationDefaults`** sets
  `github.copilot.chat.summarizeAgentConversationHistoryThreshold` to `0.8` — Copilot's own native
  proactive-compaction threshold, which defaults to `null` (only compact when the context window is
  already completely full — the exact overflow failure this fixes). Confirmed by direct code trace
  against the shipping Copilot Chat bundle that this setting is genuinely read during prompt
  construction and gates a background summarization applied *before* the next request is sent — not
  just a documented description. An explicit user-set value (including an explicit `null`) always
  wins; VS Code's own settings layering handles this with no custom write/refuse logic.
- **`capabilities.untrustedWorkspaces: "limited"`** — without this, VS Code's Restricted Mode disables
  the extension entirely (a default-path trigger for any unfamiliar/large repo, correlating with
  exactly the sessions most likely to overflow), silently reverting to the broken compact-at-100%
  default. Found and fixed via the FORGE run's own red-team pass.

**Known limit, stated honestly:** the `0.8` threshold value is carried over from the setting's own
documented example, not independently re-tuned against real-world Agent-mode sessions — that
confirmation needs the user's own usage, since Copilot Chat is not this development machine's daily
driver.

**Not committed to the repo:** the built `.vsix` — build from source (`npm install && npm run compile
&& npm run package`), per README.md. This keeps the repo free of binary build artifacts; there is no
current publish-to-Marketplace or CI-build pipeline for this extension.

## 0.1.0

Initial build. Ships:

- Language Model Tool `ravenclaude_forceCompactWithDigest` — the agent-cooperative path.
- Command `ravenclaude.forceCompactWithDigest` (`RavenClaude: Force Compact with Critical-Info
  Digest`) — the human-triggered backstop, prompts for a digest via input box.
- Status bar item (right-aligned) — always-visible affordance, one click away.

Not published to the VS Code Marketplace — local `.vsix` install only. See README.md.
