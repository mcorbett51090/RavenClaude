---
name: demo-design
description: Design a demo that maps to the buyer's discovered pain instead of touring features — build a Great Demo!-style storyline (show the compelling result first, then peel back only the layers the buyer asked for), tie every moment to a discovered pain and its business impact, and script the honest shipped-vs-roadmap boundaries. Reach for this after discovery, when the user needs to build or tighten a demo. Used by `sales-engineer` (primary).
---

# Skill: demo-design

> **Invoked by:** `sales-engineer` (primary).
>
> **When to invoke:** "help me build a demo for <prospect>"; "my demo is a feature tour — fix it"; "what should I show given they care about <pain>?". **Precondition:** discovery has happened (run `technical-discovery` first); a demo with no discovered pain is the thing this skill exists to prevent.
>
> **Output:** a pain-mapped demo storyline + the demo script ([`../../templates/demo-script.md`](../../templates/demo-script.md)) with the cuts and honesty boundaries called out.

## Procedure

1. **Anchor to the critical business issue.** From discovery, restate the one pain + its quantified impact the demo must resolve. Everything in the demo serves this; anything that doesn't gets cut.
2. **Do-It-first (Great Demo!).** Open with the **compelling result** — the "after" state that resolves the pain — before any setup or navigation. Lead with the destination, not the journey. See [`../../knowledge/discovery-and-demo-playbook.md`](../../knowledge/discovery-and-demo-playbook.md).
3. **Peel back only the requested layers.** After the result lands, reveal *how* — but only the depth the buyer asks for. Resist the menu tour ("and here's another tab"). Illustrate, don't educate.
4. **Map each beat to a pain.** Build the storyline as a table: demo beat → discovered pain it resolves → business impact. A beat with no pain in its row is cut.
5. **Script the honesty boundaries.** Pre-decide where you'll say "that's on the roadmap" or "we don't do that — here's the workaround." Scripting it keeps you from improvising a fabricated "yes" under pressure.
6. **Plan the interaction, not the monologue.** Insert check-in questions ("does that match how you'd use it?"). A demo is a conversation; if you talk more than half the time, you're educating.

## Output

The demo script (storyline + beat-to-pain table + honesty boundaries + check-in questions) and a one-line **call to action** for the end of the demo (the next step into the mutual action plan). Hand a real gap to `poc-success-criteria` (POC) or `product-management` (roadmap).

## Anti-patterns this skill prevents

- The feature-tour / menu-dump demo (no pain mapping).
- Burying the compelling result under setup and navigation.
- Improvising a fabricated capability when asked "can it do X?".
- A demo that ends with no agreed next step.
