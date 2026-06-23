---
name: manage-breaking-changes-and-deprecations
description: Ship a breaking change without stranding users — run a deprecation lifecycle (warn -> window -> remove), author a migration guide, and pair the removal with a major bump and a BREAKING changelog note. Returns the deprecation plan, the migration guide skeleton, and the support-window statement. Used by `release-and-versioning-engineer` (primary).
---

# Skill: manage-breaking-changes-and-deprecations

> **Invoked by:** `release-and-versioning-engineer` (primary).
>
> **When to invoke:** "we need to remove/rename this API"; "how long do we support the old way?"; "plan a deprecation".
>
> **Output:** a deprecation lifecycle plan + a migration guide + the support-window statement.

## The deprecation lifecycle (never skip a stage)

1. **Announce + warn (minor release).** Mark the API deprecated in code (runtime warning / `@deprecated` / compiler hint) and in the changelog under **Deprecated**. The warning names the replacement and links the migration guide. *No behavior change yet.*
2. **Hold the window.** Keep both paths working for a published window — at least one minor cycle, ideally a calendar duration users can plan around. State the window; don't leave it implicit.
3. **Remove (next major release).** Delete the old path, bump **MAJOR**, lead the changelog with `**BREAKING:**`, and link the migration guide. Removal only happens in a major — never yank in a minor or patch.

## Authoring the migration guide

A migration guide is before/after, not prose. For each removed/changed surface:

```
### `createClient(url)` -> `createClient({ url })`
**Why:** options object lets us add config without more positional args.
**Before:**  const c = createClient("https://api.example.com")
**After:**   const c = createClient({ url: "https://api.example.com" })
**Automated:** `npx my-codemod v2-client` rewrites call sites.
```

Offer a **codemod** for mechanical changes when the surface is large — it converts an angry upgrade into a one-command upgrade.

## Support-window statement

Publish which versions get fixes and for how long, e.g.:

> The current major and the previous major receive security fixes for 12 months after the next major ships. Older majors are end-of-life.

## Guardrails
- **A breaking change without a deprecation window is a betrayal of trust** — warn first, every time, unless a security fix forces an immediate break (and then say so). See [`../../best-practices/breaking-changes-need-a-deprecation-window.md`](../../best-practices/breaking-changes-need-a-deprecation-window.md).
- **The deprecation warning must name the replacement** — "deprecated" with no path forward is just noise.
- **Below `1.0.0`, breaking in a minor is allowed but still announced** — `0ver` is a promise to break, not a license to surprise.
- **An unstated support window means "forever"** — which you cannot keep. State it.
