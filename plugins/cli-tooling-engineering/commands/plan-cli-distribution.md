---
description: "Plan how a CLI ships and updates — single binary vs runtime package, cross-compile matrix, install channels, --version + update path."
argument-hint: "[tool language + target users/OSes]"
---

You are running `/cli-tooling-engineering:plan-cli-distribution`. Use `cli-distribution-engineer` + the `cli-distribution-and-packaging` skill.

## Steps

1. Traverse the distribution tree in `knowledge/cli-tooling-decision-trees.md`; decide single static binary vs runtime package; name the friction trade.
2. Define the cross-compile matrix (OS/arch artifacts + checksums).
3. Pick install channels (Homebrew / Scoop / winget / npm / pipx) and keep version+checksum in sync.
4. Stamp `--version` (semver + commit) at build; choose the update story.
5. If a `curl | sh` installer is wanted, make it verify a checksum/signature and be auditable.
6. Emit (from `templates/distribution-plan.md`) + a Structured Output block; route CI release + code-signing to `devops-cicd`.
