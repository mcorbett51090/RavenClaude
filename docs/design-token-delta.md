# Design token delta — Phase 0 item 8

**Status: `[blocked]` — the comparison this doc exists to state cannot be made this session.**

## The route, named precisely (never a silent skip)

Per `plugins/ravenclaude-core/CLAUDE.md` § "Design-project binding": this repo dogfoods a
binding to **claude.ai/design**, recorded at `.ravenclaude/design-project.json`
(`project_id: 76e5ef74-a8c4-4cf7-9423-86ca92eddbdc`, "RavenClaude Design System" — tokens,
core components, guidelines, UI kits for the dashboard + portal). The documented read path
is the **`DesignSync` tool** (`get_file`) or the **`/design-sync` skill** (plan-gated write).

**The binding file exists and is valid** (verified — read successfully, above). **The block is
narrower than "the design tool is unavailable":** `DesignSync` is not in this agent's tool
allowlist. Per `AGENTS.md` item 9 (least-privilege `tools:` allowlists) and this repo's own
accuracy discipline (`AGENTS.md` § "Accuracy discipline"), a tool absent from *my* allowlist is
evidence about *this agent's* route, not proof the capability is absent from the environment —
naming that distinction precisely is the point of a `[blocked]` row rather than a silent skip.

**What this blocks:** Phase 0 item 8's instruction — *"the design project wins for values"* —
requires reading the live claude.ai/design project and diffing it against
`shared-tokens.css`. That diff is what is blocked. It does not block anything else in this
phase; no other Phase 0 item depends on it.

**Next step for whoever holds `DesignSync`/`/design-sync` access:** run `/design-sync` (or a
`DesignSync get_file` read) against project `76e5ef74-a8c4-4cf7-9423-86ca92eddbdc`, diff its
token values against the table below, and replace this file's `[blocked]` status with the real
delta. Phase 1 (`design-token-delta.md` is its pre-build gate) cannot start until that happens.

---

## What IS verified this session — the generate-time mechanism's current state

`plugins/ravenclaude-core/dashboard-assets/shared-tokens.css` is confirmed as the live
generate-time source (read directly, values below are exact). This is **not** the delta — it
is the "before" side, so the eventual delta has a known baseline the instant `DesignSync`
access lands.

| Token | Light value | Dark value | Contrast note (as commented in the file) |
|---|---|---|---|
| `--rc-gold` (dashboard accent) | `#a8882e` | `#c9a84c` | Light: "~3.6:1 on --rc-bg — AA-LARGE only. Never use as body text." |
| `--rc-gold-soft` | `#c9aa55` | `#e0c478` | — |
| `--rc-teal` (index/repo-guide accent) | `#1f7f78` | `#3aa391` | Light: "passes AA on --rc-bg at ~4.5:1 — safe for body text" |
| `--rc-teal-soft` | `#4a9590` | `#5fbfae` | — |
| `--rc-focus-ring` | `0 0 0 3px rgba(31,127,120,.32)` | brighter accent variant | teal at .32 alpha |
| `--rc-focus-ring-gold` | `0 0 0 3px rgba(168,136,46,.32)` | `rgba(201,168,76,.45)` | gold at .32/.45 alpha |

**Cross-reference — the plan's own re-measurement (§1 binding ruling 3, Phase 1 build):**
the plan states the *adopted* gold value is `#C9A249` at **7.84:1 on `#14110d`** (dark mode,
AAA) and corrects the light-mode comment from "~3.6:1" to the real **3.12:1**. `shared-tokens.css`
as read this session still carries the **pre-Phase-1** values above (`#a8882e` light /
`#c9a84c` dark, `~3.6:1` comment uncorrected) — consistent with Phase 1 not having landed yet
(this is Phase 0; Phase 1 is next on the DAG and owns this file's edit). **Not a discrepancy —
the expected pre-Phase-1 state**, recorded here so Phase 1's diff has a clean starting point.

## Acceptance note

Per the plan's Phase 0 acceptance: *"`design-token-delta.md` (or `[blocked]`) — never a silent
skip."* This file satisfies that literally — the block is named, the route is named, the
blocked scope is narrowed to exactly the value-diff (not the whole item), and the known-good
baseline is recorded so no work is lost once access is available.
