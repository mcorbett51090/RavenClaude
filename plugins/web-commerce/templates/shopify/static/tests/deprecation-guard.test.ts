/**
 * Deprecation + secret-hygiene guard — static tier.
 *
 * Enforces two of the plugin's hard invariants over every source file this
 * tier ships (CLAUDE.md §2 #4 and #6, and
 * ../../../knowledge/deprecated-paths-do-not-scaffold.md):
 *
 *   1. No JS Buy SDK / self-hosted-checkout code is emitted (both dead:
 *      hard cutover 2025-07-01 / shutdown 2025-04-01).
 *   2. No secret-shaped string lives outside `.env.example`'s placeholders.
 */
import { readFileSync, readdirSync, statSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const TIER_DIR = path.resolve(__dirname, "..");

function listSourceFiles(
  dir: string,
  exts: string[],
  opts: { skipDirs?: string[] } = {},
): string[] {
  const skipDirs = new Set(["node_modules", ...(opts.skipDirs ?? [])]);
  const out: string[] = [];
  for (const entry of readdirSync(dir)) {
    if (skipDirs.has(entry)) continue;
    const full = path.join(dir, entry);
    const stat = statSync(full);
    if (stat.isDirectory()) {
      out.push(...listSourceFiles(full, exts, opts));
    } else if (exts.some((ext) => entry.endsWith(ext))) {
      out.push(full);
    }
  }
  return out;
}

const DEPRECATED_PATTERNS: Array<{ pattern: RegExp; label: string }> = [
  {
    pattern: /shopify-buy/i,
    label: "Shopify JS Buy SDK package reference (deprecated 2025-07-01)",
  },
  { pattern: /js-buy-sdk/i, label: "Shopify JS Buy SDK reference (deprecated 2025-07-01)" },
  {
    pattern: /\bcheckoutCreate\b/,
    label: "custom Checkout API `checkoutCreate` mutation (shut down 2025-04-01)",
  },
  {
    pattern: /\bCheckout\.create\(/,
    label: "custom Checkout API client call (shut down 2025-04-01)",
  },
  {
    pattern: /\bcheckoutLineItemsAdd\b/,
    label: "custom Checkout API mutation (shut down 2025-04-01)",
  },
];

describe("deprecation guard — no dead Shopify checkout paths", () => {
  // Scans only the RUNTIME code this tier scaffolds into a consumer's repo —
  // provider.ts / webhook.ts / cart.ts. README.md and tests/ are excluded on
  // purpose: the README legitimately NAMES the deprecated paths in prose to
  // explain why they're avoided (required by the task brief), and this test
  // file itself necessarily contains the forbidden strings as pattern
  // literals to check against. Neither is emitted/executable checkout code.
  const files = listSourceFiles(TIER_DIR, [".ts"], { skipDirs: ["tests"] });

  it("scans at least the expected runtime source files (guards against an empty/broken glob)", () => {
    expect(files.length).toBeGreaterThanOrEqual(3);
  });

  for (const file of files) {
    const relative = path.relative(TIER_DIR, file);
    it(`${relative} contains no deprecated checkout path`, () => {
      const contents = readFileSync(file, "utf8");
      for (const { pattern, label } of DEPRECATED_PATTERNS) {
        expect(pattern.test(contents), `${relative} matched forbidden pattern: ${label}`).toBe(
          false,
        );
      }
    });
  }

  it("cart.ts only ever ends checkout at cart.checkoutUrl (hosted redirect)", () => {
    const contents = readFileSync(path.join(TIER_DIR, "cart.ts"), "utf8");
    expect(contents).toMatch(/checkoutUrl/);
    expect(contents).not.toMatch(/checkoutCreate/);
  });
});

describe("secret hygiene — no secret-shaped string outside .env.example", () => {
  // Real-world Shopify secret/token prefixes. A match here (outside
  // .env.example, whose values are all placeholders) means a live credential
  // leaked into source.
  const SECRET_SHAPE_PATTERNS = [/shpat_[a-zA-Z0-9]+/, /shpss_[a-zA-Z0-9]+/, /shpca_[a-zA-Z0-9]+/];

  const files = listSourceFiles(TIER_DIR, [".ts", ".md"]);

  for (const file of files) {
    const relative = path.relative(TIER_DIR, file);
    it(`${relative} contains no secret-shaped string`, () => {
      const contents = readFileSync(file, "utf8");
      for (const pattern of SECRET_SHAPE_PATTERNS) {
        expect(
          pattern.test(contents),
          `${relative} contains what looks like a real Shopify credential`,
        ).toBe(false);
      }
    });
  }

  it(".env.example holds only placeholder values, never a live-shaped secret", () => {
    const contents = readFileSync(path.join(TIER_DIR, ".env.example"), "utf8");
    const assignments = contents
      .split("\n")
      .filter((line) => line.includes("=") && !line.trim().startsWith("#"));
    expect(assignments.length).toBeGreaterThan(0);
    for (const line of assignments) {
      const value = line.split("=")[1]?.trim() ?? "";
      expect(value === "xxx" || value === "xxx.myshopify.com").toBe(true);
    }
  });
});
