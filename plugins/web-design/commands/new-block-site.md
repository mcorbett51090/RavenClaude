---
description: Build a site from section blocks that is pixel-perfect on every screen. Starts from the plugin's tested starter kit (tokens, layout contract, block and manifest schemas, exemplar blocks), gates every step with the contract checker, and proves the rendered site with stress fixtures and the device matrix.
argument-hint: "[the site, e.g. 'a five-page site for a Fairhope diner' or 'add a team page to our block site']"
---

# New block site

You are running `/web-design:new-block-site` for what the user described (`$ARGUMENTS`). Follow the
`block-composed-site` skill: Mode 0 if there is no block catalog yet, Mode A if the project already has a composer.
Each step ends at a gate; do not start the next step until it passes. Report each gate's actual output.

## Steps

1. **Ground the facts.** Gather the business's real name, address, phone, hours, offerings, prices and photos from its
   own pages and listings. Anything you cannot verify goes in the manifest's `ownerTodos`, never in a rendered field.
   Ask the user one question when two readings of the request would build different sites.
2. **Copy the kit** from `templates/block-site/` into the project (`tokens.css`, `layout.css`, the two schemas, the
   catalog), unless the project already has one.
3. **Brand** by changing values in `tokens.css`, never role names.
   - **Gate:** `python3 <plugin>/scripts/block_site_check.py tokens <site>/tokens.css`.
4. **Choose blocks by purpose** from `templates/block-site/catalog.md`. Write a closed, bounded `block.json` for each
   one, starting from the exemplars.
   - **Gate:** `block_site_check.py catalog <site>/catalog`.
5. **Build each block to the anatomy** in the kit's README: slots on grid lines, components inside slots, CSS in
   `@layer blocks` that reads only tokens, and `@container slot` queries.
   - **Gate:** the block renders in a gallery page, and `node <plugin>/scripts/device_matrix.mjs --dir <site>
     --pages /gallery.html --full --sweep 320:1600:8` reports no findings.
6. **Write the manifest.** Write image alt text while looking at each image, and give every asset its real width,
   height and focal point.
   - **Gate:** `block_site_check.py manifest <site>/site.manifest.json --catalog <site>/catalog`. Fix its warnings
     about small sources and heavy crops too.
7. **Render and stress.** Build the site. Generate `block_site_check.py fixtures <site>/catalog --out stress.manifest.json`
   and render those pages too.
8. **Prove it.**
   - Run the device matrix on the built site and the stress pages with `--full --sweep 320:1600:8`.
   - Save baselines with `--shots`.
   - Look at element screenshots at 390 and 1280px in light and dark, especially hero copy over photos (see
     `text-over-photo-contrast-2026.md`).
   - **Gate:** zero findings, and screenshots you would show the customer.

## Guardrails

- Never pad, margin or max-width a slot, and never set grid placement, section padding or a colour inside a block.
  `layout.css` owns those.
- Never put a placeholder in a rendered field: `TODO`, lorem ipsum and `{{…}}` are refused by the manifest check.
- A green device matrix is necessary, not sufficient. Say plainly that a real iPhone and iPad are the last step, and
  whether they were checked.
- Anything touching forms that collect personal data, payments or uploads goes through `ravenclaude-core`'s
  `security-reviewer`.
