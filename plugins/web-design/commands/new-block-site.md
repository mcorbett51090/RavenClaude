---
description: Build a site from section blocks that is pixel-perfect on every screen. Starts from the plugin's tested starter kit (tokens, layout contract, block CSS, schemas, ten exemplar blocks) and reference renderer, gates every step, and proves the rendered site with stress fixtures and the device matrix.
argument-hint: "[the site, e.g. 'a five-page site for a Fairhope diner' or 'add a team page to our block site']"
---

# New block site

You are running `/web-design:new-block-site` for what the user described (`$ARGUMENTS`). Follow the
`block-composed-site` skill: Mode 0 if there is no block catalog yet, Mode A if the project already has a composer.
Each step ends at a gate; do not start the next step until it passes. Report each gate's actual output.

## Steps

1. **Ground the facts.** Gather the business's real name, address, phone, hours, special days, offerings, prices and
   photos from its own pages and listings. Anything you cannot verify goes in the manifest's `ownerTodos`, never in a
   rendered field. Ask the user one question when two readings of the request would build different sites.
2. **Copy the kit** from `templates/block-site/` into the project (`tokens.css`, `layout.css`, `blocks.css`, the two
   schemas, `catalog.json`), unless the project already has one. Render the kit's own example once with
   `scripts/block_site_render.py render … --placeholders` to see the whole path working.
   - **Gate:** `python3 <plugin>/scripts/block_site_check.py catalog <site>/catalog.json`.
3. **Brand** by changing values in `tokens.css` (colours, font stacks), never role names.
   - **Gate:** `block_site_check.py tokens <site>/tokens.css`.
4. **Choose blocks by purpose** from the block catalog in `templates/block-site/README.md`. Use the ten exemplars as
   they are, or write a closed, bounded contract for each new block in `catalog.json`, with a render function in your project's own `blocks.py` (a `RENDER` dict of block id to function, passed with `--blocks`; it may import the renderer's helpers: `from block_site_render import e, a, picture`), and its CSS
   in `blocks.css`. Never edit the plugin's scripts.
   - **Gate:** `block_site_check.py catalog <site>/catalog.json`.
5. **Write the manifest:** business facts, the chrome (nav, header action, footer links), assets and pages. Write
   image alt text while looking at each image. Give every asset its real width, height and focal point, smaller
   `sources` for `srcset`, and a portrait crop for a full-bleed photo that crops badly on a phone.
   A page in another language needs `strings` (the renderer's own words) and `alternates`; emergency-only hours are
   `"kind": "emergency"`.
   - **Gate:** `block_site_check.py manifest <site>/site.manifest.json --catalog <site>/catalog.json`. Fix its
     warnings about photos too small for their box, and about a page in another language with no strings, too.
6. **Render** with `block_site_render.py render <site>/site.manifest.json --catalog <site>/catalog.json --blocks
   <site>/blocks.py --out dist` (leave out `--blocks` if the site uses only the exemplars).
   - **Gate:** it exits 0, and its `styles:` line names `<site>`, not the kit. It refuses a manifest the checker
     refuses, then checks its own HTML.
7. **Stress it.** Run `block_site_check.py fixtures <site>/catalog.json --out stress/stress.manifest.json`, and render
   those pages into their own folder (`--out stress/dist`), never into `dist`, so they are never published.
8. **Prove it.**
   - Run `node <plugin>/scripts/device_matrix.mjs --dir dist --manifest <site>/site.manifest.json --full --sweep
     320:1600:8` for the site, and `--dir stress/dist --manifest stress/stress.manifest.json --themes light` for the
     stress pages (one theme: six take hours on a full catalog). A `basePath` site is tested under its path.
   - Save baselines with `--shots`.
   - Look at element screenshots at 390 and 1280px in light and dark, especially hero copy over the real photos.
   - **Gate:** zero findings, and screenshots you would show the customer.

## Guardrails

- Never pad, margin or max-width a slot, and never set grid placement, section padding or a colour inside a block.
  `layout.css` owns those.
- Never put a placeholder in a rendered field: `TODO`, lorem ipsum and `{{…}}` are refused by the manifest check.
- A green device matrix is necessary, not sufficient. Say plainly that a real iPhone and iPad are the last step, and
  whether they were checked.
- Anything touching forms that collect personal data, payments or uploads goes through `ravenclaude-core`'s
  `security-reviewer`.
