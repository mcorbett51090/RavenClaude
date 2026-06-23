# CLI distribution plan

**Tool:** <name>  **Language:** <go / rust / python / node>

## Form

| Decision | Choice |
|---|---|
| Single binary vs runtime package | <static binary / npm / pipx> |
| Friction trade accepted | <what we give up> |

## Build matrix

| OS | Arch | Artifact | Checksum |
|---|---|---|---|
| macOS | arm64 / x64 | | |
| Linux | x64 / arm64 | | |
| Windows | x64 | | |

## Channels

| Channel | Manifest/formula | Version source |
|---|---|---|
| Homebrew | <tap/formula> | release |
| Scoop / winget | <manifest> | release |
| npm / pipx | <package> | release |

## Version + update

- `--version` stamped at build with **semver + commit**
- Update story: <package-manager upgrade / update notice / verified self-update>

## Install script (if any)

- [ ] Verifies checksum/signature
- [ ] Picks the correct OS/arch artifact
- [ ] Installs to a sane path · is auditable

**Routed to `devops-cicd`:** CI release job, code-signing, secret handling.
