// extension.ts — ravenclaude-precompact-guard
//
// Programmatically triggers GitHub Copilot Chat's `/compact` command with
// custom steering text, so a curated critical-info digest lands verbatim in
// the compaction summarization prompt.
//
// Verified mechanism (RavenClaude FORGE plan
// .ravenclaude/runs/forge/precompact-critical-context/claims-table.md, row 15
// — sourced from microsoft/vscode's own extensions/copilot
// src/extension/conversation/vscode-node/conversationFeature.ts:277, the
// exact call Microsoft's own Copilot "compact" button uses):
//
//   vscode.commands.executeCommand('workbench.action.chat.open', {
//     query: '/compact ' + digestText,
//     preserveInput: true,
//   });
//
// This is a stable, public VS Code command — no proposed-API allowlist
// needed. Do NOT use ChatSummarizer / chatContextProvider / any
// vscode.proposed.* API: those are allowlisted exclusively to
// GitHub.copilot-chat in the shipping product.json and are unusable by a
// third-party extension (claims-table row 15).
//
// This extension is genuinely a non-participant with respect to live chat
// history (claims-table row 17) — it cannot read the conversation to build
// its own digest. The digest always comes from one of two places: the model
// itself (via the Language Model Tool, when it calls this proactively from
// inside its own turn) or the user (via the manual command's input box).
// The extension never reads chat history, transcripts, or any on-disk VS
// Code storage to construct a digest.

import * as vscode from "vscode";

/** Hard cap on digest length before it is embedded in the /compact query string. */
const MAX_DIGEST_CHARS = 4000;

/** Sanitize a digest: trim, collapse to a single reasonable length. */
function sanitizeDigest(raw: string): string {
  const trimmed = raw.trim();
  if (trimmed.length <= MAX_DIGEST_CHARS) {
    return trimmed;
  }
  return trimmed.slice(0, MAX_DIGEST_CHARS) + " …[digest truncated]";
}

/**
 * The shared trigger: opens Copilot Chat with a `/compact <digest>` query,
 * exactly mirroring Microsoft's own Copilot "compact" button implementation
 * (claims-table row 15). Both the Language Model Tool path and the manual
 * command path funnel through this one function.
 *
 * `PreCompact`'s systemMessage/stopReason are a verified no-op on VS Code
 * (claims-table row 20) — there is no user-visible signal when compaction
 * happens automatically. This function compensates by always showing an
 * explicit confirmation that IT took the action, so the user never wonders
 * whether anything happened.
 */
async function forceCompact(digestRaw: string): Promise<void> {
  const digest = sanitizeDigest(digestRaw);

  await vscode.commands.executeCommand("workbench.action.chat.open", {
    query: digest.length > 0 ? `/compact ${digest}` : "/compact",
    preserveInput: true,
  });

  const preview =
    digest.length > 0
      ? digest.length > 80
        ? `${digest.slice(0, 80)}…`
        : digest
      : "(no digest text — plain /compact)";

  void vscode.window.showInformationMessage(
    `RavenClaude: triggered /compact with your digest — "${preview}"`,
  );
}

export function activate(context: vscode.ExtensionContext): void {
  // (a) Language Model Tool — the agent-cooperative path. The model calls
  // this itself, from inside its own turn, with a digest it authored from
  // its own live conversation context. This extension never reads that
  // context itself (claims-table row 17).
  const toolDisposable = vscode.lm.registerTool<{ digest: string }>(
    "ravenclaude_forceCompactWithDigest",
    {
      async invoke(
        options: vscode.LanguageModelToolInvocationOptions<{ digest: string }>,
        _token: vscode.CancellationToken,
      ): Promise<vscode.LanguageModelToolResult> {
        const digest = typeof options.input?.digest === "string" ? options.input.digest : "";

        await forceCompact(digest);

        const confirmation =
          digest.trim().length > 0
            ? `Triggered /compact with the supplied critical-info digest (${sanitizeDigest(digest).length} chars, capped at ${MAX_DIGEST_CHARS}).`
            : "Triggered /compact with no digest text supplied — compacted without steering.";

        return new vscode.LanguageModelToolResult([new vscode.LanguageModelTextPart(confirmation)]);
      },
    },
  );

  // (b) Manual command — the human-triggered backstop. When invoked with no
  // digest already available, prompt the user for free text (never
  // auto-extracted from anywhere on-disk — claims-table row 17 established
  // that on-disk chat storage is unreliable, undocumented, and
  // format-unstable territory this extension deliberately avoids).
  const commandDisposable = vscode.commands.registerCommand(
    "ravenclaude.forceCompactWithDigest",
    async () => {
      const digest = await vscode.window.showInputBox({
        title: "RavenClaude: Force Compact with Critical-Info Digest",
        prompt:
          "What must survive compaction? (open decisions, TODOs, key facts, file paths, unresolved questions)",
        placeHolder:
          "e.g. Still need to fix auth.ts:42 before merging; DB migration is pending review",
        ignoreFocusOut: true,
      });

      // A cancelled input box (Escape) returns undefined — do nothing rather
      // than compact with an empty digest the user never confirmed.
      if (digest === undefined) {
        return;
      }

      await forceCompact(digest);
    },
  );

  // (c) Status bar item — the "before it's too late" affordance. Since a
  // non-participant extension genuinely cannot auto-detect context pressure
  // (claims-table row 17), the honest design is "always one click away," not
  // a silent auto-trigger. This is NOT automatic compaction steering — see
  // README.md for the one real limitation this extension has.
  const statusBarItem = vscode.window.createStatusBarItem(
    "ravenclaude.forceCompact",
    vscode.StatusBarAlignment.Right,
    100,
  );
  statusBarItem.name = "RavenClaude: Force Compact";
  statusBarItem.text = "$(save) Compact";
  statusBarItem.tooltip = "Force a critical-info-preserving compact now";
  statusBarItem.command = "ravenclaude.forceCompactWithDigest";
  statusBarItem.show();

  context.subscriptions.push(toolDisposable, commandDisposable, statusBarItem);
}

export function deactivate(): void {
  // No explicit teardown needed — every disposable was pushed onto
  // context.subscriptions and VS Code disposes them automatically.
}
