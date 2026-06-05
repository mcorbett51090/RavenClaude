# Design channel-aware turn state in custom-engine agents — not all channels deliver the same payload

**Status:** Pattern
**Domain:** Custom-engine agents / M365 Agents SDK
**Applies to:** `microsoft-365-copilot`

---

## Why this exists

The M365 Agents SDK (and the Bot Framework it inherits) delivers conversation turns as `Activity` objects — but the `Activity` schema and the conversational features available differ across channels. An adaptive card that renders in Teams does not render in an SMS channel. A `typing` event exists in Teams but not in email. A voice channel delivers the user's message as recognized speech text, not a keyboard-typed string. Custom-engine agents that assume Teams-shaped activities fail silently in other channels and produce unhandled exceptions when the activity shape they expect is absent. Channel-aware turn handling is not a polish item — it is a correctness requirement for any multi-channel agent.

## How to apply

In the `onMessage` turn handler, inspect the channel before rendering rich content:

```typescript
import { ActivityTypes, TurnContext } from '@microsoft/agents-sdk';

async onMessage(context: TurnContext): Promise<void> {
    const channel = context.activity.channelId;  // "msteams", "webchat", "email", "sms", etc.

    if (channel === 'msteams') {
        // Render adaptive card
        await context.sendActivity({ attachments: [adaptiveCardAttachment] });
    } else {
        // Fallback to plain text for all other channels
        await context.sendActivity({ type: ActivityTypes.Message, text: this.cardToText(data) });
    }
}
```

State management:
- Use `ConversationState` for per-conversation state (shared across all users in the conversation).
- Use `UserState` for per-user state (follows the user across conversations).
- Use `TempState` (storage bag on the `TurnContext`) for within-turn ephemeral data only.
- Always `saveChanges()` on all state objects at the end of the turn handler — unflushed state is lost.

**Do:**
- Define a channel capability matrix at design time: list every channel the agent targets and the feature set available on each.
- Provide a plain-text fallback for every adaptive card or rich attachment.
- Test on every channel in the capability matrix before publishing — Teams behavior and web-chat behavior diverge in subtle ways.

**Don't:**
- Hardcode `channelId === 'msteams'` as the only code path without a fallback — new channels added later will silently receive the wrong output.
- Use `context.activity.channelData` without null-checking — it is undefined on channels that don't send it.
- Store large payloads in `ConversationState` — state storage has per-record size limits; use a Cosmos DB or Table Storage reference if the payload is large.

## Edge cases / when the rule does NOT apply

An agent explicitly scoped to Teams-only deployment (documented channel restriction in the app manifest) may use Teams-specific features without a cross-channel fallback. Document the channel restriction and add it as a test gate.

## See also

- [`../agents/agents-sdk-engineer.md`](../agents/agents-sdk-engineer.md) — owns the M365 Agents SDK surface and multi-channel publish
- [`./cea-escalate-to-custom-engine-only-when-a-hard-limit-forces-it.md`](./cea-escalate-to-custom-engine-only-when-a-hard-limit-forces-it.md) — the upstream decision that routes to a custom-engine agent

## Provenance

Codifies the `agents-sdk-engineer`'s domain knowledge from CLAUDE.md §8 knowledge bank `agents-sdk-and-toolkit-2026.md` on channel/turn state; M365 Agents SDK documentation.

---

_Last reviewed: 2026-06-05 by `claude`_
