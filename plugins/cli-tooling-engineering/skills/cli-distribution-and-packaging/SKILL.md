---
name: cli-distribution-and-packaging
description: "Plan how a CLI ships and updates — single static binary vs runtime package, cross-compilation, install channels (Homebrew/Scoop/winget/npm/pipx), a build-stamped --version, and a safe installer. Use when making a tool installable and keeping it current."
---

# CLI Distribution & Packaging

## Pick the distribution form

| Language | Form | Why |
|---|---|---|
| Go / Rust (compiled) | **Single static binary** per OS/arch | Lowest install friction, no runtime to install |
| Node | **npm** package with a `bin` entry | Users already have npm |
| Python | **pipx** (isolated app install) | Avoids polluting the user's Python env |

A static single binary is the gold standard when the language can produce one — name the friction trade if you can't.

## Cross-compile the matrix

Produce per-**OS/arch** artifacts (at least macOS arm64+x64, Linux x64+arm64, Windows x64) with **checksums** and consistent archive names. Keep the build reproducible. CI wiring of this job + code-signing route to `devops-cicd`.

## Publish where users look

- macOS/Linux → **Homebrew** (tap + formula).
- Windows → **Scoop** and/or **winget**.
- Cross-platform script tools → **npm** / **pipx**.

Keep each channel's version + checksum in sync with the release so they never drift.

## `--version` and updates

- Stamp the binary at **build time** with **semver + commit**; `--version` must report exactly what's running (a version without the commit makes bug triage guesswork).
- Choose an update story: let the package manager upgrade, or add an **update check/notice** — and make sure it never blocks or surprises a non-interactive run.

## `curl | sh` installers (only if safe)

If you ship one, it must **verify a checksum/signature**, select the correct OS/arch artifact, install to a sane path, and be auditable. An unverified installer is arbitrary code execution.

Package the generated **shell completions** + a **man page** with the release. See the distribution tree in [`../../knowledge/cli-tooling-decision-trees.md`](../../knowledge/cli-tooling-decision-trees.md).
