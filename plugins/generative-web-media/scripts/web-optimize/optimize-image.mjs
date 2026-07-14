#!/usr/bin/env node
/**
 * optimize-image.mjs — turn a raw generated image into a production web asset.
 *
 * Emits AVIF + WebP + a JPEG/PNG safety net at 3–5 responsive widths, reports the
 * intrinsic dimensions (for CLS-safe markup), and prints a ready-to-paste <picture>
 * element. Deterministic post-processing owned by this plugin (the generation itself
 * is the substrate's job).
 *
 * PROBE-AND-DEGRADE: this needs Node >= 18 and the `sharp` package. If `sharp` is not
 * resolvable it LOUD-SKIPs — prints the exact prerequisite and "THIS IS NOT A PASS" —
 * and exits non-zero. It NEVER silently succeeds without producing the derivatives.
 *
 * Usage:
 *   node optimize-image.mjs --in hero.png --outdir ./media --name hero \
 *        [--widths 480,768,1200,1600] [--sizes "(max-width:768px) 100vw, 1200px"] \
 *        [--fallback jpeg|png] [--lcp]
 *
 * Run on demand via npx (no repo install needed):
 *   npx --yes --package=sharp@0.33.5 node optimize-image.mjs --in … --outdir … --name …
 */

import { argv, exit, stderr, stdout } from "node:process";
import { mkdir, access } from "node:fs/promises";
import { basename, join } from "node:path";

const DEFAULT_WIDTHS = [480, 768, 1200, 1600];

function parseArgs(args) {
  const out = {
    widths: DEFAULT_WIDTHS,
    sizes: "100vw",
    fallback: "jpeg",
    lcp: false,
  };
  for (let i = 0; i < args.length; i += 1) {
    const a = args[i];
    const next = () => args[(i += 1)];
    if (a === "--in") out.in = next();
    else if (a === "--outdir") out.outdir = next();
    else if (a === "--name") out.name = next();
    else if (a === "--widths") {
      const parsed = next()
        .split(",")
        .map((w) => parseInt(w.trim(), 10))
        .filter(Boolean);
      // Fall back to the defaults if --widths parsed to nothing (e.g. "--widths abc"
      // or "--widths ,,") — never let an empty list produce `hero-undefined.jpg`.
      out.widths = parsed.length ? parsed : DEFAULT_WIDTHS;
    } else if (a === "--sizes") out.sizes = next();
    else if (a === "--fallback") out.fallback = next();
    else if (a === "--lcp") out.lcp = true;
    else if (a === "--help" || a === "-h") out.help = true;
  }
  return out;
}

function loudFail(message) {
  stderr.write(`\n[optimize-image] LOUD-SKIP — THIS IS NOT A PASS.\n${message}\n\n`);
  exit(1);
}

async function loadSharp() {
  try {
    const mod = await import("sharp");
    return mod.default ?? mod;
  } catch {
    loudFail(
      "The `sharp` image library is not resolvable in this environment.\n" +
        "This script does NOT degrade to a silent success — it produces the AVIF/WebP\n" +
        "derivatives or it fails loudly.\n\n" +
        "Fix (one of):\n" +
        "  • npx --yes --package=sharp@0.33.5 node optimize-image.mjs --in … --outdir … --name …\n" +
        "  • cd scripts/web-optimize && npm install && node optimize-image.mjs …\n\n" +
        "On an offline / no-node host the web pipeline degrades to GUIDANCE-ONLY:\n" +
        "hand-run the AVIF+WebP+fallback + responsive-widths + explicit-dims steps from\n" +
        "knowledge/web-media-pipeline.md. The web-ready output is gold WHEN this optimizer\n" +
        "runs; partial otherwise. Do not report it as gold on a degraded host.",
    );
  }
  return null; // unreachable — loudFail exits
}

const HELP = `optimize-image.mjs — raw image -> AVIF/WebP/fallback responsive <picture>

  --in <file>       source image (required)
  --outdir <dir>    output directory (required)
  --name <base>     output basename, e.g. "hero" (required)
  --widths a,b,c    responsive widths (default 480,768,1200,1600)
  --sizes "<…>"     the <img> sizes attribute (default "100vw")
  --fallback jpeg|png  safety-net format: jpeg (default) or png (alpha)
  --lcp             emit LCP-hero markup (eager + fetchpriority=high)

PROBE-AND-DEGRADE: needs Node>=18 + sharp; LOUD-SKIPs (non-zero) if sharp is absent.`;

async function main() {
  const opts = parseArgs(argv.slice(2));
  if (opts.help) {
    stdout.write(`${HELP}\n`);
    exit(0);
  }
  const missing = ["in", "outdir", "name"].filter((k) => !opts[k]);
  if (missing.length) {
    loudFail(`Missing required argument(s): ${missing.map((m) => `--${m}`).join(", ")}\n\n${HELP}`);
  }
  // Only jpeg/png are supported safety-net formats. Reject anything else loudly
  // rather than silently encode JPEG while the JSON report claims the bogus format
  // (produced[].fmt / formats[] would otherwise mislabel the actual artifact).
  if (opts.fallback !== "jpeg" && opts.fallback !== "png") {
    loudFail(
      `--fallback must be "jpeg" or "png" (got ${JSON.stringify(opts.fallback)}).\n\n${HELP}`,
    );
  }
  try {
    await access(opts.in);
  } catch {
    loudFail(`Input file not found: ${opts.in}`);
  }

  const sharp = await loadSharp();
  await mkdir(opts.outdir, { recursive: true });

  const meta = await sharp(opts.in).metadata();
  // CLS-safety is this tool's whole job — guessing a 16:9 aspect when the source
  // has no intrinsic dimensions defeats it (the emitted width/height would be wrong,
  // reintroducing layout shift). Fail loudly instead.
  if (!meta.width || !meta.height) {
    loudFail(
      `Source image has no intrinsic dimensions (width=${meta.width}, height=${meta.height}).\n` +
        "Cannot emit CLS-safe width/height without them — refusing to guess an aspect ratio.\n" +
        "The source may be corrupt, an unsupported format, or an SVG without a viewBox.",
    );
  }
  const intrinsicW = meta.width;
  const intrinsicH = meta.height;
  const aspect = intrinsicH / intrinsicW;

  // Never upscale: cap requested widths at the source width.
  const widths = [...new Set(opts.widths.map((w) => Math.min(w, intrinsicW)))].sort(
    (a, b) => a - b,
  );
  const fallbackExt = opts.fallback === "png" ? "png" : "jpg";

  const produced = [];
  for (const w of widths) {
    for (const [fmt, ext, fn] of [
      ["avif", "avif", (s) => s.avif({ quality: 50 })],
      ["webp", "webp", (s) => s.webp({ quality: 74 })],
      [
        opts.fallback,
        fallbackExt,
        (s) => (opts.fallback === "png" ? s.png() : s.jpeg({ quality: 80, mozjpeg: true })),
      ],
    ]) {
      const outName = `${opts.name}-${w}.${ext}`;
      await fn(sharp(opts.in).resize({ width: w })).toFile(join(opts.outdir, outName));
      produced.push({ fmt, w, file: outName });
    }
  }

  const srcset = (ext) => widths.map((w) => `${opts.name}-${w}.${ext} ${w}w`).join(", ");
  const heroAttrs = opts.lcp
    ? `fetchpriority="high" decoding="async"`
    : `loading="lazy" decoding="async"`;
  const picture = [
    `<picture>`,
    `  <source type="image/avif" srcset="${srcset("avif")}" sizes="${opts.sizes}" />`,
    `  <source type="image/webp" srcset="${srcset("webp")}" sizes="${opts.sizes}" />`,
    `  <img src="${opts.name}-${widths[widths.length - 1]}.${fallbackExt}"`,
    `       srcset="${srcset(fallbackExt)}" sizes="${opts.sizes}"`,
    `       width="${intrinsicW}" height="${intrinsicH}"`,
    `       ${heroAttrs} alt="" />  <!-- set a real alt; run the accessibility gate -->`,
    `</picture>`,
  ].join("\n");

  stdout.write(
    JSON.stringify(
      {
        ok: true,
        source: basename(opts.in),
        intrinsic: {
          width: intrinsicW,
          height: intrinsicH,
          aspectRatio: Number(aspect.toFixed(4)),
        },
        widths,
        formats: ["avif", "webp", opts.fallback],
        produced: produced.length,
        lcp: opts.lcp,
        note: "CLS-safe: width/height set. LCP hero should be eager + fetchpriority=high, capped 1-2/page.",
      },
      null,
      2,
    ) + "\n",
  );
  stdout.write(
    `\n<!-- paste into your template; alt text still required (accessibility gate) -->\n${picture}\n`,
  );
}

main().catch((err) => loudFail(`Unexpected error: ${err?.message ?? err}`));
