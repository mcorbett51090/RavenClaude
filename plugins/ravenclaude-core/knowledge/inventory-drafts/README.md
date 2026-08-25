# Inventory drafts lane

⛔ **This directory is OUTSIDE the concepts glob, and that is the point.**
`scripts/concepts.py` reads `knowledge/concepts/*.md`. A skeleton here with
`nuance: TODO` is therefore invisible to the dashboard and to CI, so **promotion
into `knowledge/concepts/` is the gate** — a half-written entry can never render
as a real one.

Verified allowed by `.repo-layout.json` (`plugins/*/knowledge/**`).
`check-lineup-citations.py` is opt-in via an explicit marker and
`generate-document-map.py` globs non-recursively, so drafts escape both.

## ⛔ A draft older than 90 days is PROMOTED or REMOVED

Plan A omitted this. Without it the drafts lane becomes the 162 stale summaries,
**relocated** — and relocated somewhere with no dashboard and no CI, which is
strictly worse than leaving them in view.

`scripts/inventory-coverage.py` reports every draft past the window. Give each
draft a `drafted: YYYY-MM-DD` line in its frontmatter or it cannot be aged, and
an un-ageable draft is the one that lives here forever.

## Shape

Copy the template from
[`docs/best-practices/inventory-authoring.md`](../../../../docs/best-practices/inventory-authoring.md)
§4, add `drafted: YYYY-MM-DD`, and leave `nuance:` empty until you have measured
something. ⛔ Do not pre-fill a nuance you intend to "firm up later" — that is the
restatement the whole project exists to prevent, written down early.
