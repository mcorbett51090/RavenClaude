# RavenClaude Precompact Guard

A VS Code extension that lets you (or GitHub Copilot Chat's own agent) trigger an **explicit,
steered `/compact`** — forcing Copilot Chat to compact the conversation right now, with a
curated critical-info digest injected into the summarization system prompt, instead of letting
context vanish into an unsteered automatic compaction later.

## What this does

VS Code Copilot Chat supports `/compact [instructions]` as a manual slash command: whatever
follows `/compact` is passed to the summarization pass as `## Additional instructions from the
user:` — verified against `microsoft/vscode`'s own source (this is literally how Microsoft's own
Copilot "compact" button works). This extension exposes two ways to invoke that mechanism without
typing it yourself:

1. **A Language Model Tool** (`ravenclaude_forceCompactWithDigest`) that Copilot's own agent can
   call proactively, from inside its own turn, when it judges the conversation is approaching its
   context limit. The agent already has full conversation context at that point — no snooping or
   heuristics are needed — so it authors its own digest (open decisions, pending TODOs, key
   facts, file paths, unresolved questions) and hands it straight to this tool.
2. **A manual command** (`RavenClaude: Force Compact with Critical-Info Digest`, also reachable
   from the status bar) that prompts you for the same kind of digest via a simple text box, then
   triggers the identical `/compact <digest>` action.

Both paths funnel through the same mechanism:

```ts
vscode.commands.executeCommand("workbench.action.chat.open", {
  query: "/compact " + digest,
  preserveInput: true,
});
```

This is a **stable, public** VS Code command — no proposed-API allowlist, publishable to the
Marketplace as-is.

## The one real limitation — read this before relying on it

**This extension can only trigger EXPLICIT, on-demand compaction. It cannot influence VS Code
Copilot Chat's automatic background compaction in any way.**

The `summarizationInstructions` field this mechanism writes into is referenced in exactly two
files in the Copilot Chat source (`agentIntent.ts`, `summarizedConversationHistory.tsx`).
`backgroundSummarizer.ts` — the code path that runs *automatic* compaction — has zero references
to it. There is no first-party hook, event, or API that lets a third-party extension observe or
steer an automatic compaction pass; two Microsoft-maintainer-closed feature requests
(#289194, #319648) confirm none is coming.

The design response to this limit is not to try to fake automatic detection — it's to make
**triggering compaction yourself, proactively, before the automatic one would fire** genuinely
easy: one Language Model Tool call for the agent, one click for you. That's what "before it's too
late" means here — an always-visible status bar affordance, not a silent background watcher.
This extension also cannot see your live chat history to decide *when* to nudge you (a
non-participant extension has no visibility into an ongoing Copilot Chat session unless it's an
`@`-mentioned participant) — so it does not try. It's one click away, always; it never
auto-fires.

## Install

Not published to the VS Code Marketplace yet (that needs the repo owner's own publisher
account/token — see below). Until then, install the locally-built `.vsix`:

```shell
code --install-extension ravenclaude-precompact-guard-0.2.0.vsix
```

## Build it yourself

```shell
cd plugins/ravenclaude-core/vscode-extension
npm install
npm run compile      # bundles src/extension.ts -> dist/extension.js
npm run package       # runs `npx vsce package`, produces the .vsix
```

## Marketplace publishing — not done here

Publishing to the VS Code Marketplace requires a real publisher account and a personal access
token that only the repo owner holds. This extension ships `publisher: "ravenclaude"` as a
placeholder so it packages and installs locally; a real Marketplace publish needs:

1. Create (or use an existing) publisher at https://marketplace.visualstudio.com/manage
2. `npx vsce login <publisher-id>` with a PAT scoped to Marketplace
3. `npx vsce publish` from this directory

None of that is attempted by this build — it is explicitly human-only residue.
