# Target the correct Teams resource — channel message vs chat message vs reply

**Status:** Primary diagnostic
**Domain:** Microsoft Graph / Teams workloads
**Applies to:** `microsoft-graph`

---

## Why this exists

Microsoft Graph exposes three distinct Teams messaging surfaces — channel messages (`/teams/{id}/channels/{id}/messages`), chat messages (`/chats/{id}/messages`), and replies (`/teams/{id}/channels/{id}/messages/{id}/replies`) — and they are not interchangeable. A `POST` to the channel-messages endpoint sends to a channel; the same operation against a chat requires a completely different resource path and permission scope. Developers who conflate them produce code that silently posts to the wrong surface or fails with a `403` because the permission covers one surface but not the other. The reply endpoint is frequently missed, producing flat message threads instead of nested conversations.

## How to apply

| Intent | Endpoint | Permission (delegated / app) |
|---|---|---|
| Send to a Teams channel | `POST /teams/{teamId}/channels/{channelId}/messages` | `ChannelMessage.Send` / `Teamwork.Migrate.Messages` |
| Read channel messages | `GET /teams/{teamId}/channels/{channelId}/messages` | `ChannelMessage.Read.All` |
| Reply to a channel message | `POST /teams/{teamId}/channels/{channelId}/messages/{msgId}/replies` | `ChannelMessage.Send` |
| Send in a 1:1 or group chat | `POST /chats/{chatId}/messages` | `Chat.ReadWrite` |
| List all chats for the signed-in user | `GET /me/chats` | `Chat.ReadBasic` (delegated only) |

```http
# Correct: post a message to a Teams channel
POST https://graph.microsoft.com/v1.0/teams/{team-id}/channels/{channel-id}/messages
Authorization: Bearer {token}
Content-Type: application/json

{
  "body": {
    "contentType": "html",
    "content": "<b>Hello from Graph</b>"
  }
}
```

**Do:**
- Use `importance: urgent` or `importance: important` only for genuinely time-sensitive messages — excessive use desensitizes users.
- Prefer `contentType: html` for rich messages; `contentType: text` for plain text — mixing them produces garbled output.
- When replying, use the `/replies` endpoint, not a new top-level post — this keeps the conversation thread intact.

**Don't:**
- Use a channel-message permission to send a chat message — they are separate permission families.
- Use application permissions (`Teamwork.Migrate.Messages`) outside the migration scenario it was designed for — it requires an import-mode channel that cannot be used normally.
- Hardcode `teamId` or `channelId` GUIDs — look them up via `GET /me/joinedTeams` and `GET /teams/{id}/channels` or store them in environment configuration.

## Edge cases / when the rule does NOT apply

For bot-framework / Copilot Studio bots sending proactive messages, the Bot Framework SDK handles the surface routing — use it rather than calling the Graph endpoint directly, to preserve threading and activity IDs.

## See also

- [`../agents/graph-workloads-engineer.md`](../agents/graph-workloads-engineer.md) — owns Teams workload Graph calls
- [`./api-select-only-what-you-need.md`](./api-select-only-what-you-need.md) — always `$select` when listing messages at scale

## Provenance

Codifies CLAUDE.md §3 routing discipline for Teams workloads; Microsoft Graph v1.0 Teams messaging documentation.

---

_Last reviewed: 2026-06-05 by `claude`_
