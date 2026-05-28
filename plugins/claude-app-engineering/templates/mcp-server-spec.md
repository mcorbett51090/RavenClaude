# MCP server spec — <SERVER>

> Owned by `mcp-and-server-tools-engineer`. See `knowledge/mcp-server-authoring.md`.

## Why a server (not an in-process tool)
- <reused across apps/clients/processes? runs as its own service? → server. Else → in-process tool.>

## Capabilities
| Capability | Item | Schema / shape |
|---|---|---|
| Tools | <name> | <input_schema summary> |
| Resources | <uri/template> | <what it returns> |
| Prompts | <name> | <args> |
| Sampling / elicitation / roots | <if used> | <why> |

## Transport & auth
- **Transport:** <stdio (local) | Streamable HTTP (remote)>
- **Auth:** <none (local) | OAuth-style bearer (remote)>; honor client roots
- **Client config:** <e.g. mcp_servers entry / command+args or URL>

## Security (→ core/security-reviewer)
- [ ] Inputs validated/parameterized; tool args treated as untrusted
- [ ] Responses are untrusted downstream (injection)
- [ ] No secrets in source; secret manager for creds
- [ ] Scope respected (no reads outside client roots)

## Testing
- [ ] Each tool: happy + bad-input + auth-failure
- [ ] Resource fetch returns expected shape
